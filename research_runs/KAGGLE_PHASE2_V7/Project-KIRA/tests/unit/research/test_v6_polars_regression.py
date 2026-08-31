"""Regression Test for V6 Polars Heterogeneous Schema Inference Failure.

Reproduces the exact data shape that caused V6 S-02/S-03 to fail:
thousands of rows with agent_id=None followed by an agent-subverted transaction
with a string agent_id (e.g. 'agent_c_08869').
"""

from datetime import datetime
import polars as pl
import pytest

from mcdl.research.phase2.graph_temporal import TemporalPaymentGraph
from mcdl.schemas import Channel, Transaction


def test_polars_agent_id_heterogeneous_schema_inference_regression():
    """Reproduces the V6 failure condition and verifies the fix with infer_schema_length=None."""
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    txns = []

    # 1. First 250 rows have agent_id = None (exceeds default Polars 100 row inference limit)
    for i in range(250):
        txns.append(
            Transaction(
                txn_id=f"tx_normal_{i:05d}",
                customer_id=f"c_{i:04d}",
                merchant_id="m_001",
                device_id=f"d_{i:04d}",
                timestamp=t0,
                amount=25.0,
                mcc="5411",
                channel=Channel.CARD_PRESENT,
                lat=40.0,
                lon=-74.0,
                ip_prefix="192.168",
                is_new_device=False,
                auth_failed_count=0,
                agent_id=None,
                mandate_id=None,
                balance_before=1000.0,
                available_credit=5000.0,
                is_fraud=False,
            )
        )

    # 2. Row 251 introduces agent_id string (the exact failure case from V6 log)
    txns.append(
        Transaction(
            txn_id="tx_agent_00251",
            customer_id="c_08869",
            merchant_id="m_002",
            device_id="d_08869",
            timestamp=t0,
            amount=450.0,
            mcc="5411",
            channel=Channel.AGENT,
            lat=40.0,
            lon=-74.0,
            ip_prefix="10.0",
            is_new_device=True,
            auth_failed_count=1,
            agent_id="agent_c_08869",
            mandate_id="mandate_c_08869_01",
            balance_before=2000.0,
            available_credit=4000.0,
            is_fraud=True,
            attack_family="agent_subversion",
        )
    )

    # 3. Construct TemporalPaymentGraph - must succeed without ComputeError
    graph = TemporalPaymentGraph(txns)
    assert graph.n_txns == 251
    assert "agent_id" in graph.raw_df.columns
    agent_row = graph.raw_df.filter(pl.col("txn_id") == "tx_agent_00251")
    assert len(agent_row) == 1
    assert agent_row["agent_id"][0] == "agent_c_08869"
