"""OPS-002 Degraded Telemetry Harness.

Evaluates defense resilience against missing signals and implements
explicit fallback gating to prevent silent failure to ALLOW.
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
from mcdl.schemas import Decision

class DegradedTelemetryRouter:
    """Wrapper that enforces safe fallback on missing telemetry."""
    def __init__(self, base_router):
        self.base_router = base_router
        self.required_signals = [
            "is_new_device", "cust_device_txn_count",
            "cust_ip_txn_count", "speed_kmh"
        ]
        
    def route(self, txn_id, amount, risk_score, calibrated_score, feature_dict, **kwargs):
        # Explicit governed fallback path
        missing = [f for f in self.required_signals if feature_dict.get(f) is None or np.isnan(feature_dict.get(f))]
        
        from mcdl.schemas import BlueDecision
        if len(missing) >= 2:
            return BlueDecision(
                txn_id=txn_id,
                risk_score=risk_score,
                calibrated_score=calibrated_score,
                decision=Decision.STEP_UP,
                reason_codes=["DEGRADED_TELEMETRY_FALLBACK"]
            )
            
        return self.base_router.route(txn_id, amount, risk_score, calibrated_score, feature_dict, **kwargs)

class OPS002Runner:
    def __init__(self, scale: str = "smoke", output_dir: Path | str | None = None):
        self.scale = scale
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "OPS-002"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self):
        print("Starting OPS-002 Degraded Telemetry Harness...")
        start_time = time.perf_counter()
        
        cfg = load_config(scale="tiny" if self.scale == "smoke" else "small")
        world = generate_world(cfg)
        feature_df = compute_batch_features(world.transactions, customers=world.customers)
        
        # Train baseline model
        train_df = feature_df[:int(len(feature_df)*0.7)]
        eval_df = feature_df[int(len(feature_df)*0.7):]
        
        detector = ChallengerDetector(model_version="ops002_base")
        from mcdl.research.advanced.adv003.knowledge import DefensiveKnowledgeStore
        detector.fit_with_defensive_replay(train_df, train_df, DefensiveKnowledgeStore(self.output_dir))
        
        # Decorate the router
        detector.router = DegradedTelemetryRouter(detector.router)
        
        scenarios = {
            "full_telemetry": [],
            "missing_device": ["is_new_device", "cust_device_txn_count"],
            "missing_ip": ["cust_ip_txn_count", "speed_kmh"],
            "missing_merchant_history": ["merch_txns_1h", "merch_txns_24h"],
            "partial_graph": ["agent_txn_count", "cust_merch_txn_count"],
            "delayed_label_state": ["cust_amount_to_avg_ratio", "auth_failed_count"],
            "multiple_missing_signals": [
                "is_new_device", "cust_ip_txn_count", "agent_txn_count", "merch_txns_1h"
            ]
        }
        
        results = {}
        for scenario_name, drop_cols in scenarios.items():
            mod_df = eval_df.clone()
            
            for col in drop_cols:
                if col in mod_df.columns:
                    mod_df = mod_df.with_columns(pl.lit(np.nan).alias(col))
                    
            X = mod_df.select(detector.feature_names).to_numpy()
            y_true = mod_df["is_fraud"].to_numpy()
            
            # Predict
            probs = detector.model.predict_proba(X)[:, 1]
            cal_probs = detector.calibrator.transform(probs)
            
            # Route decisions
            decisions = []
            dict_records = mod_df.to_dicts()
            
            for i, row in enumerate(dict_records):
                dec = detector.router.route(
                    txn_id=row["txn_id"],
                    amount=row["amount"],
                    risk_score=probs[i],
                    calibrated_score=cal_probs[i],
                    feature_dict=row
                )
                decisions.append(dec.decision.value)
                
            y_pred_binary = np.array([1 if d != "ALLOW" else 0 for d in decisions])
            
            pr_auc = float(average_precision_score(y_true, probs)) if len(np.unique(y_true)) > 1 else 0.0
            
            # FPR = FP / N
            fp = np.sum((y_pred_binary == 1) & (y_true == 0))
            tn = np.sum((y_pred_binary == 0) & (y_true == 0))
            fpr = float(fp / max(1, (fp + tn)))
            
            # ASR = FN / P
            fn = np.sum((y_pred_binary == 0) & (y_true == 1))
            tp = np.sum((y_pred_binary == 1) & (y_true == 1))
            asr = float(fn / max(1, (fn + tp)))
            
            brier = float(brier_score_loss(y_true, cal_probs))
            
            dec_dist = {
                "ALLOW": decisions.count("ALLOW"),
                "STEP_UP": decisions.count("STEP_UP"),
                "BLOCK": decisions.count("BLOCK")
            }
            
            results[scenario_name] = {
                "PR_AUC": round(pr_auc, 4),
                "FPR": round(fpr, 4),
                "ASR": round(asr, 4),
                "Brier": round(brier, 4),
                "decision_distribution": dec_dist,
                "fallback_activated": dec_dist["STEP_UP"] > 0 and len(drop_cols) > 0
            }
            
        with open(self.output_dir / "metrics.json", "w") as f:
            json.dump(results, f, indent=2)
            
        with open(self.output_dir / "status.json", "w") as f:
            json.dump({"status": "COMPLETED", "runtime": time.perf_counter() - start_time}, f)
        print("OPS-002 completed.")

if __name__ == "__main__":
    OPS002Runner().run()
