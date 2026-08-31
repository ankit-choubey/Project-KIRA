"""ADV-003 Deterministic Adaptive Red Attacker.

Generates bounded adversarial attacks against defending detector versions using
deterministic historical weakness feedback across disjoint population splits.
"""

from __future__ import annotations

from typing import Any
import numpy as np

from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.search import AttackFamily, RedSearchEngine
from mcdl.research.advanced.adv003.challenger import ChallengerDetector
from mcdl.schemas import Customer, Decision, Mandate, Merchant, Transaction


class DeterministicAdaptiveRedAttacker:
    """Non-RL deterministic adaptive adversarial attacker."""

    def __init__(
        self,
        engine: RedSearchEngine | None = None,
        base_seed: int = 20260831,
    ) -> None:
        self.engine = engine
        self.base_seed = base_seed
        self.families = [
            AttackFamily.BURST_DRAIN,
            AttackFamily.SLOW_SIPHON,
            AttackFamily.GEO_HOP,
            AttackFamily.AGENT_SUBVERSION,
            AttackFamily.CROSS_MERCHANT_FANOUT,
        ]
        self._family_weights: dict[str, float] = {f.value: 1.0 for f in self.families}

    def update_strategy_weights(self, prior_attack_outcomes: list[dict[str, Any]]) -> None:
        """Updates attack family selection weights based on prior round evasion outcomes."""
        if not prior_attack_outcomes:
            return

        family_evasions: dict[str, int] = {f.value: 0 for f in self.families}
        family_counts: dict[str, int] = {f.value: 0 for f in self.families}

        for atk in prior_attack_outcomes:
            fam = atk.get("family", "")
            if fam in family_counts:
                family_counts[fam] += 1
                if atk.get("decision") == "ALLOW":
                    family_evasions[fam] += 1

        for fam in self.families:
            f_val = fam.value
            cnt = family_counts[f_val]
            ev = family_evasions[f_val]
            asr = (ev / max(1, cnt)) if cnt > 0 else 0.20
            # Exponentially weight successful evasion families
            self._family_weights[f_val] = float(0.10 + (asr ** 2) * 2.0)

    def generate_attacks_for_population(
        self,
        detector: ChallengerDetector,
        target_transactions: list[Transaction],
        round_number: int,
        population_name: str,
        rolling_extractor: StreamingFeatureExtractor,
        world_customers: dict[str, Customer],
        world_merchants: dict[str, Merchant],
        world_mandates: dict[str, Mandate],
        budget: int = 20,
    ) -> list[dict[str, Any]]:
        """Generates bounded adversarial attacks against the specified detector for a transaction split."""
        attacks: list[dict[str, Any]] = []

        weights_arr = np.array([self._family_weights[f.value] for f in self.families], dtype=np.float64)
        probs = weights_arr / np.sum(weights_arr)

        if self.engine is not None:
            self.engine.detector = detector

        for i, target_txn in enumerate(target_transactions):
            # Deterministic selection based on seed and index
            rng = np.random.RandomState(int((self.base_seed + round_number * 10007 + i * 31) % (2**31 - 1)))
            chosen_family_idx = int(rng.choice(len(self.families), p=probs))
            chosen_family = self.families[chosen_family_idx]
            seed_val = int(rng.randint(1, 1000000))

            if self.engine is not None:
                prov = self.engine.attack(
                    source_txn=target_txn,
                    family=chosen_family,
                    budget=budget,
                    seed=seed_val,
                    feature_extractor_state=rolling_extractor,
                )

                best_cand = prov.best_candidate or target_txn
                cand_ext = rolling_extractor.clone()
                cand_feats = cand_ext.extract(best_cand)

                attack_record = {
                    "attack_id": f"atk_adv003_{population_name}_r{round_number:02d}_{i:04d}_{target_txn.txn_id}",
                    "round": round_number,
                    "population": population_name,
                    "target_txn_id": target_txn.txn_id,
                    "customer_id": target_txn.customer_id,
                    "merchant_id": target_txn.merchant_id,
                    "amount": float(best_cand.amount),
                    "family": chosen_family.value,
                    "features": cand_feats,
                    "blue_score": float(prov.final_risk),
                    "decision": prov.final_decision.value,
                    "perturbation_distance": float(prov.med or 0.0),
                    "queries_used": prov.queries_used,
                    "evasion": prov.success,
                }
            else:
                # Mock generation if engine is None
                state_snapshot = rolling_extractor.clone()
                orig_features = state_snapshot.extract(target_txn)
                dec = detector.score_transaction(target_txn, orig_features, mandates=world_mandates)
                attack_record = {
                    "attack_id": f"atk_adv003_{population_name}_r{round_number:02d}_{i:04d}_{target_txn.txn_id}",
                    "round": round_number,
                    "population": population_name,
                    "target_txn_id": target_txn.txn_id,
                    "customer_id": target_txn.customer_id,
                    "merchant_id": target_txn.merchant_id,
                    "amount": float(target_txn.amount),
                    "family": chosen_family.value,
                    "features": orig_features,
                    "blue_score": float(dec.risk_score),
                    "decision": dec.decision.value,
                    "perturbation_distance": 0.0,
                    "queries_used": 1,
                    "evasion": (dec.decision == Decision.ALLOW),
                }

            attacks.append(attack_record)

        return attacks
