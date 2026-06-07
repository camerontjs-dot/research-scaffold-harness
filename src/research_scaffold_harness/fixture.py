"""Synthetic fixture builder for C-A scaffold-run artifacts.

Loads a source packet from disk and generates hardcoded per-condition claims
(no LLM). Used by the CLI and tests to produce valid artifacts without any
external dependencies.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import get_args

from research_scaffold_harness.contracts.hashing import (
    compute_corpus_hash,
    hash_file,
    hash_text,
)
from research_scaffold_harness.contracts.writer import (
    CAWriteInput,
    IntermediatesWriteInput,
    SourceWriteInput,
)
from research_scaffold_harness.contracts.yaml_io import load_model_yaml
from research_scaffold_harness.models.ca import (
    ClaimsRegistry,
    ScaffoldClaim,
    ScaffoldConfigInfo,
    ScaffoldCorpusInfo,
    ScaffoldModelInfo,
    ScaffoldPassage,
    ScaffoldRunManifest,
    ScaffoldRunMetadata,
    ScaffoldTaskInfo,
    SourceBibliographic,
    SourceMetadata,
    SourcePassages,
    SourceRef,
    SourceRetrieval,
)
from research_scaffold_harness.models.common import (
    WRITER_SCHEMA_VERSION,
    WorkflowCondition,
)
from research_scaffold_harness.models.task import TaskSourceMeta, TaskSpec
from research_scaffold_harness.prompts import hash_template, load_template


class FixtureError(Exception):
    """Raised when a fixture source packet is invalid or cannot be loaded."""


@dataclass(frozen=True)
class FixtureSource:
    """Validated source-packet source input."""

    source_id: str
    content_path: Path
    metadata: TaskSourceMeta


def _now_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_run_id() -> str:
    return f"fixture-{uuid.uuid4().hex[:12]}"


def _load_source_packet(task_dir: Path) -> tuple[TaskSpec, list[FixtureSource]]:
    """Load task.yaml and discover sources under sources/."""
    task_path = task_dir / "task.yaml"
    if not task_path.exists():
        raise FixtureError(f"task.yaml not found in {task_dir}")
    try:
        task = load_model_yaml(TaskSpec, task_path)
    except Exception as exc:
        raise FixtureError(f"Invalid task.yaml in {task_dir}: {exc}") from exc

    sources_dir = task_dir / "sources"
    if not sources_dir.is_dir():
        raise FixtureError(f"sources/ directory not found in {task_dir}")

    sources: list[FixtureSource] = []
    for source_dir in sorted(sources_dir.iterdir()):
        if not source_dir.is_dir():
            continue
        content_path = source_dir / "content.md"
        meta_path = source_dir / "metadata.yaml"
        if not content_path.exists():
            raise FixtureError(f"content.md missing in {source_dir}")
        if not meta_path.exists():
            raise FixtureError(f"metadata.yaml missing in {source_dir}")
        try:
            meta = load_model_yaml(TaskSourceMeta, meta_path)
        except Exception as exc:
            raise FixtureError(f"Invalid metadata.yaml in {source_dir}: {exc}") from exc
        sources.append(FixtureSource(
            source_id=source_dir.name,
            content_path=content_path,
            metadata=meta,
        ))

    if not sources:
        raise FixtureError(f"No source directories found under {sources_dir}")
    return task, sources


def _build_passages(source_id: str, content_path: Path) -> list[ScaffoldPassage]:
    """Extract three fixed passages from the source content."""
    text = content_path.read_text(encoding="utf-8")
    paragraphs = [
        p.strip() for p in text.split("\n\n")
        if p.strip() and not p.strip().startswith("#")
    ]

    passages: list[ScaffoldPassage] = []
    for i, para in enumerate(paragraphs[:3]):
        offset = text.index(para)
        preview = para[:80] + ("..." if len(para) > 80 else "")
        passages.append(ScaffoldPassage(
            passage_id=f"{source_id}-p{i + 1:03d}",
            section=None,
            paragraph_index=i,
            char_start=offset,
            char_end=offset + len(para),
            text_preview=preview,
            used_for_claims=[],
            extraction_method="scaffold_cited",
        ))
    return passages


def _baseline_claims(run_id: str) -> list[ScaffoldClaim]:
    return [
        ScaffoldClaim(
            claim_id=f"{run_id}-c001",
            claim_type="extracted_claim",
            claim_text="A pharmaceutical quality system integrates CGMP with risk management.",
            support_status="uncertain",
            claim_strength=0.5,
            extraction_fidelity=0.5,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c002",
            claim_type="extracted_claim",
            claim_text="Senior management establishes quality policy and allocates resources.",
            support_status="uncertain",
            claim_strength=0.5,
            extraction_fidelity=0.5,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c003",
            claim_type="extracted_claim",
            claim_text="Analytical methods undergo validation for specificity and accuracy.",
            support_status="uncertain",
            claim_strength=0.5,
            extraction_fidelity=0.5,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
    ]


def _format_only_claims(run_id: str) -> list[ScaffoldClaim]:
    return [
        ScaffoldClaim(
            claim_id=f"{run_id}-c001",
            claim_type="extracted_claim",
            claim_text="A pharmaceutical quality system integrates CGMP with risk management.",
            support_status="sourced",
            claim_strength=0.8,
            extraction_fidelity=0.7,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c002",
            claim_type="extracted_claim",
            claim_text="Senior management establishes quality policy and allocates resources.",
            support_status="inferred",
            claim_strength=0.6,
            extraction_fidelity=0.6,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c003",
            claim_type="extracted_claim",
            claim_text="Analytical methods undergo validation for specificity and accuracy.",
            support_status="uncertain",
            claim_strength=0.4,
            extraction_fidelity=0.5,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
        ),
    ]


def _provenance_claims(
    run_id: str, source_id: str, passages: list[ScaffoldPassage],
) -> list[ScaffoldClaim]:
    refs = [
        [SourceRef(source_id=source_id, passage_id=passages[0].passage_id)],
        [SourceRef(source_id=source_id, passage_id=passages[1].passage_id)],
        [SourceRef(source_id=source_id, passage_id=passages[2].passage_id)],
    ]
    return [
        ScaffoldClaim(
            claim_id=f"{run_id}-c001",
            claim_type="extracted_claim",
            claim_text="A pharmaceutical quality system integrates CGMP with risk management.",
            support_status="sourced",
            claim_strength=0.9,
            extraction_fidelity=0.85,
            source_refs=refs[0],
            counterevidence_checked=True,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c002",
            claim_type="extracted_claim",
            claim_text="Senior management establishes quality policy and allocates resources.",
            support_status="sourced",
            claim_strength=0.85,
            extraction_fidelity=0.8,
            source_refs=refs[1],
            counterevidence_checked=True,
            counterevidence_found=False,
            downgraded=False,
        ),
        ScaffoldClaim(
            claim_id=f"{run_id}-c003",
            claim_type="extracted_claim",
            claim_text="Analytical methods undergo validation for specificity and accuracy.",
            support_status="sourced",
            claim_strength=0.85,
            extraction_fidelity=0.8,
            source_refs=refs[2],
            counterevidence_checked=True,
            counterevidence_found=False,
            downgraded=False,
        ),
    ]


def _full_scaffold_claims(
    run_id: str, source_id: str, passages: list[ScaffoldPassage],
) -> list[ScaffoldClaim]:
    return _provenance_claims(run_id, source_id, passages)


def build_fixture_write_input(
    task_dir: Path, condition: WorkflowCondition,
) -> CAWriteInput:
    """Build a complete CAWriteInput from a fixture source packet.

    Generates hardcoded per-condition claims (no LLM). The returned object is
    ready to pass to ``write_scaffold_run``.
    """
    valid_conditions = get_args(WorkflowCondition)
    if condition not in valid_conditions:
        raise FixtureError(
            f"Invalid condition {condition!r}; expected one of {valid_conditions}"
        )

    task, raw_sources = _load_source_packet(task_dir)
    prompt_template = load_template(condition)
    run_id = _make_run_id()
    now = _now_utc()

    source_inputs: list[SourceWriteInput] = []
    all_passages: list[ScaffoldPassage] = []
    first_source_id = raw_sources[0].source_id

    for src in raw_sources:
        content_path = src.content_path
        source_id = src.source_id
        raw_meta = src.metadata
        content_hash = hash_file(content_path)
        passages = _build_passages(source_id, content_path)
        all_passages.extend(passages)

        metadata = SourceMetadata(
            source_id=source_id,
            schema_version=WRITER_SCHEMA_VERSION,
            bibliographic=SourceBibliographic(
                source_type=raw_meta.source_type,
                title=raw_meta.title,
                authors=raw_meta.authors,
                publication_date=raw_meta.publication_date,
                url=raw_meta.url,
                access_date_utc=now,
            ),
            trust_level=raw_meta.trust_level,
            content_hash=content_hash,
            retrieval=SourceRetrieval(
                retrieved_for=[f"{run_id}-c001"],
                retrieval_query=task.research_question,
                retrieval_rank=1,
            ),
        )

        source_passages = SourcePassages(
            source_id=source_id,
            schema_version=WRITER_SCHEMA_VERSION,
            passages=passages,
        )

        source_inputs.append(SourceWriteInput(
            source_id=source_id,
            content_path=content_path,
            metadata=metadata,
            passages=source_passages,
        ))

    first_passages = [p for p in all_passages if p.passage_id.startswith(first_source_id)]
    if condition == "baseline":
        claims = _baseline_claims(run_id)
    elif condition == "format_only":
        claims = _format_only_claims(run_id)
    elif condition == "provenance_scaffold":
        claims = _provenance_claims(run_id, first_source_id, first_passages)
    else:
        claims = _full_scaffold_claims(run_id, first_source_id, first_passages)

    for src_input in source_inputs:
        for passage in src_input.passages.passages:
            passage.used_for_claims = [
                c.claim_id for c in claims
                if any(
                    r.source_id == src_input.source_id and r.passage_id == passage.passage_id
                    for r in c.source_refs
                )
            ]

    intermediates = None
    if condition == "full_scaffold":
        intermediates = IntermediatesWriteInput(
            disconfirmation_pass={
                "run_id": run_id,
                "checked_claims": [c.claim_id for c in claims],
                "counterevidence_found": False,
                "notes": "Fixture disconfirmation pass — no counterevidence by construction.",
            },
            claim_table_draft={
                "run_id": run_id,
                "claims": [
                    {"claim_id": c.claim_id, "claim_text": c.claim_text, "status": c.support_status}
                    for c in claims
                ],
                "notes": "Fixture claim table draft.",
            },
        )

    corpus_hash = _compute_fixture_corpus_hash(source_inputs)

    manifest = ScaffoldRunManifest(
        run_id=run_id,
        task_id=task.task_id,
        workflow_condition=condition,
        timestamp_utc=now,
        scaffold=ScaffoldConfigInfo(
            version="0.1.0",
            prompt_template_id=prompt_template.template_id,
            prompt_template_hash=hash_template(prompt_template),
            config_hash=hash_text("fixture-no-config"),
        ),
        model=ScaffoldModelInfo(
            model_id="fixture-hardcoded",
            model_version="0.0.0",
            api_endpoint="none",
            temperature=0.0,
            max_tokens=1,
        ),
        task=ScaffoldTaskInfo(
            research_question=task.research_question,
            domain=task.domain,
            expert_checkable=task.expert_checkable,
            ground_truth_ref=task.ground_truth_ref,
        ),
        corpus=ScaffoldCorpusInfo(
            total_sources=len(source_inputs),
            corpus_hash=corpus_hash,
            retrieval_strategy="fixture-static",
            retrieval_timestamp_utc=now,
        ),
        intermediates_present=intermediates is not None,
        run_metadata=ScaffoldRunMetadata(
            operator="fixture-builder",
            environment="test",
        ),
    )

    claims_registry = ClaimsRegistry(
        schema_version=WRITER_SCHEMA_VERSION,
        run_id=run_id,
        generated_at_utc=now,
        claims=claims,
    )

    return CAWriteInput(
        manifest=manifest,
        claims=claims_registry,
        sources=source_inputs,
        intermediates=intermediates,
    )


def _compute_fixture_corpus_hash(sources: list[SourceWriteInput]) -> str:
    """Pre-compute corpus hash by simulating the on-disk layout.

    The writer copies content files into corpus/{source_id}/content{ext} and
    writes metadata.yaml + passages.yaml beside them, then hashes the tree.
    We replicate that layout in a temp dir to get the same hash.
    """
    import shutil
    import tempfile

    from research_scaffold_harness.contracts.yaml_io import write_model_yaml

    with tempfile.TemporaryDirectory() as tmp:
        corpus_dir = Path(tmp) / "corpus"
        corpus_dir.mkdir()
        for src in sources:
            src_dir = corpus_dir / src.source_id
            src_dir.mkdir()
            dest = src_dir / f"content{src.content_path.suffix}"
            shutil.copy2(src.content_path, dest)
            write_model_yaml(src.metadata, src_dir / "metadata.yaml", exclude_none=True)
            write_model_yaml(src.passages, src_dir / "passages.yaml", exclude_none=True)
        return compute_corpus_hash(corpus_dir)
