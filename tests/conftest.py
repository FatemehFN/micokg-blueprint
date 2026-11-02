import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.kg import build_store  # noqa: E402


@pytest.fixture(scope="session")
def kg():
    """In-memory Oxigraph store with all valid examples, slims and curated mappings."""
    return build_store()
