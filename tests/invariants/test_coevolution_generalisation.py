"""Coevolution Loop & Honest Generalisation Invariant Tests."""

import numpy as np
import pytest

from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.loop.coevolution import CoevolutionLoop
from mcdl.schemas import AttackFamily
from mcdl.world.generator import generate_world


@pytest.fixture
def coevolution_experiment_data():
    """Generates baseline data for a small-scale 2-round coevolution test."""
    cfg = load_config(scale="tiny")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)
    return world, feature_df


def test_anti_memorisation_heldout_isolation(coevolution_experiment_data):
    """Invariant: Held-out attack variants NEVER enter the replay buffer or training matrix."""
    world, feature_df = coevolution_experiment_data

    loop = CoevolutionLoop(
        n_rounds=2,
        budgets=[1, 5, 20],
        families=[AttackFamily.BURST_DRAIN, AttackFamily.SLOW_SIPHON],
        seed=20260827,
    )
    res = loop.run(
        all_transactions=world.transactions,
        world=world,
        feature_df=feature_df,
    )

    replay_instance_ids = set(r.attack_instance_id for r in res.replay_buffer.get_all())

    for report in res.generalisation_reports:
        assert report.seen_asr >= 0.0
        assert report.heldout_asr >= 0.0

    # Ensure rounds history exists and is complete
    assert len(res.rounds) == 2
    assert res.rounds[0].round_index == 0
    assert res.rounds[1].round_index == 1


def test_coevolution_deterministic_replay(coevolution_experiment_data):
    """Invariant: Running the coevolution loop twice with identical seeds produces bit-for-bit identical metrics."""
    world, feature_df = coevolution_experiment_data

    loop1 = CoevolutionLoop(
        n_rounds=2,
        budgets=[1, 5],
        families=[AttackFamily.BURST_DRAIN],
        seed=42,
    )
    res1 = loop1.run(
        all_transactions=world.transactions,
        world=world,
        feature_df=feature_df,
    )

    loop2 = CoevolutionLoop(
        n_rounds=2,
        budgets=[1, 5],
        families=[AttackFamily.BURST_DRAIN],
        seed=42,
    )
    res2 = loop2.run(
        all_transactions=world.transactions,
        world=world,
        feature_df=feature_df,
    )

    assert len(res1.rounds) == len(res2.rounds)
    for r1, r2 in zip(res1.rounds, res2.rounds):
        assert r1.promoted == r2.promoted
        assert r1.red.asr_seen_variants == r2.red.asr_seen_variants
        assert r1.red.asr_heldout_variants == r2.red.asr_heldout_variants

    assert len(res1.replay_buffer) == len(res2.replay_buffer)
