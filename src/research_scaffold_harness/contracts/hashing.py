"""Deterministic SHA-256 hashing for C-A artifact integrity.

The corpus hash algorithm must produce output identical to Evidence Bundler's
``compute_corpus_hash`` so that downstream ``verify-intake`` passes.
"""

from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path

SHA256_PREFIX = "sha256:"


def sha256_hexdigest(data: bytes) -> str:
    """Return the SHA-256 hex digest for bytes."""
    return sha256(data).hexdigest()


def sha256_value(data: bytes) -> str:
    """Return a contract-shaped SHA-256 value for bytes."""
    return f"{SHA256_PREFIX}{sha256_hexdigest(data)}"


def hash_text(text: str) -> str:
    """Return a contract-shaped SHA-256 value for UTF-8 text."""
    return sha256_value(text.encode("utf-8"))


def hash_file(path: Path) -> str:
    """Return a contract-shaped SHA-256 value for a file's exact bytes."""
    return sha256_value(path.read_bytes())


def hash_file_hex(path: Path) -> str:
    """Return a raw SHA-256 hex digest for a file's exact bytes."""
    return sha256_hexdigest(path.read_bytes())


def iter_handoff_files(root: Path, *, exclude_names: Iterable[str] = ("SHA256SUMS",)) -> list[Path]:
    """Return sorted handoff files beneath root, excluding names such as SHA256SUMS."""
    excluded = set(exclude_names)
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in excluded and "deviations" not in path.parts
    )


def compute_directory_hash(root: Path) -> str:
    """Hash a directory tree from sorted relative paths and file digests."""
    hasher = sha256()
    for path in iter_handoff_files(root, exclude_names=()):
        rel = path.relative_to(root).as_posix()
        digest = hash_file_hex(path)
        hasher.update(f"{rel}\0{digest}\n".encode())
    return f"{SHA256_PREFIX}{hasher.hexdigest()}"


def compute_corpus_hash(corpus_dir: Path) -> str:
    """Compute the C-A corpus_hash from the corpus/ directory tree only."""
    return compute_directory_hash(corpus_dir)


def write_sha256sums(root: Path) -> Path:
    """Write SHA256SUMS for every handoff file under root except SHA256SUMS itself."""
    lines = []
    for path in iter_handoff_files(root):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{hash_file_hex(path)}  {rel}")
    sums_path = root / "SHA256SUMS"
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


def verify_sha256sums(root: Path) -> list[str]:
    """Return mismatch messages for SHA256SUMS, or an empty list if it verifies."""
    sums_path = root / "SHA256SUMS"
    if not sums_path.exists():
        return ["SHA256SUMS file missing"]

    errors: list[str] = []
    expected_paths: set[str] = set()
    for line_number, line in enumerate(sums_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected_hash, rel = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"SHA256SUMS line {line_number} is malformed")
            continue
        expected_paths.add(rel)
        target = root / rel
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {rel}")
            continue
        actual_hash = hash_file_hex(target)
        if actual_hash != expected_hash:
            errors.append(f"SHA256SUMS mismatch for {rel}")

    actual_paths = {path.relative_to(root).as_posix() for path in iter_handoff_files(root)}
    missing_from_sums = sorted(actual_paths - expected_paths)
    if missing_from_sums:
        errors.append(f"SHA256SUMS missing entries: {', '.join(missing_from_sums)}")
    return errors
