from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tarfile
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any

CAMPAIGN = "cal_pipeline_v1_prototype_freeze_rc0"
EXPECTED_OLD_RESOLVER = "43b571464734325277374ee81098553fb7c1b944"


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dir_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        safe = label.replace(":", "_").replace("/", "_")
        prefix = self.logs / f"{self.index:04d}-{safe}"
        prefix.with_suffix(".stdout").write_bytes(result.stdout)
        prefix.with_suffix(".stderr").write_bytes(result.stderr)
        prefix.with_suffix(".command.txt").write_text(
            f"cwd={cwd or Path.cwd()}\n" + " ".join(cmd) + "\n", encoding="utf-8"
        )
        if expect is not None and result.returncode != expect:
            raise RuntimeError(
                f"{label}: expected {expect}, got {result.returncode}: "
                + result.stderr.decode("utf-8", "replace")[:1600]
            )
        return result

    def rejects(self, label: str, cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
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
    case_root: Path,
    label: str,
) -> tuple[Path, dict[str, Any]]:
    script = eb_root / "scripts/run_v1_integration_candidate.py"
    carrier = eb_root / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
    seed = case_root / "eb-seed"
    runner.run(
        f"{label}-eb-seed",
        [eb_python, str(script), str(contract_a_path), "--compatibility-carrier", str(carrier), "--out-dir", str(seed)],
        cwd=eb_root,
    )
    package = json.loads((seed / "native_eb_v1_package.json").read_text(encoding="utf-8"))
    retained = [row for row in package["candidates"] if row["selection_state"] == "retained"]
    if not retained:
        raise RuntimeError(f"{label}: EB retained no candidates")
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
    admission_path = case_root / "admission.json"
    json_write(admission_path, admission)
    final = case_root / "eb-final"
    replay = case_root / "eb-replay"
    base = [
        eb_python,
        str(script),
        str(contract_a_path),
        "--admission",
        str(admission_path),
        "--compatibility-carrier",
        str(carrier),
    ]
    runner.run(f"{label}-eb-final", [*base, "--out-dir", str(final)], cwd=eb_root)
    runner.run(f"{label}-eb-replay", [*base, "--out-dir", str(replay)], cwd=eb_root)
    if dir_hashes(final) != dir_hashes(replay):
        raise RuntimeError(f"{label}: EB deterministic replay drift")
    package = json.loads((final / "native_eb_v1_package.json").read_text(encoding="utf-8"))
    if package["config"]["candidate_depth"] != 10 or package["config"]["retained_k"] != 3:
        raise RuntimeError(f"{label}: EB profile drift from 10/3")
    return final / "contract_b", {
        "retained": len(retained),
        "admitted": len(admission["decisions"]),
        "package_sha256": package["package_sha256"],
        "replay_identical": True,
    }


def run_cal(
    runner: Runner,
    cal_cli: str,
    cal_root: Path,
    bundle: Path,
    target: Path,
    case_root: Path,
    label: str,
    expected: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    runner.run(f"{label}-cal-validate", [cal_cli, "validate-bundle", str(bundle), str(target)], cwd=cal_root)
    run1 = case_root / "cal-run-1"
    run2 = case_root / "cal-run-2"
    runner.run(f"{label}-cal-run-1", [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run1)], cwd=cal_root)
    runner.run(f"{label}-cal-run-2", [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run2)], cwd=cal_root)
    if dir_hashes(run1) != dir_hashes(run2):
        raise RuntimeError(f"{label}: CAL deterministic replay drift")
    value = json.loads((run1 / "result.json").read_text(encoding="utf-8"))
    observed = value["result"]
    if observed["conclusion"] != expected["conclusion"] or observed["failure_code"] != expected["failure_code"]:
        raise RuntimeError(f"{label}: unexpected CAL terminal {observed}")
    runner.rejects(
        f"{label}-cal-nonempty-output",
        [cal_cli, "run-bundle", str(bundle), str(target), "--out-dir", str(run1)],
        cwd=cal_root,
    )
    return run1, {
        "conclusion": observed["conclusion"],
        "failure_code": observed["failure_code"],
        "semantic_implementation_sha": value["semantic_implementation_sha"],
        "result_sha256": sha256_bytes((run1 / "result.json").read_bytes()),
        "replay_identical": True,
    }


