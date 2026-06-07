"""Uniform extraction orchestration for raw runner output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from research_scaffold_harness.extractor.adapters import (
    ExtractorAdapter,
    ExtractorRequest,
)
from research_scaffold_harness.models.ca import ClaimsRegistry, ScaffoldClaim
from research_scaffold_harness.models.common import WRITER_SCHEMA_VERSION
from research_scaffold_harness.runner import RunnerResult


@dataclass(frozen=True)
class UniformExtractionResult:
    """Claim registry plus extractor identity and diagnostics."""

    extractor_id: str
    extractor_version: str
    is_stub: bool
    diagnostics: tuple[str, ...]
    final_claims_text: str
    claims: ClaimsRegistry


def extract_claims_from_runner_result(
    result: RunnerResult,
    run_id: str,
    adapter: ExtractorAdapter,
    *,
    generated_at_utc: str | None = None,
) -> UniformExtractionResult:
    """Extract official claim candidates from a raw runner result.

    The adapter is required so callers must choose between deterministic test
    plumbing and future live extractor implementations deliberately.
    """
    response = adapter.extract(ExtractorRequest(
        run_id=run_id,
        task_id=result.task_id,
        condition=result.condition,
        raw_output=result.output_text,
    ))
    return _result_from_response(
        response=response,
        run_id=run_id,
        adapter=adapter,
        generated_at_utc=generated_at_utc,
    )


def extract_think_claims_from_runner_result(
    result: RunnerResult,
    run_id: str,
    adapter: ExtractorAdapter,
    *,
    generated_at_utc: str | None = None,
) -> UniformExtractionResult:
    """Extract exploratory claim candidates from a live extractor's think-block path."""
    extract_think_block = getattr(adapter, "extract_think_block", None)
    if extract_think_block is None:
        raise TypeError(f"Extractor {adapter.extractor_id!r} has no think-block path")
    response = extract_think_block(ExtractorRequest(
        run_id=run_id,
        task_id=result.task_id,
        condition=result.condition,
        raw_output=result.output_text,
    ))
    return _result_from_response(
        response=response,
        run_id=run_id,
        adapter=adapter,
        generated_at_utc=generated_at_utc,
    )


def _result_from_response(
    *,
    response,
    run_id: str,
    adapter: ExtractorAdapter,
    generated_at_utc: str | None,
) -> UniformExtractionResult:
    """Build the typed extraction result from an adapter response."""

    claims = ClaimsRegistry(
        schema_version=WRITER_SCHEMA_VERSION,
        run_id=run_id,
        generated_at_utc=generated_at_utc or _now_utc(),
        claims=[
            ScaffoldClaim(
                claim_id=f"{run_id}-c{index:03d}",
                claim_type="extracted_claim",
                claim_text=claim_text,
                support_status="uncertain",
                claim_strength=0.5,
                extraction_fidelity=0.5,
                source_refs=[],
                counterevidence_checked=False,
                counterevidence_found=False,
                downgraded=False,
                scaffold_notes=(
                    f"extractor_id={adapter.extractor_id}; "
                    f"stub={str(adapter.is_stub).lower()}"
                ),
            )
            for index, claim_text in enumerate(response.claim_texts, start=1)
        ],
    )

    return UniformExtractionResult(
        extractor_id=adapter.extractor_id,
        extractor_version=adapter.extractor_version,
        is_stub=adapter.is_stub,
        diagnostics=response.diagnostics,
        final_claims_text=response.final_claims_text,
        claims=claims,
    )


def _now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
