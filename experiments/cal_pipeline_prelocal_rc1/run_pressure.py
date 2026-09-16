from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import traceback
from pathlib import Path
from typing import Any

RAW_CLAIM = "Valve Cerulean was inactive."
POSITIVE_CLAIM = "Women had a higher rate than Men."


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_write(path: Path, value: Any, *, pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)
        if pretty
        else json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )
    path.write_text(text + "\n", encoding="utf-8")


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
        expect: int | None = 0,
    ) -> subprocess.CompletedProcess[bytes]:
        self.index += 1
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        prefix = self.logs / f"{self.index:03d}-{label}"
        prefix.with_suffix(".stdout").write_bytes(result.stdout)
        prefix.with_suffix(".stderr").write_bytes(result.stderr)
        prefix.with_suffix(".command.txt").write_text(
            f"cwd={cwd or Path.cwd()}\n" + " ".join(cmd) + "\n", encoding="utf-8"
        )
        if expect is not None and result.returncode != expect:
            raise RuntimeError(
                f"{label}: expected {expect}, got {result.returncode}: "
                + result.stderr.decode("utf-8", "replace")[:1200]
            )
        return result

    def rejects(self, label: str, cmd: list[str], *, cwd: Path | None = None):
        result = self.run(label, cmd, cwd=cwd, expect=None)
        if result.returncode == 0:
            raise RuntimeError(f"{label}: hostile control unexpectedly succeeded")
        return result


def decision_cmd(
    node: str,
    decision_root: Path,
    c2_path: Path,
    c2_sha: str,
    c2_root: Path,
    d_root: Path,
    expected_b: Path,
    context: Path,
    python: str,
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
        python,
    ]


def validate_contract_a(runner: Runner, python: str, c2_root: Path, path: Path, label: str) -> None:
    runner.run(label, [python, str(c2_root / "validators/contract_a_rc2.py"), str(path)])


def run_eb(
    runner: Runner,
    eb_python: str,
    eb_root: Path,
    contract_a_path: Path,
    out_root: Path,
    lane: str,
) -> tuple[Path, dict[str, Any]]:
    script = eb_root / "scripts/run_v1_integration_candidate.py"
    carrier = eb_root / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
    seed = out_root / f"{lane}-eb-seed"
    runner.run(
        f"{lane}-eb-seed",
        [eb_python, str(script), str(contract_a_path), "--compatibility-carrier", str(carrier), "--out-dir", str(seed)],
        cwd=eb_root,
    )
    package = json.loads((seed / "native_eb_v1_package.json").read_text(encoding="utf-8"))
    retained = [row for row in package["candidates"] if row["selection_state"] == "retained"]
    if not retained:
        raise RuntimeError(f"{lane}: EB retained no candidates")
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
    admission_path = out_root / "inputs" / f"{lane}-admission.json"
    json_write(admission_path, admission)
    final = out_root / f"{lane}-eb-final"
    replay = out_root / f"{lane}-eb-replay"
    base = [
        eb_python,
        str(script),
        str(contract_a_path),
        "--admission",
        str(admission_path),
        "--compatibility-carrier",
        str(carrier),
    ]
    runner.run(f"{lane}-eb-final", [*base, "--out-dir", str(final)], cwd=eb_root)
    runner.run(f"{lane}-eb-replay", [*base, "--out-dir", str(replay)], cwd=eb_root)
    if dir_hashes(final) != dir_hashes(replay):
        raise RuntimeError(f"{lane}: EB deterministic replay drift")
    package = json.loads((final / "native_eb_v1_package.json").read_text(encoding="utf-8"))
    if package["config"]["candidate_depth"] != 10 or package["config"]["retained_k"] != 3:
        raise RuntimeError(f"{lane}: EB profile drift from 10/3")
    return final / "contract_b", {
        "retained": len(retained),
        "accepted_by_test_harness": len(admission["decisions"]),
        "package_sha256": package["package_sha256"],
        "replay_identical": True,
    }


