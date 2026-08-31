"""Mutability Mask & Immutability Policy for Red Team Attack Engine.

Strictly separates attacker-controllable attributes from immutable physical
and identity ledger state.
"""

from __future__ import annotations

from typing import Any
from mcdl.schemas import AttackFamily, MutabilityMask, Transaction

IMMUTABLE_FIELDS: list[str] = [
    "txn_id",
    "timestamp",
    "customer_id",
    "balance_before",
    "available_credit",
    "is_fraud",
    "attack_family",
    "attack_instance_id",
    "attack_variant",
    "hard_negative",
]

FAMILY_MUTABLE_FIELDS: dict[AttackFamily, list[str]] = {
    AttackFamily.BURST_DRAIN: ["amount", "channel", "auth_failed_count"],
    AttackFamily.SLOW_SIPHON: ["amount", "channel", "auth_failed_count"],
    AttackFamily.GEO_HOP: ["lat", "lon", "merchant_id", "mcc", "channel"],
    AttackFamily.AGENT_SUBVERSION: ["amount", "channel", "agent_id", "mandate_id", "mcc", "auth_failed_count"],
    AttackFamily.CROSS_MERCHANT_FANOUT: ["merchant_id", "mcc", "amount", "channel"],
    # Aliases
    AttackFamily.R1_ATO: ["amount", "channel", "auth_failed_count", "lat", "lon", "merchant_id", "mcc"],
    AttackFamily.R2_VELOCITY_BURST: ["amount", "channel", "auth_failed_count"],
    AttackFamily.R3_LOW_AND_SLOW: ["amount", "channel", "auth_failed_count"],
    AttackFamily.R4_MULE_RING: ["merchant_id", "mcc", "amount", "channel"],
    AttackFamily.R8_INTENT_DRIFT: ["amount", "channel", "agent_id", "mandate_id", "mcc"],
}


def get_mutability_mask(family: AttackFamily) -> MutabilityMask:
    """Returns the strict mutability mask for the given attack family."""
    mutable = FAMILY_MUTABLE_FIELDS.get(family, ["amount", "channel"])
    # All other Transaction observable fields are immutable
    all_fields = Transaction.observable_fields() + Transaction.hidden_fields()
    immutable = [f for f in all_fields if f not in mutable]
    return MutabilityMask(mutable=mutable, immutable=immutable)


def check_mask_violations(
    before: Transaction,
    after: Transaction,
    allowed_mutable: list[str],
) -> list[str]:
    """Inspects two transactions and returns any unauthorized mutated fields."""
    before_dict = before.model_dump()
    after_dict = after.model_dump()

    violations = []
    # 1. Hard invariant: strictly immutable fields must never change
    for field in IMMUTABLE_FIELDS:
        if before_dict.get(field) != after_dict.get(field):
            violations.append(f"IMMUTABLE_VIOLATION:{field} (before={before_dict.get(field)} after={after_dict.get(field)})")

    # 2. Family-specific mutability constraints
    for field, val in after_dict.items():
        if field not in allowed_mutable and field not in IMMUTABLE_FIELDS:
            if before_dict.get(field) != val:
                violations.append(f"UNAUTHORIZED_MUTATION:{field}")

    return violations
