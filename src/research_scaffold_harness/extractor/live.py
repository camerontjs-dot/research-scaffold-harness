"""Live MLX claim extractors for visible-answer claim extraction."""

from __future__ import annotations

import gc
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

import yaml

from research_scaffold_harness.extractor.adapters import (
    ExtractorRequest,
    ExtractorResponse,
)
from research_scaffold_harness.extractor.surfaces import prepare_extraction_surfaces
from research_scaffold_harness.runner.mlx_adapter import (
    MLX_ENDPOINT,
    MLXAdapterError,
    _apply_chat_template,
    _clear_mlx_cache,
    _import_mlx_lm,
    _mlx_generate,
    _quantization_from_repo,
    _resolve_mlx_lm_version,
    _resolve_revision,
)


class LiveExtractorError(Exception):
    """Raised when a live extractor cannot produce or parse extraction output."""


@dataclass(frozen=True)
class LiveExtractorGeneration:
    """Raw text returned by a live extractor backend."""

    text: str
    model_id: str
    model_version: str
    model_revision: str
    quantization: str
    api_endpoint: str
    chat_template_applied: bool


class LiveExtractorBackend(Protocol):
    """Backend used by the live extractor adapter."""

    def generate(
        self,
        *,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> LiveExtractorGeneration:
        """Generate extractor output from an extraction prompt."""


class MlxExtractorBackend:
    """MLX backend for one extractor model."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.quantization = _quantization_from_repo(model_id)
        self._model = None
        self._tokenizer = None
        self._revision = ""
        self._version = ""

    def generate(
        self,
        *,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> LiveExtractorGeneration:
        model, tokenizer = self._load()
        mlx_lm = _import_mlx_lm()
        templated, applied = _apply_chat_template(tokenizer=tokenizer, prompt=prompt)
        text = _mlx_generate(
            mlx_lm,
            model=model,
            tokenizer=tokenizer,
            prompt=templated,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return LiveExtractorGeneration(
            text=text,
            model_id=self.model_id,
            model_version=self._version,
            model_revision=self._revision,
            quantization=self.quantization,
            api_endpoint=MLX_ENDPOINT,
            chat_template_applied=applied,
        )

    def _load(self):
        if self._model is not None and self._tokenizer is not None:
            return self._model, self._tokenizer
        self._version = _resolve_mlx_lm_version()
        mlx_lm = _import_mlx_lm()
        # Mistral MLX tokenizers ship a known-bad default regex; fix_mistral_regex
        # corrects tokenization for both Nemo and Small 3.1 (verified accepted by
        # the installed transformers; silences the load-time warning).
        self._model, self._tokenizer = mlx_lm.load(
            self.model_id, tokenizer_config={"fix_mistral_regex": True}
        )
        self._revision = _resolve_revision(self.model_id)
        if not self._revision:
            raise MLXAdapterError(
                f"Could not resolve HuggingFace revision for extractor {self.model_id!r}"
            )
        return self._model, self._tokenizer

    def close(self) -> None:
        """Drop the cached model and tokenizer and free MLX/Metal memory."""
        self._model = None
        self._tokenizer = None
        gc.collect()
        _clear_mlx_cache()


class MlxLiveExtractor:
    """Common adapter for live MLX answer-body extractors."""

    extractor_version = "0.1.0"
    is_stub = False
    max_tokens = 768
    temperature = 0.0

    def __init__(
        self,
        *,
        model_id: str,
        extractor_id: str,
        backend: LiveExtractorBackend | None = None,
    ) -> None:
        self._model_id = model_id
        self._extractor_id = extractor_id
        self._backend = backend or MlxExtractorBackend(model_id)

    @property
    def extractor_id(self) -> str:
        return self._extractor_id

    @property
    def model_id(self) -> str:
        return self._model_id

    def close(self) -> None:
        """Free the extractor's model so the next model can load (ADR: sequential)."""
        backend_close = getattr(self._backend, "close", None)
        if callable(backend_close):
            backend_close()

    def extract(self, request: ExtractorRequest) -> ExtractorResponse:
        surfaces = prepare_extraction_surfaces(request.raw_output)
        if not surfaces.official_answer_text:
            return ExtractorResponse(
                claim_texts=(),
                diagnostics=surfaces.diagnostics + ("official-answer-body-empty",),
                final_claims_text="",
            )

        generation = self._backend.generate(
            prompt=_build_extraction_prompt(surfaces.official_answer_text),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        claims, parse_diagnostics = _parse_claim_texts(generation.text)
        diagnostics = surfaces.diagnostics + parse_diagnostics
        return ExtractorResponse(
            claim_texts=tuple(claims),
            diagnostics=diagnostics,
            final_claims_text=surfaces.official_answer_text,
        )

    def extract_think_block(self, request: ExtractorRequest) -> ExtractorResponse:
        surfaces = prepare_extraction_surfaces(request.raw_output)
        if not surfaces.think_block_text:
            return ExtractorResponse(
                claim_texts=(),
                diagnostics=("think-block-not-present",),
                final_claims_text="",
            )
        generation = self._backend.generate(
            prompt=_build_extraction_prompt(surfaces.think_block_text),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        claims, parse_diagnostics = _parse_claim_texts(generation.text)
        return ExtractorResponse(
            claim_texts=tuple(claims),
            diagnostics=("exploratory-think-block",) + parse_diagnostics,
            final_claims_text=surfaces.think_block_text,
        )


def _build_extraction_prompt(answer_body: str) -> str:
    return (
        "Extract every atomic substantive claim from the visible answer body below.\n"
        "Return YAML only, with this exact shape:\n\n"
        "claims:\n"
        '  - claim_text: "..."' "\n\n"
        "Do not evaluate support. Do not add claims that are not stated.\n\n"
        "VISIBLE ANSWER BODY:\n"
        "---\n"
        f"{answer_body}\n"
        "---\n"
    )


def _parse_claim_texts(text: str) -> tuple[list[str], tuple[str, ...]]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        data = None
    claims: list[str] = []
    if isinstance(data, dict):
        raw_claims = data.get("claims") or data.get("claim_texts") or []
        if isinstance(raw_claims, list):
            for item in raw_claims:
                if isinstance(item, str):
                    claims.append(item)
                elif isinstance(item, dict) and isinstance(item.get("claim_text"), str):
                    claims.append(item["claim_text"])
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                claims.append(item)
            elif isinstance(item, dict) and isinstance(item.get("claim_text"), str):
                claims.append(item["claim_text"])

    normalized = _dedupe(_normalize_claim(claim) for claim in claims)
    if normalized:
        return normalized, ()
    return [], ("live-extractor-produced-no-parseable-claims",)


def _normalize_claim(claim: str) -> str:
    return " ".join(claim.strip().strip("-*").split())


def _dedupe(claims: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for claim in claims:
        if not isinstance(claim, str) or not claim:
            continue
        key = claim.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(claim)
    return result