def run_cal(
    runner: Runner,
    cal_cli: str,
    cal_root: Path,
    bundle: Path,
    target: Path,
    out_root: Path,
    lane: str,
    expected_conclusion: str,
    expected_failure: str | None,
) -> tuple[Path, dict[str, Any]]:
    runner.run(f"{lane}-cal-validate", [cal_cli, "validate-bundle", str(bundle), str(target)], cwd=cal_root)
    run1 = out_root / f"{lane}-cal-run-1"
    run2 = out_root / f"{lane}-cal-run-2"
    runner.run(f"{lane}-cal-run-1", [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run1)], cwd=cal_root)
    runner.run(f"{lane}-cal-run-2", [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run2)], cwd=cal_root)
    if dir_hashes(run1) != dir_hashes(run2):
        raise RuntimeError(f"{lane}: CAL deterministic replay drift")
    value = json.loads((run1 / "result.json").read_text(encoding="utf-8"))
    observed = value["result"]
    if observed["conclusion"] != expected_conclusion or observed["failure_code"] != expected_failure:
        raise RuntimeError(f"{lane}: unexpected CAL terminal {observed}")
    runner.rejects(
        f"{lane}-cal-nonempty-output",
        [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run1)],
        cwd=cal_root,
    )
    return run1, {
        "conclusion": observed["conclusion"],
        "failure_code": observed["failure_code"],
        "semantic_implementation_sha": value["semantic_implementation_sha"],
        "replay_identical": True,
    }


def materialize_c2(
    runner: Runner,
    python: str,
    root: Path,
    bundle: Path,
    target: Path,
    c2_root: Path,
    out: Path,
    lane: str,
) -> dict[str, Any]:
    helper = root / "experiments/cal_pipeline_prelocal_rc0/materialize_current_cal_c2.py"
    runner.run(
        f"{lane}-current-cal-to-c2",
        [python, str(helper), "--bundle", str(bundle), "--target", str(target), "--apparatus", str(c2_root), "--out-dir", str(out)],
        cwd=root,
    )
    return json.loads((out / "summary.json").read_text(encoding="utf-8"))


