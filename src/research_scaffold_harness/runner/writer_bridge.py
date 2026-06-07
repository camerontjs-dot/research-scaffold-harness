"""Glue between runner output, uniform extractor results, and the Phase 1 C-A writer.

Takes a :class:`RunnerResult`, a :class:`UniformExtractionResult`, and the
:class:`SourcePacket` that fed the runner, then produces a complete
``scaffold-run-{run_id}/`` directory by invoking
:func:`research_scaffold_harness.contracts.writer.write_scaffold_run`.

Stub-origin extractor identity (``extractor_id``, ``is_stub``, diagnostics) is
preserved verbatim in ``run_metadata.notes`` so downstream consumers can see
without inference that the official claims came from a stub extractor.

No new C-A schema fields are introduced. Model identity beyond the existing
``ScaffoldModelInfo`` triple (model_id, model_version, api_endpoint) lands in
``run_metadata.notes`` as a structured YAML-like block.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from research_scaffold_harness.contracts.hashing import (
    compute_corpus_hash,
    hash_file,
    hash_text,
)
from research_scaffold_harness.contracts.writer import (
    CAWriteInput,
    SidecarTextWriteInput,
    SourceWriteInput,
    write_scaffold_run,
)
from research_scaffold_harness.contracts.yaml_io import (
    model_to_yaml_dict,
    write_model_yaml,
    yaml_to_string,
)
from research_scaffold_harness.extractor import UniformExtractionResult
from research_scaffold_harness.extractor.surfaces import prepare_extraction_surfaces
from research_scaffold_harness.models.ca import (
    ClaimsRegistry,
    ScaffoldClaim,
    ScaffoldConfigInfo,
    ScaffoldCorpusInfo,
    ScaffoldModelInfo,
    ScaffoldRunManifest,
    ScaffoldRunMetadata,
    ScaffoldTaskInfo,
    SourceBibliographic,
    SourceMetadata,
    SourcePassages,
    SourceRetrieval,
)
from research_scaffold_harness.models.common import WRITER_SCHEMA_VERSION
from research_scaffold_harness.runner.core import RunnerResult
from research_scaffold_harness.runner.source_packet import SourcePacket


class WriterBridgeError(Exception):
    """Raised when the bridge cannot construct a valid C-A write input."""


@dataclass(frozen=True)
class BridgeWriteResult:
    """Bridge output: path to the produced scaffold-run directory plus run identity."""

    scaffold_run_dir: Path
    run_id: str
    extractor_id: str
    is_stub: bool


def mint_run_id(prefix: str = "rsh") -> str:
    """Mint a fresh run id using a short uuid4 suffix."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def now_utc() -> str:
    """Return a contract-shaped UTC timestamp."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_evidence_bundler_binary() -> Path | None:
    """Resolve the ``evidence-bundler`` CLI, preferring the same venv as ``sys.executable``.

    `pip install -e` places the entry point in ``<venv>/bin/`` but that
    directory may not be on shell ``PATH`` when invoking ``.venv/bin/python``
    directly (without ``source .venv/bin/activate``). Looking next to
    ``sys.executable`` keeps the resolver working regardless of activation
    state. Falls back to ``shutil.which`` so an externally-installed binary
    still resolves.
    """
    venv_bin = Path(sys.executable).parent / "evidence-bundler"
    if venv_bin.exists():
        return venv_bin
    which_path = shutil.which("evidence-bundler")
    return Path(which_path) if which_path else None


def write_scaffold_run_from_extraction(
    runner_result: RunnerResult,
    extraction: UniformExtractionResult,
    source_packet: SourcePacket,
    output_dir: Path,
    *,
    operator: str = "harness-runner",
    environment: str = "mlx-local",
    scaffold_version: str = "0.1.0",
    retrieval_strategy: str = "bounded-source-packet",
    extra_notes: str = "",
    extractor_sidecars: list[UniformExtractionResult] | None = None,
    exploratory_think_extraction: UniformExtractionResult | None = None,
) -> BridgeWriteResult:
    """Produce a complete C-A artifact directory from runner + stub extractor output.

    The caller is responsible for choosing the run_id (already stamped into
    ``extraction.claims.run_id``). The bridge propagates that id everywhere so
    claim ids, manifest, and the produced directory stay consistent.
    """
    run_id = extraction.claims.run_id
    if not run_id:
        raise WriterBridgeError(
            "extraction.claims.run_id is blank; mint a run id before extracting"
        )
    if runner_result.task_id != source_packet.task.task_id:
        raise WriterBridgeError(
            "runner_result.task_id does not match source_packet.task.task_id"
        )

    timestamp = now_utc()
    response = runner_result.response

    sources = _build_source_inputs(
        source_packet=source_packet,
        run_id=run_id,
        research_question=source_packet.task.research_question,
        timestamp=timestamp,
    )
    corpus_hash = _compute_corpus_hash_for_sources(sources)

    claims_registry = _rebuild_claims_with_extractor_notes(
        extraction=extraction,
        run_id=run_id,
        timestamp=timestamp,
    )

    notes = _build_run_metadata_notes(
        runner_result=runner_result,
        extraction=extraction,
        extra=extra_notes,
    )

    config_hash = _compute_config_hash(
        runner_result=runner_result,
        extraction=extraction,
    )

    manifest = ScaffoldRunManifest(
        run_id=run_id,
        task_id=runner_result.task_id,
        workflow_condition=runner_result.condition,
        timestamp_utc=timestamp,
        scaffold=ScaffoldConfigInfo(
            version=scaffold_version,
            prompt_template_id=runner_result.prompt_template_id,
            prompt_template_hash=runner_result.prompt_template_hash,
            config_hash=config_hash,
        ),
        model=ScaffoldModelInfo(
            model_id=response.model_id,
            model_version=_encode_model_version(response),
            api_endpoint=response.api_endpoint or "unknown",
            temperature=response.temperature,
            max_tokens=response.max_tokens if response.max_tokens > 0 else 1,
        ),
        task=ScaffoldTaskInfo(
            research_question=source_packet.task.research_question,
            domain=source_packet.task.domain,
            expert_checkable=source_packet.task.expert_checkable,
            ground_truth_ref=source_packet.task.ground_truth_ref,
        ),
        corpus=ScaffoldCorpusInfo(
            total_sources=len(sources),
            corpus_hash=corpus_hash,
            retrieval_strategy=retrieval_strategy,
            retrieval_timestamp_utc=timestamp,
        ),
        intermediates_present=False,
        run_metadata=ScaffoldRunMetadata(
            operator=operator,
            environment=environment,
            notes=notes,
        ),
    )

    write_input = CAWriteInput(
        manifest=manifest,
        claims=claims_registry,
        sources=sources,
        intermediates=None,
        sidecars=_build_sidecars(
            runner_result=runner_result,
            extraction=extraction,
            extractor_sidecars=extractor_sidecars or [],
            exploratory_think_extraction=exploratory_think_extraction,
            timestamp=timestamp,
        ),
    )

    scaffold_run_dir = write_scaffold_run(write_input, output_dir)
    return BridgeWriteResult(
        scaffold_run_dir=scaffold_run_dir,
        run_id=run_id,
        extractor_id=extraction.extractor_id,
        is_stub=extraction.is_stub,
    )


def _build_sidecars(
    *,
    runner_result: RunnerResult,
    extraction: UniformExtractionResult,
    extractor_sidecars: list[UniformExtractionResult],
    exploratory_think_extraction: UniformExtractionResult | None,
    timestamp: str,
) -> list[SidecarTextWriteInput]:
    sidecars = [
        SidecarTextWriteInput(
            relative_path="raw_output.txt",
            text=runner_result.response.text,
        ),
        SidecarTextWriteInput(
            relative_path="run_disposition.yaml",
            text=yaml_to_string(_build_run_disposition(
                runner_result=runner_result,
                extraction=extraction,
                timestamp=timestamp,
            )),
        ),
    ]
    for result in extractor_sidecars:
        sidecars.append(SidecarTextWriteInput(
            relative_path=f"intermediates/claims_extractor_{_extractor_slug(result)}.yaml",
            text=yaml_to_string(_extractor_result_to_sidecar(result)),
        ))
    if exploratory_think_extraction is not None:
        sidecars.append(SidecarTextWriteInput(
            relative_path="exploratory/think_block_claims.yaml",
            text=yaml_to_string(_exploratory_result_to_sidecar(exploratory_think_extraction)),
        ))
    return sidecars


def _build_run_disposition(
    *,
    runner_result: RunnerResult,
    extraction: UniformExtractionResult,
    timestamp: str,
) -> dict:
    return build_run_disposition_fields(
        raw_output=runner_result.response.text,
        run_id=extraction.claims.run_id,
        task_id=runner_result.task_id,
        workflow_condition=runner_result.condition,
        generated_at_utc=timestamp,
        extractor_id=extraction.extractor_id,
        extractor_is_stub=extraction.is_stub,
        extracted_claim_count=len(extraction.claims.claims),
        extractor_diagnostics=list(extraction.diagnostics),
    )


def build_run_disposition_fields(
    *,
    raw_output: str,
    run_id: str,
    task_id: str,
    workflow_condition: str,
    generated_at_utc: str,
    extractor_id: str,
    extractor_is_stub: bool,
    extracted_claim_count: int,
    extractor_diagnostics: list[str],
) -> dict:
    """Compute a run-disposition mapping from pure inputs.

    Factored out of :func:`_build_run_disposition` so the post-calibration
    re-pointing tool (``promote_official_extractor.py``) can recompute a cell's
    disposition over the frozen ``raw_output.txt`` using the *exact* routing the
    writer bridge applies — no second copy of the gate logic. Surfaces are
    recomputed from ``raw_output`` so the official-answer-body and think-block
    flags stay extractor-independent.
    """
    surfaces = prepare_extraction_surfaces(raw_output)
    if not raw_output:
        disposition = "missing_raw_output"
        human_review_required = False
        metric_handling = "exclude_from_confirmatory_analysis"
    elif extracted_claim_count > 0:
        disposition = "ready_for_audit"
        human_review_required = False
        metric_handling = "include_in_support_metrics"
    elif not surfaces.official_answer_text:
        disposition = "missing_final_answer"
        human_review_required = False
        metric_handling = "exclude_from_support_rate_denominator"
    else:
        disposition = "requires_human_zero_claim_scan"
        human_review_required = True
        metric_handling = "exclude_until_human_zero_claim_scan"

    return {
        "schema_version": "run-disposition-v1",
        "run_id": run_id,
        "task_id": task_id,
        "workflow_condition": workflow_condition,
        "generated_at_utc": generated_at_utc,
        "disposition": disposition,
        "human_review_required": human_review_required,
        "metric_handling": metric_handling,
        "allowed_after_human_review": [
            "ready_for_audit",
            "extractor_failure_claims_present",
            "valid_zero_claim_answer",
            "missing_final_answer",
        ] if human_review_required else [],
        "raw_output_present": bool(raw_output),
        "official_answer_body_present": bool(surfaces.official_answer_text),
        "think_block_present": bool(surfaces.think_block_text),
        "extractor_id": extractor_id,
        "extractor_is_stub": extractor_is_stub,
        "extracted_claim_count": extracted_claim_count,
        "extractor_diagnostics": list(extractor_diagnostics),
        "surface_diagnostics": list(surfaces.diagnostics),
        "zero_claim_queue_rule": {
            "max_pending_cells_before_stop": 4,
            "action_if_exceeded": "produce_adjudication_packet_before_re_reporting",
        },
    }


def _extractor_result_to_sidecar(extraction: UniformExtractionResult) -> dict:
    return {
        "schema_version": "extractor-output-sidecar-v1",
        "extractor_id": extraction.extractor_id,
        "extractor_version": extraction.extractor_version,
        "extractor_is_stub": extraction.is_stub,
        "diagnostics": list(extraction.diagnostics),
        "claim_count": len(extraction.claims.claims),
        "claims": model_to_yaml_dict(extraction.claims),
    }


def _exploratory_result_to_sidecar(extraction: UniformExtractionResult) -> dict:
    data = _extractor_result_to_sidecar(extraction)
    data["extraction_source"] = "think_block"
    data["exploratory"] = True
    return data


def _extractor_slug(extraction: UniformExtractionResult) -> str:
    extractor_id = extraction.extractor_id.lower()
    if "nemo" in extractor_id:
        return "nemo"
    if "small" in extractor_id:
        return "small3"
    if "stub" in extractor_id:
        return "stub"
    return "".join(char if char.isalnum() else "_" for char in extractor_id).strip("_")


OFFICIAL_EXTRACTOR_CHOICES: tuple[str, ...] = ("stub", "nemo", "small3")


def resolve_official_extractor(extractor_set: str, requested: str | None) -> str:
    """Resolve the effective official-extractor slug.

    ``extractor_set`` is the ``--extractor`` value (``stub``/``nemo``/``small3``/
    ``all``); ``requested`` is an explicit ``--official-extractor`` or ``None``
    for the default. Post-calibration the default is **nemo** whenever the full
    set runs (the calibrated production path); for a single-extractor run the
    one extractor that ran is official, so the offline stub path keeps working
    without flags. Calibration of record: Nemo F1 0.8916 (strong tier).
    """
    if requested is not None:
        return requested
    return "nemo" if extractor_set == "all" else extractor_set


def select_official_extraction(
    extractions: list[UniformExtractionResult],
    official_extractor: str,
) -> UniformExtractionResult:
    """Return the run extraction designated official by ``official_extractor``.

    Selection uses the same slug mapping as the sidecar filenames so the
    official claims and their sidecar carry a consistent identity. Raises
    :class:`WriterBridgeError` when the requested extractor did not run (e.g.
    asking for nemo official when only the stub ran) — replacing the old
    pre-calibration hard block with a deliberate, explicit selection error.
    """
    matches = [
        extraction for extraction in extractions
        if _extractor_slug(extraction) == official_extractor
    ]
    if not matches:
        ran = ", ".join(sorted({_extractor_slug(e) for e in extractions})) or "(none)"
        raise WriterBridgeError(
            f"official extractor {official_extractor!r} did not run; ran: [{ran}]. "
            "Add it to --extractor or use --extractor=all."
        )
    return matches[0]


def _build_source_inputs(
    *,
    source_packet: SourcePacket,
    run_id: str,
    research_question: str,
    timestamp: str,
) -> list[SourceWriteInput]:
    inputs: list[SourceWriteInput] = []
    for rank, packet_source in enumerate(source_packet.sources, start=1):
        content_hash = hash_file(packet_source.content_path)
        bibliographic = SourceBibliographic(
            source_type=packet_source.metadata.source_type,
            title=packet_source.metadata.title,
            authors=list(packet_source.metadata.authors),
            publication_date=packet_source.metadata.publication_date,
            url=packet_source.metadata.url,
            access_date_utc=timestamp,
        )
        metadata = SourceMetadata(
            source_id=packet_source.source_id,
            schema_version=WRITER_SCHEMA_VERSION,
            bibliographic=bibliographic,
            trust_level=packet_source.metadata.trust_level,
            content_hash=content_hash,
            retrieval=SourceRetrieval(
                retrieved_for=[run_id],
                retrieval_query=research_question,
                retrieval_rank=rank,
            ),
        )
        passages = SourcePassages(
            source_id=packet_source.source_id,
            schema_version=WRITER_SCHEMA_VERSION,
            passages=[],
        )
        inputs.append(SourceWriteInput(
            source_id=packet_source.source_id,
            content_path=packet_source.content_path,
            metadata=metadata,
            passages=passages,
        ))
    return inputs


def _compute_corpus_hash_for_sources(sources: list[SourceWriteInput]) -> str:
    """Pre-compute the corpus_hash by mirroring the writer's on-disk layout.

    The Phase 1 writer copies each ``content_path`` into
    ``corpus/{source_id}/content{ext}`` and writes metadata.yaml plus
    passages.yaml beside it, then hashes the whole tree. We mirror that
    layout in a temp dir so the manifest carries the correct hash before
    the writer verifies it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        corpus_dir = Path(tmp) / "corpus"
        corpus_dir.mkdir()
        for source in sources:
            source_dir = corpus_dir / source.source_id
            source_dir.mkdir()
            dest = source_dir / f"content{source.content_path.suffix}"
            shutil.copy2(source.content_path, dest)
            write_model_yaml(source.metadata, source_dir / "metadata.yaml", exclude_none=True)
            write_model_yaml(source.passages, source_dir / "passages.yaml", exclude_none=True)
        return compute_corpus_hash(corpus_dir)


