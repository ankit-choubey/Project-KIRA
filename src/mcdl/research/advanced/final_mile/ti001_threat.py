"""TI-001 Threat Intelligence Enrichment Harness.

Evaluates performance gains from simulated Threat Intelligence (TI) 
records (e.g., compromised devices, suspicious IPs).
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any
import numpy as np
import polars as pl
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from mcdl.config import REPO_ROOT, load_config
from mcdl.features.batch import compute_batch_features
from mcdl.research.advanced.adv003.challenger import ChallengerDetector
from mcdl.world.generator import generate_world

class SyntheticThreatIntel:
    """Mock Threat Intelligence Feed."""
    def __init__(self, txns: list[Any], fraud_ratio: float = 0.5):
        self.compromised_devices = set()
        self.suspicious_ips = set()
        self.compromised_merchants = set()
        
        # Populate with some deterministic subset of actual fraudsters
        self.txn_map = {t.txn_id: t for t in txns}
        fraud_txns = [t for t in txns if t.is_fraud]
        for t in fraud_txns[:int(len(fraud_txns) * fraud_ratio)]:
            if getattr(t, "device_id", None): self.compromised_devices.add(t.device_id)
            if getattr(t, "ip_prefix", None): self.suspicious_ips.add(t.ip_prefix)
            if getattr(t, "merchant_id", None): self.compromised_merchants.add(t.merchant_id)

    def enrich(self, feature_df: pl.DataFrame) -> pl.DataFrame:
        """Adds TI risk flags to feature dataframe."""
        device_flag = [1 if getattr(self.txn_map.get(txn_id), "device_id", None) in self.compromised_devices else 0 for txn_id in feature_df["txn_id"]]
        ip_flag = [1 if getattr(self.txn_map.get(txn_id), "ip_prefix", None) in self.suspicious_ips else 0 for txn_id in feature_df["txn_id"]]
        merch_flag = [1 if getattr(self.txn_map.get(txn_id), "merchant_id", None) in self.compromised_merchants else 0 for txn_id in feature_df["txn_id"]]
        
        # We synthesize a TI Risk Score (0.0 to 1.0)
        ti_score = np.array(device_flag) * 0.4 + np.array(ip_flag) * 0.3 + np.array(merch_flag) * 0.3
        
        return feature_df.with_columns(
            pl.Series("ti_risk_score", ti_score)
        )

class TI001Runner:
    def __init__(self, scale: str = "smoke", output_dir: Path | str | None = None):
        self.scale = scale
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "TI-001"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate(self, detector: ChallengerDetector, df: pl.DataFrame, has_ti: bool) -> dict[str, Any]:
        X = df.select(detector.feature_names).to_numpy()
        y_true = df["is_fraud"].to_numpy()
        
        probs = detector.model.predict_proba(X)[:, 1]
        
        # If TI is present, we adjust the probability directly as an ensemble or just append it to features.
        # But wait, the model wasn't trained on TI. The prompt says:
        # "TI must provide context. It must never independently issue final payment decision."
        # So we can fuse TI score with calibrated model score before routing.
        cal_probs = detector.calibrator.transform(probs)
        
        if has_ti and "ti_risk_score" in df.columns:
            ti_scores = df["ti_risk_score"].to_numpy()
            # Simple Bayesian-like update or weighted average
            fused_probs = 0.7 * cal_probs + 0.3 * ti_scores
        else:
            fused_probs = cal_probs
            
        decisions = []
        dict_records = df.to_dicts()
        for i, row in enumerate(dict_records):
            dec = detector.router.route(
                txn_id=row["txn_id"],
                amount=row["amount"],
                risk_score=probs[i],
                calibrated_score=fused_probs[i],
                feature_dict=row
            )
            decisions.append(dec.decision.value)
            
        y_pred_binary = np.array([1 if d != "ALLOW" else 0 for d in decisions])
        
        pr_auc = float(average_precision_score(y_true, probs)) if len(np.unique(y_true)) > 1 else 0.0
        
        fp = np.sum((y_pred_binary == 1) & (y_true == 0))
        tn = np.sum((y_pred_binary == 0) & (y_true == 0))
        fpr = float(fp / max(1, (fp + tn)))
        
        fn = np.sum((y_pred_binary == 0) & (y_true == 1))
        tp = np.sum((y_pred_binary == 1) & (y_true == 1))
        asr = float(fn / max(1, (fn + tp)))
        
        brier = float(brier_score_loss(y_true, fused_probs))
        
        return {
            "PR_AUC": round(pr_auc, 4),
            "FPR": round(fpr, 4),
            "ASR": round(asr, 4),
            "Brier": round(brier, 4),
            "false_positive_change": 0.0, # Computed later
            "time_to_detection": 0.0      # Not applicable in static batch
        }

    def run(self):
        print("Starting TI-001 Threat Intelligence...")
        start_time = time.perf_counter()
        
        cfg = load_config(scale="tiny" if self.scale == "smoke" else "small")
        world = generate_world(cfg)
        feature_df = compute_batch_features(world.transactions, customers=world.customers)
        
        train_df = feature_df[:int(len(feature_df)*0.7)]
        eval_df = feature_df[int(len(feature_df)*0.7):]
        
        detector = ChallengerDetector(model_version="ti001_base")
        from mcdl.research.advanced.adv003.knowledge import DefensiveKnowledgeStore
        detector.fit_with_defensive_replay(train_df, train_df, DefensiveKnowledgeStore(self.output_dir))
        
        # 1. Baseline Evaluate
        res_baseline = self.evaluate(detector, eval_df, has_ti=False)
        
        # 2. Enrich with Threat Intel
        ti_feed = SyntheticThreatIntel(world.transactions)
        enriched_eval_df = ti_feed.enrich(eval_df)
        
        # 3. Evaluate with TI
        res_ti = self.evaluate(detector, enriched_eval_df, has_ti=True)
        
        res_ti["false_positive_change"] = round(res_ti["FPR"] - res_baseline["FPR"], 4)
        
        output = {
            "experiment_id": "TI-001",
            "metrics": {
                "baseline": res_baseline,
                "with_ti": res_ti
            },
            "deltas": {
                "ASR_reduction": round(res_baseline["ASR"] - res_ti["ASR"], 4),
                "FPR_increase": round(res_ti["FPR"] - res_baseline["FPR"], 4)
            },
            "status": "COMPLETED",
            "runtime": time.perf_counter() - start_time
        }
        
        with open(self.output_dir / "metrics.json", "w") as f:
            json.dump(output, f, indent=2)
            
        with open(self.output_dir / "status.json", "w") as f:
            json.dump({"status": "COMPLETED"}, f)
            
        print("TI-001 completed.")

if __name__ == "__main__":
    TI001Runner().run()
