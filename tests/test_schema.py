"""Schema embedding tests — Phase 1 Unit 2.

The harness embeds a byte-identical copy of the canonical apparatus
vocabulary, plus a contract-version pin file. These tests assert both
files exist with the expected shape.
"""

from __future__ import annotations

from pathlib import Path

import yaml

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema"


def test_contract_version_pin_reads_one_one_zero() -> None:
    pin_path = SCHEMA_DIR / ".contract-version"
    assert pin_path.exists(), f"missing contract-version pin at {pin_path}"
    assert pin_path.read_text(encoding="utf-8").strip() == "1.1.0"


def test_vocabulary_includes_format_only() -> None:
    vocab_path = SCHEMA_DIR / "vocabulary.yaml"
    assert vocab_path.exists(), f"missing vocabulary at {vocab_path}"
    data = yaml.safe_load(vocab_path.read_text(encoding="utf-8"))
    assert data["contract_version"] == "1.1.0"
    workflow_values = data["vocabularies"]["workflow_condition"]["values"]
    assert "format_only" in workflow_values
    assert set(workflow_values) == {
        "baseline",
        "format_only",
        "provenance_scaffold",
        "full_scaffold",
    }