def run_c2(
    runner: Runner,
    python: str,
    root: Path,
    cal_root: Path,
    c2_root: Path,
    resolver_root: Path,
    predecessor_resolver_root: Path,
    bundle: Path,
    target: Path,
    case_root: Path,
    label: str,
) -> tuple[Path, dict[str, Any]]:
    out = case_root / "contract-c2"
    helper = root / f"qualification/{CAMPAIGN}/materialize_authorized_c2.py"
    runner.run(
        f"{label}-c2",
        [
            python,
            str(helper),
            "--bundle",
            str(bundle),
            "--target",
            str(target),
            "--cal-root",
            str(cal_root),
            "--apparatus",
            str(c2_root),
            "--resolver-root",
            str(resolver_root),
            "--predecessor-resolver-root",
            str(predecessor_resolver_root),
            "--out-dir",
            str(out),
        ],
        cwd=root,
    )
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    if summary["producer_policy_resolution"] != "pass":
        raise RuntimeError(f"{label}: C2 producer authority did not resolve")
    if set(summary["hostile_controls"]) != {
        "predecessor_resolver_rejects_current_cal",
        "wrong_policy_digest_rejected",
        "resolver_commit_substitution_rejected",
    }:
        raise RuntimeError(f"{label}: incomplete C2 resolver hostile controls")
    return out, summary


