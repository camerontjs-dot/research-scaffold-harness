#!/usr/bin/env python3
"""Run the extractor calibration eval from committed files (git-reproducible).

The matrix-v2 build dir is gitignored, so the 8 gold cells' extractor sidecars
are copied into ``tests/calibration/extractor-outputs-<date>/<cell_id>/``. This
runner globs that tracked directory, rebuilds the per-extractor predictions, and
prints the calibration report — so the metrics in findings-log are recomputable
from the repository alone, with no build artifacts.

Usage (defaults point at the 2026-05-31 frozen gold + tracked sidecars):

    python scripts/calibration/run_calibration.py
    python scripts/calibration/run_calibration.py --match-mode exact

Extractor id is inferred from the sidecar filename suffix
(``claims_extractor_<id>.yaml``).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
_SPEC = importlib.util.spec_from_file_location("extractor_eval", _HERE / "extractor_eval.py")
assert _SPEC is not None and _SPEC.loader is not None
extractor_eval = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(extractor_eval)

DEFAULT_GOLD = _REPO / "tests" / "calibration" / "gold_2026-05-31.yaml"
DEFAULT_OUTPUTS = _REPO / "tests" / "calibration" / "extractor-outputs-2026-05-31"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--match-mode", choices=extractor_eval.MATCH_MODES, default="containment")
    parser.add_argument("--match-threshold", type=float, default=extractor_eval.DEFAULT_THRESHOLD)
    args = parser.parse_args()

    gold = extractor_eval.load_gold(args.gold)
    predictions: dict[str, dict[str, set[str]]] = {}
    sidecars = sorted(args.outputs_dir.glob("*/claims_extractor_*.yaml"))
    if not sidecars:
        raise SystemExit(f"No sidecars found under {args.outputs_dir}")
    for sidecar in sidecars:
        extractor_id = sidecar.stem.removeprefix("claims_extractor_")
        predictions.setdefault(extractor_id, {}).update(extractor_eval.load_predictions(sidecar))

    report = extractor_eval.evaluate_extractors(
        gold,
        predictions,
        match_mode=args.match_mode,
        threshold=args.match_threshold,
    )
    report = {
        "gold_file": str(args.gold.relative_to(_REPO)),
        "outputs_dir": str(args.outputs_dir.relative_to(_REPO)),
        "sidecar_count": len(sidecars),
        **report,
    }
    yaml.safe_dump(report, sys.stdout, sort_keys=False, allow_unicode=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
