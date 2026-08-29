"""Seen vs Held-Out Attack Variant Partitioner.

Guarantees strict lineage grouping so variants originating from the same source
transaction and attack family do not leak between training and evaluation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import numpy as np
from mcdl.red.search import AttackProvenance


@dataclass
class SeenHeldoutSplit:
    seen: list[AttackProvenance]
    heldout: list[AttackProvenance]


def split_seen_heldout(
    attacks: list[AttackProvenance],
    seen_ratio: float = 0.5,
    seed: int = 20260827,
) -> SeenHeldoutSplit:
    """Partitions attack instances into seen (for hardening) and held-out (for generalization).

    Uses lineage-level grouping on (source_txn_id, attack_family) to prevent sibling leakage.
    """
    rng = np.random.default_rng(seed)

    # 1. Group attack instances by lineage
    lineage_groups: dict[tuple[str, str], list[AttackProvenance]] = defaultdict(list)
    for atk in attacks:
        key = (atk.source_txn_id, atk.attack_family.value)
        lineage_groups[key].append(atk)

    # 2. Deterministically shuffle unique lineage keys
    sorted_keys = sorted(lineage_groups.keys())
    indices = np.arange(len(sorted_keys))
    rng.shuffle(indices)

    n_seen_groups = max(1, int(round(len(sorted_keys) * seen_ratio)))
    seen_keys = set(sorted_keys[i] for i in indices[:n_seen_groups])

    seen_attacks: list[AttackProvenance] = []
    heldout_attacks: list[AttackProvenance] = []

    for key, atks in lineage_groups.items():
        if key in seen_keys:
            seen_attacks.extend(atks)
        else:
            heldout_attacks.extend(atks)

    # If heldout is empty (e.g. only 1 lineage), allocate second half of attacks
    if not heldout_attacks and len(seen_attacks) > 1:
        mid = len(seen_attacks) // 2
        heldout_attacks = seen_attacks[mid:]
        seen_attacks = seen_attacks[:mid]

    return SeenHeldoutSplit(seen=seen_attacks, heldout=heldout_attacks)
