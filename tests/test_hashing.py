"""Hashing tests — Phase 1 Unit 5."""

from __future__ import annotations

import hashlib

from research_scaffold_harness.contracts.hashing import (
    compute_corpus_hash,
    hash_file,
    hash_file_hex,
    hash_text,
    iter_handoff_files,
    sha256_value,
    verify_sha256sums,
    write_sha256sums,
)


def test_sha256_value_format() -> None:
    result = sha256_value(b"hello")
    assert result.startswith("sha256:")
    assert len(result) == len("sha256:") + 64
    assert all(c in "0123456789abcdef" for c in result[7:])


def test_sha256_value_matches_stdlib() -> None:
    data = b"test data"
    expected = "sha256:" + hashlib.sha256(data).hexdigest()
    assert sha256_value(data) == expected


def test_hash_text_known_digest() -> None:
    result = hash_text("hello")
    expected = "sha256:" + hashlib.sha256(b"hello").hexdigest()
    assert result == expected


def test_hash_file_matches_content(tmp_path) -> None:
    path = tmp_path / "file.txt"
    path.write_bytes(b"file content")
    expected = "sha256:" + hashlib.sha256(b"file content").hexdigest()
    assert hash_file(path) == expected


def test_hash_file_hex_no_prefix(tmp_path) -> None:
    path = tmp_path / "file.txt"
    path.write_bytes(b"data")
    result = hash_file_hex(path)
    assert not result.startswith("sha256:")
    assert result == hashlib.sha256(b"data").hexdigest()


def test_iter_handoff_files_excludes_sha256sums(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("a: 1\n")
    (tmp_path / "b.yaml").write_text("b: 2\n")
    (tmp_path / "SHA256SUMS").write_text("fake\n")
    files = iter_handoff_files(tmp_path)
    names = [f.name for f in files]
    assert "SHA256SUMS" not in names
    assert "a.yaml" in names
    assert "b.yaml" in names


def test_iter_handoff_files_excludes_deviations(tmp_path) -> None:
    (tmp_path / "top.yaml").write_text("x: 1\n")
    dev_dir = tmp_path / "deviations"
    dev_dir.mkdir()
    (dev_dir / "dev.yaml").write_text("d: 1\n")
    files = iter_handoff_files(tmp_path)
    names = [f.name for f in files]
    assert "top.yaml" in names
    assert "dev.yaml" not in names


def test_iter_handoff_files_sorted(tmp_path) -> None:
    (tmp_path / "z.yaml").write_text("z\n")
    sub = tmp_path / "a_dir"
    sub.mkdir()
    (sub / "inner.yaml").write_text("i\n")
    (tmp_path / "m.yaml").write_text("m\n")
    files = iter_handoff_files(tmp_path)
    rel_paths = [f.relative_to(tmp_path).as_posix() for f in files]
    assert rel_paths == sorted(rel_paths)


def _make_corpus(tmp_path) -> None:
    """Create a minimal corpus tree for hashing tests."""
    src = tmp_path / "src-001"
    src.mkdir()
    (src / "content.md").write_text("Source content here.\n", encoding="utf-8")
    (src / "metadata.yaml").write_text("source_id: src-001\n", encoding="utf-8")
    (src / "passages.yaml").write_text("passages: []\n", encoding="utf-8")


def test_compute_corpus_hash_deterministic(tmp_path) -> None:
    _make_corpus(tmp_path)
    h1 = compute_corpus_hash(tmp_path)
    h2 = compute_corpus_hash(tmp_path)
    assert h1 == h2
    assert h1.startswith("sha256:")
    assert len(h1) == 71


def test_compute_corpus_hash_changes_on_content_change(tmp_path) -> None:
    _make_corpus(tmp_path)
    h1 = compute_corpus_hash(tmp_path)
    (tmp_path / "src-001" / "content.md").write_text("Changed.\n", encoding="utf-8")
    h2 = compute_corpus_hash(tmp_path)
    assert h1 != h2


def test_compute_corpus_hash_changes_on_file_add(tmp_path) -> None:
    _make_corpus(tmp_path)
    h1 = compute_corpus_hash(tmp_path)
    (tmp_path / "src-001" / "extra.txt").write_text("extra\n", encoding="utf-8")
    h2 = compute_corpus_hash(tmp_path)
    assert h1 != h2


def test_write_sha256sums_format(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("a: 1\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("b: 2\n", encoding="utf-8")
    sums_path = write_sha256sums(tmp_path)
    assert sums_path.name == "SHA256SUMS"
    content = sums_path.read_text(encoding="utf-8")
    lines = [line for line in content.splitlines() if line.strip()]
    assert len(lines) == 2
    for line in lines:
        parts = line.split(maxsplit=1)
        assert len(parts) == 2
        hex_part, rel = parts
        assert len(hex_part) == 64
        assert "  " in line  # two-space separator in original line


def test_verify_sha256sums_passes_intact(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("content\n", encoding="utf-8")
    write_sha256sums(tmp_path)
    errors = verify_sha256sums(tmp_path)
    assert errors == []


def test_verify_sha256sums_detects_tampered_file(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("original\n", encoding="utf-8")
    write_sha256sums(tmp_path)
    (tmp_path / "a.yaml").write_text("tampered\n", encoding="utf-8")
    errors = verify_sha256sums(tmp_path)
    assert any("mismatch" in e for e in errors)


def test_verify_sha256sums_reports_missing_file(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("content\n", encoding="utf-8")
    write_sha256sums(tmp_path)
    (tmp_path / "a.yaml").unlink()
    errors = verify_sha256sums(tmp_path)
    assert any("missing file" in e for e in errors)


def test_verify_sha256sums_reports_unlisted_file(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text("content\n", encoding="utf-8")
    write_sha256sums(tmp_path)
    (tmp_path / "b.yaml").write_text("new file\n", encoding="utf-8")
    errors = verify_sha256sums(tmp_path)
    assert any("missing entries" in e for e in errors)


def test_verify_sha256sums_missing_sums_file(tmp_path) -> None:
    errors = verify_sha256sums(tmp_path)
    assert errors == ["SHA256SUMS file missing"]
