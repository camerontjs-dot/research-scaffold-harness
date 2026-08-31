"""Confirm the pre-freeze aperture blobs match the TASK.md git identities."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_INPUT = ROOT / "authority_input"

EXPECTED_GIT_BLOBS = {
    "SPEC-CANDIDATE.json": "9c1090335d87eb5e4885a755542923b453c45317",
    "SPEC-SHAPES.json": "c3f293430ae6ddb87523d83ea6e5380b8b832136",
    "SPEC-PARTICIPANT-BOUNDARY.json": "8b1d292a240300388949d502e7b656e7a23a0b8e",
    "BASIS-BINDING-SPEC.json": "63c952c9c28f1be2173e69c79976c7dfe5880c10",
    "RC3C-SPEC.json": "f05feac88128fd693cca2fb25a0b2951654377eb",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def test_authorized_blobs_match_task_identities() -> None:
    for name, expected in EXPECTED_GIT_BLOBS.items():
        assert git_blob_sha1(AUTHORITY_INPUT / name) == expected
