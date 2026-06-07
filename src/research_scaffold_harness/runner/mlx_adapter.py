"""Live MLX runner adapter.

Loads a HuggingFace MLX 4-bit checkpoint via ``mlx-lm`` and applies the model's
native chat template before generation. Construction is gated by an allowlist
that mirrors the five models in ``DECISIONS.md`` § "Model selection."

``mlx-lm`` and ``huggingface_hub`` are optional dependencies. Install via
``pip install -e '.[mlx]'``. The adapter imports them lazily inside
``_load`` so the rest of the harness can run on platforms without MLX.
"""

from __future__ import annotations

import gc
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

from research_scaffold_harness.runner.adapters import ModelRequest, ModelResponse


class MLXAdapterError(Exception):
    """Raised when an MLX adapter cannot load a model or resolve its identity."""


MLX_MODEL_ALLOWLIST: tuple[str, ...] = (
    "lmstudio-community/Phi-4-mini-reasoning-MLX-4bit",
    "mlx-community/Qwen3-8B-4bit",
    "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
    "mlx-community/gemma-3-12b-it-qat-4bit",
    "mlx-community/Phi-4-reasoning-plus-4bit",
)

MLX_ENDPOINT = "mlx://local"


@dataclass(frozen=True)
class _LoadedModel:
    model: Any
    tokenizer: Any
    revision: str


