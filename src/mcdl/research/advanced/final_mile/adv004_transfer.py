"""ADV-004 Attack Transferability Module.

Evaluates how defensive knowledge against one attack family generalizes
to held-out attack families.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any
import numpy as np
import polars as pl

from mcdl.config import REPO_ROOT, load_config
from mcdl.features.batch import compute_batch_features
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.search import AttackFamily, RedSearchEngine
from mcdl.research.advanced.adv003.challenger import ChallengerDetector
from mcdl.research.advanced.adv003.knowledge import DefensiveKnowledgeStore
from mcdl.world.generator import generate_world

class ADV004Runner:
    def __init__(self, scale: str = "smoke", output_dir: Path | str | None = None):
        self.scale = scale
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "ADV-004"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.families = [
            AttackFamily.BURST_DRAIN,
            AttackFamily.SLOW_SIPHON,
            AttackFamily.GEO_HOP,
            AttackFamily.AGENT_SUBVERSION,
            AttackFamily.CROSS_MERCHANT_FANOUT,
        ]
        
    def run(self):
        print("Starting ADV-004 Transferability Matrix generation...")
        start_time = time.perf_counter()
        
        cfg = load_config(scale="tiny" if self.scale == "smoke" else "small")
        world = generate_world(cfg)
        feature_df = compute_batch_features(world.transactions, customers=world.customers)
        
        # Partition data for base training vs evaluation
        n_total = len(feature_df)
        train_idx = int(n_total * 0.70)
        base_train_df = feature_df[:train_idx]
        eval_txns = world.transactions[train_idx:]
        
        # Base engine
        rolling_extractor = StreamingFeatureExtractor()
        for t in world.transactions[:train_idx]:
            rolling_extractor.extract(t)
            
        matrix = {}
        for f in self.families:
            matrix[f.value] = {}
            for e in self.families:
                matrix[f.value][e.value] = {
                    "ASR": 0.0,
                    "sample_count": 0,
                    "confidence_interval": [0.0, 0.0],
                    "model_version": f"blue_v01_{f.value}",
                    "training_family": f.value,
                    "evaluation_family": e.value,
                    "seed": 20260831,
                    "artifact": f"matrix_{f.value}_{e.value}.json"
                }

        engine = RedSearchEngine(detector=None, customers=world.customers, merchants=world.merchants, mandates=world.mandates)
        
        if self.scale == "smoke":
            samples_per_cell = 2
            budget = 5
        else:
            samples_per_cell = 10
            budget = 20

        # Run unhardened baseline first
        baseline_detector = ChallengerDetector(model_version="baseline")
        baseline_detector.fit_with_defensive_replay(base_train_df, base_train_df, DefensiveKnowledgeStore(self.output_dir))
        
        # We will generate attacks on the base test set
        for train_fam in self.families:
            # 1. Generate training attacks from train_fam to teach the Challenger
            train_atk_txns = world.transactions[train_idx-50:train_idx]
            store = DefensiveKnowledgeStore(self.output_dir / train_fam.value)
            
            for i, txn in enumerate(train_atk_txns[:samples_per_cell]):
                engine.detector = baseline_detector
                prov = engine.attack(
                    source_txn=txn,
                    family=train_fam,
                    budget=budget,
                    seed=i,
                    feature_extractor_state=rolling_extractor
                )
                cand = prov.best_candidate or txn
                feats = rolling_extractor.clone().extract(cand)
                decision = baseline_detector.router.route(
                    txn_id=cand.txn_id,
                    amount=cand.amount,
                    risk_score=baseline_detector.model.predict_proba(np.array([list(feats.values())]))[0, 1] if baseline_detector.is_fitted else 0.5,
                    calibrated_score=0.5,
                    feature_dict=feats
                )
                store.validate_and_add_attack(
                    round_number=0,
                    attack_id=f"atk_{i}",
                    attack_family=train_fam.value,
                    features=feats,
                    target_txn_id=cand.txn_id,
                    customer_id=cand.customer_id,
                    merchant_id=cand.merchant_id,
                    amount=cand.amount,
                    blue_score_before=0.5,
                    blue_decision_before=decision.decision.value,
                    perturbation_distance=prov.med or 0.0,
                    queries_used=prov.queries_used,
                    source_experiment="ADV-004",
                )
                
            # 2. Train challenger
            challenger = ChallengerDetector(model_version=f"blue_v01_{train_fam.value}")
            challenger.fit_with_defensive_replay(base_train_df, base_train_df, store)
            
            # 3. Evaluate against all evaluation families
            for eval_fam in self.families:
                engine.detector = challenger
                successes = 0
                count = 0
                for i, eval_txn in enumerate(eval_txns[:samples_per_cell]):
                    prov = engine.attack(
                        source_txn=eval_txn,
                        family=eval_fam,
                        budget=budget,
                        seed=i,
                        feature_extractor_state=rolling_extractor
                    )
                    cand = prov.best_candidate or eval_txn
                    feats = rolling_extractor.clone().extract(cand)
                    if challenger.is_fitted:
                        p = challenger.model.predict_proba(np.array([list(feats.values())]))[0, 1]
                    else:
                        p = 0.5
                    decision = challenger.router.route(cand.txn_id, cand.amount, p, p, feats)
                    if decision.decision.value == "ALLOW":
                        successes += 1
                    count += 1
                
                asr = successes / max(1, count)
                matrix[train_fam.value][eval_fam.value].update({
                    "ASR": round(asr, 4),
                    "sample_count": count
                })

        with open(self.output_dir / "transferability_matrix.json", "w") as f:
            json.dump(matrix, f, indent=2)
            
        with open(self.output_dir / "status.json", "w") as f:
            json.dump({"status": "COMPLETED", "runtime": time.perf_counter() - start_time}, f)
        print("ADV-004 completed.")

if __name__ == "__main__":
    ADV004Runner().run()
