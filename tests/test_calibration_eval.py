"""Calibration metric script tests (round-2 containment matcher + exact baseline)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

_SCRIPT = Path(__file__).parents[1] / "scripts" / "calibration" / "extractor_eval.py"
_SPEC = importlib.util.spec_from_file_location("extractor_eval", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
extractor_eval = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(extractor_eval)


def test_evaluate_extractors_exact_mode_reports_precision_recall_f1() -> None:
    gold = {
        "cell-a": {"claim one", "claim two"},
        "cell-b": {"claim three"},
    }
    predictions = {
        "stub": {
            "cell-a": {"claim one", "extra claim"},
            "cell-b": {"claim three"},
        },
        "nemo": {
            "cell-a": {"claim one", "claim two"},
            "cell-b": set(),
        },
    }

    report = extractor_eval.evaluate_extractors(gold, predictions, match_mode="exact")

    assert report["match_mode"] == "exact"
    assert report["gold_cell_count"] == 2
    assert report["gold_claim_count"] == 3
    assert report["extractors"]["stub"]["true_positive"] == 2
    assert report["extractors"]["stub"]["false_positive"] == 1
    assert report["extractors"]["stub"]["false_negative"] == 1
    assert report["extractors"]["stub"]["f1"] == 0.6667
    assert "nemo__vs__stub" in report["pairwise_agreement"]


def test_containment_compound_claim_satisfies_split_gold() -> None:
    """The anchor case (rsh-f6e603ab0646): Nemo's compound claim must recall
    BOTH split gold claims it covers — the exact-match round-1 bug scored it 0."""
    gold = {
        "anchor": {
            # G1 — the "core elements include X, Y, Z" framing claim Nemo never states.
            "the core elements of a pharmaceutical quality system under fda cgmp "
            "guidance include management responsibility production system controls "
            "and laboratory and documentation controls",
            # G2 + G3 — the split pair Nemo lumps into one compound claim.
            "senior management establishes quality policy objectives",
            "senior management allocates adequate resources for manufacturing operations",
            # G4, G5 — verbatim matches.
            "process validation demonstrates that manufacturing operations produce "
            "consistent results within predefined specifications",
            "analytical methods undergo validation to confirm specificity accuracy "
            "and reproducibility",
        }
    }
    nemo = {
        "anchor": {
            # N1 — compound: covers G2 AND G3.
            "senior management establishes quality policy objectives and allocates "
            "adequate resources for manufacturing operations",
            "process validation demonstrates that manufacturing operations produce "
            "consistent results within predefined specifications",
            "analytical methods undergo validation to confirm specificity accuracy "
            "and reproducibility",
        }
    }

    containment = extractor_eval.evaluate_extractors(
        gold, {"nemo": nemo}, match_mode="containment", threshold=0.6
    )["extractors"]["nemo"]
    exact = extractor_eval.evaluate_extractors(
        gold, {"nemo": nemo}, match_mode="exact"
    )["extractors"]["nemo"]

    # Containment: G2, G3, G4, G5 all found (4/5); only the framing claim G1 missed.
    assert containment["gold_matched"] == 4
    assert containment["false_negative"] == 1
    # Every Nemo claim covers >=1 gold claim -> no false positives, precision 1.0.
    assert containment["true_positive"] == 3
    assert containment["false_positive"] == 0
    assert containment["recall"] == 0.8
    assert containment["precision"] == 1.0
    assert containment["f1"] == 0.8889
    assert containment["f1_tier"] == "strong"  # 0.85 <= 0.8889 < 0.95
    assert containment["clears_hard_floor"] is True

    # Exact match (round-1): the compound N1 matches nothing, so only the two
    # verbatim claims count -> the granularity penalty the round-2 matcher fixes.
    assert exact["gold_matched"] == 2
    assert exact["false_negative"] == 3
    assert containment["gold_matched"] > exact["gold_matched"]


def test_containment_flags_unmatched_prediction_as_false_positive() -> None:
    gold = {"cell": {"process validation demonstrates consistent manufacturing results"}}
    predictions = {
        "noise": {"cell": {"the weather today is sunny and warm"}},
    }

    report = extractor_eval.evaluate_extractors(gold, predictions, match_mode="containment")
    noise = report["extractors"]["noise"]

    assert noise["true_positive"] == 0
    assert noise["false_positive"] == 1
    assert noise["gold_matched"] == 0
    assert noise["false_negative"] == 1
    assert noise["f1"] == 0.0
    assert noise["clears_hard_floor"] is False


def test_content_tokens_strip_bullets_stopwords_and_fold_plurals() -> None:
    tokens = extractor_eval._content_tokens("- Management Responsibility is crucial")
    assert "management" in tokens
    assert "responsibility" in tokens
    assert "crucial" in tokens
    assert "is" not in tokens  # stopword
    assert "-" not in tokens  # bullet artifact stripped

    assert extractor_eval._fold_plural("controls") == "control"
    assert extractor_eval._fold_plural("objectives") == "objective"
    assert extractor_eval._fold_plural("operations") == "operation"
    assert extractor_eval._fold_plural("policies") == "policy"
    assert extractor_eval._fold_plural("process") == "process"  # -ss not folded
    assert extractor_eval._fold_plural("data") == "data"  # short token untouched


def test_plural_fold_lets_singular_and_plural_match() -> None:
    gold = {"cell": {"senior management establishes quality policy objectives"}}
    # Prediction uses the singular "objective" — should still match after folding.
    pred = {"cell": {"senior management establishes quality policy objective"}}

    report = extractor_eval.evaluate_extractors(gold, {"x": pred}, match_mode="containment")
    assert report["extractors"]["x"]["gold_matched"] == 1


def test_f1_tier_boundaries() -> None:
    assert extractor_eval._f1_tier(0.59) == ("hard_floor", False)
    assert extractor_eval._f1_tier(0.60) == ("minimum_acceptable", True)
    assert extractor_eval._f1_tier(0.75) == ("adequate", True)
    assert extractor_eval._f1_tier(0.85) == ("strong", True)
    assert extractor_eval._f1_tier(0.95) == ("excellent", True)


def test_kappa_uses_gold_claim_coverage_only() -> None:
    """κ should be measured over gold-claim coverage (DECISIONS § 2026-05-25),
    so two extractors that both catch the same gold claim agree perfectly."""
    gold = {"cell": {"alpha beta gamma delta", "epsilon zeta eta theta"}}
    left = {"cell": {"alpha beta gamma delta"}}
    right = {"cell": {"alpha beta gamma delta"}}

    report = extractor_eval.evaluate_extractors(
        gold, {"left": left, "right": right}, match_mode="containment"
    )
    assert report["pairwise_agreement"]["left__vs__right"]["cohen_kappa"] == 1.0


def test_load_predictions_accepts_extractor_sidecar(tmp_path: Path) -> None:
    sidecar = tmp_path / "claims_extractor_stub.yaml"
    sidecar.write_text(
        yaml.safe_dump({
            "extractor_id": "stub",
            "claims": {
                "run_id": "cell-a",
                "claims": [
                    {"claim_text": "Claim one"},
                    {"claim_text": "Claim two"},
                ],
            },
        }),
        encoding="utf-8",
    )

    assert extractor_eval.load_predictions(sidecar) == {
        "cell-a": {"claim one", "claim two"}
    }


def test_load_gold_rejects_sample_and_template_files(tmp_path: Path) -> None:
    for status in ("template_only_not_adjudicated", "sample_only_not_calibration_gold"):
        gold = tmp_path / f"{status}.yaml"
        gold.write_text(
            yaml.safe_dump({
                "status": status,
                "cells": [
                    {
                        "cell_id": "cell-a",
                        "adjudicated_claims": [{"claim_text": "Claim one"}],
                    }
                ],
            }),
            encoding="utf-8",
        )

        try:
            extractor_eval.load_gold(gold)
        except ValueError as exc:
            assert "copy the template to a dated, adjudicated gold file" in str(exc)
        else:
            raise AssertionError("sample/template gold file should be rejected")
