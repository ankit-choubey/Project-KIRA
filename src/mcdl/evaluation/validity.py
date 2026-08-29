"""Layer 1 Validity Filter — Physical and business invariant assertions.

Physics, not statistics: a hard boolean gate. Zero violations is the Gate 1 requirement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math

from mcdl.schemas import Customer, Device, Mandate, Merchant, Transaction
from mcdl.world.generator import WorldResult
from mcdl.world.ledger import haversine_distance_km


@dataclass
class ValidityReport:
    total_transactions: int
    negative_balance_violations: int = 0
    timestamp_order_violations: int = 0
    device_registration_violations: int = 0
    mcc_validity_violations: int = 0
    geo_speed_violations: int = 0
    mandate_violations: int = 0
    foreign_key_violations: int = 0
    violation_samples: list[str] = field(default_factory=list)

    @property
    def total_violations(self) -> int:
        return (
            self.negative_balance_violations
            + self.timestamp_order_violations
            + self.device_registration_violations
            + self.mcc_validity_violations
            + self.geo_speed_violations
            + self.mandate_violations
            + self.foreign_key_violations
        )

    @property
    def passed(self) -> bool:
        return self.total_violations == 0


def check_world(world: WorldResult) -> ValidityReport:
    """Evaluates Layer 1 physical validity across the entire synthetic world."""
    return check_transactions(
        transactions=world.transactions,
        customers=world.customers,
        merchants=world.merchants,
        devices=world.devices,
        mandates=world.mandates,
    )


def check_transactions(
    transactions: list[Transaction],
    customers: dict[str, Customer],
    merchants: dict[str, Merchant],
    devices: dict[str, Device],
    mandates: dict[str, Mandate],
) -> ValidityReport:
    """Validates physical invariants on a list of Transaction records."""
    report = ValidityReport(total_transactions=len(transactions))

    last_ts_by_customer: dict[str, datetime] = {}
    last_pos_by_customer: dict[str, tuple[float, float, datetime]] = {}
    last_state_by_customer: dict[str, tuple[float, float, float]] = {}  # (balance_before, amount, available_credit)

    for txn in transactions:
        # 1. Negative balance or available credit check & non-positive amounts
        if txn.balance_before < 0.0 or txn.available_credit < 0.0 or txn.amount <= 0.0:
            report.negative_balance_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(
                    f"Balance/amount violation: txn {txn.txn_id}, bal={txn.balance_before}, avail={txn.available_credit}, amt={txn.amount}"
                )

        # 1b. Customer balance transition consistency (if customer exists)
        cust = customers.get(txn.customer_id)
        if cust is not None:
            # Credit limit boundary assertion
            if round(txn.balance_before + txn.available_credit, 2) != round(cust.credit_limit, 2):
                report.negative_balance_violations += 1
                if len(report.violation_samples) < 10:
                    report.violation_samples.append(
                        f"Balance accounting violation: txn {txn.txn_id}, bal={txn.balance_before} + avail={txn.available_credit} != limit={cust.credit_limit}"
                    )

            # Sequential balance sanity check: balance_before must not exceed credit limit
            if txn.balance_before > cust.credit_limit:
                report.negative_balance_violations += 1
                if len(report.violation_samples) < 10:
                    report.violation_samples.append(
                        f"Balance exceeds credit limit: txn {txn.txn_id}, bal={txn.balance_before} > limit={cust.credit_limit}"
                    )

        last_state_by_customer[txn.customer_id] = (txn.balance_before, txn.amount, txn.available_credit)

        # 2. Foreign Key referential integrity
        if txn.customer_id not in customers:
            report.foreign_key_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(f"Unknown customer {txn.customer_id} in txn {txn.txn_id}")

        if txn.merchant_id not in merchants:
            report.foreign_key_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(f"Unknown merchant {txn.merchant_id} in txn {txn.txn_id}")

        if txn.device_id not in devices:
            report.foreign_key_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(f"Unknown device {txn.device_id} in txn {txn.txn_id}")

        # 3. Monotonic timestamps per customer
        prev_ts = last_ts_by_customer.get(txn.customer_id)
        if prev_ts is not None and txn.timestamp <= prev_ts:
            report.timestamp_order_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(
                    f"Timestamp violation: customer {txn.customer_id}, prev={prev_ts}, curr={txn.timestamp}"
                )
        last_ts_by_customer[txn.customer_id] = txn.timestamp

        # 4. Device registration before transaction
        dev = devices.get(txn.device_id)
        if dev is not None and txn.timestamp < dev.first_seen:
            report.device_registration_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(
                    f"Device registration violation: txn {txn.txn_id} ts={txn.timestamp} < dev first_seen={dev.first_seen}"
                )

        # 5. MCC validity
        if not (txn.mcc.isdigit() and len(txn.mcc) == 4):
            report.mcc_validity_violations += 1
            if len(report.violation_samples) < 10:
                report.violation_samples.append(f"Invalid MCC: {txn.mcc} in txn {txn.txn_id}")

        # 6. Geographic travel speed feasibility (< 900 km/h)
        prev_pos = last_pos_by_customer.get(txn.customer_id)
        if prev_pos is not None:
            prev_lat, prev_lon, prev_pos_ts = prev_pos
            dt_h = (txn.timestamp - prev_pos_ts).total_seconds() / 3600.0
            if dt_h > 0:
                dist_km = haversine_distance_km(prev_lat, prev_lon, txn.lat, txn.lon)
                speed = dist_km / dt_h
                if speed > 900.0 and dist_km > 100.0:
                    report.geo_speed_violations += 1
                    if len(report.violation_samples) < 10:
                        report.violation_samples.append(
                            f"Speed violation: customer {txn.customer_id}, speed={speed:.1f} km/h, dist={dist_km:.1f} km, dt={dt_h:.2f} h"
                        )
        last_pos_by_customer[txn.customer_id] = (txn.lat, txn.lon, txn.timestamp)

        # 7. Agent Mandate compliance
        if txn.mandate_id is not None:
            mandate = mandates.get(txn.mandate_id)
            if mandate is None:
                report.mandate_violations += 1
                if len(report.violation_samples) < 10:
                    report.violation_samples.append(f"Unknown mandate {txn.mandate_id} in txn {txn.txn_id}")
            else:
                if txn.amount > mandate.max_amount:
                    report.mandate_violations += 1
                    if len(report.violation_samples) < 10:
                        report.violation_samples.append(
                            f"Mandate amount exceeded: txn {txn.txn_id}, amt={txn.amount} > max={mandate.max_amount}"
                        )

    return report
