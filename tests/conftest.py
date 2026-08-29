"""Make `src/` importable without an editable install.

Keeps `pytest` working straight from a clean clone, which matters because gate 0
shells out to pytest and both developers must be able to run it immediately.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
