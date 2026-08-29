"""Red Team Adversarial Search Engine.

Executes constrained black-box query-budgeted attack optimization against Blue detector.
Enforces strict mutability masks, Layer-1 physical validity, and stops on evasion or budget exhaustion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.distance import compute_evasion_distance
from mcdl.red.mask import FAMILY_MUTABLE_FIELDS, check_mask_violations
from mcdl.red.strategies import generate_candidate_mutation
from mcdl.schemas import AttackFamily, Decision, Customer, Mandate, Merchant, Transaction
from mcdl.world.ledger import haversine_distance_km


@dataclass
class AttackProvenance:
    attack_instance_id: str
    attack_family: AttackFamily
    source_txn_id: str
    seed: int
    query_budget: int
    queries_used: int
    mutations_attempted: int
    valid_mutations: int
    invalid_mutations: int
    original_decision: Decision
    final_decision: Decision
    original_risk: float
    final_risk: float
    med: float
    success: bool
    rejection_reasons: list[str] = field(default_factory=list)
    best_candidate: Transaction | None = None


def validate_physical_candidate(
    candidate: Transaction,
    customer: Customer,
    merchants: dict[str, Merchant],
    mandates: dict[str, Mandate],
) -> list[str]:
    """Validates that a mutated transaction adheres to Layer-1 physical validity."""
    reasons = []

    # 1. Amount validity and credit limit
    if candidate.amount <= 0:
        reasons.append("NON_POSITIVE_AMOUNT")
    if candidate.amount > customer.credit_limit:
        reasons.append("EXCEEDS_CREDIT_LIMIT")

    # 2. Balance equation consistency
    if round(candidate.balance_before + candidate.available_credit, 2) != round(customer.credit_limit, 2):
        reasons.append("BALANCE_EQUATION_VIOLATION")

    # 3. Coordinate bounds
    if not (-90.0 <= candidate.lat <= 90.0 and -180.0 <= candidate.lon <= 180.0):
        reasons.append("INVALID_COORDINATES")

    # 4. MCC validity
    if not (candidate.mcc.isdigit() and len(candidate.mcc) == 4):
        reasons.append("INVALID_MCC_FORMAT")

    # 5. Mandate constraints if agent-initiated
    if candidate.channel.value == "agent":
        if not candidate.agent_id or not candidate.mandate_id:
            reasons.append("MISSING_AGENT_OR_MANDATE_ID")
        elif candidate.mandate_id in mandates:
            mandate = mandates[mandate_id]
            if candidate.amount > mandate.max_amount:
                # Mandates allow reject, but physical world rejects if over limit
                pass

    return reasons


class RedSearchEngine:
    """Constrained black-box query attacker against Blue defense."""

    def __init__(
        self,
        detector: BlueDetector,
        customers: dict[str, Customer],
        merchants: dict[str, Merchant],
        mandates: dict[str, Mandate],
    ) -> None:
        self.detector = detector
        self.customers = customers
        self.merchants = merchants
        self.mandates = mandates

    def attack(
        self,
        source_txn: Transaction,
        family: AttackFamily,
        budget: int = 20,
        seed: int = 20260827,
    ) -> AttackProvenance:
        """Runs budgeted adversarial search for a single transaction."""
        rng = np.random.default_rng(seed)
        customer = self.customers.get(source_txn.customer_id)
        if customer is None:
            raise ValueError(f"Customer {source_txn.customer_id} not found")

        # 1. Evaluate baseline decision on source transaction
        extractor_baseline = StreamingFeatureExtractor(customers=self.customers)
        base_feats = extractor_baseline.extract(source_txn)
        base_decision = self.detector.score_transaction(source_txn, base_feats, mandates=self.mandates)

        orig_decision = base_decision.decision
        orig_risk = base_decision.calibrated_score

        # If already ALLOWed, evasion is trivially 0-distance
        if orig_decision == Decision.ALLOW:
            return AttackProvenance(
                attack_instance_id=f"atk_{source_txn.txn_id}_{family.value}_{budget}",
                attack_family=family,
                source_txn_id=source_txn.txn_id,
                seed=seed,
                query_budget=budget,
                queries_used=1,
                mutations_attempted=0,
                valid_mutations=0,
                invalid_mutations=0,
                original_decision=orig_decision,
                final_decision=orig_decision,
                original_risk=orig_risk,
                final_risk=orig_risk,
                med=0.0,
                success=True,
                best_candidate=source_txn,
            )

        allowed_mutable = FAMILY_MUTABLE_FIELDS.get(family, ["amount", "channel"])

        queries_used = 0
        mutations_attempted = 0
        valid_mutations = 0
        invalid_mutations = 0
        rejection_reasons = []

        best_candidate: Transaction | None = None
        best_decision = orig_decision
        best_risk = orig_risk
        success = False

        # 2. Budgeted candidate mutation loop
        for q in range(budget):
            queries_used += 1
            mutations_attempted += 1

            candidate = generate_candidate_mutation(
                family=family,
                source_txn=source_txn,
                customer=customer,
                merchants=self.merchants,
                mandates=self.mandates,
                rng=rng,
                query_idx=q,
            )

            # Check mutability mask violations
            mask_violations = check_mask_violations(source_txn, candidate, allowed_mutable)
            if mask_violations:
                invalid_mutations += 1
                rejection_reasons.extend(mask_violations)
                continue

            # Check physical validity
            physics_violations = validate_physical_candidate(
                candidate, customer, self.merchants, self.mandates
            )
            if physics_violations:
                invalid_mutations += 1
                rejection_reasons.extend(physics_violations)
                continue

            valid_mutations += 1

            # Score candidate with Blue detector
            extractor = StreamingFeatureExtractor(customers=self.customers)
            cand_feats = extractor.extract(candidate)
            cand_decision = self.detector.score_transaction(candidate, cand_feats, mandates=self.mandates)

            cand_score = cand_decision.calibrated_score
            cand_action = cand_decision.decision

            # Track lowest risk valid candidate
            if cand_score < best_risk:
                best_risk = cand_score
                best_decision = cand_action
                best_candidate = candidate

            # Early stopping on successful evasion (ALLOW)
            if cand_action == Decision.ALLOW:
                success = True
                best_candidate = candidate
                best_decision = cand_action
                best_risk = cand_score
                break

        final_cand = best_candidate or source_txn
        med = compute_evasion_distance(source_txn, final_cand) if success else None

        return AttackProvenance(
            attack_instance_id=f"atk_{source_txn.txn_id}_{family.value}_{budget}",
            attack_family=family,
            source_txn_id=source_txn.txn_id,
            seed=seed,
            query_budget=budget,
            queries_used=queries_used,
            mutations_attempted=mutations_attempted,
            valid_mutations=valid_mutations,
            invalid_mutations=invalid_mutations,
            original_decision=orig_decision,
            final_decision=best_decision,
            original_risk=orig_risk,
            final_risk=best_risk,
            med=med if med is not None else compute_evasion_distance(source_txn, final_cand),
            success=success,
            rejection_reasons=list(set(rejection_reasons)),
            best_candidate=best_candidate,
        )
