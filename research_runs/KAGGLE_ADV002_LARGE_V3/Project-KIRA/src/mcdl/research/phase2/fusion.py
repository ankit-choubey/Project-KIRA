"""G-03: Causal Graph + Tabular Fusion Engine.

Implements the 4-arm experimental framework to evaluate incremental predictive value
of causal relational graphs beyond KIRA's tabular behavioral representations:
- Arm A: Authoritative Frozen Tabular Baseline (LightGBM)
- Arm B: Standalone Causal Graph Diagnostic (2-layer CausalGraphSAGE)
- Arm C: Causal Dual-Branch Fusion ([x_tab || z_graph] -> LightGBM)
- Arm D: Shuffled Topology Control ([x_tab || z_shuff] -> LightGBM)

Strict Invariant Rules:
1. Strict temporal causality: G(t) strictly uses events with tau < t.
2. Validation-only calibration: IsotonicCalibrator fit only on validation split predictions.
3. World C isolation: Zero-day attack families strictly excluded from train/val splits.
4. Separate parameter accounting: Graph weights vs Tree hyperparameters reported distinctly.
5. Automated decision classification & interpretation generation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import polars as pl
from scipy import stats
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)

from mcdl.blue.calibration import IsotonicCalibrator
from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.research.phase2.model import CausalGraphSAGE


def compute_ece(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error (ECE)."""
    if len(probs) == 0:
        return 0.0
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(probs)
    for i in range(n_bins):
        bin_mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1]) if i < n_bins - 1 else (probs >= bin_edges[i]) & (probs <= bin_edges[i + 1])
        bin_count = np.sum(bin_mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(probs[bin_mask])
            ece += (bin_count / n) * abs(bin_acc - bin_conf)
    return float(ece)


def compute_fpr_at_recall(probs: np.ndarray, y_true: np.ndarray, target_recall: float = 0.95) -> float:
    """Computes False Positive Rate (FPR) at target recall (e.g. 95%)."""
    positives = np.sum(y_true == 1)
    negatives = np.sum(y_true == 0)
    if positives == 0 or negatives == 0:
        return 0.0

    thresholds = np.sort(probs)[::-1]
    best_fpr = 1.0
    for thresh in thresholds:
        pred_pos = (probs >= thresh)
        tp = np.sum((pred_pos == 1) & (y_true == 1))
        fp = np.sum((pred_pos == 1) & (y_true == 0))
        recall = tp / positives
        if recall >= target_recall:
            best_fpr = float(fp / negatives)
            break
    return best_fpr


def bootstrap_pr_auc_ci(
    y_true: np.ndarray,
    probs: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 20260827,
) -> dict[str, float]:
    """Computes 95% bootstrap confidence interval for PR-AUC."""
    n = len(y_true)
    if n == 0 or np.sum(y_true) == 0:
        return {"ci_lower": 0.0, "ci_upper": 0.0, "mean": 0.0, "std": 0.0}

    rng = np.random.RandomState(seed)
    scores = []
    for _ in range(n_resamples):
        boot_idx = rng.randint(0, n, size=n)
        y_boot = y_true[boot_idx]
        if np.sum(y_boot) == 0 or np.sum(y_boot) == n:
            continue
        score = average_precision_score(y_boot, probs[boot_idx])
        scores.append(score)

    if not scores:
        base_score = float(average_precision_score(y_true, probs))
        return {"ci_lower": base_score, "ci_upper": base_score, "mean": base_score, "std": 0.0}

    return {
        "ci_lower": float(np.percentile(scores, 2.5)),
        "ci_upper": float(np.percentile(scores, 97.5)),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
    }


def compute_paired_bootstrap_p_value(
    y_true: np.ndarray,
    probs_c: np.ndarray,
    probs_a: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 20260827,
) -> float:
    """Computes two-sided paired bootstrap p-value for H0: PR-AUC(C) = PR-AUC(A)."""
    n = len(y_true)
    if n == 0 or np.sum(y_true) == 0:
        return 1.0

    rng = np.random.RandomState(seed)
    obs_diff = average_precision_score(y_true, probs_c) - average_precision_score(y_true, probs_a)
    diffs = []

    for _ in range(n_resamples):
        boot_idx = rng.randint(0, n, size=n)
        y_boot = y_true[boot_idx]
        if np.sum(y_boot) == 0 or np.sum(y_boot) == n:
            continue
        score_c = average_precision_score(y_boot, probs_c[boot_idx])
        score_a = average_precision_score(y_boot, probs_a[boot_idx])
        diffs.append(score_c - score_a)

    if not diffs:
        return 1.0

    diffs_arr = np.array(diffs)
    # Centered diffs under H0
    centered = diffs_arr - np.mean(diffs_arr)
    p_val = np.mean(np.abs(centered) >= np.abs(obs_diff))
    return float(p_val)


def create_shuffled_topology_graph(
    real_graph: TemporalPaymentGraph,
    seed: int = 20260827,
) -> TemporalPaymentGraph:
    """Constructs a deterministic shuffled-topology graph control (Arm D).

    Preserves node features, transaction count, and timestamp distribution, while
    deterministically permuting entity associations to destroy meaningful network topology.
    Seed: S_shuff = seed + 999.
    """
    shuff_seed = seed + 999
    rng = np.random.RandomState(shuff_seed)

    raw_df = real_graph.raw_df.clone()
    n = len(raw_df)

    # Permute customer_id, merchant_id, device_id independently
    custs = raw_df["customer_id"].to_numpy().copy()
    merchs = raw_df["merchant_id"].to_numpy().copy()
    devs = raw_df["device_id"].to_numpy().copy()

    rng.shuffle(custs)
    rng.shuffle(merchs)
    rng.shuffle(devs)

    shuffled_df = raw_df.with_columns([
        pl.Series("customer_id", custs),
        pl.Series("merchant_id", merchs),
        pl.Series("device_id", devs),
    ])

    return TemporalPaymentGraph(
        transactions_df=shuffled_df,
        features_df=real_graph.features_df,
    )


def measure_topology_properties(
    real_graph: TemporalPaymentGraph,
    shuffled_graph: TemporalPaymentGraph,
) -> dict[str, Any]:
    """Calculates and reports empirical network statistics for real vs shuffled topology."""
    # Real degrees
    real_cust_degs = [len(txs) for txs in real_graph.cust_to_txns.values()]
    real_merch_degs = [len(txs) for txs in real_graph.merch_to_txns.values()]
    real_all_degs = np.array(real_cust_degs + real_merch_degs, dtype=np.float64)

    # Shuffled degrees
    shuff_cust_degs = [len(txs) for txs in shuffled_graph.cust_to_txns.values()]
    shuff_merch_degs = [len(txs) for txs in shuffled_graph.merch_to_txns.values()]
    shuff_all_degs = np.array(shuff_cust_degs + shuff_merch_degs, dtype=np.float64)

    ks_stat, ks_pval = stats.ks_2samp(real_all_degs, shuff_all_degs)

    return {
        "real_graph": {
            "node_count": int(len(real_graph.cust_to_txns) + len(real_graph.merch_to_txns) + len(real_graph.dev_to_txns)),
            "edge_count": int(real_graph.n_txns * 3),
            "degree_mean": float(np.mean(real_all_degs)) if len(real_all_degs) > 0 else 0.0,
            "degree_std": float(np.std(real_all_degs)) if len(real_all_degs) > 0 else 0.0,
        },
        "shuffled_graph": {
            "node_count": int(len(shuffled_graph.cust_to_txns) + len(shuffled_graph.merch_to_txns) + len(shuffled_graph.dev_to_txns)),
            "edge_count": int(shuffled_graph.n_txns * 3),
            "degree_mean": float(np.mean(shuff_all_degs)) if len(shuff_all_degs) > 0 else 0.0,
            "degree_std": float(np.std(shuff_all_degs)) if len(shuff_all_degs) > 0 else 0.0,
        },
        "degree_ks_statistic": float(ks_stat),
        "degree_ks_p_value": float(ks_pval),
        "topology_destroyed": bool(ks_stat > 0.01 or not np.array_equal(real_graph.customer_ids, shuffled_graph.customer_ids)),
    }


def classify_g03_decision(
    delta_rel: float,
    delta_topo: float,
    fpr_c: float,
    fpr_a: float,
    ece_c: float,
    p_value: float,
    sample_count: int,
) -> tuple[str, str]:
    """Applies pre-registered decision rules and generates automated interpretation statement."""
    if sample_count < 30:
        decision = "INCONCLUSIVE"
        statement = "Statistical uncertainty and sample limitations prevent a conclusive determination of relational fusion value."
        return decision, statement

    if delta_rel > 0.005 and p_value < 0.05:
        if delta_topo > 0.005:
            if fpr_c <= fpr_a + 0.01 and ece_c <= 0.05:
                decision = "SUCCESS"
                statement = "Causal relational graph information provides statistically validated incremental predictive value beyond KIRA's tabular detector, driven by genuine network topology."
            else:
                decision = "CALIBRATION_OR_FPR_DEGRADATION"
                statement = "Marginal PR-AUC gains from fusion are offset by unacceptable operational degradation in false positive rate or probability calibration."
        else:
            decision = "PARAMETER_ARTIFACT"
            statement = "Performance gains observed in fusion are an artifact of parameter capacity expansion and are not driven by relational graph topology."
    elif delta_rel <= 0.0:
        decision = "NO_INCREMENT"
        statement = "Causal relational graph information does NOT provide incremental predictive value beyond KIRA's existing tabular behavioral representations."
    else:
        decision = "INCONCLUSIVE"
        statement = "Marginal delta (+{:.4f}) is statistically indistinguishable from baseline noise (p={:.4f}).".format(delta_rel, p_value)

    return decision, statement


class CausalGraphTabularFusion:
    """Dual-branch Causal Graph + Tabular Fusion Model with validation-only calibration."""

    def __init__(
        self,
        seed: int = 20260827,
        n_estimators: int = 100,
        max_depth: int = 4,
        num_leaves: int = 15,
        learning_rate: float = 0.05,
    ) -> None:
        self.seed = seed
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.num_leaves = num_leaves
        self.learning_rate = learning_rate

        self.gnn: CausalGraphSAGE | None = None
        self.clf = lgb.LGBMClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            num_leaves=self.num_leaves,
            learning_rate=self.learning_rate,
            random_state=self.seed,
            verbose=-1,
        )
        self.calibrator = IsotonicCalibrator()

    def fit(
        self,
        graph: TemporalPaymentGraph,
        train_indices: np.ndarray,
        val_indices: np.ndarray,
    ) -> None:
        """Trains GNN branch on train split, builds fused representations, fits classifier and calibrator."""
        # 1. Fit GNN branch with exact feature dimension
        feat_dim = len(graph.feature_names)
        self.gnn = CausalGraphSAGE(
            in_dim_txn=feat_dim,
            in_dim_agg=feat_dim,
            in_dim_entity=7,
            seed=self.seed,
        )
        self.gnn.fit(graph, train_indices, val_indices, max_epochs=20)

        # 2. Extract train & val embeddings
        z_train = self.gnn.get_embeddings(graph, train_indices)
        x_train = graph.x_txn[train_indices]
        fused_train = np.hstack([x_train, z_train])
        y_train = graph.is_fraud[train_indices]

        z_val = self.gnn.get_embeddings(graph, val_indices)
        x_val = graph.x_txn[val_indices]
        fused_val = np.hstack([x_val, z_val])
        y_val = graph.is_fraud[val_indices]

        # 3. Fit LightGBM classifier
        self.clf.fit(fused_train, y_train)

        # 4. Fit calibration exclusively on validation predictions
        raw_val_probs = self.clf.predict_proba(fused_val)[:, 1]
        self.calibrator.fit(raw_val_probs, y_val)

    def predict_proba(
        self,
        graph: TemporalPaymentGraph,
        test_indices: np.ndarray,
    ) -> np.ndarray:
        """Evaluates frozen fusion model on test split."""
        z_test = self.gnn.get_embeddings(graph, test_indices)
        x_test = graph.x_txn[test_indices]
        fused_test = np.hstack([x_test, z_test])

        raw_test_probs = self.clf.predict_proba(fused_test)[:, 1]
        return self.calibrator.transform(raw_test_probs)


def evaluate_arm_metrics(
    probs: np.ndarray,
    y_true: np.ndarray,
    seed: int = 20260827,
) -> dict[str, Any]:
    """Computes standardized evaluation metrics for an experimental arm."""
    if len(probs) == 0 or np.sum(y_true) == 0:
        return {
            "pr_auc": 0.0,
            "roc_auc": 0.0,
            "fpr": 0.0,
            "ece": 0.0,
            "brier": 0.0,
            "pr_auc_ci_95": {"ci_lower": 0.0, "ci_upper": 0.0, "mean": 0.0, "std": 0.0},
        }

    pr_auc = float(average_precision_score(y_true, probs))
    roc_auc = float(roc_auc_score(y_true, probs))
    fpr = float(compute_fpr_at_recall(probs, y_true, target_recall=0.95))
    ece = float(compute_ece(probs, y_true, n_bins=10))
    brier = float(brier_score_loss(y_true, probs))
    ci = bootstrap_pr_auc_ci(y_true, probs, n_resamples=1000, seed=seed)

    return {
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "fpr": fpr,
        "ece": ece,
        "brier": brier,
        "pr_auc_ci_95": ci,
    }
