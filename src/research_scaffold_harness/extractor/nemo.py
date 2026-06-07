"""Mistral Nemo live extractor adapter."""

from __future__ import annotations

from research_scaffold_harness.extractor.live import LiveExtractorBackend, MlxLiveExtractor

NEMO_EXTRACTOR_MODEL_ID = "mlx-community/Mistral-Nemo-Instruct-2407-4bit"
NEMO_EXTRACTOR_ID = "mlx-mistral-nemo-12b"


class MlxNemoExtractor(MlxLiveExtractor):
    """Live extractor using Mistral Nemo 12B through MLX."""

    def __init__(self, backend: LiveExtractorBackend | None = None) -> None:
        super().__init__(
            model_id=NEMO_EXTRACTOR_MODEL_ID,
            extractor_id=NEMO_EXTRACTOR_ID,
            backend=backend,
        )
