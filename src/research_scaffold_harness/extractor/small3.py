"""Mistral Small 3.1 live extractor adapter."""

from __future__ import annotations

from research_scaffold_harness.extractor.live import LiveExtractorBackend, MlxLiveExtractor

SMALL3_EXTRACTOR_MODEL_ID = "mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit"
SMALL3_EXTRACTOR_ID = "mlx-mistral-small3"


class MlxSmallExtractor(MlxLiveExtractor):
    """Live extractor using Mistral Small 3.1 through MLX."""

    def __init__(self, backend: LiveExtractorBackend | None = None) -> None:
        super().__init__(
            model_id=SMALL3_EXTRACTOR_MODEL_ID,
            extractor_id=SMALL3_EXTRACTOR_ID,
            backend=backend,
        )
