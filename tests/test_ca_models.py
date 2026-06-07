"""C-A artifact model tests — Phase 1 Unit 4."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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

# ---------------------------------------------------------------------------
# Fixtures — minimal valid payloads for each model
# ---------------------------------------------------------------------------

_HASH = "sha256:" + "a" * 64


def _scaffold_config() -> dict:
    return {
        "version": "0.1.0",
        "prompt_template_id": "tpl-001",
        "prompt_template_hash": _HASH,
        "config_hash": _HASH,
    }


def _scaffold_model() -> dict:
    return {
        "model_id": "claude-sonnet-4-6",
        "model_version": "20250514",
        "api_endpoint": "https://api.anthropic.com/v1",
        "temperature": 0.0,
        "max_tokens": 4096,
    }


def _scaffold_task() -> dict:
    return {
        "research_question": "Does X cause Y?",
        "domain": "pharmacology",
        "expert_checkable": True,
    }


def _scaffold_corpus() -> dict:
    return {
        "total_sources": 3,
        "corpus_hash": _HASH,
        "retrieval_strategy": "semantic_search",
        "retrieval_timestamp_utc": "2026-05-17T00:00:00Z",
    }


def _run_metadata() -> dict:
    return {"operator": "harness-ci", "environment": "test"}


def _run_manifest() -> dict:
    return {
        "run_id": "run-001",
        "task_id": "task-001",
        "workflow_condition": "full_scaffold",
        "timestamp_utc": "2026-05-17T00:00:00Z",
        "scaffold": _scaffold_config(),
        "model": _scaffold_model(),
        "task": _scaffold_task(),
        "corpus": _scaffold_corpus(),
        "intermediates_present": False,
        "run_metadata": _run_metadata(),
    }


def _source_ref() -> dict:
    return {"source_id": "src-001", "passage_id": "p-001"}


def _scaffold_claim() -> dict:
    return {
        "claim_id": "c-001",
        "claim_type": "extracted_claim",
        "claim_text": "X causes Y",
        "support_status": "sourced",
        "claim_strength": 0.85,
        "extraction_fidelity": 0.9,
        "source_refs": [_source_ref()],
        "counterevidence_checked": True,
        "counterevidence_found": False,
        "downgraded": False,
    }


def _claims_registry(version: str = "1.0.0") -> dict:
    return {
        "schema_version": version,
        "run_id": "run-001",
        "generated_at_utc": "2026-05-17T00:00:00Z",
        "claims": [_scaffold_claim()],
    }


def _source_bibliographic() -> dict:
    return {
        "source_type": "journal_article",
        "title": "A Study",
        "url": "https://example.com/study",
        "access_date_utc": "2026-05-17T00:00:00Z",
    }


def _source_retrieval() -> dict:
    return {
        "retrieval_query": "X causes Y",
        "retrieval_rank": 1,
    }


def _source_metadata(version: str = "1.0.0") -> dict:
    return {
        "source_id": "src-001",
        "schema_version": version,
        "bibliographic": _source_bibliographic(),
        "trust_level": "primary",
        "content_hash": _HASH,
        "retrieval": _source_retrieval(),
    }


def _scaffold_passage() -> dict:
    return {
        "passage_id": "p-001",
        "paragraph_index": 0,
        "char_start": 0,
        "char_end": 50,
        "text_preview": "X causes Y in rats.",
        "extraction_method": "scaffold_cited",
    }


def _source_passages(version: str = "1.0.0") -> dict:
    return {
        "source_id": "src-001",
        "schema_version": version,
        "passages": [_scaffold_passage()],
    }


# ---------------------------------------------------------------------------
# Happy-path round-trip per model
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_cls,payload_fn",
    [
        (ScaffoldConfigInfo, _scaffold_config),
        (ScaffoldModelInfo, _scaffold_model),
        (ScaffoldTaskInfo, _scaffold_task),
        (ScaffoldCorpusInfo, _scaffold_corpus),
        (ScaffoldRunMetadata, _run_metadata),
        (ScaffoldRunManifest, _run_manifest),
        (SourceRef, _source_ref),
        (ScaffoldClaim, _scaffold_claim),
        (ClaimsRegistry, _claims_registry),
        (SourceBibliographic, _source_bibliographic),
        (SourceRetrieval, _source_retrieval),
        (SourceMetadata, _source_metadata),
        (ScaffoldPassage, _scaffold_passage),
        (SourcePassages, _source_passages),
    ],
    ids=lambda x: x.__name__ if isinstance(x, type) else x.__name__,
)
def test_round_trip(model_cls, payload_fn) -> None:
    payload = payload_fn()
    instance = model_cls.model_validate(payload)
    dumped = instance.model_dump(mode="json")
    reconstructed = model_cls.model_validate(dumped)
    assert reconstructed == instance


# ---------------------------------------------------------------------------
# Reject extras (StrictBaseModel enforcement)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_cls,payload_fn",
    [
        (ScaffoldConfigInfo, _scaffold_config),
        (ScaffoldModelInfo, _scaffold_model),
        (ScaffoldTaskInfo, _scaffold_task),
        (ScaffoldCorpusInfo, _scaffold_corpus),
        (ScaffoldRunMetadata, _run_metadata),
        (ScaffoldRunManifest, _run_manifest),
        (SourceRef, _source_ref),
        (ScaffoldClaim, _scaffold_claim),
        (ClaimsRegistry, _claims_registry),
        (SourceBibliographic, _source_bibliographic),
        (SourceRetrieval, _source_retrieval),
        (SourceMetadata, _source_metadata),
        (ScaffoldPassage, _scaffold_passage),
        (SourcePassages, _source_passages),
    ],
    ids=lambda x: x.__name__ if isinstance(x, type) else x.__name__,
)
def test_rejects_extra_fields(model_cls, payload_fn) -> None:
    payload = {**payload_fn(), "unknown_field": "x"}
    with pytest.raises(ValidationError):
        model_cls.model_validate(payload)


# ---------------------------------------------------------------------------
# Reject missing required (NonBlankStr fields)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_cls,payload_fn,field",
    [
        (ScaffoldConfigInfo, _scaffold_config, "version"),
        (ScaffoldModelInfo, _scaffold_model, "model_id"),
        (ScaffoldTaskInfo, _scaffold_task, "research_question"),
        (ScaffoldCorpusInfo, _scaffold_corpus, "retrieval_strategy"),
        (ScaffoldRunMetadata, _run_metadata, "operator"),
        (ScaffoldRunManifest, _run_manifest, "run_id"),
        (SourceRef, _source_ref, "source_id"),
        (ScaffoldClaim, _scaffold_claim, "claim_id"),
        (ClaimsRegistry, _claims_registry, "run_id"),
        (SourceBibliographic, _source_bibliographic, "title"),
        (SourceRetrieval, _source_retrieval, "retrieval_query"),
        (SourceMetadata, _source_metadata, "source_id"),
        (ScaffoldPassage, _scaffold_passage, "passage_id"),
        (SourcePassages, _source_passages, "source_id"),
    ],
    ids=lambda x: x.__name__ if isinstance(x, type) else x.__name__ if callable(x) else x,
)
def test_rejects_missing_required(model_cls, payload_fn, field) -> None:
    payload = payload_fn()
    del payload[field]
    with pytest.raises(ValidationError):
        model_cls.model_validate(payload)


# ---------------------------------------------------------------------------
# Vocabulary rejection on a C-A model field
# ---------------------------------------------------------------------------


def test_manifest_rejects_freeform_workflow_condition() -> None:
    payload = _run_manifest()
    payload["workflow_condition"] = "freeform"
    with pytest.raises(ValidationError):
        ScaffoldRunManifest.model_validate(payload)


# ---------------------------------------------------------------------------
# Custom validators
# ---------------------------------------------------------------------------


class TestClaimsRegistryValidator:
    def test_duplicate_claim_ids_rejected(self) -> None:
        claim_a = _scaffold_claim()
        claim_b = {**_scaffold_claim(), "claim_text": "different claim"}
        payload = _claims_registry()
        payload["claims"] = [claim_a, claim_b]
        with pytest.raises(ValidationError, match="Duplicate claim_id: c-001"):
            ClaimsRegistry.model_validate(payload)

    def test_unique_claim_ids_accepted(self) -> None:
        claim_a = _scaffold_claim()
        claim_b = {**_scaffold_claim(), "claim_id": "c-002"}
        payload = _claims_registry()
        payload["claims"] = [claim_a, claim_b]
        registry = ClaimsRegistry.model_validate(payload)
        assert len(registry.claims) == 2


class TestSourcePassagesValidator:
    def test_duplicate_passage_ids_rejected(self) -> None:
        p_a = _scaffold_passage()
        p_b = {**_scaffold_passage(), "text_preview": "different text"}
        payload = _source_passages()
        payload["passages"] = [p_a, p_b]
        with pytest.raises(ValidationError, match="Duplicate passage_id: p-001"):
            SourcePassages.model_validate(payload)

    def test_unique_passage_ids_accepted(self) -> None:
        p_a = _scaffold_passage()
        p_b = {**_scaffold_passage(), "passage_id": "p-002"}
        payload = _source_passages()
        payload["passages"] = [p_a, p_b]
        sp = SourcePassages.model_validate(payload)
        assert len(sp.passages) == 2


class TestScaffoldPassageOffsets:
    def test_char_end_equals_char_start_rejected(self) -> None:
        payload = {**_scaffold_passage(), "char_start": 10, "char_end": 10}
        with pytest.raises(ValidationError, match="char_end must be greater"):
            ScaffoldPassage.model_validate(payload)

    def test_char_end_less_than_char_start_rejected(self) -> None:
        payload = {**_scaffold_passage(), "char_start": 10, "char_end": 5}
        with pytest.raises(ValidationError, match="char_end must be greater"):
            ScaffoldPassage.model_validate(payload)

    def test_char_end_one_greater_accepted(self) -> None:
        payload = {**_scaffold_passage(), "char_start": 10, "char_end": 11}
        p = ScaffoldPassage.model_validate(payload)
        assert p.char_start == 10 and p.char_end == 11


# ---------------------------------------------------------------------------
# schema_version dual-literal acceptance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["1.0.0", "1.1.0"])
class TestSchemaVersionAcceptsBoth:
    def test_claims_registry(self, version: str) -> None:
        payload = _claims_registry(version)
        assert ClaimsRegistry.model_validate(payload).schema_version == version

    def test_source_metadata(self, version: str) -> None:
        payload = _source_metadata(version)
        assert SourceMetadata.model_validate(payload).schema_version == version

    def test_source_passages(self, version: str) -> None:
        payload = _source_passages(version)
        assert SourcePassages.model_validate(payload).schema_version == version


# ---------------------------------------------------------------------------
# Hash field shape on ScaffoldCorpusInfo
# ---------------------------------------------------------------------------


class TestCorpusHashShape:
    def test_accepts_full_sha256(self) -> None:
        payload = _scaffold_corpus()
        payload["corpus_hash"] = "sha256:" + "b" * 64
        c = ScaffoldCorpusInfo.model_validate(payload)
        assert c.corpus_hash == "sha256:" + "b" * 64

    def test_accepts_pending(self) -> None:
        payload = _scaffold_corpus()
        payload["corpus_hash"] = "sha256:pending"
        c = ScaffoldCorpusInfo.model_validate(payload)
        assert c.corpus_hash == "sha256:pending"

    def test_rejects_bare_hex(self) -> None:
        payload = _scaffold_corpus()
        payload["corpus_hash"] = "a" * 64
        with pytest.raises(ValidationError):
            ScaffoldCorpusInfo.model_validate(payload)

    def test_rejects_wrong_prefix(self) -> None:
        payload = _scaffold_corpus()
        payload["corpus_hash"] = "md5:" + "a" * 64
        with pytest.raises(ValidationError):
            ScaffoldCorpusInfo.model_validate(payload)
