from __future__ import annotations

import argparse
import json
from pathlib import Path

from proposition_authoring.contract_a import emit_not_decomposed
from proposition_authoring.model import AuthoringRequest, SourceRepresentation

CLAIM = "Women had a higher rate than Men."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    request = AuthoringRequest(
        handoff_id="pipeline-prelocal-positive-control",
        producer_id="pipeline-prelocal-test-fixture",
        producer_version="rc1",
        work_id="pipeline-prelocal-positive-control",
        root_id="pipeline-positive-strict-comparison",
        root_text=CLAIM,
        sources=(
            SourceRepresentation(
                source_id="pipeline-positive-source-001",
                media_type="text/plain; charset=utf-8",
                content=CLAIM,
            ),
        ),
        context_source_id=None,
    )
    value = emit_not_decomposed(request)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(value["handoff_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
