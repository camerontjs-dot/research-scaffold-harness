"""C-A writer tests — Phase 1 Unit 6."""

from __future__ import annotations

from pathlib import Path

import pytest

from research_scaffold_harness.contracts.hashing import (
    compute_corpus_hash,
    hash_file,
    verify_sha256sums,
)
from research_scaffold_harness.contracts.writer import (
    CAWriteInput,
    CAWriterError,
    IntermediatesWriteInput,
    SidecarTextWriteInput,
    SourceWriteInput,
    write_scaffold_run,
)
from research_scaffold_harness.contracts.yaml_io import load_model_yaml
from research_scaffold_harness.models.ca import (
    ClaimsRegistry,
    ScaffoldClaim,
    ScaffoldPassage,
    ScaffoldRunManifest,
    SourceMetadata,
    SourcePassages,
)
from research_scaffold_harness.models.common import WRITER_SCHEMA_VERSION

_HASH = "sha256:" + "a" * 64


def _make_content_file(tmp_path: Path, text: str = "Source content.\n") -> Path:
    path = tmp_path / "source_content.md"
    path.write_text(text, encoding="utf-8")
    return path


def _make_write_input(
    tmp_path: Path,
    *,
    n_sources: int = 1,
    with_intermediates: bool = False,
    content_text: str = "Source content.\n",
) -> CAWriteInput:
    """Build a valid CAWriteInput with pre-computed hashes."""
    sources: list[SourceWriteInput] = []
    for i in range(n_sources):
        source_id = f"src-{i + 1:03d}"
        content_path = tmp_path / f"content_{source_id}.md"
        content_path.write_text(content_text, encoding="utf-8")
        content_hash = hash_file(content_path)

        passage = ScaffoldPassage.model_validate({
            "passage_id": f"p-{i + 1:03d}",
            "paragraph_index": 0,
            "char_start": 0,
            "char_end": len(content_text),
            "text_preview": content_text[:20].strip(),
            "extraction_method": "scaffold_cited",
        })

        metadata = SourceMetadata.model_validate({
            "source_id": source_id,
            "schema_version": WRITER_SCHEMA_VERSION,
            "bibliographic": {
                "source_type": "journal_article",
                "title": f"Source {i + 1}",
                "url": f"https://example.com/{source_id}",
                "access_date_utc": "2026-05-17T00:00:00Z",
            },
            "trust_level": "primary",
            "content_hash": content_hash,
            "retrieval": {
                "retrieval_query": "test query",
                "retrieval_rank": 1,
            },
        })

        passages = SourcePassages.model_validate({
            "source_id": source_id,
            "schema_version": WRITER_SCHEMA_VERSION,
            "passages": [passage.model_dump(mode="json")],
        })

        sources.append(SourceWriteInput(
            source_id=source_id,
            content_path=content_path,
            metadata=metadata,
            passages=passages,
        ))

    corpus_hash = _precompute_corpus_hash(tmp_path, sources, content_text)

    claim = ScaffoldClaim.model_validate({
        "claim_id": "c-001",
        "claim_type": "extracted_claim",
        "claim_text": "Test claim",
        "support_status": "sourced",
        "claim_strength": 0.8,
        "extraction_fidelity": 0.9,
        "source_refs": [{"source_id": "src-001", "passage_id": "p-001"}],
        "counterevidence_checked": True,
        "counterevidence_found": False,
        "downgraded": False,
    })

    claims = ClaimsRegistry.model_validate({
        "schema_version": WRITER_SCHEMA_VERSION,
        "run_id": "run-001",
        "generated_at_utc": "2026-05-17T00:00:00Z",
        "claims": [claim.model_dump(mode="json")],
    })

    manifest = ScaffoldRunManifest.model_validate({
        "run_id": "run-001",
        "task_id": "task-001",
        "workflow_condition": "full_scaffold",
        "timestamp_utc": "2026-05-17T00:00:00Z",
        "scaffold": {
            "version": "0.1.0",
            "prompt_template_id": "tpl-001",
            "prompt_template_hash": _HASH,
            "config_hash": _HASH,
        },
        "model": {
            "model_id": "test-model",
            "model_version": "1.0",
            "api_endpoint": "http://localhost",
            "temperature": 0.0,
            "max_tokens": 4096,
        },
        "task": {
            "research_question": "Does X cause Y?",
            "domain": "pharmacology",
            "expert_checkable": True,
        },
        "corpus": {
            "total_sources": n_sources,
            "corpus_hash": corpus_hash,
            "retrieval_strategy": "semantic_search",
            "retrieval_timestamp_utc": "2026-05-17T00:00:00Z",
        },
        "intermediates_present": with_intermediates,
        "run_metadata": {"operator": "test", "environment": "ci"},
    })

    intermediates = None
    if with_intermediates:
        intermediates = IntermediatesWriteInput(
            disconfirmation_pass={"checked": ["c-001"], "result": "none_found"},
            claim_table_draft={"claims": [{"id": "c-001", "status": "sourced"}]},
        )

    return CAWriteInput(
        manifest=manifest,
        claims=claims,
        sources=sources,
        intermediates=intermediates,
    )


