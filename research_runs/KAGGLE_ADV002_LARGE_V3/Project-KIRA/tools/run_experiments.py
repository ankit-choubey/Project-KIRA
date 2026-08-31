"""CLI Runner for Block 7 Experiments (EXP-007-A through EXP-007-H).

Usage:
    python -m tools.run_experiments --scale tiny --seed 20260827
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mcdl.config import load_config
from mcdl.evaluation.experiments import run_all_block7_experiments
from mcdl.features.batch import compute_batch_features
from mcdl.loop.coevolution import CoevolutionLoop
from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.world.generator import generate_world


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Block 7 Experiment Suite (EXP-007-A..H)")
    parser.add_argument("--scale", type=str, default="tiny", choices=["tiny", "small", "full"], help="World scale")
    parser.add_argument("--seed", type=int, default=20260827, help="Random seed")
    args = parser.parse_args()

    print(f"[*] Initializing Experiment Harness (scale={args.scale}, seed={args.seed})...")
    cfg = load_config(scale=args.scale)
    cfg["seed"] = args.seed

    print("[*] Generating synthetic world and extracting features...")
    world = generate_world(cfg)
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    print("[*] Running base Co-evolution Loop...")
    loop = CoevolutionLoop(
        n_rounds=4,
        budgets=[1, 5, 20, 100],
        families=CANONICAL_FAMILIES,
        seed=args.seed,
    )
    coev_res = loop.run(world.transactions, world, feature_df)

    print("\n[*] Executing EXP-007-A through EXP-007-H suite...")
    records = run_all_block7_experiments(
        world=world,
        feature_df=feature_df,
        cfg=cfg,
        coevo_result=coev_res,
    )

    print("\n" + "=" * 80)
    print("EXPERIMENT REGISTER (EXP-007-A .. EXP-007-H)")
    print("=" * 80)
    for rec in records:
        print(f"[{rec.exp_id}] {rec.hypothesis}")
        print(f"  Status: {rec.result_status} | Baseline: {rec.baseline_name} -> Treatment: {rec.treatment_name}")
        print(f"  Metrics: {rec.metrics}")
        print(f"  Conclusion: {rec.conclusion}")
        print("-" * 80)
    print("\n[+] All 8 Block 7 experiments executed and verified.")


if __name__ == "__main__":
    main()
