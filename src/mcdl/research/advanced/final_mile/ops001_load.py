"""OPS-001 Capacity / Load Stress Harness.

Progressive API load testing from 10 req/s to 5000 req/s.
Evaluates the FastAPI /api/score endpoint using an async client.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any
import numpy as np
from httpx import AsyncClient, ASGITransport

from api.main import app
from mcdl.config import REPO_ROOT

class OPS001Runner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir else REPO_ROOT / "research_runs" / "ADVANCED" / "OPS-001"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rates = [10, 100, 500, 1000, 2000, 5000]
        self.duration_sec = 5  # Test each tier for 5 seconds
        
    async def load_test_tier(self, client: AsyncClient, txns: list[dict], target_rate: int) -> dict[str, Any]:
        """Runs a constant-throughput load test at target_rate req/s."""
        total_requests = target_rate * self.duration_sec
        interval = 1.0 / target_rate
        
        latencies = []
        errors = 0
        successes = 0
        
        async def make_req(txn):
            t0 = time.perf_counter()
            try:
                resp = await client.post("/api/score", json={"transaction": txn})
                if resp.status_code == 200:
                    return time.perf_counter() - t0, True
                else:
                    return time.perf_counter() - t0, False
            except Exception:
                return 0.0, False

        tasks = []
        start_time = time.perf_counter()
        
        # We fire off tasks at the requested rate
        for i in range(total_requests):
            expected_time = start_time + (i * interval)
            now = time.perf_counter()
            if expected_time > now:
                await asyncio.sleep(expected_time - now)
            
            txn = txns[i % len(txns)]
            tasks.append(asyncio.create_task(make_req(txn)))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        actual_duration = time.perf_counter() - start_time
        
        for r in results:
            if isinstance(r, tuple):
                lat, success = r
                if success:
                    successes += 1
                    latencies.append(lat * 1000.0)
                else:
                    errors += 1
            else:
                errors += 1
                
        if latencies:
            lat_arr = np.array(latencies)
            p50 = float(np.percentile(lat_arr, 50))
            p95 = float(np.percentile(lat_arr, 95))
            p99 = float(np.percentile(lat_arr, 99))
            mean_lat = float(np.mean(lat_arr))
        else:
            p50 = p95 = p99 = mean_lat = 0.0
            
        throughput = successes / actual_duration if actual_duration > 0 else 0.0
        
        return {
            "target_rate": target_rate,
            "actual_throughput": round(throughput, 2),
            "P50": round(p50, 3),
            "P95": round(p95, 3),
            "P99": round(p99, 3),
            "mean_latency": round(mean_lat, 3),
            "error_rate": round(errors / max(1, total_requests), 4),
            "successful_requests": successes,
            "failed_requests": errors
        }

    async def run_async(self):
        print("Starting OPS-001 Capacity Load Stress...")
        # Use baseline artifacts for txns
        txns_path = REPO_ROOT / "artifacts" / "run_tiny_s20260827_193f7897_40997ab" / "transactions.json"
        if txns_path.exists():
            txns = json.loads(txns_path.read_text())
        else:
            txns = [{"txn_id": "dummy", "amount": 100.0}] * 100
            
        results = []
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Warmup
            print("Warming up...")
            await self.load_test_tier(client, txns, 10)
            
            for rate in self.rates:
                print(f"Testing {rate} req/s...")
                res = await self.load_test_tier(client, txns, rate)
                results.append(res)
                if res["error_rate"] > 0.05 or res["P95"] > 200.0:
                    print(f"Degradation threshold met at {rate} req/s. Stopping.")
                    break
                await asyncio.sleep(1) # cool down
                
        output = {
            "experiment_id": "OPS-001",
            "load_curve": results,
            "final_status": "COMPLETED",
            "infrastructure": "Cloud Kaggle CPU" if "KAGGLE_KERNEL_RUN_TYPE" in __import__("os").environ else "Local Dev"
        }
        
        with open(self.output_dir / "load_curve.json", "w") as f:
            json.dump(output, f, indent=2)
            
        with open(self.output_dir / "status.json", "w") as f:
            json.dump({"status": "COMPLETED"}, f)
            
    def run(self):
        asyncio.run(self.run_async())

if __name__ == "__main__":
    OPS001Runner().run()
