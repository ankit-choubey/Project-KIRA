"""Unit tests for Block 7 Experiments (EXP-007-A through EXP-007-H)."""

from __future__ import annotations

import pytest
from mcdl.config import load_config
from mcdl.evaluation.experiments import (
    run_exp_007_a_static_baseline,
    run_exp_007_b_adaptive_red_no_hardening,
    run_exp_007_c_full_coevolution,
    run_exp_007_d_heldout_variants,
    run_exp_007_e_hidden_families,
    run_exp_007_f_query_budget_sweep,
    run_exp_007_g_med_shift,
    run_exp_007_h_intent_ablation,
)
from mcdl.features.batch import compute_batch_features
from mcdl.loop.coevolution import CoevolutionLoop
from mcdl.loop.worlds import CANONICAL_ADAPTATION_FAMILIES
from mcdl.world.generator import generate_world


@pytest.fixture
def experiment_fixture():
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    loop = CoevolutionLoop(n_rounds=2, budgets=[1, 5, 20], families=CANONICAL_ADAPTATION_FAMILIES, seed=20260827)
    coev_res = loop.run(world.transactions, world, feature_df)

    return {"cfg": cfg, "world": world, "feature_df": feature_df, "coev_res": coev_res}


def test_experiments_exp_007_a_through_h(experiment_fixture):
    cfg = experiment_fixture["cfg"]
    world = experiment_fixture["world"]
    feature_df = experiment_fixture["feature_df"]
    coev_res = experiment_fixture["coev_res"]

    # EXP-007-A
    rec_a = run_exp_007_a_static_baseline(world, feature_df, cfg)
    assert rec_a.exp_id == "EXP-007-A"
    assert "asr_budget_20" in rec_a.metrics

    # EXP-007-B
    rec_b = run_exp_007_b_adaptive_red_no_hardening(world, feature_df, cfg)
    assert rec_b.exp_id == "EXP-007-B"
    assert rec_b.metrics["total_diagnosed_failures"] >= 0

    # EXP-007-C
    rec_c = run_exp_007_c_full_coevolution(world, feature_df, cfg, coev_res)
    assert rec_c.exp_id == "EXP-007-C"
    assert "r0_seen_asr" in rec_c.metrics

    # EXP-007-D
    rec_d = run_exp_007_d_heldout_variants(coev_res, cfg)
    assert rec_d.exp_id == "EXP-007-D"
    assert "generalisation_retention" in rec_d.metrics

    # EXP-007-E
    rec_e = run_exp_007_e_hidden_families(world, coev_res.final_champion, cfg)
    assert rec_e.exp_id == "EXP-007-E"
    assert rec_e.metrics["zero_day_leakage_violations"] == 0.0

    # EXP-007-F
    rec_f = run_exp_007_f_query_budget_sweep(coev_res, cfg)
    assert rec_f.exp_id == "EXP-007-F"

    # EXP-007-G
    rec_g = run_exp_007_g_med_shift(coev_res, cfg)
    assert rec_g.exp_id == "EXP-007-G"

    # EXP-007-H
    rec_h = run_exp_007_h_intent_ablation(world, coev_res.final_champion, cfg)
    assert rec_h.exp_id == "EXP-007-H"
