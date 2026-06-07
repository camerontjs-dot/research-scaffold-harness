#!/usr/bin/env python3
"""Evaluate extractor claim output against a human-adjudicated gold YAML file.

Matching modes (``--match-mode``):

* ``containment`` (default, round-2 matcher) — alignment-aware, deterministic
  token-overlap. A gold claim is *found* if some extractor claim contains at
  least ``--match-threshold`` of the gold claim's content tokens (stopword
  stripped, lightly plural-folded). The match is **non-consuming**: one
  compound extractor claim may satisfy several split gold claims (e.g. Nemo's
  "establishes objectives *and* allocates resources" covers two split gold
  claims). Symmetrically, an extractor claim that covers no gold claim is a
  false positive. Precision is extractor-claim-centric (fraction of emitted
  claims that hit gold); recall is gold-centric (fraction of gold claims
  surfaced). This is the matcher chosen in findings-log 2026-05-31: fully
  recomputable, no model, transparent to reviewers.

* ``exact`` — round-1 behaviour, retained as a comparison baseline. A gold and
  extractor claim match iff their normalized strings are identical.

Cohen's κ is computed per DECISIONS § 2026-05-25: for each gold claim, label
"did extractor X catch it" (covered / not) and compute κ over those per-claim
binary assignments, restricted to cells where at least one of the two
extractors produced ≥1 claim.

Known v0.1 limitations (documented, not silently capped):

* **One-directional.** Coverage is denominated in the *gold* claim's tokens, so
  one compound extractor claim can satisfy several split gold claims (handled),
  but several fine extractor shards canNOT jointly satisfy one lumped gold claim
  — each shard covers < threshold of the lump and is scored a false positive.
  This mildly under-rates extractors that split finer than the gold's adjudicated
  granularity.
* **Kitchen-sink.** A single verbose claim containing every gold token is not
  penalised on precision.
* **No paraphrase/synonym handling.** Local-embedding cosine is the recorded
  v0.2 fallback if validation shows paraphrase is silently hurting recall.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

DEFAULT_THRESHOLD = 0.6
MATCH_MODES = ("containment", "exact")

# Pure function words only. Domain verbs ("establishes", "validates",
# "demonstrates") and enumeration cues are intentionally NOT stopwords — they
# carry propositional content. Applied identically to gold and predictions.
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "of", "for",
    "to", "in", "on", "at", "by", "with", "from", "into", "onto", "upon", "as",
    "is", "are", "was", "were", "be", "been", "being", "am", "this", "that",
    "these", "those", "it", "its", "their", "they", "them", "which", "who",
    "whom", "whose", "such", "via", "per", "each", "any", "all", "both", "also",
    "not", "no", "nor", "so", "than", "within", "across", "under", "over",
    "between", "through", "during", "while", "about", "above", "below", "out",
    "up", "down", "off", "again", "further", "there", "here", "when", "where",
    "why", "how",
})

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def main() -> int:
    args = _parse_args()
    gold = load_gold(args.gold)
    predictions: dict[str, dict[str, set[str]]] = {}
    for spec in args.extractor_output:
        extractor_id, path = _parse_extractor_spec(spec)
        predictions.setdefault(extractor_id, {}).update(load_predictions(path))

    report = evaluate_extractors(
        gold,
        predictions,
        match_mode=args.match_mode,
        threshold=args.match_threshold,
    )
    yaml.safe_dump(report, sys.stdout, sort_keys=False, allow_unicode=True)
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True, help="Human gold YAML file.")
    parser.add_argument(
        "--extractor-output",
        action="append",
        default=[],
        metavar="EXTRACTOR_ID=PATH",
        help="Extractor output YAML. Repeat for stub, Nemo, and Small 3.",
    )
    parser.add_argument(
        "--match-mode",
        choices=MATCH_MODES,
        default="containment",
        help="Claim matcher: 'containment' (default, token-overlap) or 'exact' (round-1 baseline).",
    )
    parser.add_argument(
        "--match-threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=(
            "Containment threshold: a gold claim is found when an extractor "
            f"claim contains >= this fraction of its content tokens (default {DEFAULT_THRESHOLD})."
        ),
    )
    return parser.parse_args()


def _parse_extractor_spec(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise SystemExit(f"Invalid --extractor-output {spec!r}; expected EXTRACTOR_ID=PATH")
    extractor_id, path = spec.split("=", 1)
    if not extractor_id or not path:
        raise SystemExit(f"Invalid --extractor-output {spec!r}; expected EXTRACTOR_ID=PATH")
    return extractor_id, Path(path)


def load_gold(path: Path) -> dict[str, set[str]]:
    data = _load_yaml(path)
    status = str(data.get("status", "")).strip()
    if status in {"template_only_not_adjudicated", "sample_only_not_calibration_gold"}:
        raise ValueError(
            f"{path} is {status!r}; copy the template to a dated, adjudicated gold "
            "file before running calibration."
        )
    cells = data.get("cells", [])
    if not isinstance(cells, list):
        raise ValueError("gold YAML must contain a cells list")
    gold: dict[str, set[str]] = {}
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_id = str(cell.get("cell_id", "")).strip()
        if not cell_id:
            continue
        claims = cell.get("adjudicated_claims", [])
        gold[cell_id] = _claim_set(claims)
    return gold


def load_predictions(path: Path) -> dict[str, set[str]]:
    data = _load_yaml(path)
    if isinstance(data.get("cells"), list):
        return {
            str(cell.get("cell_id")): _claim_set(cell.get("claims", []))
            for cell in data["cells"]
            if isinstance(cell, dict) and cell.get("cell_id")
        }
    claims_doc = data.get("claims", data)
    if isinstance(claims_doc, dict) and isinstance(claims_doc.get("claims"), dict):
        claims_doc = claims_doc["claims"]
    if isinstance(claims_doc, dict):
        cell_id = str(claims_doc.get("run_id", data.get("run_id", ""))).strip()
        return {cell_id: _claim_set(claims_doc.get("claims", []))} if cell_id else {}
    return {}


def evaluate_extractors(
    gold: dict[str, set[str]],
    predictions: dict[str, dict[str, set[str]]],
    *,
    match_mode: str = "containment",
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    if match_mode not in MATCH_MODES:
        raise ValueError(f"match_mode must be one of {MATCH_MODES}, got {match_mode!r}")
    metrics = {
        extractor_id: _precision_recall_f1(
            gold, by_cell, match_mode=match_mode, threshold=threshold
        )
        for extractor_id, by_cell in sorted(predictions.items())
    }
    agreements: dict[str, Any] = {}
    extractor_ids = sorted(predictions)
    for left_index, left in enumerate(extractor_ids):
        for right in extractor_ids[left_index + 1:]:
            kappa = _cohen_kappa(
                predictions[left],
                predictions[right],
                gold,
                match_mode=match_mode,
                threshold=threshold,
            )
            agreements[f"{left}__vs__{right}"] = {
                "cohen_kappa": kappa,
                "kappa_tier": _kappa_tier(kappa),
            }
    return {
        "match_mode": match_mode,
        "match_threshold": threshold if match_mode == "containment" else None,
        "gold_cell_count": len(gold),
        "gold_claim_count": sum(len(claims) for claims in gold.values()),
        "extractors": metrics,
        "pairwise_agreement": agreements,
    }


def _precision_recall_f1(
    gold: dict[str, set[str]],
    predictions: dict[str, set[str]],
    *,
    match_mode: str,
    threshold: float,
) -> dict[str, Any]:
    gold_total = gold_matched = 0
    pred_total = pred_matched = 0
    per_cell: dict[str, Any] = {}
    for cell_id, gold_claims in gold.items():
        preds = predictions.get(cell_id, set())
        recalled = {
            g for g in gold_claims
            if any(_matches(g, p, match_mode, threshold) for p in preds)
        }
        useful = {
            p for p in preds
            if any(_matches(g, p, match_mode, threshold) for g in gold_claims)
        }
        gold_total += len(gold_claims)
        gold_matched += len(recalled)
        pred_total += len(preds)
        pred_matched += len(useful)
        missed = sorted(gold_claims - recalled)
        spurious = len(preds) - len(useful)
        if missed or spurious:
            per_cell[cell_id] = {
                "recall": f"{len(recalled)}/{len(gold_claims)}",
                "precision": f"{len(useful)}/{len(preds)}",
                "missed_gold": missed,
                "false_positive": spurious,
            }
    false_negative = gold_total - gold_matched
    false_positive = pred_total - pred_matched
    precision = pred_matched / pred_total if pred_total else 0.0
    recall = gold_matched / gold_total if gold_total else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    tier, clears = _f1_tier(f1)
    return {
        "true_positive": pred_matched,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "gold_matched": gold_matched,
        "gold_total": gold_total,
        "pred_total": pred_total,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "f1_tier": tier,
        "clears_hard_floor": clears,
        "per_cell": per_cell,
    }


def _cohen_kappa(
    left: dict[str, set[str]],
    right: dict[str, set[str]],
    gold: dict[str, set[str]],
    *,
    match_mode: str,
    threshold: float,
) -> float:
    # Per DECISIONS § 2026-05-25: for each gold claim, label "extractor caught
    # it" (covered / not) for each extractor; κ over those binary labels.
    # Restrict to cells where >=1 of the two extractors produced >=1 claim.
    pairs: list[tuple[bool, bool]] = []
    for cell_id, gold_claims in gold.items():
        left_preds = left.get(cell_id, set())
        right_preds = right.get(cell_id, set())
        if not left_preds and not right_preds:
            continue
        for claim in gold_claims:
            caught_left = any(_matches(claim, p, match_mode, threshold) for p in left_preds)
            caught_right = any(_matches(claim, p, match_mode, threshold) for p in right_preds)
            pairs.append((caught_left, caught_right))
    if not pairs:
        return 0.0
    observed = sum(1 for a, b in pairs if a == b) / len(pairs)
    left_yes = sum(1 for a, _ in pairs if a) / len(pairs)
    right_yes = sum(1 for _, b in pairs if b) / len(pairs)
    expected = left_yes * right_yes + (1 - left_yes) * (1 - right_yes)
    if expected == 1.0:
        return 1.0
    return round((observed - expected) / (1 - expected), 4)


def _matches(gold_claim: str, pred_claim: str, match_mode: str, threshold: float) -> bool:
    if match_mode == "exact":
        return gold_claim == pred_claim
    gold_tokens = _content_tokens(gold_claim)
    if not gold_tokens:
        # Degenerate gold claim (all stopwords): fall back to exact equality.
        return gold_claim == pred_claim
    pred_tokens = _content_tokens(pred_claim)
    overlap = len(gold_tokens & pred_tokens) / len(gold_tokens)
    return overlap >= threshold


def _content_tokens(text: str) -> frozenset[str]:
    """Lowercase, drop punctuation/bullets, remove stopwords, light plural fold."""
    tokens = (
        _fold_plural(tok)
        for tok in _TOKEN_RE.findall(text.casefold())
        if tok not in _STOPWORDS
    )
    return frozenset(tok for tok in tokens if tok and tok not in _STOPWORDS)


def _fold_plural(token: str) -> str:
    """Deterministic light plural folding (controls->control, objectives->objective)."""
    if len(token) <= 4:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("ses", "xes", "zes", "ches", "shes")):
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _f1_tier(f1: float) -> tuple[str, bool]:
    """Map F1 to the DECISIONS § 2026-05-25 graduated tier; bool = clears hard floor."""
    if f1 < 0.60:
        return ("hard_floor", False)
    if f1 < 0.75:
        return ("minimum_acceptable", True)
    if f1 < 0.85:
        return ("adequate", True)
    if f1 < 0.95:
        return ("strong", True)
    return ("excellent", True)


def _kappa_tier(kappa: float) -> str:
    if kappa < 0.40:
        return "hard_floor"
    if kappa < 0.60:
        return "minimum_acceptable"
    if kappa < 0.75:
        return "adequate"
    if kappa < 0.85:
        return "strong"
    return "excellent"


def _claim_set(claims: Any) -> set[str]:
    normalized: set[str] = set()
    if not isinstance(claims, list):
        return normalized
    for claim in claims:
        text = ""
        if isinstance(claim, str):
            text = claim
        elif isinstance(claim, dict):
            text = str(claim.get("claim_text", ""))
        cleaned = _normalize_claim(text)
        if cleaned:
            normalized.add(cleaned)
    return normalized


def _normalize_claim(text: str) -> str:
    return " ".join(text.casefold().strip().split())


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


if __name__ == "__main__":
    raise SystemExit(main())
