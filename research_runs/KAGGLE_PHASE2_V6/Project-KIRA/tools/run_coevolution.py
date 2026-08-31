"""CLI Runner for Multi-Round Adversarial Co-Evolution.

Usage:
    python -m tools.run_coevolution --scale tiny --rounds 4 --seed 20260827
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mcdl.config import load_config
from mcdl.features.batch import compute_batch_features
from mcdl.loop.coevolution import CoevolutionLoop
from mcdl.red.evaluator import CANONICAL_FAMILIES
from mcdl.world.generator import generate_world


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Multi-Round Adversarial Co-Evolution Loop")
    parser.add_argument("--scale", type=str, default="tiny", choices=["tiny", "small", "full"], help="World scale")
    parser.add_argument("--rounds", type=int, default=4, help="Number of co-evolution rounds")
    parser.add_argument("--seed", type=int, default=20260827, help="Random seed")
    args = parser.parse_args()

    print(f"[*] Initializing Co-Evolution Loop (scale={args.scale}, rounds={args.rounds}, seed={args.seed})...")
    cfg = load_config(scale=args.scale)
    cfg["seed"] = args.seed

    print("[*] Generating synthetic payment world...")
    world = generate_world(cfg)

    print("[*] Extracting causal batch features...")
    feature_df = compute_batch_features(world.transactions, customers=world.customers)

    print("[*] Executing Co-Evolution Loop...")
    loop = CoevolutionLoop(
        n_rounds=args.rounds,
        budgets=[1, 5, 20, 100],
        families=CANONICAL_FAMILIES,
        seed=args.seed,
    )
    result = loop.run(
        all_transactions=world.transactions,
        world=world,
        feature_df=feature_df,
    )

    print("\n" + "=" * 70)
    print("CO-EVOLUTION SCOREBOARD")
    print("=" * 70)
    for entry in result.scoreboard:
        print(
            f"Round {entry.round_index} [{entry.champion_version}]: "
            f"Seen ASR={entry.red_asr_seen:.2%} | Held-out ASR={entry.heldout_asr:.2%} | "
            f"PR-AUC={entry.blue_pr_auc:.4f} | FPR={entry.blue_fpr:.6f} | "
            f"Retention={entry.robustness_retention:.4f} | Plasticity={entry.plasticity:.4f}"
        )
    print("=" * 70 + "\n")
    print("[+] Co-Evolution execution complete.")


if __name__ == "__main__":
    main()