def _precompute_corpus_hash(
    tmp_path: Path, sources: list[SourceWriteInput], content_text: str
) -> str:
    """Build a temporary corpus tree to compute the expected hash."""
    scratch = tmp_path / "_corpus_hash_scratch"
    scratch.mkdir()
    for source in sources:
        sd = scratch / source.source_id
        sd.mkdir()
        (sd / f"content{source.content_path.suffix}").write_text(
            content_text, encoding="utf-8"
        )
        from research_scaffold_harness.contracts.yaml_io import write_model_yaml

        write_model_yaml(source.metadata, sd / "metadata.yaml", exclude_none=True)
        write_model_yaml(source.passages, sd / "passages.yaml", exclude_none=True)
    return compute_corpus_hash(scratch)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_produces_expected_directory_structure(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)

    assert run_dir.name == "scaffold-run-run-001"
    assert (run_dir / "scaffold_run.yaml").is_file()
    assert (run_dir / "claims.yaml").is_file()
    assert (run_dir / "CONTRACT_VERSION").is_file()
    assert (run_dir / "SHA256SUMS").is_file()
    assert (run_dir / "corpus" / "src-001" / "content.md").is_file()
    assert (run_dir / "corpus" / "src-001" / "metadata.yaml").is_file()
    assert (run_dir / "corpus" / "src-001" / "passages.yaml").is_file()


