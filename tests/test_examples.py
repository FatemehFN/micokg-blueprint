"""Valid examples must pass schema validation; invalid examples must fail."""

from pathlib import Path

import pytest
import yaml
from linkml.validator import validate

from scripts.kg import ROOT, merged_schema

VALID = sorted((ROOT / "examples" / "valid").glob("*.yaml"))
INVALID = sorted((ROOT / "examples" / "invalid").glob("*.yaml"))


def _errors(path: Path) -> list[str]:
    instance = yaml.safe_load(path.read_text()) or {}
    report = validate(instance, merged_schema(), "Container")
    return [r.message for r in report.results]


@pytest.mark.parametrize("path", VALID, ids=[p.name for p in VALID])
def test_valid_example(path):
    assert _errors(path) == []


@pytest.mark.parametrize("path", INVALID, ids=[p.name for p in INVALID])
def test_invalid_example(path):
    assert _errors(path), f"{path.name} should fail validation"
