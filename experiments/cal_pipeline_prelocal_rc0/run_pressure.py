from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

CLAIM = "Women had a higher rate than Men."


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_write(path: Path, value: Any, *, pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    else:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def dir_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class Runner:
    def __init__(self, logs: Path):
        self.logs = logs
        self.logs.mkdir(parents=True, exist_ok=True)
        self.index = 0

    def run(
        self,
        label: str,
        cmd: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        expect: int | None = 0,
        input_bytes: bytes | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        self.index += 1
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=merged_env,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        prefix = self.logs / f"{self.index:03d}-{label}"
        prefix.with_suffix(".stdout").write_bytes(result.stdout)
        prefix.with_suffix(".stderr").write_bytes(result.stderr)
        prefix.with_suffix(".command.txt").write_text(
            "cwd=" + (str(cwd) if cwd else str(Path.cwd())) + "\n" + " ".join(cmd) + "\n",
            encoding="utf-8",
        )
        if expect is not None and result.returncode != expect:
            raise RuntimeError(
                f"{label}: expected exit {expect}, got {result.returncode}; "
                f"stderr={result.stderr.decode('utf-8', 'replace')[:1000]}"
            )
        return result

    def rejects(self, label: str, cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
        result = self.run(label, cmd, cwd=cwd, expect=None)
        if result.returncode == 0:
            raise RuntimeError(f"{label}: hostile control unexpectedly succeeded")
        return result


def git_head(runner: Runner, path: Path) -> str:
    return runner.run("git-head-" + path.name, ["git", "rev-parse", "HEAD"], cwd=path).stdout.decode().strip()


def decision_cmd(
    node: str,
    decision_root: Path,
    c2_path: Path,
    c2_sha: str,
    c2_root: Path,
    d_root: Path,
    expected_b: Path,
    context: Path,
    cal_python: str,
) -> list[str]:
    return [
        node,
        str(decision_root / "scripts/decision-engine-evaluate-c2.mjs"),
        "--contract-c2",
        str(c2_path),
        "--contract-c2-sha256",
        c2_sha,
        "--contract-c2-authority",
        str(c2_root),
        "--contract-d-authority",
        str(d_root),
        "--expected-contract-b",
        str(expected_b),
        "--policy",
        "decision-engine.contract-c.supported-claim-verification@1.0.0",
        "--context",
        str(context),
        "--python",
        cal_python,
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    exp = root / "experiments/cal_pipeline_prelocal_rc0"
    manifest = json.loads((exp / "MANIFEST.json").read_text(encoding="utf-8"))
    out = root / "build/cal_pipeline_prelocal_rc0"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    runner = Runner(out / "logs")
    result: dict[str, Any] = {
        "schema": "cal-pipeline-prelocal-pressure-result-v1",
        "manifest": manifest,
        "stages": {},
        "controls": {},
        "irregularities": [],
    }

    cg = root / "deps/claimgate"
    eb = root / "deps/eb"
    cal = root / "deps/cal"
    c2 = root / "deps/apparatus-c2"
    decision = root / "deps/decision"
    droot = root / "deps/apparatus-d"
    eroot = root / "deps/apparatus-e"
    cg_python = str((root / ".venv-cg/bin/python").resolve())
    eb_python = str((root / ".venv-eb/bin/python").resolve())
    cal_python = str((root / ".venv-cal/bin/python").resolve())
    cg_cli = str((root / ".venv-cg/bin/proposition-authoring").resolve())
    cal_cli = str((root / ".venv-cal/bin/claim-audit-v1").resolve())
    node = shutil.which("node") or "node"

    try:
        # 0. Exact authority manifest.
        expected_heads = {
            cg: manifest["subjects"]["claimgate"]["commit"],
            eb: manifest["subjects"]["evidence_bundler"]["frozen_head"],
            cal: manifest["subjects"]["cal"]["records_head"],
            c2: manifest["subjects"]["contract_c2"]["promotion_head"],
            decision: manifest["subjects"]["decision"]["c2_integration_head"],
            droot: manifest["subjects"]["decision"]["contract_d_authority"],
            eroot: manifest["subjects"]["contract_e"]["research_head"],
        }
        observed_heads = {path.name: git_head(runner, path) for path in expected_heads}
        for path, expected in expected_heads.items():
            observed = git_head(runner, path)
            if observed != expected:
                raise RuntimeError(f"authority drift for {path}: {observed} != {expected}")
        result["stages"]["authority_manifest"] = {"status": "PASS", "heads": observed_heads}

        # 1. Raw claim -> ClaimGate -> Contract A.
        inputs = out / "inputs"
        canary_request = {
            "handoff_id": "pipeline-prelocal-canary-001",
            "producer_id": "pipeline-prelocal-pressure",
            "producer_version": "rc0",
            "work_id": "pipeline-prelocal-canary-001",
            "root_id": "pipeline-canary-claim-001",
            "root_text": CLAIM,
            "sources": [
                {
                    "source_id": "pipeline-canary-source-001",
                    "media_type": "text/plain; charset=utf-8",
                    "content": CLAIM,
                }
            ],
        }
        request_path = inputs / "canary-request.json"
        json_write(request_path, canary_request)
        cg_out = out / "claimgate"
        cg_out.mkdir()
        receipt_path = cg_out / "receipt.json"
        contract_a_path = cg_out / "contract_a.json"
        cg_run = runner.run(
            "claimgate-canary",
            [
                cg_cli,
                "author",
                str(request_path),
                "--receipt",
                str(receipt_path),
                "--contract-a",
                str(contract_a_path),
            ],
            cwd=cg,
        )
        if not contract_a_path.exists():
            raise RuntimeError("ClaimGate canary produced no authoritative Contract A")
        contract_a = json.loads(contract_a_path.read_text(encoding="utf-8"))
        if contract_a["root_proposition"]["text"] != CLAIM:
            raise RuntimeError("ClaimGate changed canary root proposition text")
        result["stages"]["claimgate"] = {
            "status": "PASS",
            "stdout": cg_run.stdout.decode("utf-8", "replace").strip(),
            "root_id": contract_a["root_proposition"]["proposition_id"],
            "contract_a_sha256": sha256_bytes(contract_a_path.read_bytes()),
        }

        a_validator = c2 / "validators/contract_a_rc2.py"
        runner.run("contract-a-external-validation", [cal_python, str(a_validator), str(contract_a_path)])
        result["stages"]["contract_a"] = {"status": "PASS", "version": "2.0.0"}

        tampered_a = json.loads(contract_a_path.read_text(encoding="utf-8"))
        tampered_a["root_proposition"]["text"] = CLAIM + " tampered"
        tampered_a_path = cg_out / "contract_a.stale-root.json"
        json_write(tampered_a_path, tampered_a)
        runner.rejects("contract-a-stale-root-validator", [cal_python, str(a_validator), str(tampered_a_path)])
        result["controls"]["contract_a_stale_root_rejected"] = True

        # 2. Contract A -> EB seed -> explicit test admission -> B1.2.
        carrier = eb / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
        eb_seed = out / "eb-seed"
        eb_script = eb / "scripts/run_v1_integration_candidate.py"
        runner.run(
            "eb-seed",
            [eb_python, str(eb_script), str(contract_a_path), "--compatibility-carrier", str(carrier), "--out-dir", str(eb_seed)],
            cwd=eb,
        )
        seed_package = json.loads((eb_seed / "native_eb_v1_package.json").read_text(encoding="utf-8"))
        retained = [row for row in seed_package["candidates"] if row["selection_state"] == "retained"]
        if not retained:
            raise RuntimeError("EB positive canary retained no candidates")
        admission = {
            "schema": "evidence-bundler-admission-v1",
            "decisions": [
                {
                    "proposition_id": row["proposition_id"],
                    "passage_id": row["passage_id"],
                    "decision": "accepted",
                }
                for row in retained
            ],
        }
        admission_path = inputs / "admission.json"
        json_write(admission_path, admission)
        eb_final = out / "eb-final"
        eb_replay = out / "eb-replay"
        eb_base_cmd = [
            eb_python,
            str(eb_script),
            str(contract_a_path),
            "--admission",
            str(admission_path),
            "--compatibility-carrier",
            str(carrier),
        ]
        runner.run("eb-final", [*eb_base_cmd, "--out-dir", str(eb_final)], cwd=eb)
        runner.run("eb-replay", [*eb_base_cmd, "--out-dir", str(eb_replay)], cwd=eb)
        final_package = json.loads((eb_final / "native_eb_v1_package.json").read_text(encoding="utf-8"))
        if final_package["config"]["candidate_depth"] != 10 or final_package["config"]["retained_k"] != 3:
            raise RuntimeError("EB integration profile drifted from 10/3")
        if final_package["contract_a"]["root_proposition"]["text"] != CLAIM:
            raise RuntimeError("EB changed authoritative proposition text")
        if dir_hashes(eb_final) != dir_hashes(eb_replay):
            raise RuntimeError("EB exact replay drift")
        result["stages"]["evidence_bundler"] = {
            "status": "PASS",
            "profile": "eb-v1-integration-10x3-rc0",
            "retained_count": len(retained),
            "accepted_by_test_harness": len(admission["decisions"]),
            "replay_identical": True,
            "native_package_sha256": final_package["package_sha256"],
        }
        bad_eb_dir = out / "eb-tampered-a"
        runner.rejects(
            "eb-rejects-stale-contract-a",
            [eb_python, str(eb_script), str(tampered_a_path), "--compatibility-carrier", str(carrier), "--out-dir", str(bad_eb_dir)],
            cwd=eb,
        )
        result["controls"]["eb_rejects_tampered_contract_a"] = True

        # 3. B1.2 -> current CAL integration candidate.
        claim_id = contract_a["root_proposition"]["proposition_id"]
        target = {
            "claim_id": claim_id,
            "proposition": {
                "proposition_id": claim_id,
                "text_sha256": sha256_text(CLAIM),
                "semantic_family": "strict_comparison",
                "fields": {
                    "lhs_entity": "Women",
                    "rhs_entity": "Men",
                    "comparison_direction": "MORE_THAN",
                },
            },
        }
        target_path = inputs / "cal-target.json"
        json_write(target_path, target)
        bundle_dir = eb_final / "contract_b"
        runner.run("cal-validate-bundle", [cal_cli, "validate-bundle", str(bundle_dir), str(target_path)], cwd=cal)
        cal_run1 = out / "cal-run-1"
        cal_run2 = out / "cal-run-2"
        runner.run("cal-run-1", [cal_cli, "run-bundle", str(bundle_dir), str(target_path), "--out-dir", str(cal_run1)], cwd=cal)
        runner.run("cal-run-2", [cal_cli, "run-bundle", str(bundle_dir), str(target_path), "--out-dir", str(cal_run2)], cwd=cal)
        if dir_hashes(cal_run1) != dir_hashes(cal_run2):
            raise RuntimeError("CAL exact replay drift")
        cal_result = json.loads((cal_run1 / "result.json").read_text(encoding="utf-8"))
        if cal_result["result"]["conclusion"] != "supported":
            raise RuntimeError(f"positive canary did not support in current CAL: {cal_result['result']}")
        result["stages"]["cal"] = {
            "status": "PASS",
            "conclusion": cal_result["result"]["conclusion"],
            "failure_code": cal_result["result"]["failure_code"],
            "semantic_implementation_sha": cal_result["semantic_implementation_sha"],
            "replay_identical": True,
        }
        stale_target = json.loads(target_path.read_text(encoding="utf-8"))
        stale_target["proposition"]["text_sha256"] = "0" * 64
        stale_target_path = inputs / "cal-target.stale-hash.json"
        json_write(stale_target_path, stale_target)
        runner.rejects("cal-rejects-stale-text-hash", [cal_cli, "validate-bundle", str(bundle_dir), str(stale_target_path)], cwd=cal)
        alias_target = json.loads(target_path.read_text(encoding="utf-8"))
        alias_target["proposition"]["proposition_id"] = "alias-id"
        alias_target_path = inputs / "cal-target.alias-id.json"
        json_write(alias_target_path, alias_target)
        runner.rejects("cal-rejects-aliased-id", [cal_cli, "validate-bundle", str(bundle_dir), str(alias_target_path)], cwd=cal)
        runner.rejects("cal-refuses-nonempty-output", [cal_cli, "run-bundle", str(bundle_dir), str(target_path), "--out-dir", str(cal_run1)], cwd=cal)
        result["controls"].update(
            {
                "cal_stale_text_hash_rejected": True,
                "cal_alias_id_rejected": True,
                "cal_nonempty_output_rejected": True,
            }
        )

        # 4. Actual current CAL object -> C2 structural materialization + frozen producer authority pressure.
        c2_out = out / "current-cal-to-c2"
        runner.run(
            "current-cal-to-c2",
            [
                cal_python,
                str(exp / "materialize_current_cal_c2.py"),
                "--bundle",
                str(bundle_dir),
                "--target",
                str(target_path),
                "--apparatus",
                str(c2),
                "--out-dir",
                str(c2_out),
            ],
            cwd=root,
        )
        c2_summary = json.loads((c2_out / "summary.json").read_text(encoding="utf-8"))
        if c2_summary["structural_c2_validation"] != "pass":
            raise RuntimeError("current CAL C2 structural materialization failed")
        result["stages"]["cal_to_contract_c2"] = {
            "status": "BLOCKED_AUTHORITY" if c2_summary["producer_authority_gap_observed"] else "PASS",
            **c2_summary,
        }

        # 5. Continue in explicitly structural-only lane: actual C2 -> Decision -> canonical D.
        c2_path = c2_out / "contract_c2.json"
        expected_b = c2_out / "expected_contract_b.json"
        decision_context = c2_out / "decision_context.json"
        c2_sha = c2_summary["whole_object_sha256"]
        d_path = out / "contract_d.json"
        cmd = decision_cmd(node, decision, c2_path, c2_sha, c2, droot, expected_b, decision_context, cal_python)
        d_run = runner.run("decision-c2-to-d", cmd, cwd=decision)
        d_path.write_bytes(d_run.stdout)
        d_value = json.loads(d_run.stdout.decode("utf-8"))
        if d_value.get("evaluation") != {"state": "completed", "disposition": "clear"}:
            raise RuntimeError(f"Decision did not CLEAR positive canary: {d_value.get('evaluation')}")
        d_replay = runner.run("decision-c2-to-d-replay", cmd, cwd=decision)
        if d_replay.stdout != d_run.stdout:
            raise RuntimeError("Decision/Contract D replay drift")
        result["stages"]["decision_to_contract_d"] = {
            "status": "PASS_STRUCTURAL_ONLY_PENDING_UPSTREAM_C2_PRODUCER_AUTHORITY",
            "evaluation": d_value["evaluation"],
            "contract_d_sha256": sha256_bytes(d_run.stdout),
            "replay_identical": True,
        }
        stale_cmd = decision_cmd(node, decision, c2_path, "sha256:" + "0" * 64, c2, droot, expected_b, decision_context, cal_python)
        stale = runner.rejects("decision-rejects-stale-c2-hash", stale_cmd, cwd=decision)
        if b"contract_c_whole_object_mismatch" not in stale.stderr:
            raise RuntimeError("Decision stale-C2 control failed with unexpected class")
        wrong_b = json.loads(expected_b.read_text(encoding="utf-8"))
        wrong_b["bundle_id"] = "wrong-bundle"
        wrong_b_path = inputs / "wrong-expected-b.json"
        json_write(wrong_b_path, wrong_b)
        wrong_b_cmd = decision_cmd(node, decision, c2_path, c2_sha, c2, droot, wrong_b_path, decision_context, cal_python)
        wrong_b_result = runner.rejects("decision-rejects-wrong-b", wrong_b_cmd, cwd=decision)
        if b"contract_b_binding_mismatch" not in wrong_b_result.stderr:
            raise RuntimeError("Decision wrong-B control failed with unexpected class")
        bad_context = json.loads(decision_context.read_text(encoding="utf-8"))
        bad_context["target"]["content_sha256"] = "sha256:" + "1" * 64
        bad_context_path = inputs / "decision-context.wrong-target.json"
        json_write(bad_context_path, bad_context)
        bad_context_cmd = decision_cmd(node, decision, c2_path, c2_sha, c2, droot, expected_b, bad_context_path, cal_python)
        runner.rejects("decision-rejects-target-substitution", bad_context_cmd, cwd=decision)
        wrong_authority_cmd = decision_cmd(node, decision, c2_path, c2_sha, droot, droot, expected_b, decision_context, cal_python)
        wrong_authority = runner.rejects("decision-rejects-wrong-c2-authority", wrong_authority_cmd, cwd=decision)
        if b"authority_identity_mismatch" not in wrong_authority.stderr:
            raise RuntimeError("Decision wrong-authority control failed with unexpected class")
        result["controls"].update(
            {
                "decision_stale_c2_hash_rejected": True,
                "decision_wrong_b_binding_rejected": True,
                "decision_target_substitution_rejected": True,
                "decision_wrong_c2_authority_rejected": True,
            }
        )

        # 6. Contract E research-only dry authorization pressure with actual D as non-conferring support.
        e_summary_path = out / "contract_e_dry_summary.json"
        runner.run(
            "contract-e-dry-pressure",
            [
                cal_python,
                str(exp / "contract_e_dry_pressure.py"),
                "--apparatus",
                str(eroot),
                "--contract-d",
                str(d_path),
                "--out",
                str(e_summary_path),
            ],
            cwd=root,
        )
        e_summary = json.loads(e_summary_path.read_text(encoding="utf-8"))
        result["stages"]["contract_e_dry_authorization"] = {
            "status": "PASS_RESEARCH_ONLY_NO_EXECUTION",
            **e_summary,
        }

        if c2_summary["producer_authority_gap_observed"]:
            result["classification"] = "BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY"
        else:
            result["classification"] = "SUPPORTED_FOR_LOCAL_PIPELINE_SMOKE_WITH_BOUNDS"
    except Exception as exc:  # noqa: BLE001
        result["classification"] = "FALSIFIED_PRELOCAL_INTEROPERABILITY_CLAIM"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()

    result_path = out / "RESULT.json"
    json_write(result_path, result)
    print(json.dumps({"classification": result["classification"], "result": str(result_path)}, sort_keys=True))
    return 0 if result["classification"] != "FALSIFIED_PRELOCAL_INTEROPERABILITY_CLAIM" else 1


if __name__ == "__main__":
    raise SystemExit(main())