def test_scaffold_run_yaml_valid_model(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    loaded = load_model_yaml(ScaffoldRunManifest, run_dir / "scaffold_run.yaml")
    assert loaded.run_id == "run-001"


def test_claims_yaml_valid_model(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    loaded = load_model_yaml(ClaimsRegistry, run_dir / "claims.yaml")
    assert loaded.run_id == "run-001"
    assert len(loaded.claims) == 1


def test_source_metadata_yaml_valid_model(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    loaded = load_model_yaml(
        SourceMetadata, run_dir / "corpus" / "src-001" / "metadata.yaml"
    )
    assert loaded.source_id == "src-001"


def test_source_passages_yaml_valid_model(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    loaded = load_model_yaml(
        SourcePassages, run_dir / "corpus" / "src-001" / "passages.yaml"
    )
    assert loaded.source_id == "src-001"
    assert len(loaded.passages) == 1


def test_content_file_copied(tmp_path) -> None:
    content_text = "Unique test content.\n"
    write_input = _make_write_input(tmp_path, content_text=content_text)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    copied = (run_dir / "corpus" / "src-001" / "content.md").read_text(encoding="utf-8")
    assert copied == content_text


def test_contract_version_file_content(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    version = (run_dir / "CONTRACT_VERSION").read_text(encoding="utf-8").strip()
    assert version == "1.0.0"


def test_sha256sums_verifies_clean(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    errors = verify_sha256sums(run_dir)
    assert errors == []


def test_corpus_hash_matches_manifest(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    actual = compute_corpus_hash(run_dir / "corpus")
    assert actual == write_input.manifest.corpus.corpus_hash


def test_content_hash_matches_metadata(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    actual = hash_file(run_dir / "corpus" / "src-001" / "content.md")
    assert actual == write_input.sources[0].metadata.content_hash


def test_intermediates_written_when_provided(tmp_path) -> None:
    write_input = _make_write_input(tmp_path, with_intermediates=True)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    assert (run_dir / "intermediates" / "disconfirmation_pass.yaml").is_file()
    assert (run_dir / "intermediates" / "claim_table_draft.yaml").is_file()


def test_intermediates_absent_when_none(tmp_path) -> None:
    write_input = _make_write_input(tmp_path, with_intermediates=False)
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)
    assert not (run_dir / "intermediates").exists()


def test_sidecar_written_and_covered_by_sha256sums(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    write_input = CAWriteInput(
        manifest=write_input.manifest,
        claims=write_input.claims,
        sources=write_input.sources,
        sidecars=[
            SidecarTextWriteInput(
                relative_path="raw_output.txt",
                text="Exact raw output without added terminator",
            )
        ],
    )
    out = tmp_path / "out"
    out.mkdir()
    run_dir = write_scaffold_run(write_input, out)

    assert (run_dir / "raw_output.txt").read_text(encoding="utf-8") == (
        "Exact raw output without added terminator"
    )
    assert verify_sha256sums(run_dir) == []
    assert "raw_output.txt" in (run_dir / "SHA256SUMS").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_raises_on_content_hash_mismatch(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    # Tamper the content file after hash was computed
    write_input.sources[0].content_path.write_text("tampered!\n", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError, match="content_hash mismatch"):
        write_scaffold_run(write_input, out)


def test_raises_on_corpus_hash_mismatch(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    # Replace manifest with a wrong corpus_hash
    bad_manifest_data = write_input.manifest.model_dump(mode="json")
    bad_manifest_data["corpus"]["corpus_hash"] = "sha256:" + "f" * 64
    bad_manifest = ScaffoldRunManifest.model_validate(bad_manifest_data)
    bad_input = CAWriteInput(
        manifest=bad_manifest,
        claims=write_input.claims,
        sources=write_input.sources,
    )
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError, match="corpus_hash mismatch"):
        write_scaffold_run(bad_input, out)


def test_raises_on_dangling_source_ref(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    # Add a claim with a source_ref to a nonexistent source
    bad_claim_data = {
        "claim_id": "c-bad",
        "claim_type": "extracted_claim",
        "claim_text": "Bad claim",
        "support_status": "sourced",
        "claim_strength": 0.5,
        "extraction_fidelity": 0.5,
        "source_refs": [{"source_id": "src-999", "passage_id": "p-999"}],
        "counterevidence_checked": False,
        "counterevidence_found": False,
        "downgraded": False,
    }
    bad_claims_data = write_input.claims.model_dump(mode="json")
    bad_claims_data["claims"].append(bad_claim_data)
    bad_claims = ClaimsRegistry.model_validate(bad_claims_data)
    bad_input = CAWriteInput(
        manifest=write_input.manifest,
        claims=bad_claims,
        sources=write_input.sources,
    )
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError, match="references missing passage"):
        write_scaffold_run(bad_input, out)


def test_raises_on_total_sources_mismatch(tmp_path) -> None:
    write_input = _make_write_input(tmp_path, n_sources=1)
    # Forge manifest to claim 5 sources
    bad_data = write_input.manifest.model_dump(mode="json")
    bad_data["corpus"]["total_sources"] = 5
    bad_manifest = ScaffoldRunManifest.model_validate(bad_data)
    bad_input = CAWriteInput(
        manifest=bad_manifest,
        claims=write_input.claims,
        sources=write_input.sources,
    )
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError, match="total_sources mismatch"):
        write_scaffold_run(bad_input, out)


def test_raises_on_missing_content_file(tmp_path) -> None:
    write_input = _make_write_input(tmp_path)
    # Delete the content file
    write_input.sources[0].content_path.unlink()
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError, match="Content file missing"):
        write_scaffold_run(write_input, out)


@pytest.mark.parametrize(
    "relative_path",
    (
        "../escape.txt",
        "/tmp/escape.txt",
        "corpus/src-001/extra.txt",
        "claims.yaml",
        "SHA256SUMS",
    ),
)
def test_rejects_unsafe_sidecar_paths(tmp_path, relative_path: str) -> None:
    write_input = _make_write_input(tmp_path)
    bad_input = CAWriteInput(
        manifest=write_input.manifest,
        claims=write_input.claims,
        sources=write_input.sources,
        sidecars=[SidecarTextWriteInput(relative_path=relative_path, text="bad")],
    )
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(CAWriterError):
        write_scaffold_run(bad_input, out)
