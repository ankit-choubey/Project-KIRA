"""Environment Profile & Compute Resource Detection.

Dynamically probes CPU, RAM, and GPU resources without making rigid hardware assumptions.
"""

from __future__ import annotations

import os
import platform
import sys
from typing import Any


def detect_environment_profile() -> dict[str, Any]:
    """Inspects host machine resources and returns execution profile."""
    profile: dict[str, Any] = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count() or 1,
        "gpu_available": False,
        "gpu_count": 0,
        "gpu_name": None,
        "gpu_vram_gb": 0.0,
        "ram_gb": 0.0,
        "torch_available": False,
        "lightgbm_available": False,
    }

    # Memory inspection
    try:
        import psutil
        profile["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        profile["ram_gb"] = "UNKNOWN (psutil not installed)"

    # PyTorch & Accelerator inspection
    try:
        import torch
        profile["torch_available"] = True
        profile["torch_version"] = torch.__version__
        if torch.cuda.is_available():
            profile["gpu_available"] = True
            profile["gpu_count"] = torch.cuda.device_count()
            profile["gpu_name"] = torch.cuda.get_device_name(0)
            profile["gpu_vram_gb"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
            )
    except ImportError:
        profile["torch_available"] = False

    # LightGBM inspection
    try:
        import lightgbm
        profile["lightgbm_available"] = True
        profile["lightgbm_version"] = lightgbm.__version__
    except ImportError:
        profile["lightgbm_available"] = False

    return profile