class MLXModelAdapter:
    """Live MLX adapter loading models via ``mlx-lm``.

    Construction is fast; the model itself loads lazily on first
    ``generate`` and is cached for the adapter's lifetime so process-per-model
    scripts pay the load cost once.
    """

    api_endpoint = MLX_ENDPOINT

    def __init__(self, model_id: str) -> None:
        if model_id not in MLX_MODEL_ALLOWLIST:
            raise MLXAdapterError(
                f"Model {model_id!r} is not in the five-model ADR allowlist. "
                f"Allowed: {MLX_MODEL_ALLOWLIST}"
            )
        self._model_id = model_id
        self._loaded: _LoadedModel | None = None
        self._mlx_lm_version_cached: str | None = None
        self._quantization = _quantization_from_repo(model_id)

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def model_version(self) -> str:
        if self._mlx_lm_version_cached is None:
            self._mlx_lm_version_cached = _resolve_mlx_lm_version()
        return self._mlx_lm_version_cached

    @property
    def quantization(self) -> str:
        return self._quantization

    @property
    def loaded_revision(self) -> str:
        return self._loaded.revision if self._loaded is not None else ""

    @property
    def is_loaded(self) -> bool:
        return self._loaded is not None

    def _load(self) -> _LoadedModel:
        if self._loaded is not None:
            return self._loaded
        if self._mlx_lm_version_cached is None:
            self._mlx_lm_version_cached = _resolve_mlx_lm_version()
        mlx_lm = _import_mlx_lm()
        model, tokenizer = mlx_lm.load(self._model_id)
        revision = _resolve_revision(self._model_id)
        self._loaded = _LoadedModel(model=model, tokenizer=tokenizer, revision=revision)
        return self._loaded

    def generate(self, request: ModelRequest) -> ModelResponse:
        loaded = self._load()
        mlx_lm = _import_mlx_lm()

        templated, chat_template_applied = _apply_chat_template(
            tokenizer=loaded.tokenizer, prompt=request.prompt,
        )

        text = _mlx_generate(
            mlx_lm,
            model=loaded.model,
            tokenizer=loaded.tokenizer,
            prompt=templated,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        finish_reason = "length" if _looks_truncated(text, request.max_tokens) else "stop"

        return ModelResponse(
            model_id=self._model_id,
            model_version=self.model_version,
            api_endpoint=MLX_ENDPOINT,
            text=text,
            finish_reason=finish_reason,
            output_tokens=len(text.split()),
            model_revision=loaded.revision,
            quantization=self._quantization,
            chat_template_applied=chat_template_applied,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def close(self) -> None:
        """Release the loaded model and free MLX/Metal memory.

        The ADR mandates sequential (not concurrent) model residency on the
        24 GB unified-memory budget. Process-per-cell scripts call this after
        generation so an extractor model can load without the generator still
        occupying memory.
        """
        self._loaded = None
        gc.collect()
        _clear_mlx_cache()


def _import_mlx_lm() -> Any:
    try:
        import mlx_lm  # type: ignore[import-not-found]
    except ImportError as exc:
        raise MLXAdapterError(
            "mlx-lm is not installed; install with `pip install -e '.[mlx]'`"
        ) from exc
    return mlx_lm


def _clear_mlx_cache() -> None:
    """Return MLX's buffer cache to the OS after model references are dropped.

    Newer ``mlx`` exposes ``mx.clear_cache``; older builds expose
    ``mx.metal.clear_cache``. No-op when ``mlx`` is unavailable.
    """
    try:
        import mlx.core as mx
    except ImportError:
        return
    clear = getattr(mx, "clear_cache", None)
    if clear is None:
        metal = getattr(mx, "metal", None)
        clear = getattr(metal, "clear_cache", None) if metal is not None else None
    if callable(clear):
        clear()


def _resolve_mlx_lm_version() -> str:
    try:
        return importlib_metadata.version("mlx-lm")
    except importlib_metadata.PackageNotFoundError as exc:
        raise MLXAdapterError(
            "mlx-lm package metadata not found; install with `pip install -e '.[mlx]'`"
        ) from exc


def _quantization_from_repo(model_id: str) -> str:
    lowered = model_id.lower()
    if "qat-4bit" in lowered:
        return "qat-4bit"
    if "4bit" in lowered:
        return "4bit"
    if "8bit" in lowered:
        return "8bit"
    return "unknown"


def _apply_chat_template(*, tokenizer: Any, prompt: str) -> tuple[str, bool]:
    apply = getattr(tokenizer, "apply_chat_template", None)
    if apply is None:
        return prompt, False
    try:
        templated = apply(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
    except Exception:
        return prompt, False
    if not isinstance(templated, str) or not templated.strip():
        return prompt, False
    return templated, True


def _mlx_generate(
    mlx_lm: Any,
    *,
    model: Any,
    tokenizer: Any,
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Invoke ``mlx_lm.generate`` across known signature variations.

    mlx-lm 0.18+ accepts a ``sampler`` produced by ``make_sampler``. Older
    versions accept ``temp=`` directly. Both shapes return either ``str`` or a
    ``(text, metadata)`` tuple depending on version.
    """
    sampler = _build_sampler(mlx_lm, temperature)
    try:
        if sampler is not None:
            raw = mlx_lm.generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False,
                sampler=sampler,
            )
        else:
            raw = mlx_lm.generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False,
                temp=temperature,
            )
    except TypeError as exc:
        raise MLXAdapterError(
            f"mlx_lm.generate signature mismatch for installed mlx-lm: {exc}"
        ) from exc

    if isinstance(raw, tuple):
        return str(raw[0])
    return str(raw)


def _build_sampler(mlx_lm: Any, temperature: float) -> Any | None:
    for module_name in ("sample_utils", "utils"):
        try:
            module = __import__(f"mlx_lm.{module_name}", fromlist=["make_sampler"])
        except ImportError:
            continue
        make_sampler = getattr(module, "make_sampler", None)
        if make_sampler is None:
            continue
        try:
            return make_sampler(temp=temperature)
        except TypeError:
            continue
    return None


def _resolve_revision(model_id: str) -> str:
    """Resolve the HuggingFace commit SHA of the cached snapshot we just loaded.

    Reads the local huggingface_hub snapshot symlink target first; falls back
    to the HF Hub API if the snapshot path doesn't carry the SHA. Empty string
    means resolution failed — callers should treat that as a gate failure
    rather than silently writing a blank revision.
    """
    sha = _resolve_revision_from_snapshot(model_id)
    if sha:
        return sha
    return _resolve_revision_from_api(model_id)


def _resolve_revision_from_snapshot(model_id: str) -> str:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        return ""
    try:
        snapshot_path = Path(snapshot_download(model_id, local_files_only=True))
    except Exception:
        return ""
    name = snapshot_path.name
    if _looks_like_sha(name):
        return name
    refs_path = snapshot_path.parent.parent / "refs"
    main_ref = refs_path / "main"
    if main_ref.exists():
        candidate = main_ref.read_text(encoding="utf-8").strip()
        if _looks_like_sha(candidate):
            return candidate
    return ""


def _resolve_revision_from_api(model_id: str) -> str:
    try:
        from huggingface_hub import HfApi
    except ImportError:
        return ""
    try:
        info = HfApi().repo_info(model_id)
    except Exception:
        return ""
    sha = getattr(info, "sha", "") or ""
    if _looks_like_sha(sha):
        return sha
    return ""


def _looks_like_sha(value: str) -> bool:
    if not value:
        return False
    if len(value) < 7 or len(value) > 64:
        return False
    return all(c in "0123456789abcdef" for c in value.lower())


def _looks_truncated(text: str, max_tokens: int) -> bool:
    return len(text.split()) >= max_tokens
