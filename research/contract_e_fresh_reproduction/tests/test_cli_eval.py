from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path

from research.contract_e_fresh_reproduction.cli import main
from research.contract_e_fresh_reproduction.tests.helpers import source_case


def test_cli_accepts_happy_path() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "case.json"
        path.write_text(json.dumps(source_case()), encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main([str(path)])
        payload = json.loads(buf.getvalue())
        assert code == 0
        assert payload["outcome"] == "accept"
