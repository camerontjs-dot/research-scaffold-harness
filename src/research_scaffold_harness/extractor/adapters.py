"""Uniform claim-extractor interfaces and deterministic offline adapter."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from research_scaffold_harness.models.common import WorkflowCondition


@dataclass(frozen=True)
class ExtractorRequest:
    """Raw model output plus run identity passed to a claim extractor."""

    run_id: str
    task_id: str
    condition: WorkflowCondition
    raw_output: str


@dataclass(frozen=True)
class ExtractorResponse:
    """Extractor-normalized claim text before C-A model conversion."""

    claim_texts: tuple[str, ...]
    diagnostics: tuple[str, ...] = ()
    final_claims_text: str = ""


class ExtractorAdapter(Protocol):
    """Minimal interface shared by offline stubs and future live extractors."""

    @property
    def extractor_id(self) -> str:
        """Stable extractor identifier."""

    @property
    def extractor_version(self) -> str:
        """Extractor implementation version."""

    @property
    def is_stub(self) -> bool:
        """Whether this extractor is deterministic non-assessment plumbing."""

    def extract(self, request: ExtractorRequest) -> ExtractorResponse:
        """Extract normalized claim text from a raw model output."""


class StubUniformExtractor:
    """Deterministic offline extractor for Unit 3 plumbing tests.

    This is not an evidence assessment. It only proves that all workflow
    conditions can flow through the same post-run extraction boundary.
    """

    extractor_id = "stub-offline-deterministic"
    extractor_version = "0.1.0"
    is_stub = True

    def extract(self, request: ExtractorRequest) -> ExtractorResponse:
        """Extract claim-like lines from the final-claims segment only."""
        final_claims = _last_final_claims_segment(request.raw_output)
        if final_claims is None:
            return ExtractorResponse(
                claim_texts=(),
                diagnostics=("final-claims marker not found",),
            )

        claims = _dedupe_preserving_order(_claim_like_segments(final_claims))
        diagnostics = ()
        if not claims:
            diagnostics = ("final-claims segment contained no extractable claims",)

        return ExtractorResponse(
            claim_texts=tuple(claims),
            diagnostics=diagnostics,
            final_claims_text=final_claims,
        )


def _last_final_claims_segment(raw_output: str) -> str | None:
    markers = list(re.finditer(r"(?im)^final claims:\s*$", raw_output))
    if not markers:
        return None
    segments = [raw_output[marker.end():].strip() for marker in markers]
    for segment in reversed(segments):
        if _claim_like_segments(segment):
            return segment
    return segments[-1]


def _claim_like_segments(text: str) -> list[str]:
    claims: list[str] = []
    for line in text.splitlines():
        normalized = _normalize_candidate(line)
        if not normalized:
            continue
        claims.extend(_split_sentences(normalized))
    return [claim for claim in claims if claim]


def _normalize_candidate(line: str) -> str:
    normalized = " ".join(line.strip().split())
    if not normalized:
        return ""
    normalized = re.sub(r"^[-*]\s+", "", normalized).strip()
    if not normalized:
        return ""
    if normalized.startswith("|") and normalized.endswith("|"):
        return ""
    return normalized


def _split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text)
    return [piece.strip() for piece in pieces if _is_substantive(piece)]


def _is_substantive(text: str) -> bool:
    words = re.findall(r"[A-Za-z0-9]+", text)
    return len(words) >= 4


def _dedupe_preserving_order(claims: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for claim in claims:
        key = claim.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(claim)
    return deduped
