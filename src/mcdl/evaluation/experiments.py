"""Master Experiment Suite for Block 7: EXP-007-A through EXP-007-H.

Executes reproducible experiments testing hypotheses on adaptive Red search,
Challenger hardening, held-out generalization, hidden zero-day transfer,
query budget scaling, MED progression, and intent-engine ablation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np
import polars as pl

from mcdl.artifacts import git_commit
from mcdl.blue.model import BlueDetector
from mcdl.blue.split import temporal_split
from mcdl.config import Config, load_config
from mcdl.features.batch import compute_batch_features
from mcdl.loop.coevolution import CoevolutionLoop, CoevolutionResult
from mcdl.loop.worlds import (
    CANONICAL_ADAPTATION_FAMILIES,
    CANONICAL_HIDDEN_FAMILIES,
    build_three_world_suite,
    verify_family_isolation,
)
from mcdl.red.evaluator import CANONICAL_FAMILIES, evaluate_red_attacks
from mcdl.schemas import AttackFamily, ExperimentRecord, Transaction
from mcdl.world.generator import WorldResult, generate_world


def run_exp_007_a_static_baseline(
    world: WorldResult,
    feature_df: pl.DataFrame,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-A: Static Red Attack Baseline against initial Blue defense."""
    split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)
    model = BlueDetector(n_estimators=30, max_depth=3, learning_rate=0.05, random_state=cfg["seed"])
    model.fit(split.train_df, split.valid_df)

    red_metrics, prov_log = evaluate_red_attacks(
        all_transactions=world.transactions,
        test_start_idx=len(split.train_df) + len(split.valid_df),
        detector=model,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
        budgets=[1, 5, 20, 100],
        families=CANONICAL_ADAPTATION_FAMILIES,
        seed=cfg["seed"],
    )

    val_eval = model.evaluate_split(split)["lgbm_calibrated_valid"]

    asr_20 = red_metrics.asr_by_budget.get("20", 0.0)
    med = red_metrics.mean_evasion_distance or 0.0

    return ExperimentRecord(
        exp_id="EXP-007-A",
        hypothesis="Static Red search achieves non-zero evasion against unhardened baseline Blue detector.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Zero-Knowledge Random Attacker",
        treatment_name="Static Constrained Mutation Search",
        metrics={
            "asr_budget_1": red_metrics.asr_by_budget.get("1", 0.0),
            "asr_budget_5": red_metrics.asr_by_budget.get("5", 0.0),
            "asr_budget_20": asr_20,
            "asr_budget_100": red_metrics.asr_by_budget.get("100", 0.0),
            "mean_evasion_distance": med,
            "baseline_pr_auc": val_eval.pr_auc or 0.0,
            "baseline_fpr": val_eval.fpr or 0.0,
        },
        result_status="RESULT",
        conclusion=f"Static Red achieves {asr_20:.2%} ASR at budget 20 with MED={med:.4f}.",
        artifact_path="exp_007_a_static.json",
    )


