"""Write a deterministic SHA-256 manifest of the reproduction tree."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_NAMES = {"__pycache__", ".pytest_cache", "MANIFEST.sha256"}
SKIP_SUFFIXES = {".pyc"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_NAMES for part in path.parts):
            continue
        if path.name in SKIP_NAMES or path.suffix in SKIP_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def build_manifest() -> dict[str, str]:
    return {path.relative_to(ROOT).as_posix(): file_sha256(path) for path in iter_files()}


def main() -> None:
    manifest = build_manifest()
    lines = [f"{digest}  {name}" for name, digest in manifest.items()]
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(manifest), "path": "MANIFEST.sha256"}))


if __name__ == "__main__":
    main()
