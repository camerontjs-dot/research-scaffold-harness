"""Prompt runner skeleton, deterministic offline adapter, and live MLX adapter.

Note: the writer bridge lives at :mod:`research_scaffold_harness.runner.writer_bridge`
and is intentionally not re-exported here — it transitively depends on
:mod:`research_scaffold_harness.extractor`, which itself imports from this
package, so re-exporting would create a circular import. Import bridge symbols
directly:

    from research_scaffold_harness.runner.writer_bridge import (
        write_scaffold_run_from_extraction,
        mint_run_id,
    )
"""

from research_scaffold_harness.runner.adapters import (
    ModelAdapter,
    ModelRequest,
    ModelResponse,
    StubModelAdapter,
)
from research_scaffold_harness.runner.core import (
    RunnerError,
    RunnerResult,
    RunnerSettings,
    run_source_packet,
    run_task,
)
from research_scaffold_harness.runner.mlx_adapter import (
    MLX_ENDPOINT,
    MLX_MODEL_ALLOWLIST,
    MLXAdapterError,
    MLXModelAdapter,
)
from research_scaffold_harness.runner.source_packet import (
    SourcePacket,
    SourcePacketError,
    SourcePacketSource,
    load_source_packet,
)

__all__ = [
    "MLX_ENDPOINT",
    "MLX_MODEL_ALLOWLIST",
    "MLXAdapterError",
    "MLXModelAdapter",
    "ModelAdapter",
    "ModelRequest",
    "ModelResponse",
    "RunnerError",
    "RunnerResult",
    "RunnerSettings",
    "SourcePacket",
    "SourcePacketError",
    "SourcePacketSource",
    "StubModelAdapter",
    "load_source_packet",
    "run_source_packet",
    "run_task",
]
