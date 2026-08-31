"""Drift Detection Module.

Implements lightweight statistical drift monitoring (e.g. KS test) 
on feature distributions to trigger challenger evaluations without
bypassing governance.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any
import numpy as np
from scipy.stats import ks_2samp
import polars as pl

from mcdl.config import REPO_ROOT, load_config
from mcdl.features.batch import compute_batch_features
from mcdl.world.generator import generate_world

class DriftDetector:
    def __init__(self, reference_df: pl.DataFrame, features_to_monitor: list[str]):
        self.reference_data = {
            f: reference_df[f].drop_nulls().to_numpy() for f in features_to_monitor
        }
        self.features_to_monitor = features_to_monitor
        self.p_value_threshold = 0.05
        
    def detect(self, current_df: pl.DataFrame) -> dict[str, Any]:
        drift_results = {}
        drift_detected = False
        
        for f in self.features_to_monitor:
            ref = self.reference_data.get(f)
            cur = current_df[f].drop_nulls().to_numpy()
            
            if ref is None or len(ref) == 0 or len(cur) == 0:
                continue
                
            stat, p_val = ks_2samp(ref, cur)
            is_drifted = bool(p_val < self.p_value_threshold)
            drift_results[f] = {
                "ks_stat": round(float(stat), 4),
                "p_value": round(float(p_val), 4),
                "drift_detected": is_drifted
            }
            if is_drifted:
                drift_detected = True
                
        return {
            "overall_drift": drift_detected,
            "feature_drift": drift_results,
            "action": "TRIGGER_INVESTIGATION" if drift_detected else "NORMAL"
        }

class DriftRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "DRIFT"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self):
        print("Starting Drift Detection...")
        start_time = time.perf_counter()
        
        cfg = load_config(scale="tiny")
        world = generate_world(cfg)
        feature_df = compute_batch_features(world.transactions, customers=world.customers)
        
        train_idx = int(len(feature_df) * 0.5)
        reference_df = feature_df[:train_idx]
        current_df = feature_df[train_idx:]
        
        # Induce synthetic drift in current_df to ensure we catch it
        shifted = current_df["amount"].to_numpy() * 1.5
        current_df = current_df.with_columns(pl.Series("amount", shifted))
        
        detector = DriftDetector(reference_df, features_to_monitor=["amount", "cust_velocity_1h_count"])
        result = detector.detect(current_df)
        
        output = {
            "experiment_id": "DRIFT",
            "metrics": result,
            "status": "COMPLETED",
            "runtime": time.perf_counter() - start_time
        }
        
        with open(self.output_dir / "metrics.json", "w") as f:
            json.dump(output, f, indent=2)
            
        with open(self.output_dir / "status.json", "w") as f:
            json.dump({"status": "COMPLETED"}, f)
            
        print("Drift Detection completed.")

if __name__ == "__main__":
    DriftRunner().run()
