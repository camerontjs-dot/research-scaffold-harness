"""Shape tests for live extractor surfaces and MLX extractor adapters."""

from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

from research_scaffold_harness.extractor import (
    MlxNemoExtractor,
    MlxSmallExtractor,
    extract_claims_from_runner_result,
    extract_think_claims_from_runner_result,
)
from research_scaffold_harness.extractor.live import LiveExtractorGeneration
from research_scaffold_harness.extractor.surfaces import prepare_extraction_surfaces
from research_scaffold_harness.runner import ModelResponse, RunnerResult


@dataclass
class _FakeBackend:
    text: str = "claims:\n  - claim_text: Visible answer contains one claim.\n"
    last_prompt: str = ""

    def generate(self, *, prompt: str, max_tokens: int, temperature: float):
        self.last_prompt = prompt
        assert max_tokens > 0
        assert temperature == 0.0
        return LiveExtractorGeneration(
            text=self.text,
            model_id="fake-mistral",
            model_version="0.0",
            model_revision="abc1234",
            quantization="4bit",
            api_endpoint="fake://local",
            chat_template_applied=False,
        )


def test_prepare_extraction_surfaces_strips_think_blocks_and_footer() -> None:
    surfaces = prepare_extraction_surfaces(
        "<think>Private draft claim.</think>\n"
        "Final answer:\n"
        "The visible answer contains one claim.\n"
        "Final claims:\n"
        "- Footer claim should not be official.\n"
    )

    assert surfaces.official_answer_text == "The visible answer contains one claim."
    assert surfaces.think_block_text == "Private draft claim."
    assert surfaces.diagnostics == ("think-block-stripped",)


def test_prepare_extraction_surfaces_removes_scaffold_tables() -> None:
    surfaces = prepare_extraction_surfaces(
        "Claim table:\n"
        "| claim text |\n"
        "| --- |\n"
        "| Draft scaffold table claim. |\n\n"
        "The visible answer contains one claim.\n"
    )

    assert "Draft scaffold table claim" not in surfaces.official_answer_text
    assert surfaces.official_answer_text == "The visible answer contains one claim."


def test_nemo_extractor_uses_visible_answer_body_only() -> None:
    backend = _FakeBackend()
    extractor = MlxNemoExtractor(backend=backend)
    result = extract_claims_from_runner_result(
        result=_runner_result(
            "<think>Private draft claim.</think>\n"
            "Final answer:\n"
            "The visible answer contains one claim.\n"
            "Final claims:\n"
            "- Footer claim should not be official.\n"
        ),
        run_id="live-run",
        adapter=extractor,
    )

    assert result.extractor_id == "mlx-mistral-nemo-12b"
    assert [claim.claim_text for claim in result.claims.claims] == [
        "Visible answer contains one claim."
    ]
    assert "Private draft claim" not in backend.last_prompt
    assert "Footer claim should not be official" not in backend.last_prompt
    assert "The visible answer contains one claim." in backend.last_prompt


def test_small3_extractor_shape() -> None:
    extractor = MlxSmallExtractor(backend=_FakeBackend())
    assert extractor.extractor_id == "mlx-mistral-small3"
    assert extractor.model_id == "mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit"
    assert extractor.is_stub is False


def test_live_extractor_close_delegates_to_backend() -> None:
    class _ClosableBackend:
        def __init__(self) -> None:
            self.closed = False

        def generate(self, *, prompt: str, max_tokens: int, temperature: float):
            raise AssertionError("generate should not run in this test")

        def close(self) -> None:
            self.closed = True

    backend = _ClosableBackend()
    MlxNemoExtractor(backend=backend).close()
    assert backend.closed is True


def test_extractor_backend_close_drops_cached_model() -> None:
    from research_scaffold_harness.extractor.live import MlxExtractorBackend

    backend = MlxExtractorBackend("mlx-community/Mistral-Nemo-Instruct-2407-4bit")
    backend._model = object()
    backend._tokenizer = object()
    backend.close()
    assert backend._model is None
    assert backend._tokenizer is None


def test_mlx_generator_adapter_close_unloads() -> None:
    from research_scaffold_harness.runner.mlx_adapter import MLXModelAdapter, _LoadedModel

    adapter = MLXModelAdapter("mlx-community/gemma-3-12b-it-qat-4bit")
    adapter._loaded = _LoadedModel(model=object(), tokenizer=object(), revision="abc1234")
    assert adapter.is_loaded is True
    adapter.close()
    assert adapter.is_loaded is False


def test_think_block_extraction_is_exploratory() -> None:
    backend = _FakeBackend(text="claims:\n  - claim_text: Private draft claim.\n")
    extractor = MlxNemoExtractor(backend=backend)
    result = extract_think_claims_from_runner_result(
        result=_runner_result("<think>Private draft claim.</think>\nFinal answer:\nOK."),
        run_id="think-run",
        adapter=extractor,
    )

    assert result.diagnostics == ("exploratory-think-block",)
    assert result.final_claims_text == "Private draft claim."
    assert [claim.claim_text for claim in result.claims.claims] == ["Private draft claim."]


@pytest.mark.live
@pytest.mark.skipif(
    os.environ.get("RSH_RUN_LIVE_EXTRACTOR_LOADS") != "1",
    reason="set RSH_RUN_LIVE_EXTRACTOR_LOADS=1 to load live extractor models",
)
def test_live_nemo_extractor_loads_and_generates() -> None:
    generation = MlxNemoExtractor()._backend.generate(
        prompt="Return YAML with claims: [].",
        max_tokens=8,
        temperature=0.0,
    )

    assert generation.model_id == "mlx-community/Mistral-Nemo-Instruct-2407-4bit"
    assert generation.model_revision
    assert generation.quantization == "4bit"


@pytest.mark.live
@pytest.mark.skipif(
    os.environ.get("RSH_RUN_LIVE_EXTRACTOR_LOADS") != "1",
    reason="set RSH_RUN_LIVE_EXTRACTOR_LOADS=1 to load live extractor models",
)
def test_live_small3_extractor_loads_and_generates() -> None:
    generation = MlxSmallExtractor()._backend.generate(
        prompt="Return YAML with claims: [].",
        max_tokens=8,
        temperature=0.0,
    )

    assert generation.model_id == "mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit"
    assert generation.model_revision
    assert generation.quantization == "4bit"


def _runner_result(raw_output: str) -> RunnerResult:
    return RunnerResult(
        task_id="rsh-001-fixture",
        condition="baseline",
        prompt_template_id="baseline-v1",
        prompt_template_hash="sha256:" + "a" * 64,
        rendered_prompt_hash="sha256:" + "b" * 64,
        prompt="Rendered prompt",
        response=ModelResponse(
            model_id="stub-offline-deterministic",
            model_version="0.1.0",
            api_endpoint="stub://offline",
            text=raw_output,
            finish_reason="stop",
            output_tokens=len(raw_output.split()),
        ),
    )