def _rebuild_claims_with_extractor_notes(
    *,
    extraction: UniformExtractionResult,
    run_id: str,
    timestamp: str,
) -> ClaimsRegistry:
    """Return a ClaimsRegistry with consistent run_id and generated_at_utc.

    The extractor already records ``extractor_id`` and ``is_stub`` in each
    claim's ``scaffold_notes``. We rebuild the registry to stamp the bridge's
    timestamp so the manifest and claims agree.
    """
    claims = [
        ScaffoldClaim(
            claim_id=claim.claim_id,
            claim_type=claim.claim_type,
            claim_text=claim.claim_text,
            support_status=claim.support_status,
            claim_strength=claim.claim_strength,
            extraction_fidelity=claim.extraction_fidelity,
            source_refs=list(claim.source_refs),
            counterevidence_checked=claim.counterevidence_checked,
            counterevidence_found=claim.counterevidence_found,
            downgraded=claim.downgraded,
            downgrade_reason=claim.downgrade_reason,
            scaffold_notes=claim.scaffold_notes,
        )
        for claim in extraction.claims.claims
    ]
    return ClaimsRegistry(
        schema_version=WRITER_SCHEMA_VERSION,
        run_id=run_id,
        generated_at_utc=timestamp,
        claims=claims,
    )


