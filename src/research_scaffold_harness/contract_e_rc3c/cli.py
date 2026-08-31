"""CLI for the research-only RC3C native authority consumer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from research_scaffold_harness.contract_e_rc3c.validator import evaluate, evaluate_envelope


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _emit(decision_dict: dict[str, Any]) -> None:
    click.echo(json.dumps(decision_dict, indent=2, sort_keys=True))


@click.group()
def main() -> None:
    """Evaluate Contract E RC3C research authority objects natively."""


@main.command("evaluate")
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Unified request JSON with kind/envelope/registry/parent/child/record.",
)
@click.option(
    "--envelope",
    "envelope_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Authority envelope JSON.",
)
@click.option(
    "--registry",
    "registry_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Authority-basis registry JSON.",
)
@click.option(
    "--mode",
    default="new_exercise",
    show_default=True,
    type=click.Choice(("new_exercise", "historical_inspection")),
)
def evaluate_cmd(
    input_path: Path | None,
    envelope_path: Path | None,
    registry_path: Path | None,
    mode: str,
) -> None:
    """Evaluate a unified request or a native envelope plus registry."""
    try:
        if input_path is not None:
            request = _load_json(input_path)
            if "mode" not in request:
                request["mode"] = mode
            decision = evaluate(request)
        elif envelope_path is not None:
            envelope = _load_json(envelope_path)
            registry = _load_json(registry_path) if registry_path is not None else {}
            decision = evaluate_envelope(envelope, registry, mode)
        else:
            click.echo("Error: provide --input or --envelope", err=True)
            raise SystemExit(2)
    except OSError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON: {exc}", err=True)
        raise SystemExit(2) from exc
    _emit(decision.to_dict())


@main.command("evaluate-envelope")
@click.option(
    "--envelope",
    "envelope_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--registry",
    "registry_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--mode",
    default="new_exercise",
    show_default=True,
    type=click.Choice(("new_exercise", "historical_inspection")),
)
def evaluate_envelope_cmd(envelope_path: Path, registry_path: Path, mode: str) -> None:
    """Evaluate a native authority envelope against a basis registry."""
    try:
        decision = evaluate_envelope(_load_json(envelope_path), _load_json(registry_path), mode)
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    _emit(decision.to_dict())


@main.command("evaluate-propagation")
@click.option(
    "--request",
    "request_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def evaluate_propagation_cmd(request_path: Path) -> None:
    """Evaluate a native propagation request."""
    try:
        payload = _load_json(request_path)
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    if isinstance(payload, dict) and payload.get("kind") == "propagation":
        decision = evaluate(payload)
    else:
        decision = evaluate({"kind": "propagation", "request": payload})
    _emit(decision.to_dict())


@main.command("evaluate-delegation")
@click.option(
    "--parent",
    "parent_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--child",
    "child_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--mode",
    default="new_exercise",
    show_default=True,
    type=click.Choice(("new_exercise", "historical_inspection")),
)
def evaluate_delegation_cmd(parent_path: Path, child_path: Path, mode: str) -> None:
    """Evaluate native delegation parent/child objects."""
    try:
        parent = _load_json(parent_path)
        child = _load_json(child_path)
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    decision = evaluate({"kind": "delegation", "parent": parent, "child": child, "mode": mode})
    _emit(decision.to_dict())


@main.command("evaluate-historical")
@click.option(
    "--record",
    "record_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--registry",
    "registry_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option("--new-exercise", is_flag=True, help="Require live currentness recheck.")
def evaluate_historical_cmd(
    record_path: Path,
    registry_path: Path | None,
    new_exercise: bool,
) -> None:
    """Evaluate a historical authority record (inspection or new-exercise recheck)."""
    try:
        record = _load_json(record_path)
        registry = _load_json(registry_path) if registry_path is not None else {}
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2) from exc
    mode = "new_exercise" if new_exercise else "historical_inspection"
    decision = evaluate(
        {"kind": "historical", "record": record, "registry": registry, "mode": mode}
    )
    _emit(decision.to_dict())


if __name__ == "__main__":
    main()
