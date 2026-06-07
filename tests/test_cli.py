"""Tests for fixture builder, CLI commands, and cross-component verification."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from research_scaffold_harness.contracts.yaml_io import load_yaml
from research_scaffold_harness.fixture import FixtureError, build_fixture_write_input
from research_scaffold_harness.prompts import hash_template, load_template

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_CONDITIONS = ("baseline", "format_only", "provenance_scaffold", "full_scaffold")
_VENV_BIN = Path(sys.executable).parent


def _bundler_cmd() -> str:
    return str(_VENV_BIN / "evidence-bundler")


def _bundler_available() -> bool:
    try:
        result = subprocess.run(
            [_bundler_cmd(), "--version"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "research_scaffold_harness.cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Fixture source packet existence
# ---------------------------------------------------------------------------


class TestFixtureSourcePacket:
    def test_fixture_source_packet_exists(self) -> None:
        assert (_FIXTURE_DIR / "task.yaml").exists()
        assert (_FIXTURE_DIR / "sources" / "src-001" / "content.md").exists()

    def test_fixture_task_yaml_parseable(self) -> None:
        data = load_yaml(_FIXTURE_DIR / "task.yaml")
        assert "task_id" in data
        assert "research_question" in data
        assert "domain" in data
        assert "expert_checkable" in data

    def test_fixture_metadata_yaml_parseable(self) -> None:
        meta = load_yaml(_FIXTURE_DIR / "sources" / "src-001" / "metadata.yaml")
        assert meta["source_type"] == "regulatory_guidance"
        assert "title" in meta
        assert "url" in meta


# ---------------------------------------------------------------------------
# build_fixture_write_input unit tests
# ---------------------------------------------------------------------------


class TestBuildFixtureWriteInput:
    def test_invalid_condition_raises(self) -> None:
        with pytest.raises(FixtureError, match="Invalid condition"):
            build_fixture_write_input(_FIXTURE_DIR, "not_a_condition")  # type: ignore[arg-type]

    def test_missing_task_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FixtureError, match="task.yaml not found"):
            build_fixture_write_input(tmp_path / "nonexistent", "baseline")

    def test_invalid_source_metadata_raises(self, tmp_path: Path) -> None:
        task_dir = tmp_path / "source-packet"
        shutil.copytree(_FIXTURE_DIR, task_dir)
        metadata_path = task_dir / "sources" / "src-001" / "metadata.yaml"
        metadata = load_yaml(metadata_path)
        metadata["trust_level"] = "tertiary"
        metadata_path.write_text(
            "\n".join(f"{key}: {value}" for key, value in metadata.items()) + "\n",
            encoding="utf-8",
        )

        with pytest.raises(FixtureError, match="Invalid metadata.yaml"):
            build_fixture_write_input(task_dir, "baseline")

    @pytest.mark.parametrize("condition", _CONDITIONS)
    def test_produces_valid_write_input(self, condition: str) -> None:
        wi = build_fixture_write_input(_FIXTURE_DIR, condition)  # type: ignore[arg-type]
        assert wi.manifest.workflow_condition == condition
        assert wi.manifest.run_id.startswith("fixture-")
        assert len(wi.claims.claims) == 3
        assert len(wi.sources) == 1

    @pytest.mark.parametrize("condition", _CONDITIONS)
    def test_fixture_uses_real_prompt_hash(self, condition: str) -> None:
        wi = build_fixture_write_input(_FIXTURE_DIR, condition)  # type: ignore[arg-type]
        template = load_template(condition)  # type: ignore[arg-type]

        assert wi.manifest.scaffold.prompt_template_id == template.template_id
        assert wi.manifest.scaffold.prompt_template_hash == hash_template(template)
        assert wi.manifest.scaffold.prompt_template_id != "fixture-none"

    def test_baseline_claims_have_no_refs(self) -> None:
        wi = build_fixture_write_input(_FIXTURE_DIR, "baseline")
        for claim in wi.claims.claims:
            assert claim.source_refs == []
            assert claim.support_status == "uncertain"
            assert claim.counterevidence_checked is False

    def test_provenance_claims_have_refs(self) -> None:
        wi = build_fixture_write_input(_FIXTURE_DIR, "provenance_scaffold")
        for claim in wi.claims.claims:
            assert len(claim.source_refs) >= 1
            assert claim.support_status == "sourced"
            assert claim.counterevidence_checked is True

    def test_full_scaffold_has_intermediates(self) -> None:
        wi = build_fixture_write_input(_FIXTURE_DIR, "full_scaffold")
        assert wi.intermediates is not None
        assert wi.manifest.intermediates_present is True

    def test_non_full_conditions_no_intermediates(self) -> None:
        for cond in ("baseline", "format_only", "provenance_scaffold"):
            wi = build_fixture_write_input(_FIXTURE_DIR, cond)  # type: ignore[arg-type]
            assert wi.intermediates is None
            assert wi.manifest.intermediates_present is False


# ---------------------------------------------------------------------------
# write-fixture-run CLI
# ---------------------------------------------------------------------------


class TestWriteFixtureRunCLI:
    @pytest.mark.parametrize("condition", _CONDITIONS)
    def test_write_fixture_run_produces_valid_artifact(
        self, condition: str, tmp_path: Path,
    ) -> None:
        result = _cli(
            "write-fixture-run",
            "--task", str(_FIXTURE_DIR),
            "--condition", condition,
            "--out", str(tmp_path),
        )
        assert result.returncode == 0, result.stderr
        assert "run_id:" in result.stdout
        assert f"condition: {condition}" in result.stdout

        run_dirs = list(tmp_path.glob("scaffold-run-*"))
        assert len(run_dirs) == 1
        run_dir = run_dirs[0]

        assert (run_dir / "scaffold_run.yaml").exists()
        assert (run_dir / "claims.yaml").exists()
        assert (run_dir / "CONTRACT_VERSION").exists()
        assert (run_dir / "SHA256SUMS").exists()
        assert (run_dir / "corpus").is_dir()

    @pytest.mark.parametrize("condition", _CONDITIONS)
    def test_verify_run_passes_on_fixture_output(
        self, condition: str, tmp_path: Path,
    ) -> None:
        write_result = _cli(
            "write-fixture-run",
            "--task", str(_FIXTURE_DIR),
            "--condition", condition,
            "--out", str(tmp_path),
        )
        assert write_result.returncode == 0, write_result.stderr

        run_dir = list(tmp_path.glob("scaffold-run-*"))[0]
        verify_result = _cli("verify-run", str(run_dir))
        assert verify_result.returncode == 0, verify_result.stderr
        assert "PASS" in verify_result.stdout


# ---------------------------------------------------------------------------
# verify-run error detection
# ---------------------------------------------------------------------------


class TestVerifyRunErrors:
    def _make_artifact(self, tmp_path: Path) -> Path:
        result = _cli(
            "write-fixture-run",
            "--task", str(_FIXTURE_DIR),
            "--condition", "provenance_scaffold",
            "--out", str(tmp_path),
        )
        assert result.returncode == 0, result.stderr
        return list(tmp_path.glob("scaffold-run-*"))[0]

    def test_verify_run_fails_on_tampered_content(self, tmp_path: Path) -> None:
        run_dir = self._make_artifact(tmp_path)
        content_files = list((run_dir / "corpus").rglob("content.*"))
        assert content_files
        content_files[0].write_text("tampered content", encoding="utf-8")

        result = _cli("verify-run", str(run_dir))
        assert result.returncode == 1
        assert "FAIL" in result.stderr

    def test_verify_run_fails_on_missing_file(self, tmp_path: Path) -> None:
        run_dir = self._make_artifact(tmp_path)
        (run_dir / "claims.yaml").unlink()

        result = _cli("verify-run", str(run_dir))
        assert result.returncode == 1
        assert "FAIL" in result.stderr


# ---------------------------------------------------------------------------
# Cross-component: evidence-bundler verify-intake
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _bundler_available(),
    reason="evidence-bundler not installed in this environment",
)
class TestCrossComponentVerifyIntake:
    @pytest.mark.parametrize("condition", _CONDITIONS)
    def test_fixture_passes_bundler_verify_intake(
        self, condition: str, tmp_path: Path,
    ) -> None:
        write_result = _cli(
            "write-fixture-run",
            "--task", str(_FIXTURE_DIR),
            "--condition", condition,
            "--out", str(tmp_path),
        )
        assert write_result.returncode == 0, write_result.stderr

        run_dir = list(tmp_path.glob("scaffold-run-*"))[0]
        verify_result = subprocess.run(
            [_bundler_cmd(), "verify-intake", str(run_dir)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert verify_result.returncode == 0, (
            f"evidence-bundler verify-intake failed for {condition}:\n"
            f"stdout: {verify_result.stdout}\n"
            f"stderr: {verify_result.stderr}"
        )
