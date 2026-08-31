"""Evaluate a Contract E authority case from JSON and emit a structured outcome."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .spec_loader import SpecLoadError, load_specs
from .validator import evaluate


def _load_case(path: Path | None) -> dict[str, Any]:
    if path is None or str(path) == "-":
        raw = sys.stdin.read()
        source = "stdin"
    else:
        raw = path.read_text(encoding="utf-8")
        source = str(path)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON ({source}): {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"case {source} is not a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independent Contract E authority/warrant evaluator (research only)."
    )
    parser.add_argument(
        "case",
        nargs="?",
        help="Path to a JSON case file, or - for stdin",
    )
    parser.add_argument(
        "--authority-input",
        dest="authority_input",
        default=None,
        help="Directory containing the four authorized specification files",
    )
    args = parser.parse_args(argv)
    try:
        spec = load_specs(Path(args.authority_input) if args.authority_input else None)
    except SpecLoadError as exc:
        print(json.dumps({"outcome": "reject", "primary_reason": "malformed_envelope", "error": str(exc)}))
        return 2
    case_path = Path(args.case) if args.case and args.case != "-" else None
    case = _load_case(case_path if args.case != "-" else None)
    result = evaluate(case, spec)
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.get("outcome") == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
