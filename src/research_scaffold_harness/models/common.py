"""Shared contract model primitives for the Research Scaffold Harness.

The harness is the PRODUCER of C-A artifacts; it owns its own copy of these
primitives so it does not import from Evidence Bundler. See `DECISIONS.md` for
the v1.0.0 / v1.1.0 accommodation: the harness knows v1.1.0 vocabulary
(includes `format_only`) but emits `"1.0.0"` in artifact CONTRACT_VERSION /
schema_version fields until Evidence Bundler bumps its pin.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "1.1.0"
WRITER_SCHEMA_VERSION = "1.0.0"
PENDING_HASH = "sha256:pending"

NonBlankStr: TypeAlias = Annotated[str, Field(min_length=1)]
ContractVersion: TypeAlias = Literal["1.0.0", "1.1.0"]
HashValue: TypeAlias = Annotated[
    str,
    Field(pattern=r"^sha256:([a-f0-9]{64}|pending)$"),
]

WorkflowCondition: TypeAlias = Literal[
    "baseline",
    "format_only",
    "provenance_scaffold",
    "full_scaffold",
]
ClaimType: TypeAlias = Literal["retrieval_seed", "extracted_claim"]
SupportStatus: TypeAlias = Literal["sourced", "inferred", "uncertain", "unsupported"]
SourceType: TypeAlias = Literal[
    "journal_article",
    "regulatory_guidance",
    "preprint",
    "web_page",
    "book",
    "other",
]
TrustLevel: TypeAlias = Literal["primary", "secondary", "background"]
ExtractionMethod: TypeAlias = Literal[
    "scaffold_cited",
    "scaffold_inferred",
    "auto_retrieved",
]


class StrictBaseModel(BaseModel):
    """Base model that rejects schema drift and normalizes surrounding whitespace."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
