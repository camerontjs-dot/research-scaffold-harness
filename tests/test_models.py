"""Shared model primitive tests — Phase 1 Unit 3."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from research_scaffold_harness.models.common import (
    CONTRACT_VERSION,
    PENDING_HASH,
    WRITER_SCHEMA_VERSION,
    ClaimType,
    ContractVersion,
    ExtractionMethod,
    HashValue,
    NonBlankStr,
    SourceType,
    StrictBaseModel,
    SupportStatus,
    TrustLevel,
    WorkflowCondition,
)


def test_constants_pinned() -> None:
    assert CONTRACT_VERSION == "1.1.0"
    assert WRITER_SCHEMA_VERSION == "1.0.0"
    assert PENDING_HASH == "sha256:pending"


class _StrictExample(StrictBaseModel):
    name: NonBlankStr


def test_strict_base_model_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        _StrictExample.model_validate({"name": "ok", "extra": "no"})


def test_strict_base_model_strips_whitespace() -> None:
    model = _StrictExample.model_validate({"name": "  trim me  "})
    assert model.name == "trim me"


def test_non_blank_str_rejects_empty() -> None:
    with pytest.raises(ValidationError):
        _StrictExample.model_validate({"name": ""})


class _HashHolder(BaseModel):
    h: HashValue


def test_hash_value_accepts_pending() -> None:
    assert _HashHolder.model_validate({"h": "sha256:pending"}).h == "sha256:pending"


def test_hash_value_accepts_full_digest() -> None:
    digest = "a" * 64
    assert _HashHolder.model_validate({"h": f"sha256:{digest}"}).h == f"sha256:{digest}"


@pytest.mark.parametrize(
    "bad",
    [
        "sha256:",
        "sha256:short",
        "md5:" + "a" * 64,
        "a" * 64,
        "sha256:" + "g" * 64,  # non-hex
    ],
)
def test_hash_value_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValidationError):
        _HashHolder.model_validate({"h": bad})


class _VocabHolder(BaseModel):
    contract: ContractVersion
    workflow: WorkflowCondition
    claim: ClaimType
    support: SupportStatus
    source_kind: SourceType
    trust: TrustLevel
    extraction: ExtractionMethod


_VALID_VOCAB = {
    "contract": "1.1.0",
    "workflow": "format_only",
    "claim": "extracted_claim",
    "support": "sourced",
    "source_kind": "regulatory_guidance",
    "trust": "primary",
    "extraction": "scaffold_cited",
}


def test_vocab_aliases_accept_locked_values() -> None:
    model = _VocabHolder.model_validate(_VALID_VOCAB)
    assert model.workflow == "format_only"
    assert model.contract == "1.1.0"


def test_contract_version_accepts_one_zero_zero_for_writer_output() -> None:
    payload = {**_VALID_VOCAB, "contract": "1.0.0"}
    assert _VocabHolder.model_validate(payload).contract == "1.0.0"


@pytest.mark.parametrize(
    "field,bad",
    [
        ("contract", "0.9.0"),
        ("workflow", "freeform"),
        ("claim", "speculative_claim"),
        ("support", "verified"),
        ("source_kind", "tweet"),
        ("trust", "tertiary"),
        ("extraction", "manual"),
    ],
)
def test_vocab_aliases_reject_unknown_values(field: str, bad: str) -> None:
    payload = {**_VALID_VOCAB, field: bad}
    with pytest.raises(ValidationError):
        _VocabHolder.model_validate(payload)
