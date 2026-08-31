"""CLI smoke tests for the native RC3C consumer."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from research_scaffold_harness.contract_e_rc3c.cli import main
from tests.contract_e_rc3c.factories import make_delegation, pair


def test_evaluate_envelope_cli(tmp_path: Path) -> None:
    envelope, registry = pair()
    envelope_path = tmp_path / "envelope.json"
    registry_path = tmp_path / "registry.json"
    envelope_path.write_text(json.dumps(envelope), encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    result = CliRunner().invoke(
        main,
        ["evaluate-envelope", "--envelope", str(envelope_path), "--registry", str(registry_path)],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["accepted"] is True
    assert payload["primary_reason"] is None


def test_evaluate_unified_request_cli(tmp_path: Path) -> None:
    envelope, registry = pair("decision_mandate")
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps({"kind": "envelope", "envelope": envelope, "registry": registry}),
        encoding="utf-8",
    )
    result = CliRunner().invoke(main, ["evaluate", "--input", str(request_path)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["accepted"] is True


def test_evaluate_delegation_cli(tmp_path: Path) -> None:
    parent_path = tmp_path / "parent.json"
    child_path = tmp_path / "child.json"
    parent_path.write_text(json.dumps(make_delegation(role="parent")), encoding="utf-8")
    child_path.write_text(json.dumps(make_delegation(role="child")), encoding="utf-8")
    result = CliRunner().invoke(
        main,
        ["evaluate-delegation", "--parent", str(parent_path), "--child", str(child_path)],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["accepted"] is True
    assert payload["evaluation_kind"] == "delegation"


def test_evaluate_historical_new_exercise_cli(tmp_path: Path) -> None:
    record_path = tmp_path / "hist.json"
    record_path.write_text(
        json.dumps(
            {
                "evaluated_at": "2026-06-15T12:00:00Z",
                "authority_was_valid_at_time": True,
                "authority_basis_ids": ["grant-1"],
            }
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        main,
        ["evaluate-historical", "--record", str(record_path), "--new-exercise"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["accepted"] is False
    assert payload["primary_reason"] == "authority_basis_not_current"


def test_evaluate_propagation_cli(tmp_path: Path) -> None:
    path = tmp_path / "prop.json"
    path.write_text(json.dumps({"mode": "none"}), encoding="utf-8")
    result = CliRunner().invoke(main, ["evaluate-propagation", "--request", str(path)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["accepted"] is True
