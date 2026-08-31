"""Contract tests.

These run in milliseconds and are the first thing gate 0 checks. Their job is to
catch the two developers drifting apart before anyone builds on a broken contract.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from mcdl.config import load_config
from mcdl.schemas import (
    AttackFamily,
    Channel,
    MutabilityMask,
    Transaction,
)


def _txn(**over) -> Transaction:
    base = dict(
        txn_id="T0000001",
        customer_id="C00001",
        merchant_id="M00001",
        device_id="D00001",
        timestamp=datetime(2026, 6, 1, 12, 0),
        amount=1250.0,
        mcc="5411",
        channel=Channel.ECOMMERCE,
        lat=19.07,
        lon=72.87,
        ip_prefix="49.36.0.0/16",
        is_new_device=False,
        balance_before=25_000.0,
        available_credit=40_000.0,
    )
    base.update(over)
    return Transaction(**base)


class TestTransaction:
    def test_minimal_transaction_validates(self):
        t = _txn()
        assert t.is_fraud is False
        assert t.attack_family is None

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            _txn(amount=0.0)
        with pytest.raises(ValidationError):
            _txn(amount=-10.0)

    def test_mcc_must_be_four_digits(self):
        with pytest.raises(ValidationError):
            _txn(mcc="541")
        with pytest.raises(ValidationError):
            _txn(mcc="grocery")

    def test_extra_fields_rejected(self):
        # extra="forbid" is what stops a stray column becoming a silent feature.
        with pytest.raises(ValidationError):
            _txn(fraud_score=0.9)

    def test_observable_and_hidden_partition_the_model(self):
        obs = set(Transaction.observable_fields())
        hid = set(Transaction.hidden_fields())
        assert not (obs & hid), f"a field is in both lists: {obs & hid}"
        assert obs | hid == set(Transaction.model_fields), (
            f"unclassified fields: {set(Transaction.model_fields) - (obs | hid)}"
        )

    def test_label_fields_are_hidden_not_observable(self):
        # The single most expensive possible mistake in this project.
        obs = set(Transaction.observable_fields())
        for leaky in ("is_fraud", "attack_family", "attack_instance_id", "hard_negative"):
            assert leaky not in obs, f"{leaky} must never be observable"


class TestMutabilityMask:
    def test_detects_immutable_change(self):
        mask = MutabilityMask(
            mutable=["amount", "timestamp"],
            immutable=["customer_id", "balance_before"],
        )
        before = {"customer_id": "C1", "balance_before": 100.0, "amount": 50.0}
        after = {"customer_id": "C2", "balance_before": 100.0, "amount": 80.0}
        assert mask.violations(before, after) == ["customer_id"]

    def test_allows_mutable_change(self):
        mask = MutabilityMask(mutable=["amount"], immutable=["customer_id"])
        before = {"customer_id": "C1", "amount": 50.0}
        after = {"customer_id": "C1", "amount": 900.0}
        assert mask.violations(before, after) == []


class TestConfig:
    def test_loads_and_validates(self):
        cfg = load_config()
        assert cfg["scale"] in ("tiny", "small", "full")
        assert abs(sum(cfg["world"]["archetypes"].values()) - 1.0) < 1e-9

    def test_scale_override(self):
        assert load_config(scale="full")["world"]["target_events"] == 1_000_000
        assert load_config(scale="tiny")["world"]["target_events"] == 10_000

    def test_rejects_unknown_scale(self):
        with pytest.raises(ValueError, match="scale must be one of"):
            load_config(scale="enormous")

    def test_hidden_families_are_real_families(self):
        cfg = load_config()
        valid = {f.value for f in AttackFamily}
        assert set(cfg["red"]["families"]) <= valid
        assert set(cfg["red"]["hidden_from_blue"]) <= set(cfg["red"]["families"])

    def test_heldout_variants_exist(self):
        # If harden_on_variants == variants_per_family there are no held-out
        # variants and the closed loop can only measure memorisation (audit F-06).
        cfg = load_config()
        assert cfg["red"]["harden_on_variants"] < cfg["red"]["variants_per_family"]

    def test_config_hash_is_stable(self):
        assert load_config().hash == load_config().hash
