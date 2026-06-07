"""Uniform claim extraction over raw runner output."""

from research_scaffold_harness.extractor.adapters import (
    ExtractorAdapter,
    ExtractorRequest,
    ExtractorResponse,
    StubUniformExtractor,
)
from research_scaffold_harness.extractor.core import (
    UniformExtractionResult,
    extract_claims_from_runner_result,
    extract_think_claims_from_runner_result,
)
from research_scaffold_harness.extractor.nemo import MlxNemoExtractor
from research_scaffold_harness.extractor.small3 import MlxSmallExtractor

__all__ = [
    "ExtractorAdapter",
    "ExtractorRequest",
    "ExtractorResponse",
    "MlxNemoExtractor",
    "MlxSmallExtractor",
    "StubUniformExtractor",
    "UniformExtractionResult",
    "extract_claims_from_runner_result",
    "extract_think_claims_from_runner_result",
]
