"""Entity generators for Customers, Merchants, Devices, and Mandates.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import numpy as np

from mcdl.schemas import Archetype, Customer, Device, Mandate, Merchant
from mcdl.world.archetypes import ARCHETYPE_PROFILES


# Category mappings for MCCs
MCC_CATEGORIES: dict[str, str] = {
    "5411": "grocery_pos",
    "5812": "food_dining",
    "5814": "fast_food",
    "5541": "gas_transport",
    "5912": "health_fitness",
    "4121": "travel_ride",
    "5311": "shopping_pos",
    "5499": "grocery_pos",
    "5942": "shopping_net",
    "4899": "entertainment",
    "7832": "entertainment",
    "5399": "shopping_pos",
    "5045": "misc_pos",
    "5085": "misc_pos",
    "5111": "shopping_net",
    "5943": "shopping_pos",
    "7399": "misc_net",
    "3000": "travel_airlines",
    "7011": "travel_hotel",
    "5651": "shopping_pos",
    "5944": "shopping_luxury",
    "4511": "travel_airlines",
}


def generate_entities(
    n_customers: int,
    n_merchants: int,
    start_date: datetime,
    archetype_shares: dict[str, float],
    agent_share: float = 0.08,
    shared_device_rate: float = 0.03,
    rng: np.random.Generator | None = None,
) -> tuple[dict[str, Customer], dict[str, Merchant], dict[str, Device], dict[str, Mandate]]:
    """Generates world entities with calibrated behavioural parameters and relationships."""
    if rng is None:
        rng = np.random.default_rng(20260827)

    # 1. Generate Merchants
    merchants: dict[str, Merchant] = {}
    mcc_list = list(MCC_CATEGORIES.keys())
    for i in range(n_merchants):
        m_id = f"m_{i:04d}"
        mcc = str(rng.choice(mcc_list))
        category = MCC_CATEGORIES[mcc]
        # Continental US bounds roughly: lat 25.0 to 48.0, lon -122.0 to -72.0
        lat = float(rng.uniform(25.0, 48.0))
        lon = float(rng.uniform(-122.0, -72.0))
        risk_tier = str(rng.choice(["low", "medium", "high"], p=[0.85, 0.12, 0.03]))
        merchants[m_id] = Merchant(
            merchant_id=m_id,
            mcc=mcc,
            category=category,
            lat=lat,
            lon=lon,
            risk_tier=risk_tier,  # type: ignore[arg-type]
        )

    # 2. Determine archetype counts
    archetypes_enum = [Archetype(k) for k in archetype_shares.keys()]
    probs = [float(archetype_shares[k]) for k in archetype_shares.keys()]
    chosen_indices = rng.choice(len(archetypes_enum), size=n_customers, p=probs)
    chosen_archetypes = [archetypes_enum[idx] for idx in chosen_indices]

    # 3. Generate Customers & Devices
    customers: dict[str, Customer] = {}
    devices: dict[str, Device] = {}
    mandates: dict[str, Mandate] = {}

    # Pool of shared family devices
    n_shared_devices = max(2, int(n_customers * shared_device_rate))
    shared_devices_pool: list[str] = []
    for d_idx in range(n_shared_devices):
        dev_id = f"dev_shared_{d_idx:03d}"
        dev_first_seen = start_date - timedelta(days=int(rng.integers(100, 500)))
        devices[dev_id] = Device(
            device_id=dev_id,
            first_seen=dev_first_seen,
            shared=True,
        )
        shared_devices_pool.append(dev_id)

    for i in range(n_customers):
        c_id = f"c_{i:05d}"
        arch = chosen_archetypes[i]
        profile = ARCHETYPE_PROFILES[arch]

        # Home location centered around major metro coordinates with variance
        home_lat = float(rng.uniform(25.5, 47.5))
        home_lon = float(rng.uniform(-120.0, -74.0))

        account_opened = start_date - timedelta(days=int(rng.integers(30, 1000)))
        credit_limit = float(rng.uniform(profile.credit_limit_min, profile.credit_limit_max))

        # Behavioural parameters drawn per customer
        mean_log_amt = float(rng.normal(profile.mean_log_amount_mu, profile.mean_log_amount_sigma))
        std_log_amt = float(max(0.2, rng.normal(profile.std_log_amount_val, 0.15)))
        daily_rate = float(rng.uniform(profile.daily_rate_min, profile.daily_rate_max))

        has_agent = bool(rng.random() < agent_share)

        customer = Customer(
            customer_id=c_id,
            archetype=arch,
            home_lat=home_lat,
            home_lon=home_lon,
            account_opened=account_opened,
            credit_limit=credit_limit,
            mean_log_amount=mean_log_amt,
            std_log_amount=std_log_amt,
            daily_txn_rate=daily_rate,
            has_agent=has_agent,
        )
        customers[c_id] = customer

        # Primary Device for Customer
        # Small probability to use a shared family device
        if rng.random() < 0.05 and shared_devices_pool:
            primary_dev_id = rng.choice(shared_devices_pool)
        else:
            primary_dev_id = f"dev_{c_id}_pri"
            dev_first_seen = account_opened + timedelta(days=int(rng.integers(0, 10)))
            devices[primary_dev_id] = Device(
                device_id=primary_dev_id,
                first_seen=dev_first_seen,
                shared=False,
            )

        # Agent Mandate if customer has an agent
        if has_agent:
            mandate_id = f"mnd_{c_id}"
            agent_id = f"agent_{c_id}"
            # Agent allowed MCCs: subset of common archetype MCCs
            n_mccs = rng.integers(2, len(profile.common_mccs) + 1)
            allowed_mccs = [str(x) for x in rng.choice(profile.common_mccs, size=n_mccs, replace=False)]
            mandates[mandate_id] = Mandate(
                mandate_id=mandate_id,
                customer_id=c_id,
                agent_id=agent_id,
                max_amount=float(min(customer.credit_limit * 0.5, np.exp(customer.mean_log_amount + 2 * customer.std_log_amount))),
                max_txn_count=int(rng.integers(5, 30)),
                allowed_mcc=allowed_mccs,
                merchant_allowlist=[],
                valid_from=start_date - timedelta(days=10),
                valid_until=start_date + timedelta(days=365),
                allowed_geo_radius_km=float(rng.uniform(50.0, 300.0)),
            )

    return customers, merchants, devices, mandates