def _build_run_metadata_notes(
    *,
    runner_result: RunnerResult,
    extraction: UniformExtractionResult,
    extra: str,
) -> str:
    """Return a YAML-like block carrying audit-trail fields not in the schema.

    Captures extractor identity, runtime model identity beyond the
    ``ScaffoldModelInfo`` triple, and final-answer length so consumers can
    cheaply see stub-origin status.
    """
    response = runner_result.response
    lines = [
        f"extractor_id: {extraction.extractor_id}",
        f"extractor_version: {extraction.extractor_version}",
        f"extractor_is_stub: {str(extraction.is_stub).lower()}",
        f"extractor_diagnostics: {list(extraction.diagnostics)}",
        f"mlx_lm_version: {response.model_version}",
        f"model_revision: {response.model_revision}",
        f"quantization: {response.quantization}",
        f"chat_template_applied: {str(response.chat_template_applied).lower()}",
        f"final_claims_char_len: {len(extraction.final_claims_text)}",
        f"raw_output_char_len: {len(response.text)}",
        f"finish_reason: {response.finish_reason}",
        f"output_tokens: {response.output_tokens}",
    ]
    if extra:
        lines.append(f"extra: {extra}")
    return "\n".join(lines)


def _compute_config_hash(
    *,
    runner_result: RunnerResult,
    extraction: UniformExtractionResult,
) -> str:
    response = runner_result.response
    components = "\n".join([
        f"model_id={response.model_id}",
        f"model_revision={response.model_revision}",
        f"quantization={response.quantization}",
        f"mlx_lm_version={response.model_version}",
        f"prompt_template_hash={runner_result.prompt_template_hash}",
        f"rendered_prompt_hash={runner_result.rendered_prompt_hash}",
        f"extractor_id={extraction.extractor_id}",
        f"extractor_is_stub={str(extraction.is_stub).lower()}",
    ])
    return hash_text(components)


def _encode_model_version(response) -> str:
    """Encode runtime model identity into the existing model_version field.

    Format: ``mlx-lm/<version> rev:<short-sha> quant:<quantization>``.
    Stays within the existing :class:`ScaffoldModelInfo` schema so no new
    field is added to C-A. Blank pieces are omitted but the leading
    ``mlx-lm/<version>`` segment is required so the field stays non-blank
    even for stub-adapter callers (the stub's model_version is its own
    adapter version, which still satisfies the non-blank constraint).
    """
    parts: list[str] = []
    base = response.model_version or "unknown"
    parts.append(base)
    revision = response.model_revision
    if revision:
        parts.append(f"rev:{revision[:12]}")
    if response.quantization:
        parts.append(f"quant:{response.quantization}")
    return " ".join(parts)
