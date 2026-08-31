"""Causal GraphSAGE Architecture & Training Pipeline.

Implements the 2-layer GraphSAGE network for heterogeneous temporal transaction graphs:
Layer 1: (28 + 28 + 7) -> 64 -> BatchNorm -> ReLU
Layer 2: 64 -> 32 -> BatchNorm -> ReLU
Output: 32 -> 1 -> Sigmoid

Includes:
- Exact parameter counting via sum(p.size for p in weights)
- Class-imbalance weighted BCE loss
- Out-of-time early stopping on validation PR-AUC
- Real forward propagation with causal relational neighborhood aggregation
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score

from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph


def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35.0, 35.0)))


@dataclass
class CausalGraphSAGE:
    """Vectorized 2-layer GraphSAGE for payment graphs."""

    in_dim_txn: int = 28
    in_dim_agg: int = 28
    in_dim_entity: int = 7
    hidden_dim: int = 64
    out_dim: int = 32
    learning_rate: float = 0.005
    seed: int = 20260827

    def __post_init__(self) -> None:
        rng = np.random.RandomState(self.seed)
        total_in = self.in_dim_txn + self.in_dim_agg + self.in_dim_entity

        # He / Xavier normal initialization
        self.w1 = rng.randn(total_in, self.hidden_dim) * math.sqrt(2.0 / total_in)
        self.b1 = np.zeros(self.hidden_dim, dtype=np.float64)
        self.gamma1 = np.ones(self.hidden_dim, dtype=np.float64)
        self.beta1 = np.zeros(self.hidden_dim, dtype=np.float64)

        self.w2 = rng.randn(self.hidden_dim, self.out_dim) * math.sqrt(2.0 / self.hidden_dim)
        self.b2 = np.zeros(self.out_dim, dtype=np.float64)
        self.gamma2 = np.ones(self.out_dim, dtype=np.float64)
        self.beta2 = np.zeros(self.out_dim, dtype=np.float64)

        self.w_out = rng.randn(self.out_dim, 1) * math.sqrt(2.0 / self.out_dim)
        self.b_out = np.zeros(1, dtype=np.float64)

        # Running stats for BatchNorm
        self.running_mean1 = np.zeros(self.hidden_dim, dtype=np.float64)
        self.running_var1 = np.ones(self.hidden_dim, dtype=np.float64)
        self.running_mean2 = np.zeros(self.out_dim, dtype=np.float64)
        self.running_var2 = np.ones(self.out_dim, dtype=np.float64)

    def count_parameters(self) -> int:
        """Returns the exact parameter count computed directly from weight arrays."""
        params = [
            self.w1, self.b1, self.gamma1, self.beta1,
            self.w2, self.b2, self.gamma2, self.beta2,
            self.w_out, self.b_out,
        ]
        return sum(p.size for p in params)

    def extract_graph_inputs(self, graph: TemporalPaymentGraph, indices: list[int] | np.ndarray) -> np.ndarray:
        """Constructs concatenated node + causal neighborhood + entity input tensors for indices."""
        idx_list = list(indices)
        n = len(idx_list)
        if n == 0:
            return np.empty((0, self.in_dim_txn + self.in_dim_agg + self.in_dim_entity), dtype=np.float64)

        x_tx = graph.x_txn[idx_list]
        x_nbr = np.zeros((n, self.in_dim_agg), dtype=np.float64)
        x_ent = np.zeros((n, self.in_dim_entity), dtype=np.float64)

        for i, idx in enumerate(idx_list):
            x_nbr[i] = graph.get_causal_neighborhood_representation(idx)
            x_ent[i] = graph.get_causal_entity_aggregates(idx)

        raw_concat = np.hstack([x_tx, x_nbr, x_ent])
        raw_concat = np.nan_to_num(raw_concat, nan=0.0, posinf=0.0, neginf=0.0)
        return np.tanh(np.clip(raw_concat, -1e4, 1e4) / 100.0)

    def forward(self, x_in: np.ndarray, training: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Forward pass through GraphSAGE layers."""
        if len(x_in) == 0:
            return np.empty((0, 1)), np.empty((0, self.out_dim)), np.empty((0, self.hidden_dim))

        # Layer 1
        z1 = x_in @ self.w1 + self.b1
        if training:
            mean1 = np.mean(z1, axis=0)
            var1 = np.var(z1, axis=0) + 1e-5
            self.running_mean1 = 0.9 * self.running_mean1 + 0.1 * mean1
            self.running_var1 = 0.9 * self.running_var1 + 0.1 * var1
            z1_norm = (z1 - mean1) / np.sqrt(var1)
        else:
            z1_norm = (z1 - self.running_mean1) / np.sqrt(self.running_var1 + 1e-5)
        h1 = _relu(z1_norm * self.gamma1 + self.beta1)

        # Layer 2
        z2 = h1 @ self.w2 + self.b2
        if training:
            mean2 = np.mean(z2, axis=0)
            var2 = np.var(z2, axis=0) + 1e-5
            self.running_mean2 = 0.9 * self.running_mean2 + 0.1 * mean2
            self.running_var2 = 0.9 * self.running_var2 + 0.1 * var2
            z2_norm = (z2 - mean2) / np.sqrt(var2)
        else:
            z2_norm = (z2 - self.running_mean2) / np.sqrt(self.running_var2 + 1e-5)
        h2 = _relu(z2_norm * self.gamma2 + self.beta2)

        # Output projection
        logits = h2 @ self.w_out + self.b_out
        probs = _sigmoid(logits).ravel()

        return probs, h2, h1

    def predict_proba(self, graph: TemporalPaymentGraph, indices: list[int] | np.ndarray) -> np.ndarray:
        """Computes fraud probabilities for target transaction indices."""
        x_in = self.extract_graph_inputs(graph, indices)
        probs, _, _ = self.forward(x_in, training=False)
        return probs

    def get_embeddings(self, graph: TemporalPaymentGraph, indices: list[int] | np.ndarray) -> np.ndarray:
        """Extracts 32-dimensional causal graph embeddings for target transaction indices."""
        x_in = self.extract_graph_inputs(graph, indices)
        _, h2, _ = self.forward(x_in, training=False)
        return h2

    def fit(
        self,
        graph: TemporalPaymentGraph,
        train_indices: list[int] | np.ndarray,
        val_indices: list[int] | np.ndarray,
        max_epochs: int = 40,
        patience: int = 10,
    ) -> dict[str, Any]:
        """Trains CausalGraphSAGE using class-weighted Adam on train_indices with early stopping on val_indices."""
        x_train = self.extract_graph_inputs(graph, train_indices)
        y_train = graph.is_fraud[train_indices].astype(np.float64)

        x_val = self.extract_graph_inputs(graph, val_indices)
        y_val = graph.is_fraud[val_indices].astype(np.float64)

        n_train = len(y_train)
        n_pos = int(np.sum(y_train))
        n_neg = n_train - n_pos
        scale_pos_weight = float(n_neg / max(1, n_pos))

        # Adam optimizer state
        m_w1, v_w1 = np.zeros_like(self.w1), np.zeros_like(self.w1)
        m_b1, v_b1 = np.zeros_like(self.b1), np.zeros_like(self.b1)
        m_w2, v_w2 = np.zeros_like(self.w2), np.zeros_like(self.w2)
        m_b2, v_b2 = np.zeros_like(self.b2), np.zeros_like(self.b2)
        m_w_out, v_w_out = np.zeros_like(self.w_out), np.zeros_like(self.w_out)
        m_b_out, v_b_out = np.zeros_like(self.b_out), np.zeros_like(self.b_out)

        beta1, beta2, eps = 0.9, 0.999, 1e-8
        best_val_pr_auc = -1.0
        best_weights: dict[str, np.ndarray] = {}
        patience_counter = 0

        # Batch training
        batch_size = min(256, n_train)
        n_batches = int(np.ceil(n_train / batch_size))

        for epoch in range(1, max_epochs + 1):
            perm = np.random.permutation(n_train)
            x_shuffled = x_train[perm]
            y_shuffled = y_train[perm]

            epoch_loss = 0.0

            for b in range(n_batches):
                start = b * batch_size
                end = min(start + batch_size, n_train)
                xb = x_shuffled[start:end]
                yb = y_shuffled[start:end]

                probs, h2, h1 = self.forward(xb, training=True)
                
                # Weighted BCE gradient
                # loss = - (w * y * log(p) + (1-y) * log(1-p))
                weights = np.where(yb == 1.0, scale_pos_weight, 1.0)
                dlogits = weights * (probs - yb) / len(yb)
                dlogits = dlogits.reshape(-1, 1)

                # Gradients for output layer
                dw_out = h2.T @ dlogits
                db_out = np.sum(dlogits, axis=0)

                # Gradients for Layer 2
                dh2 = dlogits @ self.w_out.T
                dz2 = dh2 * (h2 > 0)
                dw2 = h1.T @ dz2
                db2 = np.sum(dz2, axis=0)

                # Gradients for Layer 1
                dh1 = dz2 @ self.w2.T
                dz1 = dh1 * (h1 > 0)
                dw1 = xb.T @ dz1
                db1 = np.sum(dz1, axis=0)

                # Adam updates
                t_step = (epoch - 1) * n_batches + b + 1
                for param, grad, m, v in [
                    (self.w1, dw1, m_w1, v_w1),
                    (self.b1, db1, m_b1, v_b1),
                    (self.w2, dw2, m_w2, v_w2),
                    (self.b2, db2, m_b2, v_b2),
                    (self.w_out, dw_out, m_w_out, v_w_out),
                    (self.b_out, db_out, m_b_out, v_b_out),
                ]:
                    m_hat = m / (1 - beta1 ** t_step)
                    v_hat = v / (1 - beta2 ** t_step)
                    update = self.learning_rate * m_hat / (np.sqrt(v_hat) + eps)
                    param -= np.nan_to_num(update, nan=0.0, posinf=0.0, neginf=0.0)

            # Validation evaluation
            val_probs, _, _ = self.forward(x_val, training=False)
            if np.sum(y_val) > 0 and len(y_val) > np.sum(y_val):
                val_pr_auc = float(average_precision_score(y_val, val_probs))
            else:
                val_pr_auc = 0.5

            if val_pr_auc > best_val_pr_auc:
                best_val_pr_auc = val_pr_auc
                patience_counter = 0
                best_weights = {
                    "w1": self.w1.copy(), "b1": self.b1.copy(),
                    "w2": self.w2.copy(), "b2": self.b2.copy(),
                    "w_out": self.w_out.copy(), "b_out": self.b_out.copy(),
                    "running_mean1": self.running_mean1.copy(), "running_var1": self.running_var1.copy(),
                    "running_mean2": self.running_mean2.copy(), "running_var2": self.running_var2.copy(),
                }
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    break

        # Restore best weights
        if best_weights:
            self.w1 = best_weights["w1"]
            self.b1 = best_weights["b1"]
            self.w2 = best_weights["w2"]
            self.b2 = best_weights["b2"]
            self.w_out = best_weights["w_out"]
            self.b_out = best_weights["b_out"]
            self.running_mean1 = best_weights["running_mean1"]
            self.running_var1 = best_weights["running_var1"]
            self.running_mean2 = best_weights["running_mean2"]
            self.running_var2 = best_weights["running_var2"]

        return {
            "epochs_trained": epoch,
            "best_val_pr_auc": best_val_pr_auc,
            "parameter_count": self.count_parameters(),
            "scale_pos_weight": scale_pos_weight,
        }


def get_parameter_count(model: Any) -> int:
    """Computes exact parameter count for any model."""
    if hasattr(model, "count_parameters"):
        return model.count_parameters()
    if hasattr(model, "parameters"):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    return 0
