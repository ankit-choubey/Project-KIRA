"""Streaming Causal Feature Extractor — Online serving path.

Computes exact mathematical features one transaction at a time using causal
state memory. Evaluates features strictly BEFORE committing current transaction to state.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
import math
from typing import Any

from mcdl.features.spec import FEATURE_NAMES
from mcdl.schemas import Customer, Transaction
from mcdl.world.ledger import haversine_distance_km


class CustomerStreamState:
    def __init__(self, home_lat: float, home_lon: float, credit_limit: float) -> None:
        self.home_lat = home_lat
        self.home_lon = home_lon
        self.credit_limit = credit_limit
        self.last_ts: datetime | None = None
        self.last_lat: float = home_lat
        self.last_lon: float = home_lon
        self.cumulative_amount_sum: float = 0.0
        self.cumulative_txn_count: int = 0
        self.known_devices: set[str] = set()
        # Deques of (timestamp, txn_id, amount)
        self.events_24h: deque[tuple[datetime, str, float]] = deque()


class MerchantStreamState:
    def __init__(self) -> None:
        self.events_24h: deque[tuple[datetime, str]] = deque()
        # Confirmed 7-day lag tracking: queue of (timestamp, is_fraud)
        self.unconfirmed_labels: deque[tuple[datetime, bool]] = deque()
        self.confirmed_fraud_count: int = 0
        self.confirmed_total_count: int = 0


class DeviceStreamState:
    def __init__(self) -> None:
        self.known_customers: set[str] = set()


class StreamingFeatureExtractor:
    """Online stateful feature extractor matching batch vectorised definitions."""

    def __init__(self, customers: dict[str, Customer] | None = None) -> None:
        self.customers_state: dict[str, CustomerStreamState] = {}
        self.merchants_state: dict[str, MerchantStreamState] = {}
        self.devices_state: dict[str, DeviceStreamState] = {}

        if customers:
            for c_id, cust in customers.items():
                self.customers_state[c_id] = CustomerStreamState(
                    home_lat=cust.home_lat,
                    home_lon=cust.home_lon,
                    credit_limit=cust.credit_limit,
                )

    def clone(self) -> StreamingFeatureExtractor:
        """Fast shallow clone of extractor with cloned deques/sets."""
        cloned = StreamingFeatureExtractor()
        for c_id, cs in self.customers_state.items():
            new_cs = CustomerStreamState(cs.home_lat, cs.home_lon, cs.credit_limit)
            new_cs.last_ts = cs.last_ts
            new_cs.last_lat = cs.last_lat
            new_cs.last_lon = cs.last_lon
            new_cs.cumulative_amount_sum = cs.cumulative_amount_sum
            new_cs.cumulative_txn_count = cs.cumulative_txn_count
            new_cs.known_devices = set(cs.known_devices)
            new_cs.events_24h = deque(cs.events_24h)
            cloned.customers_state[c_id] = new_cs

        for m_id, ms in self.merchants_state.items():
            new_ms = MerchantStreamState()
            new_ms.events_24h = deque(ms.events_24h)
            new_ms.unconfirmed_labels = deque(ms.unconfirmed_labels)
            new_ms.confirmed_fraud_count = ms.confirmed_fraud_count
            new_ms.confirmed_total_count = ms.confirmed_total_count
            cloned.merchants_state[m_id] = new_ms

        for d_id, ds in self.devices_state.items():
            new_ds = DeviceStreamState()
            new_ds.known_customers = set(ds.known_customers)
            cloned.devices_state[d_id] = new_ds

        return cloned

    def extract(self, txn: Transaction) -> dict[str, Any]:
        """Extracts causal features for transaction T_i, then advances internal state."""
        c_id = txn.customer_id
        m_id = txn.merchant_id
        dev_id = txn.device_id
        t_curr = txn.timestamp
        amt = float(txn.amount)

        # 1. Resolve / initialize customer state
        c_state = self.customers_state.get(c_id)
        if c_state is None:
            c_state = CustomerStreamState(
                home_lat=txn.lat,
                home_lon=txn.lon,
                credit_limit=txn.balance_before + txn.available_credit,
            )
            self.customers_state[c_id] = c_state

        # 2. Resolve / initialize merchant & device state
        m_state = self.merchants_state.setdefault(m_id, MerchantStreamState())
        d_state = self.devices_state.setdefault(dev_id, DeviceStreamState())

        # --- A. Transaction & Temporal (Stateless) --------------------------
        log_amount = math.log(1.0 + amt)
        hour_of_day = t_curr.hour
        day_of_week = t_curr.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        # --- B. Spatial & Movement ------------------------------------------
        dist_from_home = haversine_distance_km(c_state.home_lat, c_state.home_lon, txn.lat, txn.lon)

        if c_state.last_ts is not None:
            dist_from_prev = haversine_distance_km(c_state.last_lat, c_state.last_lon, txn.lat, txn.lon)
            time_since_prev = (t_curr - c_state.last_ts).total_seconds()
            speed = (dist_from_prev / (time_since_prev / 3600.0)) if time_since_prev > 0 else 0.0
        else:
            dist_from_prev = 0.0
            time_since_prev = -1.0
            speed = 0.0

        # --- C. Customer Velocity Windows (Trailing 1h, 6h, 24h) ------------
        # Window: t_curr - delta <= t_j <= t_curr with T_j < T_i in causal order
        cutoff_24h = t_curr - timedelta(hours=24)
        while c_state.events_24h and c_state.events_24h[0][0] < cutoff_24h:
            c_state.events_24h.popleft()

        cutoff_1h = t_curr - timedelta(hours=1)
        cutoff_6h = t_curr - timedelta(hours=6)

        c_v1_count = 0
        c_v1_sum = 0.0
        c_v6_count = 0
        c_v6_sum = 0.0
        c_v24_count = 0
        c_v24_sum = 0.0

        for e_ts, e_id, e_amt in c_state.events_24h:
            # Events in deque strictly precede T_i in causal order
            c_v24_count += 1
            c_v24_sum += e_amt
            if e_ts >= cutoff_6h:
                c_v6_count += 1
                c_v6_sum += e_amt
            if e_ts >= cutoff_1h:
                c_v1_count += 1
                c_v1_sum += e_amt

        # --- D. Merchant Velocity Windows (Trailing 1h, 24h) ----------------
        while m_state.events_24h and m_state.events_24h[0][0] < cutoff_24h:
            m_state.events_24h.popleft()

        m_v1_count = 0
        m_v24_count = 0
        for e_ts, e_id in m_state.events_24h:
            m_v24_count += 1
            if e_ts >= cutoff_1h:
                m_v1_count += 1

        # --- E. Behavioral & Historical Statistics --------------------------
        if c_state.cumulative_txn_count > 0:
            cust_avg_hist = c_state.cumulative_amount_sum / c_state.cumulative_txn_count
            amount_to_avg_ratio = amt / cust_avg_hist if cust_avg_hist > 0 else 1.0
        else:
            cust_avg_hist = amt
            amount_to_avg_ratio = 1.0

        balance_util = (txn.balance_before / c_state.credit_limit) if c_state.credit_limit > 0 else 0.0

        # --- F. Entity & Relational -----------------------------------------
        is_new_dev = 1 if (c_state.cumulative_txn_count > 0 and dev_id not in c_state.known_devices) else 0
        device_cust_count = len(d_state.known_customers)
        auth_failed = txn.auth_failed_count
        is_agent = 1 if txn.agent_id is not None else 0

        # --- G. 7-Day Label-Delay Realism -----------------------------------
        # Shift events that are now >= 7 days old into confirmed counts
        cutoff_7d = t_curr - timedelta(days=7)
        while m_state.unconfirmed_labels and m_state.unconfirmed_labels[0][0] <= cutoff_7d:
            _, is_f = m_state.unconfirmed_labels.popleft()
            m_state.confirmed_total_count += 1
            if is_f:
                m_state.confirmed_fraud_count += 1

        if m_state.confirmed_total_count > 0:
            merch_fraud_rate_7d = m_state.confirmed_fraud_count / m_state.confirmed_total_count
        else:
            merch_fraud_rate_7d = 0.0

        # --- Assemble Feature Dictionary -----------------------------------
        features = {
            "amount": amt,
            "log_amount": log_amount,
            "hour_of_day": int(hour_of_day),
            "day_of_week": int(day_of_week),
            "is_weekend": int(is_weekend),
            "dist_from_home_km": float(dist_from_home),
            "dist_from_prev_txn_km": float(dist_from_prev),
            "time_since_prev_txn_seconds": float(time_since_prev),
            "speed_kmh": float(speed),
            "cust_velocity_1h_count": int(c_v1_count),
            "cust_velocity_1h_sum": float(c_v1_sum),
            "cust_velocity_6h_count": int(c_v6_count),
            "cust_velocity_6h_sum": float(c_v6_sum),
            "cust_velocity_24h_count": int(c_v24_count),
            "cust_velocity_24h_sum": float(c_v24_sum),
            "merch_velocity_1h_count": int(m_v1_count),
            "merch_velocity_24h_count": int(m_v24_count),
            "cust_avg_amount_hist": float(cust_avg_hist),
            "cust_amount_to_avg_ratio": float(amount_to_avg_ratio),
            "balance_utilization": float(balance_util),
            "is_new_device": int(is_new_dev),
            "device_cust_count": int(device_cust_count),
            "auth_failed_count": int(auth_failed),
            "is_agent_initiated": int(is_agent),
            "merch_fraud_rate_7d_lag": float(merch_fraud_rate_7d),
        }

        # --- ADVANCE STATE WITH CURRENT TRANSACTION -------------------------
        c_state.last_ts = t_curr
        c_state.last_lat = txn.lat
        c_state.last_lon = txn.lon
        c_state.cumulative_amount_sum += amt
        c_state.cumulative_txn_count += 1
        c_state.known_devices.add(dev_id)
        c_state.events_24h.append((t_curr, txn.txn_id, amt))

        m_state.events_24h.append((t_curr, txn.txn_id))
        m_state.unconfirmed_labels.append((t_curr, txn.is_fraud))

        d_state.known_customers.add(c_id)

        return features
