"""HTTP Latency Benchmark for /api/score Endpoint.

Executes a high-resolution, controlled latency benchmark of the KIRA FastAPI /api/score
path across a warm-up phase (10 requests) and a measurement phase (200 requests).
Enforces hard timeouts (<= 30s) and exports latency_benchmark.json into the target run.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any
import numpy as np
from fastapi.testclient import TestClient

from mcdl.artifacts import git_commit, resolve_run, set_latest
from mcdl.config import REPO_ROOT


def run_latency_benchmark(
    run_id: str = "run_tiny_s20260827_193f7897_40997ab",
    n_warmup: int = 10,
    n_measurements: int = 200,
    timeout_seconds: float = 30.0,
    save_artifact: bool = True,
) -> dict[str, Any]:
    """Runs a controlled in-process HTTP latency benchmark against /api/score."""
    t_benchmark_start = time.perf_counter()
    artifacts_base = REPO_ROOT / "artifacts"
    target_dir = artifacts_base / run_id

    if not target_dir.exists():
        raise FileNotFoundError(f"Target run directory not found: {target_dir}")

    # Ensure LATEST points to target run during benchmark
    set_latest(run_id, base=artifacts_base)

    # Load observable transaction corpus
    txns_path = target_dir / "transactions.json"
    if not txns_path.exists():
        raise FileNotFoundError(f"transactions.json missing from run {run_id}")

    raw_txns = json.loads(txns_path.read_text(encoding="utf-8"))
    if len(raw_txns) < (n_warmup + n_measurements):
        # Repeat corpus if fewer transactions exist
        corpus = (raw_txns * ((n_warmup + n_measurements) // len(raw_txns) + 1))
    else:
        corpus = raw_txns

    # Initialize FastAPI TestClient
    from api.main import app
    client = TestClient(app)

    # 1. Warm-up phase (10 requests, excluded from latency statistics)
    warmup_completed = 0
    for i in range(n_warmup):
        if (time.perf_counter() - t_benchmark_start) > timeout_seconds:
            break
        txn_payload = corpus[i]
        resp = client.post("/api/score", json={"transaction": txn_payload})
        if resp.status_code == 200:
            warmup_completed += 1

    # 2. Measurement phase (200 requests)
    latencies_ms: list[float] = []
    status_codes: dict[str, int] = {}
    successful_requests = 0
    failed_requests = 0

    for i in range(n_warmup, n_warmup + n_measurements):
        if (time.perf_counter() - t_benchmark_start) > timeout_seconds:
            break

        txn_payload = corpus[i]
        t0 = time.perf_counter()
        resp = client.post("/api/score", json={"transaction": txn_payload})
        t1 = time.perf_counter()

        elapsed_ms = (t1 - t0) * 1000.0
        code_str = str(resp.status_code)
        status_codes[code_str] = status_codes.get(code_str, 0) + 1

        if resp.status_code == 200:
            successful_requests += 1
            latencies_ms.append(elapsed_ms)
        else:
            failed_requests += 1

    total_elapsed_s = time.perf_counter() - t_benchmark_start

    # Compute statistics if measurements succeeded
    if latencies_ms:
        lat_arr = np.array(latencies_ms, dtype=np.float64)
        p50, p95, p99 = np.percentile(lat_arr, [50, 95, 99])
        latency_stats = {
            "min": float(round(float(np.min(lat_arr)), 3)),
            "mean": float(round(float(np.mean(lat_arr)), 3)),
            "p50": float(round(float(p50), 3)),
            "p95": float(round(float(p95), 3)),
            "p99": float(round(float(p99), 3)),
            "max": float(round(float(np.max(lat_arr)), 3)),
        }
    else:
        latency_stats = {
            "min": None,
            "mean": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "max": None,
        }

    is_complete = successful_requests == n_measurements
    classification = (
        "MEASURED — HTTP LOOPBACK BENCHMARK"
        if is_complete
        else "INCOMPLETE — LATENCY NOT CLAIMABLE"
    )

    result = {
        "experiment_id": "LATENCY-002",
        "run_id": run_id,
        "endpoint": "/api/score",
        "measurement_method": "in_process_http_testclient",
        "classification": classification,
        "warmup_requests": warmup_completed,
        "requested_measurements": n_measurements,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "timeout_seconds": timeout_seconds,
        "total_wall_time_seconds": float(round(total_elapsed_s, 3)),
        "latency_ms": latency_stats,
        "status_codes": status_codes,
        "timestamp": datetime.now().isoformat(),
        "git_commit": git_commit(),
    }

    if save_artifact:
        artifact_path = target_dir / "latency_benchmark.json"
        artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


if __name__ == "__main__":
    res = run_latency_benchmark()
    print(json.dumps(res, indent=2))
