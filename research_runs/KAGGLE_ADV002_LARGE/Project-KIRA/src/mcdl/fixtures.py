"""Schema-valid FAKE artifacts, so nobody waits for anybody.

This is the file that makes two-person parallel work possible. A builds the API,
the five views, the evaluation harness and the report against fixtures on day 1;
B builds the simulator, models and attack engine. Swapping to real artifacts is a
path change, not a rewrite.

Everything produced here sets `manifest.is_fixture = True`. The API surfaces that
flag and the UI must render a visible "FIXTURE DATA" banner. A fixture number
must never reach the report - `tools/gates.py` gate 6 fails if it does.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from mcdl.schemas import (
    AttackFamily,
    BlueDecision,
    BlueMetrics,
    Channel,
    Counterfactual,
    Decision,
    EvaluationResult,
    FidelityReport,
    HardNegative,
    RedMetrics,
    RoundResult,
    RunManifest,
    Transaction,
)

FIXTURE_RUN_ID = "run_fixture_0000"
_MCCS = ["5411", "5812", "5541", "5999", "4121", "7995", "5732"]
_CATEGORIES = ["grocery", "restaurant", "fuel", "misc_retail", "transport", "gambling", "electronics"]
_START = datetime(2026, 6, 1)


def _rng(seed: int = 7) -> np.random.Generator:
    return np.random.default_rng(seed)


def make_transactions(n: int = 2_000, seed: int = 7) -> list[Transaction]:
    """A plausible-looking stream. Deliberately NOT behaviourally realistic - it
    exists to exercise the schema and the UI, not to be scored."""
    rng = _rng(seed)
    n_customers, n_merchants, n_devices = 60, 40, 80
    txns: list[Transaction] = []

    for i in range(n):
        cust = int(rng.integers(0, n_customers))
        mcc_idx = int(rng.integers(0, len(_MCCS)))
        is_fraud = bool(rng.random() < 0.02)
        family = (
            AttackFamily(rng.choice([f.value for f in AttackFamily])) if is_fraud else None
        )
        hard_neg = HardNegative.NONE
        if not is_fraud and rng.random() < 0.05:
            hard_neg = HardNegative(
                rng.choice([h.value for h in HardNegative if h is not HardNegative.NONE])
            )

        amount = float(np.round(np.exp(rng.normal(6.2, 1.1)), 2))
        balance = float(np.round(rng.uniform(500, 90_000), 2))

        txns.append(
            Transaction(
                txn_id=f"T{i:07d}",
                customer_id=f"C{cust:05d}",
                merchant_id=f"M{int(rng.integers(0, n_merchants)):05d}",
                device_id=f"D{int(rng.integers(0, n_devices)):05d}",
                timestamp=_START + timedelta(minutes=int(rng.integers(0, 60 * 24 * 45))),
                amount=amount,
                mcc=_MCCS[mcc_idx],
                channel=Channel(rng.choice([c.value for c in Channel])),
                lat=float(np.round(rng.uniform(8.0, 34.0), 4)),
                lon=float(np.round(rng.uniform(68.0, 92.0), 4)),
                ip_prefix=f"{int(rng.integers(1, 223))}.{int(rng.integers(0, 255))}.0.0/16",
                is_new_device=bool(rng.random() < 0.08),
                auth_failed_count=int(rng.integers(0, 3)),
                balance_before=balance,
                available_credit=float(np.round(balance * rng.uniform(0.5, 2.0), 2)),
                is_fraud=is_fraud,
                attack_family=family,
                attack_instance_id=f"A{i:06d}" if is_fraud else None,
                attack_variant=int(rng.integers(0, 10)) if is_fraud else None,
                hard_negative=hard_neg,
            )
        )

    txns.sort(key=lambda t: (t.timestamp, t.txn_id))
    return txns


def make_decisions(txns: list[Transaction], seed: int = 7) -> list[BlueDecision]:
    rng = _rng(seed + 1)
    out: list[BlueDecision] = []
    for t in txns:
        # Correlate the score with the label so the UI shows something coherent.
        base = rng.beta(2, 8)
        score = float(np.clip(base + (0.45 if t.is_fraud else 0.0) + rng.normal(0, 0.05), 0, 1))
        decision = (
            Decision.BLOCK if score >= 0.70 else Decision.STEP_UP if score >= 0.25 else Decision.ALLOW
        )
        reasons = []
        if t.is_new_device:
            reasons.append("new_device")
        if t.auth_failed_count > 1:
            reasons.append("repeated_auth_failure")
        if score > 0.5:
            reasons.append("amount_deviation_vs_personal_baseline")
        out.append(
            BlueDecision(
                txn_id=t.txn_id,
                risk_score=score,
                calibrated_score=float(np.clip(score * 0.92, 0, 1)),
                decision=decision,
                reason_codes=reasons,
                intent_drift_score=(
                    float(np.round(rng.uniform(0, 1), 3)) if t.channel is Channel.AGENT else None
                ),
                latency_ms=float(np.round(rng.gamma(2.0, 0.9), 3)),
            )
        )
    return out


def make_counterfactual(txn_id: str, seed: int = 7) -> Counterfactual:
    rng = _rng(seed + 2)
    delta = float(np.round(rng.uniform(120, 3200), 2))
    return Counterfactual(
        txn_id=txn_id,
        found=True,
        changed_field="amount",
        original_value=float(np.round(rng.uniform(4000, 20000), 2)),
        evading_value=float(np.round(rng.uniform(1000, 3900), 2)),
        distance=delta,
        human_readable=f"Reducing amount by {delta:.0f} flips BLOCK to ALLOW",
    )


def make_evaluation(seed: int = 7) -> EvaluationResult:
    rng = _rng(seed + 3)

    manifest = RunManifest(
        run_id=FIXTURE_RUN_ID,
        created_at=datetime.now(),
        seed=seed,
        scale="fixture",
        is_fixture=True,
        stages_completed=["fixtures"],
        n_customers=60,
        n_merchants=40,
        n_transactions=2_000,
        notes="Generated by fixtures.py. Not a measured result. Never cite these numbers.",
    )

    fidelity = FidelityReport(
        l1_violations=0,
        l1_checks={
            "negative_balance": 0,
            "non_monotonic_timestamps": 0,
            "txn_before_device_registration": 0,
            "invalid_mcc": 0,
            "infeasible_geo_transition": 0,
            "fk_integrity": 0,
        },
        l2_ks_by_column={"amount": 0.041, "hour_of_day": 0.028, "mcc": 0.033},
        l2_correlation_distance=0.18,
        l3_p1_interarrival_ratio=None,
        l3_p2_burstiness_ratio=None,
        l3_p3_graph_motif_ratio=None,
        l3_p4_velocity_trigger_ratio=None,
        l3_published_baselines={
            "CTGAN_ieee_cis": 30.0,
            "TVAE_ieee_cis": 24.4,
            "GaussianCopula_ieee_cis": 39.0,
            "TabularARGN_amazon": 17.2,
        },
        l4_c2st_auc_row=None,
        l4_c2st_auc_entity=None,
        l4_top_giveaway_features=[],
        l5_tstr_pr_auc=None,
        l5_trtr_pr_auc=None,
    )

    rounds: list[RoundResult] = []
    asr = 0.34
    med = 340.0
    pr_auc = 0.61
    for r in range(3):
        rounds.append(
            RoundResult(
                round_index=r,
                champion_version=f"blue-v{r}",
                challenger_version=f"blue-v{r + 1}",
                promoted=r > 0,
                promotion_reasons=["heldout_variant_asr_down", "no_regression_on_old_families"]
                if r > 0
                else ["baseline_round"],
                blue=BlueMetrics(
                    pr_auc=round(pr_auc, 3),
                    roc_auc=round(0.93 + r * 0.01, 3),
                    precision=round(0.71 + r * 0.02, 3),
                    recall=round(0.58 + r * 0.04, 3),
                    fpr=round(0.021 - r * 0.002, 4),
                    ece=round(0.038 - r * 0.004, 4),
                    brier=round(0.041 - r * 0.003, 4),
                    decision_counts={"ALLOW": 1820, "STEP_UP": 140, "BLOCK": 40},
                    latency_p50_ms=round(float(rng.uniform(2, 4)), 2),
                    latency_p95_ms=round(float(rng.uniform(6, 9)), 2),
                    latency_p99_ms=round(float(rng.uniform(10, 15)), 2),
                ),
                red=RedMetrics(
                    asr_by_budget={
                        "1": round(asr * 0.10, 3),
                        "5": round(asr * 0.35, 3),
                        "20": round(asr * 0.70, 3),
                        "100": round(asr, 3),
                    },
                    asr_seen_variants=round(asr * 0.55, 3),
                    asr_heldout_variants=round(asr * 0.85, 3),
                    asr_unseen_family=round(asr * 1.15, 3),
                    mean_evasion_distance=round(med, 1),
                    mask_violations=0,
                    invalid_attacks=0,
                ),
            )
        )
        asr *= 0.72
        med *= 2.1
        pr_auc += 0.06

    return EvaluationResult(
        manifest=manifest,
        fidelity=fidelity,
        rounds=rounds,
        anchor=None,  # not measured yet - the UI must render "not measured"
        ablations={},
    )


def make_fixtures(out_dir: Path | str) -> Path:
    """Write a complete, schema-valid fake artifact set. Returns the run dir."""
    run_dir = Path(out_dir) / FIXTURE_RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)

    txns = make_transactions()
    decisions = make_decisions(txns)
    evaluation = make_evaluation()

    _dump(run_dir / "manifest.json", evaluation.manifest)
    _dump(run_dir / "evaluation.json", evaluation)
    _dump_list(run_dir / "transactions.json", txns)
    _dump_list(run_dir / "decisions.json", decisions)
    _dump(run_dir / "counterfactual_sample.json", make_counterfactual(txns[0].txn_id))

    (Path(out_dir) / "LATEST").write_text(FIXTURE_RUN_ID, encoding="utf-8")
    return run_dir


def _dump(path: Path, model) -> None:
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def _dump_list(path: Path, models: list) -> None:
    payload = [json.loads(m.model_dump_json()) for m in models]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover
    from mcdl.config import REPO_ROOT

    d = make_fixtures(REPO_ROOT / "artifacts")
    print(f"wrote fixtures to {d}")
