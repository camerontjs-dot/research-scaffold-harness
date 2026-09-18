#!/usr/bin/env python3
"""Create a deterministic byte snapshot of a directory for provenance retention."""

from __future__ import annotations

import argparse
import hashlib
import stat
import zipfile
from pathlib import Path

FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("source_dir", type=Path)
    p.add_argument("output_zip", type=Path)
    args = p.parse_args()

    src = args.source_dir.resolve()
    if not src.is_dir():
        raise SystemExit(f"not a directory: {src}")
    out = args.output_zip.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in src.rglob("*") if p.is_file())
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED) as zf:
        for path in files:
            rel = path.relative_to(src).as_posix()
            info = zipfile.ZipInfo(rel, date_time=FIXED_TIME)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            zf.writestr(info, path.read_bytes())

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"sha256:{digest}  {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
