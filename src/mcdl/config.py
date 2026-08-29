"""Config loading. One file, one `scale` knob - there are no per-machine profiles.

The compute-profile machinery in the original spec was designed around a GPU
constraint that does not apply: this whole project is CPU tabular work.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "configs" / "base.yaml"

_VALID_SCALES = ("tiny", "small", "full")


class Config(dict):
    """Dict with attribute access for the top level, plus a stable hash."""

    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as exc:  # pragma: no cover - programmer error
            raise AttributeError(item) from exc

    @property
    def hash(self) -> str:
        payload = json.dumps(self, sort_keys=True, default=str).encode()
        return hashlib.sha256(payload).hexdigest()[:12]


def load_config(path: Path | str | None = None, scale: str | None = None) -> Config:
    """Load `configs/base.yaml`, resolve the active scale preset, validate.

    Resolution order for scale: explicit arg > MCDL_SCALE env var > file value.
    """
    path = Path(path) if path else DEFAULT_CONFIG
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    scale = scale or os.environ.get("MCDL_SCALE") or raw.get("scale", "tiny")
    if scale not in _VALID_SCALES:
        raise ValueError(f"scale must be one of {_VALID_SCALES}, got {scale!r}")

    raw["scale"] = scale
    raw["world"].update(raw["scale_presets"][scale])

    _validate(raw)
    return Config(raw)


def _validate(cfg: dict[str, Any]) -> None:
    """Fail at load time rather than three modules later."""
    shares = cfg["world"]["archetypes"]
    total = sum(shares.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"world.archetypes must sum to 1.0, got {total}")

    split = cfg["split"]
    split_total = split["train_frac"] + split["valid_frac"] + split["test_frac"]
    if abs(split_total - 1.0) > 1e-9:
        raise ValueError(f"split fractions must sum to 1.0, got {split_total}")

    hidden = set(cfg["red"]["hidden_from_blue"])
    families = set(cfg["red"]["families"])
    if not hidden <= families:
        raise ValueError(f"red.hidden_from_blue not a subset of red.families: {hidden - families}")
    if not hidden:
        raise ValueError("red.hidden_from_blue is empty - the zero-day transfer test needs it")

    harden_on = cfg["red"]["harden_on_variants"]
    variants = cfg["red"]["variants_per_family"]
    if harden_on >= variants:
        raise ValueError(
            f"harden_on_variants ({harden_on}) must be < variants_per_family ({variants}), "
            "otherwise there are no held-out variants and the loop measures memorisation"
        )


def artifacts_dir(cfg: Config | None = None) -> Path:
    cfg = cfg or load_config()
    p = REPO_ROOT / cfg["paths"]["artifacts"]
    p.mkdir(parents=True, exist_ok=True)
    return p
