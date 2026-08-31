"""Minimum Evasion Distance (MED) Metric.

Measures the normalized perturbation distance between original and mutated
transactions over the allowed mutable feature space.
"""

from __future__ import annotations

import math
from mcdl.schemas import Transaction
from mcdl.world.ledger import haversine_distance_km


def compute_evasion_distance(before: Transaction, after: Transaction) -> float:
    """Calculates normalized perturbation distance d(x, x') across mutable dimensions."""
    dist = 0.0

    # 1. Amount distance (log scale: 1 unit ~ 2.7x amount change)
    if before.amount != after.amount:
        dist += abs(math.log(1.0 + after.amount) - math.log(1.0 + before.amount))

    # 2. Geographic distance (normalized to units of 100 km)
    if before.lat != after.lat or before.lon != after.lon:
        geo_km = haversine_distance_km(before.lat, before.lon, after.lat, after.lon)
        dist += geo_km / 100.0

    # 3. Authentication failures
    if before.auth_failed_count != after.auth_failed_count:
        dist += abs(after.auth_failed_count - before.auth_failed_count) * 0.25

    # 4. Categorical transitions
    if before.channel != after.channel:
        dist += 0.50
    if before.merchant_id != after.merchant_id or before.mcc != after.mcc:
        dist += 0.50
    if before.agent_id != after.agent_id or before.mandate_id != after.mandate_id:
        dist += 0.50
    if before.device_id != after.device_id:
        dist += 0.50

    return float(round(dist, 6))
