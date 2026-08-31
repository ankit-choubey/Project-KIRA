"""Focused unit tests for the HTTP Latency Benchmark (LATENCY-002)."""

from __future__ import annotations

import math
import pytest
from tools.benchmark_latency import run_latency_benchmark


def test_latency_benchmark_contracts():
    """Validates all 12 scientific contracts for the /api/score HTTP latency benchmark."""
    # Execute bounded benchmark (10 warmup, 200 measured requests)
    res = run_latency_benchmark(
        run_id="run_tiny_s20260827_193f7897_40997ab",
        n_warmup=10,
        n_measurements=200,
        timeout_seconds=30.0,
        save_artifact=True,
    )

    # 1. Endpoint & Method verification
    assert res["endpoint"] == "/api/score"
    assert res["measurement_method"] == "in_process_http_testclient"
    assert res["run_id"] == "run_tiny_s20260827_193f7897_40997ab"
    assert res["git_commit"] is not None and len(res["git_commit"]) > 0

    # 2. Warm-up and request counts
    assert res["warmup_requests"] == 10
    assert res["requested_measurements"] == 200
    assert res["successful_requests"] == 200
    assert res["failed_requests"] == 0
    assert res["status_codes"] == {"200": 200}
    assert res["classification"] == "MEASURED — HTTP LOOPBACK BENCHMARK"

    # 3. Wall clock & timeout contract
    assert res["total_wall_time_seconds"] <= 30.0

    # 4. Latency values: non-negative and finite
    lat = res["latency_ms"]
    for k in ["min", "mean", "p50", "p95", "p99", "max"]:
        val = lat[k]
        assert val is not None, f"Missing latency metric: {k}"
        assert not math.isnan(val) and not math.isinf(val)
        assert val >= 0.0, f"Negative latency metric: {k}={val}"

    # 5. Percentile monotonicity (P50 <= P95 <= P99)
    assert lat["min"] <= lat["mean"] <= lat["max"]
    assert lat["min"] <= lat["p50"] <= lat["p95"] <= lat["p99"] <= lat["max"]