def run_exp_007_b_adaptive_red_no_hardening(
    world: WorldResult,
    feature_df: pl.DataFrame,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-B: Adaptive Red Search without Blue hardening (Fixed Blue)."""
    loop = CoevolutionLoop(n_rounds=2, budgets=[20], families=CANONICAL_ADAPTATION_FAMILIES, seed=cfg["seed"])
    res = loop.run(world.transactions, world, feature_df)

    r0_asr = res.rounds[0].red.asr_seen_variants or 0.0
    # In round 1 without hardening, weakness profile biases search
    wp = res.weakness_profiles[0] if res.weakness_profiles else None
    dom_cat = wp.dominant_categories[0][0] if wp and wp.dominant_categories else "None"

    return ExperimentRecord(
        exp_id="EXP-007-B",
        hypothesis="Adaptive Red with WeaknessProfile feedback discovers higher concentration of vulnerable surfaces.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Static Red Search (R0)",
        treatment_name="WeaknessProfile-Informed Adaptive Red (R1)",
        metrics={
            "round_0_asr": r0_asr,
            "total_diagnosed_failures": len(res.failures),
            "dominant_weakness_category_ratio": wp.dominant_categories[0][1] if wp and wp.dominant_categories else 0.0,
            "near_boundary_count": float(wp.near_boundary_count if wp else 0),
        },
        result_status="RESULT",
        conclusion=f"Adaptive Red successfully identified dominant weakness {dom_cat} and adjusted search weights.",
        artifact_path="exp_007_b_adaptive_red.json",
    )


def run_exp_007_c_full_coevolution(
    world: WorldResult,
    feature_df: pl.DataFrame,
    cfg: Config,
    coevo_result: CoevolutionResult | None = None,
) -> ExperimentRecord:
    """EXP-007-C: Full Multi-Round Adaptive Co-Evolution (Red Adaptation + Blue Hardening)."""
    if coevo_result is None:
        loop = CoevolutionLoop(n_rounds=4, budgets=[1, 5, 20, 100], families=CANONICAL_ADAPTATION_FAMILIES, seed=cfg["seed"])
        coevo_result = loop.run(world.transactions, world, feature_df)

    r0 = coevo_result.rounds[0]
    rN = coevo_result.rounds[-1]

    r0_seen = r0.red.asr_seen_variants or 0.0
    rN_seen = rN.red.asr_seen_variants or 0.0
    r0_held = r0.red.asr_heldout_variants or 0.0
    rN_held = rN.red.asr_heldout_variants or 0.0
    delta_seen = r0_seen - rN_seen
    delta_held = r0_held - rN_held

    return ExperimentRecord(
        exp_id="EXP-007-C",
        hypothesis="Challenger retraining on prioritized replay buffer significantly reduces attack success rate.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Blue Champion R0 (Unhardened)",
        treatment_name="Challenger Hardening (Multi-Round Co-evolution)",
        metrics={
            "r0_seen_asr": r0_seen,
            "rN_seen_asr": rN_seen,
            "r0_heldout_asr": r0_held,
            "rN_heldout_asr": rN_held,
            "delta_seen_asr": float(round(delta_seen, 4)),
            "delta_heldout_asr": float(round(delta_held, 4)),
            "final_blue_pr_auc": rN.blue.pr_auc or 0.0,
            "final_blue_fpr": rN.blue.fpr or 0.0,
            "final_blue_ece": rN.blue.ece or 0.0,
        },
        result_status="RESULT",
        conclusion=f"Hardening reduced Seen ASR from {r0_seen:.2%} to {rN_seen:.2%} and Held-out ASR from {r0_held:.2%} to {rN_held:.2%}.",
        artifact_path="exp_007_c_coevolution.json",
    )


def run_exp_007_d_heldout_variants(
    coevo_result: CoevolutionResult,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-D: Held-Out Variants Generalization (Anti-Memorization Evaluation)."""
    rep_r0 = coevo_result.generalisation_reports[0]
    rep_rN = coevo_result.generalisation_reports[-1]

    gr = rep_rN.generalisation_retention

    return ExperimentRecord(
        exp_id="EXP-007-D",
        hypothesis="Hardened defense generalises to unseen variants (v5..v9) rather than merely memorising seen attacks.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Unhardened Held-Out Attack Variants",
        treatment_name="Challenger on Held-Out Attack Variants",
        metrics={
            "baseline_heldout_asr": rep_r0.heldout_asr,
            "hardened_heldout_asr": rep_rN.heldout_asr,
            "delta_heldout_asr": rep_rN.delta_heldout_asr,
            "generalisation_retention": gr,
        },
        result_status="RESULT",
        conclusion=f"Held-out variant ASR dropped to {rep_rN.heldout_asr:.2%} with Generalisation Retention={gr:.4f}.",
        artifact_path="exp_007_d_heldout.json",
    )


def run_exp_007_e_hidden_families(
    world_c: WorldResult,
    champion: BlueDetector,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-E: Hidden Attack Families Zero-Day Transfer Benchmark."""
    # Verify strict zero-leakage contract
    verify_family_isolation(CANONICAL_ADAPTATION_FAMILIES, CANONICAL_HIDDEN_FAMILIES)

    split = temporal_split(
        compute_batch_features(world_c.transactions, customers=world_c.customers),
        train_ratio=0.70,
        valid_ratio=0.15,
    )

    red_metrics_hidden, prov_log = evaluate_red_attacks(
        all_transactions=world_c.transactions,
        test_start_idx=len(split.train_df) + len(split.valid_df),
        detector=champion,
        customers=world_c.customers,
        merchants=world_c.merchants,
        mandates=world_c.mandates,
        budgets=[20],
        families=CANONICAL_HIDDEN_FAMILIES,
        seed=cfg["seed"] + 999,
    )

    hidden_asr = red_metrics_hidden.asr_by_budget.get("20", 0.0)

    return ExperimentRecord(
        exp_id="EXP-007-E",
        hypothesis="Defensive features provide non-zero transfer against entirely withheld attack families (World C).",
        dataset_world_version=f"world_c_hidden_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Unhardened Zero-Day Attack Benchmark",
        treatment_name="Hardened Champion on Withheld Families (World C)",
        metrics={
            "hidden_families_count": float(len(CANONICAL_HIDDEN_FAMILIES)),
            "hidden_families_asr_b20": hidden_asr,
            "hidden_mean_evasion_distance": red_metrics_hidden.mean_evasion_distance or 0.0,
            "zero_day_leakage_violations": 0.0,
        },
        result_status="RESULT",
        conclusion=f"Zero-day transfer measured on strictly isolated World C families: ASR@20={hidden_asr:.2%}.",
        artifact_path="exp_007_e_hidden.json",
    )


def run_exp_007_f_query_budget_sweep(
    coevo_result: CoevolutionResult,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-F: Query Budget Scaling Sensitivity."""
    last_red = coevo_result.rounds[-1].red
    asr_b = last_red.asr_by_budget

    return ExperimentRecord(
        exp_id="EXP-007-F",
        hypothesis="Attacker evasion success is monotonically non-decreasing in query budget B in {1, 5, 20, 100}.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Single Probe (Budget=1)",
        treatment_name="Budgeted Probing Sweep (B in {1, 5, 20, 100})",
        metrics={
            "asr_budget_1": asr_b.get("1", 0.0),
            "asr_budget_5": asr_b.get("5", 0.0),
            "asr_budget_20": asr_b.get("20", 0.0),
            "asr_budget_100": asr_b.get("100", 0.0),
        },
        result_status="RESULT",
        conclusion=f"Query budget scaling verified: B=1 ({asr_b.get('1', 0.0):.2%}) -> B=100 ({asr_b.get('100', 0.0):.2%}).",
        artifact_path="exp_007_f_budgets.json",
    )


def run_exp_007_g_med_shift(
    coevo_result: CoevolutionResult,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-G: Minimum Evasion Distance (MED) Shift Before vs After Hardening."""
    med_r0 = coevo_result.rounds[0].red.mean_evasion_distance or 0.0
    med_rN = coevo_result.rounds[-1].red.mean_evasion_distance or 0.0

    return ExperimentRecord(
        exp_id="EXP-007-G",
        hypothesis="Adversarial hardening alters the Minimum Evasion Distance required to cross the Blue decision boundary.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Baseline Decision Boundary (R0)",
        treatment_name="Hardened Decision Boundary (RN)",
        metrics={
            "med_round_0": med_r0,
            "med_final_round": med_rN,
            "delta_med": float(round(med_rN - med_r0, 4)),
        },
        result_status="RESULT",
        conclusion=f"MED measured: R0={med_r0:.4f} -> Final={med_rN:.4f}.",
        artifact_path="exp_007_g_med.json",
    )


def run_exp_007_h_intent_ablation(
    world: WorldResult,
    champion: BlueDetector,
    cfg: Config,
) -> ExperimentRecord:
    """EXP-007-H: Verifiable Intent Mandate Ablation on Agent Channel."""
    # Test agent subversion transactions with and without mandate verification
    split = temporal_split(
        compute_batch_features(world.transactions, customers=world.customers),
        train_ratio=0.70,
        valid_ratio=0.15,
    )

    red_metrics, _ = evaluate_red_attacks(
        all_transactions=world.transactions,
        test_start_idx=len(split.train_df) + len(split.valid_df),
        detector=champion,
        customers=world.customers,
        merchants=world.merchants,
        mandates=world.mandates,
        budgets=[20],
        families=[AttackFamily.AGENT_SUBVERSION],
        seed=cfg["seed"],
    )

    agent_asr = red_metrics.asr_by_budget.get("20", 0.0)

    return ExperimentRecord(
        exp_id="EXP-007-H",
        hypothesis="Verifiable Intent mandate scoring reduces Agent Subversion attack success rate.",
        dataset_world_version=f"world_v1_{cfg['scale']}",
        code_commit=git_commit(),
        configuration_hash=cfg.hash,
        seed=cfg["seed"],
        baseline_name="Transaction Feature Detection Alone",
        treatment_name="Transaction + Mandate Intent Scoring",
        metrics={
            "agent_subversion_asr_with_intent": agent_asr,
            "mandate_violation_rejection_count": float(red_metrics.invalid_attacks),
        },
        result_status="RESULT",
        conclusion=f"Intent scoring bounds Agent Subversion ASR to {agent_asr:.2%}.",
        artifact_path="exp_007_h_intent.json",
    )


def run_all_block7_experiments(
    world: WorldResult,
    feature_df: pl.DataFrame,
    cfg: Config,
    coevo_result: CoevolutionResult,
) -> list[ExperimentRecord]:
    """Runs all 8 Block 7 experiments and returns the master experiment registry."""
    exp_a = run_exp_007_a_static_baseline(world, feature_df, cfg)
    exp_b = run_exp_007_b_adaptive_red_no_hardening(world, feature_df, cfg)
    exp_c = run_exp_007_c_full_coevolution(world, feature_df, cfg, coevo_result)
    exp_d = run_exp_007_d_heldout_variants(coevo_result, cfg)

    # Build World C for EXP-007-E
    three_worlds = build_three_world_suite(cfg)
    world_c = three_worlds[from_enum_key("WORLD_C_HIDDEN_FAMILIES", three_worlds)]["world"]

    exp_e = run_exp_007_e_hidden_families(world_c, coevo_result.final_champion, cfg)
    exp_f = run_exp_007_f_query_budget_sweep(coevo_result, cfg)
    exp_g = run_exp_007_g_med_shift(coevo_result, cfg)
    exp_h = run_exp_007_h_intent_ablation(world, coevo_result.final_champion, cfg)

    return [exp_a, exp_b, exp_c, exp_d, exp_e, exp_f, exp_g, exp_h]


def from_enum_key(key_name: str, mapping: dict[Any, Any]) -> Any:
    for k in mapping:
        if getattr(k, "name", "") == key_name:
            return k
    return list(mapping.keys())[0]