def run_decision(
    runner: Runner,
    node: str,
    decision_root: Path,
    c2_root: Path,
    d_root: Path,
    c2_out: Path,
    python: str,
    lane: str,
    expected_disposition: str,
) -> tuple[Path, dict[str, Any]]:
    c2_summary = json.loads((c2_out / "summary.json").read_text(encoding="utf-8"))
    cmd = decision_cmd(
        node,
        decision_root,
        c2_out / "contract_c2.json",
        c2_summary["whole_object_sha256"],
        c2_root,
        d_root,
        c2_out / "expected_contract_b.json",
        c2_out / "decision_context.json",
        python,
    )
    first = runner.run(f"{lane}-decision", cmd, cwd=decision_root)
    second = runner.run(f"{lane}-decision-replay", cmd, cwd=decision_root)
    if first.stdout != second.stdout:
        raise RuntimeError(f"{lane}: Decision/D replay drift")
    decision = json.loads(first.stdout.decode("utf-8"))
    if decision.get("evaluation") != {"state": "completed", "disposition": expected_disposition}:
        raise RuntimeError(f"{lane}: unexpected Decision terminal {decision.get('evaluation')}")
    path = c2_out.parent / f"{lane}-contract-d.json"
    path.write_bytes(first.stdout)
    return path, {
        "evaluation": decision["evaluation"],
        "contract_d_sha256": sha256_bytes(first.stdout),
        "replay_identical": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    exp = root / "experiments/cal_pipeline_prelocal_rc1"
    manifest = json.loads((exp / "MANIFEST.json").read_text(encoding="utf-8"))
    out = root / "build/cal_pipeline_prelocal_rc1"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    runner = Runner(out / "logs")
    inputs = out / "inputs"
    inputs.mkdir()

    cg = root / "deps/claimgate"
    eb = root / "deps/eb"
    cal = root / "deps/cal"
    c2 = root / "deps/apparatus-c2"
    c1 = root / "deps/apparatus-c1"
    decision_root = root / "deps/decision"
    droot = root / "deps/apparatus-d"
    eroot = root / "deps/apparatus-e"
    cg_python = str((root / ".venv-cg/bin/python").resolve())
    eb_python = str((root / ".venv-eb/bin/python").resolve())
    cal_python = str((root / ".venv-cal/bin/python").resolve())
    cg_cli = str((root / ".venv-cg/bin/proposition-authoring").resolve())
    cal_cli = str((root / ".venv-cal/bin/claim-audit-v1").resolve())
    node = shutil.which("node") or "node"

    result: dict[str, Any] = {
        "schema": "cal-pipeline-prelocal-pressure-result-v1",
        "manifest": manifest,
        "lanes": {},
        "controls": {},
        "irregularities": [],
    }

    try:
        expected_heads = {
            cg: manifest["subjects"]["claimgate"]["commit"],
            eb: manifest["subjects"]["evidence_bundler"]["frozen_head"],
            cal: manifest["subjects"]["cal"]["records_head"],
            c2: manifest["subjects"]["contract_c2"]["promotion_head"],
            c1: manifest["subjects"]["contract_c1"]["release_commit"],
            decision_root: manifest["subjects"]["decision"]["c2_integration_head"],
            droot: manifest["subjects"]["decision"]["contract_d_authority"],
            eroot: manifest["subjects"]["contract_e"]["research_head"],
        }
        heads: dict[str, str] = {}
        for path, expected in expected_heads.items():
            observed = runner.run(f"head-{path.name}", ["git", "rev-parse", "HEAD"], cwd=path).stdout.decode().strip()
            if observed != expected:
                raise RuntimeError(f"authority drift {path}: {observed} != {expected}")
            heads[path.name] = observed
        c1_tag = runner.run("c1-tag", ["git", "rev-parse", "refs/tags/contract-c-v1.0.0"], cwd=c1).stdout.decode().strip()
        d_tag = runner.run("d-tag", ["git", "rev-parse", "refs/tags/contract-d-v1.0.0"], cwd=droot).stdout.decode().strip()
        if c1_tag != manifest["subjects"]["contract_c1"]["tag_object"]:
            raise RuntimeError("Contract C1 annotated tag authority mismatch")
        if d_tag != manifest["subjects"]["decision"]["contract_d_tag_object"]:
            raise RuntimeError("Contract D annotated tag authority mismatch")
        result["authority_manifest"] = {"status": "PASS", "heads": heads, "c1_tag": c1_tag, "d_tag": d_tag}

        # Lane A: true raw claim from exact ClaimGate supported fixture.
        raw_lane: dict[str, Any] = {}
        fixture = cg / "integration/claimgate_v1_candidate/fixtures/not_needed.json"
        raw_request = json.loads(fixture.read_text(encoding="utf-8"))
        if raw_request["root_text"] != RAW_CLAIM:
            raise RuntimeError("ClaimGate frozen not_needed fixture drift")
        raw_input = inputs / "raw-claimgate-request.json"
        json_write(raw_input, raw_request)
        raw_cg = out / "raw-claimgate"
        raw_cg.mkdir()
        raw_receipt = raw_cg / "receipt.json"
        raw_a = raw_cg / "contract_a.json"
        cg_result = runner.run(
            "raw-claimgate",
            [cg_cli, "author", str(raw_input), "--receipt", str(raw_receipt), "--contract-a", str(raw_a)],
            cwd=cg,
        )
        if not raw_a.exists():
            raise RuntimeError("raw lane ClaimGate emitted no Contract A")
        receipt = json.loads(raw_receipt.read_text(encoding="utf-8"))
        if receipt["state"] != "NOT_NEEDED":
            raise RuntimeError(f"raw lane unexpected ClaimGate state: {receipt['state']}")
        raw_contract_a = json.loads(raw_a.read_text(encoding="utf-8"))
        if raw_contract_a["decomposition"] != {"state": "not_decomposed"}:
            raise RuntimeError("raw lane expected not_decomposed Contract A")
        validate_contract_a(runner, cal_python, c2, raw_a, "raw-contract-a-validation")
        raw_lane["claimgate"] = {"state": receipt["state"], "reason": receipt["reason"], "contract_a_sha256": sha256_bytes(raw_a.read_bytes())}

        tampered = json.loads(raw_a.read_text(encoding="utf-8"))
        tampered["root_proposition"]["text"] += " tampered"
        tampered_path = inputs / "raw-contract-a-tampered.json"
        json_write(tampered_path, tampered)
        runner.rejects("raw-contract-a-tamper", [cal_python, str(c2 / "validators/contract_a_rc2.py"), str(tampered_path)])
        result["controls"]["contract_a_tamper_rejected"] = True

        raw_bundle, raw_eb = run_eb(runner, eb_python, eb, raw_a, out, "raw")
        raw_lane["evidence_bundler"] = raw_eb
        eb_script = eb / "scripts/run_v1_integration_candidate.py"
        carrier = eb / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
        runner.rejects(
            "raw-eb-rejects-tampered-a",
            [eb_python, str(eb_script), str(tampered_path), "--compatibility-carrier", str(carrier), "--out-dir", str(out / "raw-eb-bad-a")],
            cwd=eb,
        )
        result["controls"]["eb_rejects_tampered_contract_a"] = True

        raw_claim_id = raw_contract_a["root_proposition"]["proposition_id"]
        raw_target = {
            "claim_id": raw_claim_id,
            "proposition": {
                "proposition_id": raw_claim_id,
                "text_sha256": sha256_text(RAW_CLAIM),
                "semantic_family": "assertion_scope",
                "fields": {"subject": "Valve Cerulean", "state": "inactive"},
            },
        }
        raw_target_path = inputs / "raw-cal-target.json"
        json_write(raw_target_path, raw_target)
        _, raw_cal = run_cal(
            runner,
            cal_cli,
            cal,
            raw_bundle,
            raw_target_path,
            out,
            "raw",
            "not_checkable",
            "UNSUPPORTED_SEMANTIC_FAMILY",
        )
        raw_lane["cal"] = raw_cal
        raw_c2_out = out / "raw-current-cal-to-c2"
        raw_c2_summary = materialize_c2(runner, cal_python, root, raw_bundle, raw_target_path, c2, raw_c2_out, "raw")
        raw_lane["contract_c2"] = raw_c2_summary
        raw_d, raw_decision = run_decision(
            runner,
            node,
            decision_root,
            c2,
            droot,
            raw_c2_out,
            cal_python,
            "raw",
            "hold",
        )
        raw_lane["decision"] = raw_decision
        raw_lane["contract_e"] = {"state": "not_invoked_decision_hold"}
        result["lanes"]["raw_fail_closed"] = raw_lane

        # Lane B: explicit downstream positive Contract A fixture.
        positive_lane: dict[str, Any] = {
            "entry_boundary": "test_only_contract_a_emitter_not_claim_gate_semantic_decision"
        }
        positive_a = inputs / "positive-contract-a.json"
        runner.run(
            "emit-positive-contract-a",
            [cg_python, str(exp / "emit_strict_comparison_contract_a.py"), "--out", str(positive_a)],
            cwd=root,
        )
        validate_contract_a(runner, cal_python, c2, positive_a, "positive-contract-a-validation")
        positive_contract_a = json.loads(positive_a.read_text(encoding="utf-8"))
        if positive_contract_a["root_proposition"]["text"] != POSITIVE_CLAIM:
            raise RuntimeError("positive fixture claim drift")
        positive_bundle, positive_eb = run_eb(runner, eb_python, eb, positive_a, out, "positive")
        positive_lane["evidence_bundler"] = positive_eb
        positive_id = positive_contract_a["root_proposition"]["proposition_id"]
        positive_target = {
            "claim_id": positive_id,
            "proposition": {
                "proposition_id": positive_id,
                "text_sha256": sha256_text(POSITIVE_CLAIM),
                "semantic_family": "strict_comparison",
                "fields": {
                    "lhs_entity": "Women",
                    "rhs_entity": "Men",
                    "comparison_direction": "MORE_THAN",
                },
            },
        }
        positive_target_path = inputs / "positive-cal-target.json"
        json_write(positive_target_path, positive_target)
        _, positive_cal = run_cal(
            runner,
            cal_cli,
            cal,
            positive_bundle,
            positive_target_path,
            out,
            "positive",
            "supported",
            None,
        )
        positive_lane["cal"] = positive_cal

        stale_target = json.loads(positive_target_path.read_text(encoding="utf-8"))
        stale_target["proposition"]["text_sha256"] = "0" * 64
        stale_target_path = inputs / "positive-cal-target-stale.json"
        json_write(stale_target_path, stale_target)
        runner.rejects("positive-cal-stale-hash", [cal_cli, "validate-bundle", str(positive_bundle), str(stale_target_path)], cwd=cal)
        alias_target = json.loads(positive_target_path.read_text(encoding="utf-8"))
        alias_target["proposition"]["proposition_id"] = "alias-proposition"
        alias_target_path = inputs / "positive-cal-target-alias.json"
        json_write(alias_target_path, alias_target)
        runner.rejects("positive-cal-alias-id", [cal_cli, "validate-bundle", str(positive_bundle), str(alias_target_path)], cwd=cal)
        result["controls"].update({"cal_stale_text_hash_rejected": True, "cal_alias_id_rejected": True})

        positive_c2_out = out / "positive-current-cal-to-c2"
        positive_c2_summary = materialize_c2(runner, cal_python, root, positive_bundle, positive_target_path, c2, positive_c2_out, "positive")
        positive_lane["contract_c2"] = positive_c2_summary
        positive_d, positive_decision = run_decision(
            runner,
            node,
            decision_root,
            c2,
            droot,
            positive_c2_out,
            cal_python,
            "positive",
            "clear",
        )
        positive_lane["decision"] = positive_decision

        stale_cmd = decision_cmd(
            node,
            decision_root,
            positive_c2_out / "contract_c2.json",
            "sha256:" + "0" * 64,
            c2,
            droot,
            positive_c2_out / "expected_contract_b.json",
            positive_c2_out / "decision_context.json",
            cal_python,
        )
        stale = runner.rejects("decision-stale-c2", stale_cmd, cwd=decision_root)
        if b"contract_c_whole_object_mismatch" not in stale.stderr:
            raise RuntimeError("Decision stale-C2 error class drift")
        wrong_b = json.loads((positive_c2_out / "expected_contract_b.json").read_text(encoding="utf-8"))
        wrong_b["bundle_id"] = "wrong-bundle"
        wrong_b_path = inputs / "positive-wrong-b.json"
        json_write(wrong_b_path, wrong_b)
        wrong_b_cmd = decision_cmd(
            node,
            decision_root,
            positive_c2_out / "contract_c2.json",
            positive_c2_summary["whole_object_sha256"],
            c2,
            droot,
            wrong_b_path,
            positive_c2_out / "decision_context.json",
            cal_python,
        )
        wrong_b_result = runner.rejects("decision-wrong-b", wrong_b_cmd, cwd=decision_root)
        if b"contract_b_binding_mismatch" not in wrong_b_result.stderr:
            raise RuntimeError("Decision wrong-B error class drift")
        bad_context = json.loads((positive_c2_out / "decision_context.json").read_text(encoding="utf-8"))
        bad_context["target"]["content_sha256"] = "sha256:" + "1" * 64
        bad_context_path = inputs / "positive-decision-bad-target.json"
        json_write(bad_context_path, bad_context)
        bad_context_cmd = decision_cmd(
            node,
            decision_root,
            positive_c2_out / "contract_c2.json",
            positive_c2_summary["whole_object_sha256"],
            c2,
            droot,
            positive_c2_out / "expected_contract_b.json",
            bad_context_path,
            cal_python,
        )
        runner.rejects("decision-target-substitution", bad_context_cmd, cwd=decision_root)
        wrong_authority_cmd = decision_cmd(
            node,
            decision_root,
            positive_c2_out / "contract_c2.json",
            positive_c2_summary["whole_object_sha256"],
            droot,
            droot,
            positive_c2_out / "expected_contract_b.json",
            positive_c2_out / "decision_context.json",
            cal_python,
        )
        wrong_authority = runner.rejects("decision-wrong-c2-authority", wrong_authority_cmd, cwd=decision_root)
        if b"authority_identity_mismatch" not in wrong_authority.stderr:
            raise RuntimeError("Decision wrong-C2-authority error class drift")
        result["controls"].update(
            {
                "decision_stale_c2_hash_rejected": True,
                "decision_wrong_b_binding_rejected": True,
                "decision_target_substitution_rejected": True,
                "decision_wrong_c2_authority_rejected": True,
            }
        )

        e_summary_path = out / "contract_e_dry_summary.json"
        runner.run(
            "positive-contract-e-dry",
            [
                cal_python,
                str(root / "experiments/cal_pipeline_prelocal_rc0/contract_e_dry_pressure.py"),
                "--apparatus",
                str(eroot),
                "--contract-d",
                str(positive_d),
                "--out",
                str(e_summary_path),
            ],
            cwd=root,
        )
        positive_lane["contract_e"] = json.loads(e_summary_path.read_text(encoding="utf-8"))
        result["lanes"]["downstream_positive_control"] = positive_lane

        producer_gaps = [
            bool(raw_c2_summary["producer_authority_gap_observed"]),
            bool(positive_c2_summary["producer_authority_gap_observed"]),
        ]
        if any(producer_gaps):
            result["classification"] = "BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY"
        else:
            result["classification"] = "SUPPORTED_FOR_LOCAL_PIPELINE_SMOKE_WITH_BOUNDS"
    except Exception as exc:  # noqa: BLE001
        result["classification"] = "FALSIFIED_PRELOCAL_INTEROPERABILITY_CLAIM"
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()

    json_write(out / "RESULT.json", result)
    print(json.dumps({"classification": result["classification"]}, sort_keys=True))
    return 0 if result["classification"] != "FALSIFIED_PRELOCAL_INTEROPERABILITY_CLAIM" else 1


if __name__ == "__main__":
    raise SystemExit(main())
