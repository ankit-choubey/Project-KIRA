"""ADV-001 Attack Evaluator and Outcome Taxonomy Engine.

Evaluates individual attack plans against the Blue detector, assigns formal
outcome classifications, computes ASR and MED, and calculates 95% bootstrap CIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
import numpy as np

from mcdl.blue.model import BlueDetector
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.red.search import AttackProvenance, RedSearchEngine
from mcdl.research.advanced.adv001.population import AttackPlan
from mcdl.schemas import AttackFamily, Decision, Mandate, Merchant, Transaction


@dataclass
class AttackAttemptResult:
    """Standardized record of a single evaluated adversarial attack attempt."""

    attack_id: str
    family: str
    strategy: str
    seed: int
    parent_attack_id: str | None
    query_budget: int
    queries_used: int
    mutation_count: int
    perturbation_distance: float | None
    target_transaction_id: str
    blue_model_version: str
    blue_score: float
    blue_decision: str
    evasion: bool
    outcome: str
    timestamp: str
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_single_attempt(
    plan: AttackPlan,
    engine: RedSearchEngine,
    merchants: dict[str, Merchant],
    mandates: dict[str, Mandate],
    blue_model_version: str = "run_tiny_s20260827_193f7897_40997ab",
    feature_extractor_state: StreamingFeatureExtractor | None = None,
) -> AttackAttemptResult:
    """Executes a single planned attack attempt through the Red engine."""
    t_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        prov: AttackProvenance = engine.attack(
            source_txn=plan.source_txn,
            family=plan.family,
            budget=plan.query_budget,
            seed=plan.seed,
            feature_extractor_state=feature_extractor_state,
        )

        # Strict evasion condition: prov.success AND final decision is ALLOW AND not source-already-allowed
        is_allow = (
            prov.final_decision == Decision.ALLOW
            or getattr(prov.final_decision, "value", "") == "ALLOW"
            or str(prov.final_decision) == "ALLOW"
            or str(prov.final_decision) == "Decision.ALLOW"
        )
        is_step_up = (
            prov.final_decision == Decision.STEP_UP
            or getattr(prov.final_decision, "value", "") == "STEP_UP"
            or str(prov.final_decision) == "STEP_UP"
            or str(prov.final_decision) == "Decision.STEP_UP"
        )
        is_block = (
            prov.final_decision == Decision.BLOCK
            or getattr(prov.final_decision, "value", "") == "BLOCK"
            or str(prov.final_decision) == "BLOCK"
            or str(prov.final_decision) == "Decision.BLOCK"
        )

        is_evasion = bool(prov.success) and is_allow and ("SOURCE_ALREADY_ALLOWED" not in prov.rejection_reasons)

        # Map to outcome taxonomy
        if is_evasion:
            outcome = "ALLOWED_EVASION"
        elif prov.invalid_mutations > 0 and prov.valid_mutations == 0:
            if any("IMMUTABLE" in r for r in prov.rejection_reasons):
                outcome = "INVALID_MUTATION"
            else:
                outcome = "FAILED_MUTATION"
        elif is_step_up:
            outcome = "STEP_UP"
        elif is_block:
            outcome = "BLOCKED"
        else:
            outcome = "BLOCKED"

        prov_dict = {
            "attack_instance_id": prov.attack_instance_id,
            "queries_used": prov.queries_used,
            "mutations_attempted": prov.mutations_attempted,
            "valid_mutations": prov.valid_mutations,
            "invalid_mutations": prov.invalid_mutations,
            "original_decision": prov.original_decision.value if hasattr(prov.original_decision, "value") else str(prov.original_decision),
            "final_decision": prov.final_decision.value if hasattr(prov.final_decision, "value") else str(prov.final_decision),
            "original_risk": float(prov.original_risk),
            "final_risk": float(prov.final_risk),
            "rejection_reasons": prov.rejection_reasons,
        }

        return AttackAttemptResult(
            attack_id=plan.attack_id,
            family=plan.family.value if hasattr(plan.family, "value") else str(plan.family),
            strategy=plan.strategy_name,
            seed=plan.seed,
            parent_attack_id=plan.parent_attack_id,
            query_budget=plan.query_budget,
            queries_used=prov.queries_used,
            mutation_count=prov.mutations_attempted,
            perturbation_distance=float(prov.med) if (prov.med is not None and is_evasion) else None,
            target_transaction_id=plan.source_txn.txn_id,
            blue_model_version=blue_model_version,
            blue_score=float(prov.final_risk),
            blue_decision=prov.final_decision.value if hasattr(prov.final_decision, "value") else str(prov.final_decision),
            evasion=is_evasion,
            outcome=outcome,
            timestamp=t_now,
            provenance=prov_dict,
        )

    except Exception as exc:
        return AttackAttemptResult(
            attack_id=plan.attack_id,
            family=plan.family.value if hasattr(plan.family, "value") else str(plan.family),
            strategy=plan.strategy_name,
            seed=plan.seed,
            parent_attack_id=plan.parent_attack_id,
            query_budget=plan.query_budget,
            queries_used=0,
            mutation_count=0,
            perturbation_distance=None,
            target_transaction_id=plan.source_txn.txn_id,
            blue_model_version=blue_model_version,
            blue_score=1.0,
            blue_decision="BLOCK",
            evasion=False,
            outcome="ERROR",
            timestamp=t_now,
            provenance={"error": str(exc)},
        )


def compute_bootstrap_ci(
    values: list[float] | np.ndarray,
    n_bootstraps: int = 1000,
    seed: int = 20260831,
) -> tuple[float, float] | None:
    """Computes a 95% bootstrap confidence interval."""
    arr = np.array(values, dtype=np.float64)
    if len(arr) < 5:
        return None

    rng = np.random.default_rng(seed)
    n = len(arr)
    boot_means = np.zeros(n_bootstraps, dtype=np.float64)
    for i in range(n_bootstraps):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    lower = float(np.percentile(boot_means, 2.5))
    upper = float(np.percentile(boot_means, 97.5))
    return (round(lower, 4), round(upper, 4))


def compute_population_statistics(results: list[AttackAttemptResult]) -> dict[str, Any]:
    """Aggregates population-level metrics, family-level breakdowns, and query-budget metrics."""
    total_attempts = len(results)
    if total_attempts == 0:
        return {"total_attempts": 0, "status": "EMPTY"}

    outcomes: dict[str, int] = {}
    for r in results:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1

    evasions = [1.0 if r.evasion else 0.0 for r in results]
    asr = float(np.mean(evasions))
    asr_ci = compute_bootstrap_ci(evasions)

    med_values = [r.perturbation_distance for r in results if r.perturbation_distance is not None]
    mean_med = float(np.mean(med_values)) if med_values else None
    median_med = float(np.median(med_values)) if med_values else None
    med_ci = compute_bootstrap_ci(med_values) if med_values else None

    # Family-level metrics
    family_groups: dict[str, list[AttackAttemptResult]] = {}
    for r in results:
        family_groups.setdefault(r.family, []).append(r)

    family_metrics: dict[str, Any] = {}
    for fam, group in family_groups.items():
        fam_evasions = [1.0 if r.evasion else 0.0 for r in group]
        fam_meds = [r.perturbation_distance for r in group if r.perturbation_distance is not None]
        fam_queries = [r.queries_used for r in group]

        family_metrics[fam] = {
            "attempted": len(group),
            "successful_evasions": int(np.sum(fam_evasions)),
            "blocked": len(group) - int(np.sum(fam_evasions)),
            "asr": round(float(np.mean(fam_evasions)), 4),
            "asr_ci_95": compute_bootstrap_ci(fam_evasions),
            "median_query_count": float(np.median(fam_queries)) if fam_queries else 0.0,
            "mean_perturbation_distance": round(float(np.mean(fam_meds)), 4) if fam_meds else None,
            "median_perturbation_distance": round(float(np.median(fam_meds)), 4) if fam_meds else None,
            "min_perturbation_distance": round(float(np.min(fam_meds)), 4) if fam_meds else None,
        }

    # Query-budget metrics (1, 5, 20, 100)
    budget_groups: dict[int, list[AttackAttemptResult]] = {}
    for r in results:
        budget_groups.setdefault(r.query_budget, []).append(r)

    budget_metrics: dict[str, Any] = {}
    for b in sorted(budget_groups.keys()):
        b_group = budget_groups[b]
        b_evasions = [1.0 if r.evasion else 0.0 for r in b_group]
        budget_metrics[str(b)] = {
            "attempted": len(b_group),
            "successful_evasions": int(np.sum(b_evasions)),
            "asr": round(float(np.mean(b_evasions)), 4),
            "asr_ci_95": compute_bootstrap_ci(b_evasions),
        }

    return {
        "population_id": "ADV001_ATTACK_POPULATION_10K",
        "total_attempts": total_attempts,
        "valid_attacks": total_attempts - outcomes.get("FAILED_MUTATION", 0) - outcomes.get("INVALID_MUTATION", 0) - outcomes.get("ERROR", 0),
        "allowed_evasion_count": outcomes.get("ALLOWED_EVASION", 0),
        "blocked_count": outcomes.get("BLOCKED", 0),
        "step_up_count": outcomes.get("STEP_UP", 0),
        "generation_failures": outcomes.get("FAILED_MUTATION", 0) + outcomes.get("INVALID_MUTATION", 0),
        "error_count": outcomes.get("ERROR", 0),
        "aggregate_asr": round(asr, 4),
        "aggregate_asr_ci_95": asr_ci,
        "mean_med": round(mean_med, 4) if mean_med is not None else None,
        "median_med": round(median_med, 4) if median_med is not None else None,
        "med_ci_95": med_ci,
        "outcome_distribution": outcomes,
        "family_metrics": family_metrics,
        "budget_metrics": budget_metrics,
    }
