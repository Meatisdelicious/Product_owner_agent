"""Shared pytest configuration for unit and pipeline tests."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

# To run all unit tests:
# uv run pytest tests/unit_tests