def run_decision(
    runner: Runner,
    node: str,
    decision_root: Path,
    c2_root: Path,
    d_root: Path,
    c2_out: Path,
    python: str,
    case_root: Path,
    label: str,
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
    first = runner.run(f"{label}-decision", cmd, cwd=decision_root)
    second = runner.run(f"{label}-decision-replay", cmd, cwd=decision_root)
    if first.stdout != second.stdout:
        raise RuntimeError(f"{label}: Decision/D replay drift")
    decision = json.loads(first.stdout.decode("utf-8"))
    if decision.get("evaluation") != {"state": "completed", "disposition": expected_disposition}:
        raise RuntimeError(f"{label}: unexpected Decision terminal {decision.get('evaluation')}")

    dcore = load_module(f"contract_d_core_{label.replace('-', '_')}", d_root / "validators/contract_d_core.py")
    dcore.validate_decision(decision)
    if dcore.canonical_json_bytes(decision) != first.stdout:
        raise RuntimeError(f"{label}: Decision stdout is not canonical Contract D bytes")

    path = case_root / "contract-d.json"
    path.write_bytes(first.stdout)
    return path, {
        "evaluation": decision["evaluation"],
        "contract_d_sha256": sha256_bytes(first.stdout),
        "replay_identical": True,
        "canonical_contract_d": True,
    }


def authority_preflight(root: Path, runner: Runner, manifest: dict[str, Any]) -> dict[str, Any]:
    subjects = manifest["subjects"]
    paths = {
        "claimgate": (root / "deps/claimgate", subjects["claimgate"]["commit"]),
        "evidence_bundler": (root / "deps/eb", subjects["evidence_bundler"]["frozen_head"]),
        "cal": (root / "deps/cal", subjects["cal"]["producer_authority_head"]),
        "contract_c2": (root / "deps/apparatus-c2", subjects["contract_c2"]["promotion_head"]),
        "resolver": (root / "deps/apparatus-resolver", subjects["contract_c2_resolver"]["authority_freeze"]),
        "decision": (root / "deps/decision", subjects["decision"]["c2_integration_head"]),
        "contract_c1": (root / "deps/apparatus-c1", subjects["contract_c1"]["release_commit"]),
        "contract_d": (root / "deps/apparatus-d", subjects["contract_d"]["release_commit"]),
        "contract_e": (root / "deps/apparatus-e", subjects["contract_e"]["research_head"]),
    }
    observed: dict[str, str] = {}
    for name, (path, expected) in paths.items():
        got = runner.run(f"authority-{name}", ["git", "rev-parse", "HEAD"], cwd=path).stdout.decode().strip()
        if got != expected:
            raise RuntimeError(f"authority drift {name}: {got} != {expected}")
        observed[name] = got

    old = root / "deps/apparatus-resolver-old"
    old_head = runner.run("authority-old-resolver", ["git", "rev-parse", "HEAD"], cwd=old).stdout.decode().strip()
    if old_head != EXPECTED_OLD_RESOLVER:
        raise RuntimeError(f"predecessor resolver drift: {old_head}")
    observed["predecessor_resolver"] = old_head

    materializer = root / "deps/cal/research/contract_c2_current_cal_producer_conformance_rc1/materialize.py"
    materializer_blob = runner.run("materializer-blob", ["git", "hash-object", str(materializer)], cwd=root / "deps/cal").stdout.decode().strip()
    if materializer_blob != subjects["cal"]["c2_materializer_blob"]:
        raise RuntimeError(f"CAL C2 materializer blob drift: {materializer_blob}")

    resolver_file = root / "deps/apparatus-resolver/research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
    resolver_blob = runner.run("resolver-blob", ["git", "hash-object", str(resolver_file)], cwd=root / "deps/apparatus-resolver").stdout.decode().strip()
    if resolver_blob != subjects["contract_c2_resolver"]["resolver_blob"]:
        raise RuntimeError(f"resolver blob drift: {resolver_blob}")

    c1_tag = runner.run("contract-c1-tag", ["git", "rev-parse", "refs/tags/contract-c-v1.0.0"], cwd=root / "deps/apparatus-c1").stdout.decode().strip()
    d_tag = runner.run("contract-d-tag", ["git", "rev-parse", "refs/tags/contract-d-v1.0.0"], cwd=root / "deps/apparatus-d").stdout.decode().strip()
    if c1_tag != subjects["contract_c1"]["tag_object"]:
        raise RuntimeError("Contract C1 tag authority mismatch")
    if d_tag != subjects["contract_d"]["tag_object"]:
        raise RuntimeError("Contract D tag authority mismatch")

    return {
        "heads": observed,
        "materializer_blob": materializer_blob,
        "resolver_blob": resolver_blob,
        "contract_c1_tag_object": c1_tag,
        "contract_d_tag_object": d_tag,
    }


def make_request(case: dict[str, Any], cg: Path, case_root: Path) -> tuple[Path, dict[str, Any]]:
    if case["kind"] == "claimgate_fixture":
        path = cg / "integration/claimgate_v1_candidate/fixtures" / case["fixture"]
        return path, json.loads(path.read_text(encoding="utf-8"))
    value = case["request"]
    path = case_root / "raw-request.json"
    json_write(path, value)
    return path, value


def execute_campaign(
    root: Path,
    run_root: Path,
    cohort: dict[str, Any],
    manifest: dict[str, Any],
    *,
    run_name: str,
) -> dict[str, Any]:
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)
    runner = Runner(run_root / "logs")

    cg = root / "deps/claimgate"
    eb = root / "deps/eb"
    cal = root / "deps/cal"
    c2 = root / "deps/apparatus-c2"
    resolver = root / "deps/apparatus-resolver"
    old_resolver = root / "deps/apparatus-resolver-old"
    decision = root / "deps/decision"
    droot = root / "deps/apparatus-d"
    eroot = root / "deps/apparatus-e"

    cg_cli = str((root / ".venv-cg/bin/proposition-authoring").resolve())
    eb_python = str((root / ".venv-eb/bin/python").resolve())
    cal_python = str((root / ".venv-cal/bin/python").resolve())
    cal_cli = str((root / ".venv-cal/bin/claim-audit-v1").resolve())
    node = shutil.which("node") or "node"

    campaign: dict[str, Any] = {"run": run_name, "cases": {}, "controls": {}}

    for case in cohort["cases"]:
        case_id = case["id"]
        case_root = run_root / "cases" / case_id
        case_root.mkdir(parents=True)
        request_path, request = make_request(case, cg, case_root)
        cg_dir = case_root / "claimgate"
        cg_dir.mkdir()
        receipt = cg_dir / "receipt.json"
        contract_a = cg_dir / "contract_a.json"
        runner.run(
            f"{case_id}-claimgate",
            [cg_cli, "author", str(request_path), "--receipt", str(receipt), "--contract-a", str(contract_a)],
            cwd=cg,
        )
        receipt_value = json.loads(receipt.read_text(encoding="utf-8"))
        if receipt_value["state"] != case["expected_claimgate_state"]:
            raise RuntimeError(f"{case_id}: ClaimGate state {receipt_value['state']} != {case['expected_claimgate_state']}")
        has_a = contract_a.exists()
        if has_a != bool(case["expect_contract_a"]):
            raise RuntimeError(f"{case_id}: Contract A presence mismatch")

        case_summary: dict[str, Any] = {
            "claimgate": {
                "state": receipt_value["state"],
                "reason": receipt_value.get("reason"),
                "receipt_sha256": sha256_bytes(receipt.read_bytes()),
                "contract_a_emitted": has_a,
            }
        }
        campaign["cases"][case_id] = case_summary

        if not has_a:
            if case["expect_eb"]:
                raise RuntimeError(f"{case_id}: EB expected but no Contract A exists")
            continue

        validate_contract_a(runner, cal_python, c2, contract_a, f"{case_id}-contract-a-validate")
        a_value = json.loads(contract_a.read_text(encoding="utf-8"))
        case_summary["claimgate"]["contract_a_sha256"] = sha256_bytes(contract_a.read_bytes())

        if case_id == "strict-support-raw":
            tampered = json.loads(contract_a.read_text(encoding="utf-8"))
            tampered["root_proposition"]["text"] += " tampered"
            tampered_path = case_root / "contract-a-tampered.json"
            json_write(tampered_path, tampered)
            runner.rejects(
                "control-contract-a-tamper",
                [cal_python, str(c2 / "validators/contract_a_rc2.py"), str(tampered_path)],
            )
            eb_script = eb / "scripts/run_v1_integration_candidate.py"
            carrier = eb / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
            runner.rejects(
                "control-eb-tampered-a",
                [eb_python, str(eb_script), str(tampered_path), "--compatibility-carrier", str(carrier), "--out-dir", str(case_root / "eb-bad-a")],
                cwd=eb,
            )
            campaign["controls"]["contract_a_tamper_rejected"] = True
            campaign["controls"]["eb_rejects_tampered_contract_a"] = True

        bundle, eb_summary = run_eb(runner, eb_python, eb, contract_a, case_root, case_id)
        case_summary["evidence_bundler"] = eb_summary
        if case["downstream"] == "stop_after_eb":
            continue

        target_spec = case["cal_target"]
        proposition_id = a_value["root_proposition"]["proposition_id"]
        root_text = request["root_text"]
        target = {
            "claim_id": proposition_id,
            "proposition": {
                "proposition_id": proposition_id,
                "text_sha256": sha256_text(root_text),
                "semantic_family": target_spec["semantic_family"],
                "fields": target_spec["fields"],
            },
        }
        target_path = case_root / "cal-target.json"
        json_write(target_path, target)
        cal_run, cal_summary = run_cal(
            runner,
            cal_cli,
            cal,
            bundle,
            target_path,
            case_root,
            case_id,
            case["expected_cal"],
        )
        case_summary["cal"] = cal_summary

        if case_id == "strict-support-raw":
            stale = json.loads(target_path.read_text(encoding="utf-8"))
            stale["proposition"]["text_sha256"] = "0" * 64
            stale_path = case_root / "cal-target-stale.json"
            json_write(stale_path, stale)
            runner.rejects("control-cal-stale-hash", [cal_cli, "validate-bundle", str(bundle), str(stale_path)], cwd=cal)
            alias = json.loads(target_path.read_text(encoding="utf-8"))
            alias["proposition"]["proposition_id"] = "alias-proposition"
            alias_path = case_root / "cal-target-alias.json"
            json_write(alias_path, alias)
            runner.rejects("control-cal-alias-id", [cal_cli, "validate-bundle", str(bundle), str(alias_path)], cwd=cal)
            campaign["controls"]["cal_stale_text_hash_rejected"] = True
            campaign["controls"]["cal_alias_id_rejected"] = True

        c2_out, c2_summary = run_c2(
            runner,
            cal_python,
            root,
            cal,
            c2,
            resolver,
            old_resolver,
            bundle,
            target_path,
            case_root,
            case_id,
        )
        case_summary["contract_c2"] = {
            "whole_object_sha256": c2_summary["whole_object_sha256"],
            "producer_policy_resolution": c2_summary["producer_policy_resolution"],
            "resolver_authority": c2_summary["resolver_authority"],
            "hostile_controls": sorted(c2_summary["hostile_controls"]),
        }

        d_path, decision_summary = run_decision(
            runner,
            node,
            decision,
            c2,
            droot,
            c2_out,
            cal_python,
            case_root,
            case_id,
            case["expected_decision_disposition"],
        )
        case_summary["decision"] = decision_summary

        if case_id == "strict-support-raw":
            base_cmd = decision_cmd(
                node,
                decision,
                c2_out / "contract_c2.json",
                c2_summary["whole_object_sha256"],
                c2,
                droot,
                c2_out / "expected_contract_b.json",
                c2_out / "decision_context.json",
                cal_python,
            )
            stale_cmd = base_cmd.copy()
            sha_index = stale_cmd.index("--contract-c2-sha256") + 1
            stale_cmd[sha_index] = "sha256:" + "0" * 64
            runner.rejects("control-decision-stale-c2", stale_cmd, cwd=decision)

            wrong_b = json.loads((c2_out / "expected_contract_b.json").read_text(encoding="utf-8"))
            wrong_b["bundle_id"] = "wrong-bundle"
            wrong_b_path = case_root / "wrong-expected-b.json"
            json_write(wrong_b_path, wrong_b)
            wrong_b_cmd = decision_cmd(
                node,
                decision,
                c2_out / "contract_c2.json",
                c2_summary["whole_object_sha256"],
                c2,
                droot,
                wrong_b_path,
                c2_out / "decision_context.json",
                cal_python,
            )
            runner.rejects("control-decision-wrong-b", wrong_b_cmd, cwd=decision)

            bad_context = json.loads((c2_out / "decision_context.json").read_text(encoding="utf-8"))
            bad_context["target"]["content_sha256"] = "sha256:" + "1" * 64
            bad_context_path = case_root / "bad-decision-context.json"
            json_write(bad_context_path, bad_context)
            bad_context_cmd = decision_cmd(
                node,
                decision,
                c2_out / "contract_c2.json",
                c2_summary["whole_object_sha256"],
                c2,
                droot,
                c2_out / "expected_contract_b.json",
                bad_context_path,
                cal_python,
            )
            runner.rejects("control-decision-target-substitution", bad_context_cmd, cwd=decision)

            wrong_authority_cmd = decision_cmd(
                node,
                decision,
                c2_out / "contract_c2.json",
                c2_summary["whole_object_sha256"],
                droot,
                droot,
                c2_out / "expected_contract_b.json",
                c2_out / "decision_context.json",
                cal_python,
            )
            runner.rejects("control-decision-wrong-c2-authority", wrong_authority_cmd, cwd=decision)
            campaign["controls"].update(
                {
                    "decision_stale_c2_hash_rejected": True,
                    "decision_wrong_b_binding_rejected": True,
                    "decision_target_substitution_rejected": True,
                    "decision_wrong_c2_authority_rejected": True,
                }
            )

        if case.get("contract_e_dry"):
            e_summary_path = case_root / "contract-e-dry-summary.json"
            runner.run(
                f"{case_id}-contract-e-dry",
                [
                    cal_python,
                    str(root / f"qualification/{CAMPAIGN}/contract_e_dry_pressure.py"),
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
            if not all(e_summary["checks"].values()):
                raise RuntimeError("Contract E dry controls were not all satisfied")
            case_summary["contract_e_dry"] = e_summary
            campaign["controls"]["contract_e_dry_controls_pass"] = True

    return campaign


def write_deterministic_archive(evidence_root: Path, build_root: Path) -> dict[str, Any]:
    hashes = dir_hashes(evidence_root)
    hash_path = build_root / f"{CAMPAIGN}-FILE_HASHES.json"
    json_write(hash_path, hashes)
    archive_path = build_root / f"{CAMPAIGN}.tar.gz"
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                used: set[str] = set()
                for path in sorted(evidence_root.rglob("*")):
                    if not path.is_file():
                        continue
                    rel = path.relative_to(evidence_root).as_posix().replace(":", "_")
                    if rel in used:
                        raise RuntimeError(f"archive path collision after sanitization: {rel}")
                    used.add(rel)
                    info = tar.gettarinfo(str(path), arcname=rel)
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with path.open("rb") as handle:
                        tar.addfile(info, handle)
    digest = sha256_bytes(archive_path.read_bytes())
    digest_path = build_root / f"{CAMPAIGN}-ARCHIVE_SHA256.txt"
    digest_path.write_text(digest + "\n", encoding="utf-8")
    return {
        "archive": archive_path.name,
        "archive_sha256": digest,
        "file_hash_manifest": hash_path.name,
        "archive_digest_file": digest_path.name,
        "files": len(hashes),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    qroot = root / f"qualification/{CAMPAIGN}"
    manifest = json.loads((qroot / "MANIFEST.json").read_text(encoding="utf-8"))
    cohort = json.loads((qroot / "COHORT.json").read_text(encoding="utf-8"))
    build_root = root / "build"
    evidence = build_root / CAMPAIGN
    if evidence.exists():
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)

    result: dict[str, Any] = {
        "schema": "cal-pipeline-v1-prototype-freeze-result-v1",
        "manifest": manifest,
        "cohort_sha256": sha256_bytes((qroot / "COHORT.json").read_bytes()),
        "preregistration_sha256": sha256_bytes((qroot / "PREREGISTRATION.md").read_bytes()),
    }
    current_stage = "authority_preflight"
    exit_code = 1
    try:
        preflight_runner = Runner(evidence / "preflight-logs")
        result["authority_preflight"] = authority_preflight(root, preflight_runner, manifest)

        current_stage = "campaign_run_1"
        run1 = execute_campaign(root, evidence / "run-1", cohort, manifest, run_name="run-1")
        current_stage = "campaign_run_2"
        run2 = execute_campaign(root, evidence / "run-2", cohort, manifest, run_name="run-2")

        compare1 = dict(run1)
        compare2 = dict(run2)
        compare1.pop("run", None)
        compare2.pop("run", None)
        same = canonical_bytes(compare1) == canonical_bytes(compare2)
        if not same:
            raise RuntimeError("whole-campaign deterministic replay mismatch")

        result["campaign_run_1"] = run1
        result["campaign_run_2"] = run2
        result["whole_campaign_replay_identical"] = True
        result["case_count"] = len(cohort["cases"])
        result["classification"] = "CAL_PIPELINE_V1_PROTOTYPE_CANDIDATE_FROZEN_FOR_LOCAL_SMOKE"
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 - preserve terminal qualification failure
        result["classification"] = "FALSIFIED_CAL_PIPELINE_V1_PROTOTYPE_FREEZE_RC0"
        result["failure_stage"] = current_stage
        result["error"] = str(exc)
        result["traceback"] = traceback.format_exc()

    json_write(evidence / "RESULT.json", result)
    archive = write_deterministic_archive(evidence, build_root)
    result["evidence_package"] = archive
    json_write(evidence / "RESULT.json", result)
    # Rebuild once so the archive includes the final RESULT with the package metadata.
    archive = write_deterministic_archive(evidence, build_root)
    result["evidence_package"] = archive
    json_write(evidence / "RESULT.json", result)

    print(json.dumps({"classification": result["classification"], "evidence_package": archive}, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
