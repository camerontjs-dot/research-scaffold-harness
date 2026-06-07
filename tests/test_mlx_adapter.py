"""Live MLX adapter tests.

Shape-level tests run by default and require neither ``mlx-lm`` nor a loaded
model. The ``@pytest.mark.live`` tests are deselected by default and require
mlx-lm plus enough memory to load the smallest model on Apple Silicon.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from research_scaffold_harness.prompts import hash_template, load_template
from research_scaffold_harness.runner import (
    MLX_ENDPOINT,
    MLX_MODEL_ALLOWLIST,
    MLXAdapterError,
    MLXModelAdapter,
    ModelAdapter,
    RunnerSettings,
    load_source_packet,
    run_source_packet,
)
from research_scaffold_harness.runner.mlx_adapter import (
    _apply_chat_template,
    _looks_like_sha,
    _looks_truncated,
    _quantization_from_repo,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_SMALLEST_MODEL = "lmstudio-community/Phi-4-mini-reasoning-MLX-4bit"


def test_allowlist_contains_exactly_five_models() -> None:
    assert len(MLX_MODEL_ALLOWLIST) == 5
    assert len(set(MLX_MODEL_ALLOWLIST)) == 5


def test_allowlist_covers_five_organizations() -> None:
    expected_organizations = {
        "Microsoft (Phi-4-mini-reasoning)",
        "Alibaba (Qwen3-8B)",
        "Meta (Llama-3.1-8B-Instruct)",
        "Google (Gemma-3-12B QAT)",
        "Microsoft (Phi-4-reasoning-plus)",
    }
    assert any("Phi-4-mini-reasoning" in m for m in MLX_MODEL_ALLOWLIST)
    assert any("Qwen3-8B" in m for m in MLX_MODEL_ALLOWLIST)
    assert any("Llama-3.1-8B-Instruct" in m for m in MLX_MODEL_ALLOWLIST)
    assert any("gemma-3-12b-it-qat" in m.lower() for m in MLX_MODEL_ALLOWLIST)
    assert any("Phi-4-reasoning-plus" in m for m in MLX_MODEL_ALLOWLIST)
    assert len(expected_organizations) == 5


def test_construction_with_allowlisted_model_succeeds() -> None:
    adapter = MLXModelAdapter(model_id=_SMALLEST_MODEL)
    assert adapter.model_id == _SMALLEST_MODEL
    assert adapter.quantization == "4bit"
    assert adapter.api_endpoint == MLX_ENDPOINT
    assert adapter.is_loaded is False
    assert adapter.loaded_revision == ""


def test_construction_with_unknown_model_raises() -> None:
    with pytest.raises(MLXAdapterError, match="not in the five-model ADR allowlist"):
        MLXModelAdapter(model_id="some-org/random-model")


def test_construction_with_blank_model_raises() -> None:
    with pytest.raises(MLXAdapterError):
        MLXModelAdapter(model_id="")


def test_qat_model_records_qat_quantization() -> None:
    adapter = MLXModelAdapter(model_id="mlx-community/gemma-3-12b-it-qat-4bit")
    assert adapter.quantization == "qat-4bit"


def test_adapter_satisfies_model_adapter_protocol() -> None:
    adapter = MLXModelAdapter(model_id=_SMALLEST_MODEL)
    assert isinstance(adapter, ModelAdapter)


def test_api_endpoint_is_not_stub_sentinel() -> None:
    adapter = MLXModelAdapter(model_id=_SMALLEST_MODEL)
    assert adapter.api_endpoint != "stub://offline"
    assert adapter.api_endpoint.startswith("mlx://")


def test_quantization_parser_handles_known_patterns() -> None:
    assert _quantization_from_repo("mlx-community/foo-4bit") == "4bit"
    assert _quantization_from_repo("mlx-community/foo-qat-4bit") == "qat-4bit"
    assert _quantization_from_repo("mlx-community/foo-8bit") == "8bit"
    assert _quantization_from_repo("mlx-community/foo-fp16") == "unknown"


def test_sha_shape_check_accepts_valid_hex() -> None:
    assert _looks_like_sha("abc1234567890def")
    assert _looks_like_sha("abc1234")
    assert _looks_like_sha("a" * 40)


def test_sha_shape_check_rejects_invalid() -> None:
    assert not _looks_like_sha("")
    assert not _looks_like_sha("not-hex-zzz")
    assert not _looks_like_sha("ABC123!@#")
    assert not _looks_like_sha("a" * 65)


def test_truncation_heuristic() -> None:
    assert _looks_truncated("a b c d", max_tokens=4)
    assert _looks_truncated("a b c d e", max_tokens=4)
    assert not _looks_truncated("a b c", max_tokens=4)


def test_apply_chat_template_falls_back_when_tokenizer_lacks_method() -> None:
    class _MinimalTokenizer:
        pass

    templated, applied = _apply_chat_template(
        tokenizer=_MinimalTokenizer(), prompt="hello"
    )
    assert templated == "hello"
    assert applied is False


def test_apply_chat_template_uses_method_when_present() -> None:
    class _FakeTokenizer:
        def apply_chat_template(self, messages, *, tokenize, add_generation_prompt):
            assert tokenize is False
            assert add_generation_prompt is True
            return f"<chat>{messages[0]['content']}</chat>"

    templated, applied = _apply_chat_template(
        tokenizer=_FakeTokenizer(), prompt="hello"
    )
    assert templated == "<chat>hello</chat>"
    assert applied is True


def test_apply_chat_template_falls_back_when_method_raises() -> None:
    class _BrokenTokenizer:
        def apply_chat_template(self, *args, **kwargs):
            raise RuntimeError("boom")

    templated, applied = _apply_chat_template(
        tokenizer=_BrokenTokenizer(), prompt="hello"
    )
    assert templated == "hello"
    assert applied is False


def test_apply_chat_template_falls_back_when_method_returns_empty() -> None:
    class _EmptyTokenizer:
        def apply_chat_template(self, *args, **kwargs):
            return ""

    templated, applied = _apply_chat_template(
        tokenizer=_EmptyTokenizer(), prompt="hello"
    )
    assert templated == "hello"
    assert applied is False


# ---------------------------------------------------------------------------
# Live tests — require mlx-lm + Apple Silicon + downloaded model. Deselected
# by default; run with: pytest -m live tests/test_mlx_adapter.py
# ---------------------------------------------------------------------------


@pytest.mark.live
def test_live_smoke_baseline_generates_non_empty_output() -> None:
    adapter = MLXModelAdapter(model_id=_SMALLEST_MODEL)
    packet = load_source_packet(_FIXTURE_DIR)
    settings = RunnerSettings(temperature=0.7, max_tokens=256)

    result = run_source_packet(packet, "baseline", adapter, settings)

    assert result.response.text.strip()
    assert result.response.model_id == _SMALLEST_MODEL
    assert result.response.api_endpoint == MLX_ENDPOINT
    assert result.response.model_revision  # gate: revision must resolve
    assert result.response.quantization == "4bit"
    template = load_template("baseline")
    assert result.prompt_template_hash == hash_template(template)


@pytest.mark.live
def test_live_second_generate_does_not_reload_model() -> None:
    adapter = MLXModelAdapter(model_id=_SMALLEST_MODEL)
    packet = load_source_packet(_FIXTURE_DIR)
    settings = RunnerSettings(temperature=0.7, max_tokens=64)

    run_source_packet(packet, "baseline", adapter, settings)
    assert adapter.is_loaded is True
    first_revision = adapter.loaded_revision

    run_source_packet(packet, "format_only", adapter, settings)
    assert adapter.loaded_revision == first_revision
