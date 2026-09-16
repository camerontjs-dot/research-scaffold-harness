from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

CAMPAIGN = "cal_pipeline_v1_prototype_freeze_rc0"


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def json_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-root", type=Path, default=Path("build"))
    args = parser.parse_args()
    build_root = args.build_root.resolve()
    evidence = build_root / CAMPAIGN
    result_path = evidence / "RESULT.json"
    if not result_path.exists():
        raise SystemExit("no RESULT.json to package")

    # The RC0 runner initially attempted to record its own archive digest inside
    # the archive, which is a circular identity. Preserve no such self-reference.
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result.pop("evidence_package", None)
    json_write(result_path, result)

    file_hashes = hashes(evidence)
    hash_path = build_root / f"{CAMPAIGN}-FILE_HASHES.json"
    json_write(hash_path, file_hashes)

    archive_path = build_root / f"{CAMPAIGN}.tar.gz"
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                used: set[str] = set()
                for path in sorted(evidence.rglob("*")):
                    if not path.is_file():
                        continue
                    rel = path.relative_to(evidence).as_posix().replace(":", "_")
                    if rel in used:
                        raise RuntimeError(f"archive collision after safe-name normalization: {rel}")
                    used.add(rel)
                    info = tar.gettarinfo(str(path), arcname=rel)
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with path.open("rb") as handle:
                        tar.addfile(info, handle)

    archive_sha = sha256_bytes(archive_path.read_bytes())
    digest_path = build_root / f"{CAMPAIGN}-ARCHIVE_SHA256.txt"
    digest_path.write_text(archive_sha + "\n", encoding="utf-8")
    package = {
        "schema": "cal-pipeline-v1-evidence-package-v1",
        "archive": archive_path.name,
        "archive_sha256": archive_sha,
        "file_hash_manifest": hash_path.name,
        "archive_digest_file": digest_path.name,
        "file_count": len(file_hashes),
        "result_sha256": file_hashes.get("RESULT.json"),
        "self_referential_archive_identity": False,
    }
    package_path = build_root / f"{CAMPAIGN}-PACKAGE.json"
    json_write(package_path, package)
    print(json.dumps(package, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
