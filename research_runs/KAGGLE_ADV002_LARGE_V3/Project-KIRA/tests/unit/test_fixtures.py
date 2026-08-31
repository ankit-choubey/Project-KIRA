"""Fixtures must stay schema-valid and must stay honest.

Honest means: a fixture never invents a measurement. Unmeasured values are null,
so the UI learns to render "not measured" from day one rather than learning to
render a zero that later becomes a lie.
"""

from __future__ import annotations

from mcdl import artifacts as art
from mcdl.fixtures import (
    FIXTURE_RUN_ID,
    make_decisions,
    make_evaluation,
    make_fixtures,
    make_transactions,
)


class TestGenerators:
    def test_transactions_are_time_ordered(self, tmp_path):
        txns = make_transactions(n=300)
        keys = [(t.timestamp, t.txn_id) for t in txns]
        assert keys == sorted(keys), "fixture stream must be sorted by (timestamp, txn_id)"

    def test_transactions_are_deterministic(self):
        a = make_transactions(n=50, seed=3)
        b = make_transactions(n=50, seed=3)
        assert [t.txn_id for t in a] == [t.txn_id for t in b]
        assert [t.amount for t in a] == [t.amount for t in b]

    def test_every_transaction_has_a_decision(self):
        txns = make_transactions(n=200)
        decisions = make_decisions(txns)
        assert {d.txn_id for d in decisions} == {t.txn_id for t in txns}

    def test_decision_thresholds_are_consistent(self):
        txns = make_transactions(n=300)
        for d in make_decisions(txns):
            if d.decision.value == "BLOCK":
                assert d.risk_score >= 0.70
            elif d.decision.value == "ALLOW":
                assert d.risk_score < 0.25

    def test_contains_hard_negatives(self):
        # Without hard negatives the detector learns "unusual == fraud" and the
        # FPR is meaningless. The fixture must exercise that path.
        txns = make_transactions(n=1000)
        assert any(t.hard_negative.value != "none" for t in txns)


class TestEvaluationFixture:
    def test_marked_as_fixture(self):
        assert make_evaluation().manifest.is_fixture is True

    def test_unmeasured_layers_are_null_not_zero(self):
        f = make_evaluation().fidelity
        for field in (
            "l3_p1_interarrival_ratio",
            "l3_p2_burstiness_ratio",
            "l3_p3_graph_motif_ratio",
            "l3_p4_velocity_trigger_ratio",
            "l4_c2st_auc_row",
            "l4_c2st_auc_entity",
            "l5_tstr_pr_auc",
        ):
            assert getattr(f, field) is None, f"{field} must be null until measured, never 0.0"

    def test_anchor_not_measured_yet(self):
        assert make_evaluation().anchor is None

    def test_heldout_and_seen_asr_are_reported_separately(self):
        # Collapsing these two is exactly how a project ends up reporting
        # memorisation as hardening (audit F-06).
        for r in make_evaluation().rounds:
            assert r.red.asr_seen_variants is not None
            assert r.red.asr_heldout_variants is not None
            assert r.red.asr_seen_variants != r.red.asr_heldout_variants


class TestRoundTrip:
    def test_write_then_load(self, tmp_path):
        make_fixtures(tmp_path)
        d = art.resolve_run(base=tmp_path)
        assert d.name == FIXTURE_RUN_ID

        ev = art.load_evaluation(d)
        assert ev.manifest.is_fixture is True
        assert len(ev.rounds) == 3

        txns = art.load_transactions(d, limit=10)
        assert len(txns) == 10

        decisions = art.load_decisions(d)
        assert all(t.txn_id in decisions for t in txns)

    def test_paging_is_contiguous(self, tmp_path):
        make_fixtures(tmp_path)
        d = art.resolve_run(base=tmp_path)
        first = art.load_transactions(d, limit=10, offset=0)
        second = art.load_transactions(d, limit=10, offset=10)
        assert [t.txn_id for t in first] != [t.txn_id for t in second]
        assert art.load_transactions(d, limit=20, offset=0)[10:] == second

    def test_missing_run_raises_actionable_error(self, tmp_path):
        try:
            art.resolve_run(base=tmp_path)
        except FileNotFoundError as exc:
            assert "make gate 0" in str(exc), "the error must tell the reader what to run"
        else:  # pragma: no cover
            raise AssertionError("expected FileNotFoundError")
