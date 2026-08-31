"""Stateful account ledger maintaining customer balances, velocities, devices, and invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math

from mcdl.schemas import Customer, Device, Mandate, Transaction


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two points in km."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


@dataclass
class CustomerLedgerState:
    customer_id: str
    credit_limit: float
    current_balance: float = 0.0
    last_txn_time: datetime | None = None
    last_lat: float = 0.0
    last_lon: float = 0.0
    known_devices: set[str] = field(default_factory=set)
    failed_auth_streak: int = 0
    txn_count: int = 0

    @property
    def available_credit(self) -> float:
        return max(0.0, self.credit_limit - self.current_balance)


class WorldLedger:
    """Stateful ledger enforcing account invariants and causality across all entities."""

    def __init__(
        self,
        customers: dict[str, Customer],
        devices: dict[str, Device],
        mandates: dict[str, Mandate],
        allow_overdraft: bool = False,
    ) -> None:
        self.allow_overdraft = allow_overdraft
        self.devices = devices
        self.mandates = mandates
        self.customer_states: dict[str, CustomerLedgerState] = {}
        self.rejected_txns: list[tuple[str, str]] = []  # (txn_id, reason)

        # Initialize customer states
        for c_id, cust in customers.items():
            # Initial balance is typically a modest fraction of credit limit
            init_balance = round(cust.credit_limit * 0.05, 2)
            self.customer_states[c_id] = CustomerLedgerState(
                customer_id=c_id,
                credit_limit=cust.credit_limit,
                current_balance=init_balance,
                last_txn_time=None,
                last_lat=cust.home_lat,
                last_lon=cust.home_lon,
                known_devices=set(),
            )

        # Populate initial known devices
        for dev_id, dev in devices.items():
            if dev_id.startswith("dev_c_"):
                # Format: dev_c_00001_pri -> c_00001
                parts = dev_id.split("_")
                if len(parts) >= 3:
                    c_id = f"{parts[1]}_{parts[2]}"
                    if c_id in self.customer_states:
                        self.customer_states[c_id].known_devices.add(dev_id)

    def validate_and_apply(
        self,
        candidate_txn: dict,
    ) -> tuple[bool, str, float, float]:
        """Validates candidate against physical and business invariants.

        Returns (is_valid, reason, balance_before, available_credit_before).
        """
        c_id = candidate_txn["customer_id"]
        amt = float(candidate_txn["amount"])
        ts: datetime = candidate_txn["timestamp"]
        dev_id = candidate_txn["device_id"]
        lat = float(candidate_txn["lat"])
        lon = float(candidate_txn["lon"])
        txn_id = candidate_txn.get("txn_id", "unknown")

        state = self.customer_states.get(c_id)
        if state is None:
            reason = f"UNKNOWN_CUSTOMER: {c_id}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, 0.0, 0.0

        bal_before = state.current_balance
        avail_before = state.available_credit

        # 1. Amount validity
        if amt <= 0:
            reason = f"NON_POSITIVE_AMOUNT: {amt}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, bal_before, avail_before

        # 2. Credit limit / Balance check
        if not self.allow_overdraft and (bal_before + amt > state.credit_limit):
            reason = f"EXCEEDS_CREDIT_LIMIT: amt={amt}, bal={bal_before}, limit={state.credit_limit}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, bal_before, avail_before

        # 3. Monotonic timestamp per entity
        if state.last_txn_time is not None and ts <= state.last_txn_time:
            reason = f"NON_MONOTONIC_TIME: ts={ts} <= last_ts={state.last_txn_time}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, bal_before, avail_before

        # 4. Device existence & registration time
        dev = self.devices.get(dev_id)
        if dev is None:
            reason = f"UNKNOWN_DEVICE: {dev_id}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, bal_before, avail_before

        if ts < dev.first_seen:
            reason = f"DEVICE_BEFORE_REGISTRATION: ts={ts} < dev_first_seen={dev.first_seen}"
            self.rejected_txns.append((txn_id, reason))
            return False, reason, bal_before, avail_before

        # 5. Physical speed limit check (max 900 km/h for commercial flights)
        if state.last_txn_time is not None:
            dt_hours = (ts - state.last_txn_time).total_seconds() / 3600.0
            if dt_hours > 0:
                dist_km = haversine_distance_km(state.last_lat, state.last_lon, lat, lon)
                speed_kmh = dist_km / dt_hours
                if speed_kmh > 900.0 and dist_km > 100.0:
                    reason = f"SPEED_IMPOSSIBLE: {speed_kmh:.1f} km/h (dist={dist_km:.1f}km, dt={dt_hours:.2f}h)"
                    self.rejected_txns.append((txn_id, reason))
                    return False, reason, bal_before, avail_before

        # 6. Apply state updates
        state.current_balance = round(bal_before + amt, 2)
        state.last_txn_time = ts
        state.last_lat = lat
        state.last_lon = lon
        state.known_devices.add(dev_id)
        state.txn_count += 1

        # Periodic balance settlement (e.g. customer paying down balance)
        if state.txn_count % 10 == 0:
            # Pay down 40-80% of current balance
            state.current_balance = round(state.current_balance * 0.35, 2)

        return True, "OK", bal_before, avail_before
