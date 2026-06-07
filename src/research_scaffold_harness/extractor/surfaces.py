"""Extraction-surface helpers for official and exploratory claim extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionSurfaces:
    """Separated answer surfaces derived from raw model output."""

    official_answer_text: str
    think_block_text: str
    diagnostics: tuple[str, ...]


_THINK_OPEN_RE = re.compile(r"(?is)<think>")
_THINK_CLOSED_RE = re.compile(r"(?is)<think>(.*?)</think>")
_FINAL_ANSWER_RE = re.compile(
    r"(?im)^\s*(?:\*\*)?\s*final\s+answer\s*:?\s*(?:\*\*)?\s*$"
)
_FINAL_CLAIMS_RE = re.compile(
    r"(?im)^\s*(?:\*\*)?\s*final\s+claims\s*:?\s*(?:\*\*)?\s*$"
)
_SCAFFOLD_HEADING_RE = re.compile(
    r"(?i)^\s*(?:#+\s*)?(?:\*\*)?\s*("
    r"answer plan|evidence note table|claim table|disconfirmation pass|"
    r"uncertainty and scope limits|final claim audit table"
    r")\s*:?\s*(?:\*\*)?\s*$"
)


def prepare_extraction_surfaces(raw_output: str) -> ExtractionSurfaces:
    """Return the official answer body and isolated think-block text.

    The official surface excludes chain-of-thought blocks, scaffold-native
    tables, and the ``Final claims:`` footer section. The isolated think-block
    text is preserved for exploratory extraction only.
    """
    without_think, think_text, diagnostics = _strip_think_blocks(raw_output)
    official = _prefer_final_answer_segment(without_think)
    official = _strip_final_claims_section(official)
    official = _strip_scaffold_tables(official)
    official = _normalize_text_block(official)
    return ExtractionSurfaces(
        official_answer_text=official,
        think_block_text=_normalize_text_block(think_text),
        diagnostics=tuple(diagnostics),
    )


def _strip_think_blocks(raw_output: str) -> tuple[str, str, list[str]]:
    diagnostics: list[str] = []
    think_blocks = [match.group(1).strip() for match in _THINK_CLOSED_RE.finditer(raw_output)]
    without_closed = _THINK_CLOSED_RE.sub("\n", raw_output)

    open_match = _THINK_OPEN_RE.search(without_closed)
    if open_match is not None:
        think_blocks.append(without_closed[open_match.end():].strip())
        without_closed = without_closed[:open_match.start()]
        diagnostics.append("unclosed-think-block-stripped")
    elif think_blocks:
        diagnostics.append("think-block-stripped")

    return without_closed, "\n\n".join(block for block in think_blocks if block), diagnostics


def _prefer_final_answer_segment(text: str) -> str:
    matches = list(_FINAL_ANSWER_RE.finditer(text))
    if not matches:
        return text
    return text[matches[-1].end():]


def _strip_final_claims_section(text: str) -> str:
    match = _FINAL_CLAIMS_RE.search(text)
    if match is None:
        return text
    return text[:match.start()]


def _strip_scaffold_tables(text: str) -> str:
    lines: list[str] = []
    skip_scaffold_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if _SCAFFOLD_HEADING_RE.match(stripped):
            skip_scaffold_block = True
            continue
        if skip_scaffold_block:
            if not stripped:
                skip_scaffold_block = False
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _normalize_text_block(text: str) -> str:
    lines = [" ".join(line.strip().split()) for line in text.splitlines()]
    chunks: list[str] = []
    previous_blank = True
    for line in lines:
        if not line:
            if not previous_blank:
                chunks.append("")
            previous_blank = True
            continue
        chunks.append(line)
        previous_blank = False
    return "\n".join(chunks).strip()
