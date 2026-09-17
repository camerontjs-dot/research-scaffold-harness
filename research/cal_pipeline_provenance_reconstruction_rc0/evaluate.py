#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

APPARATUS_COMMIT = "1a5929295e735e351320cbd8c966dc43afed2859"
CAL_RECEIPT_COMMIT = "93c4f162c0f22a5c2e599fd332160628bc8b2986"
ATT_SCHEMA_URL = (
    "https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/"
    + APPARATUS_COMMIT
    + "/research/provenance-chain-v1-candidate/apparatus-attestation.schema.json"
)
MANIFEST_SCHEMA_URL = (
    "https://raw.githubusercontent.com/camerontjs-dot/apparatus-contracts/"
    + APPARATUS_COMMIT
    + "/research/provenance-chain-v1-candidate/run-manifest.schema.json"
)
PORTABLE_RECEIPT_URL = (
    "https://raw.githubusercontent.com/camerontjs-dot/claim-audit-lab/"
    + CAL_RECEIPT_COMMIT
    + "/research/first_genuine_b_side_001/PORTABLE_RECEIPT.md"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return (
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "cal-pipeline-provenance-rc0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def seal_attestation(obj: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(obj)
    base.pop("attestation_id", None)
    base.pop("attestation_sha256", None)
    digest = sha256_bytes(canonical_json_bytes(base))
    obj = copy.deepcopy(base)
    obj["attestation_id"] = f"attestation:sha256:{digest}"
    obj["attestation_sha256"] = f"sha256:{digest}"
    return obj


def attestation_digest(obj: dict[str, Any]) -> str:
    base = copy.deepcopy(obj)
    base.pop("attestation_id", None)
    base.pop("attestation_sha256", None)
    return sha256_bytes(canonical_json_bytes(base))


def seal_manifest(obj: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(obj)
    base.pop("manifest_id", None)
    base.pop("manifest_sha256", None)
    digest = sha256_bytes(canonical_json_bytes(base))
    obj = copy.deepcopy(base)
    obj["manifest_id"] = f"run-manifest:sha256:{digest}"
    obj["manifest_sha256"] = f"sha256:{digest}"
    return obj


def manifest_digest(obj: dict[str, Any]) -> str:
    base = copy.deepcopy(obj)
    base.pop("manifest_id", None)
    base.pop("manifest_sha256", None)
    return sha256_bytes(canonical_json_bytes(base))


def artifact_ref(kind: str, logical_id: str, data: bytes) -> dict[str, Any]:
    return {
        "kind": kind,
        "logical_id": logical_id,
        "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{sha256_bytes(data)}"}],
    }


def artifact_entry(
    artifact_id: str,
    kind: str,
    logical_id: str,
    data: bytes,
    path: Path,
    required: bool = True,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "logical_id": logical_id,
        "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{sha256_bytes(data)}"}],
        "retention": {
            "state": "retained_verified",
            "locators": [{"kind": "filesystem", "value": str(path)}],
        },
        "required_for_reconstruction": required,
    }


def expected_sha256(commitments: list[dict[str, str]]) -> str | None:
    for c in commitments:
        if c["scheme"] == "sha256-bytes" and re.fullmatch(r"sha256:[0-9a-f]{64}", c["value"]):
            return c["value"].split(":", 1)[1]
    return None


def recover_artifact(entry: dict[str, Any], base_dir: Path) -> tuple[bool, str]:
    retention = entry["retention"]
    if retention["state"] in {"locator_absent", "unknown"} or not retention["locators"]:
        return False, "locator_absent"
    locator = retention["locators"][0]
    try:
        if locator["kind"] == "filesystem":
            p = Path(locator["value"])
            if not p.is_absolute():
                p = base_dir / p
            data = p.read_bytes()
        elif locator["kind"] == "github_raw":
            data = fetch_bytes(locator["value"])
        else:
            return False, "unsupported_locator"
    except Exception:
        return False, "bytes_unavailable"
    expected = expected_sha256(entry["commitments"])
    if expected is not None and sha256_bytes(data) != expected:
        return False, "digest_mismatch"
    return True, "verified"


def evaluate_reconstruction(
    manifest: dict[str, Any],
    manifest_schema: dict[str, Any],
    expected_manifest_sha256: str,
    base_dir: Path,
) -> dict[str, Any]:
    Draft202012Validator(manifest_schema).validate(manifest)
    actual_manifest_digest = manifest_digest(manifest)
    if actual_manifest_digest != expected_manifest_sha256:
        return {
            "status": "not_reconstructable",
            "root_verified": False,
            "gaps": [{"artifact_id": "run_manifest", "reason": "digest_mismatch"}],
            "verified_artifacts": [],
        }

    by_id = {a["artifact_id"]: a for a in manifest["artifacts"]}
    gaps: list[dict[str, str]] = []
    verified: list[str] = []
    for artifact_id in manifest["reconstruction"]["required_artifact_ids"]:
        entry = by_id.get(artifact_id)
        if entry is None:
            gaps.append({"artifact_id": artifact_id, "reason": "identity_absent"})
            continue
        ok, reason = recover_artifact(entry, base_dir)
        if ok:
            verified.append(artifact_id)
        else:
            normalized = reason if reason in {
                "locator_absent",
                "bytes_unavailable",
                "digest_mismatch",
            } else "other"
            gaps.append({"artifact_id": artifact_id, "reason": normalized})

    for stage in manifest["stages"]:
        if stage["state"] == "not_present":
            continue
        aid = stage["attestation_artifact_id"]
        if aid is None or aid not in by_id:
            gaps.append({"artifact_id": f"{stage['stage_id']}:attestation", "reason": "attestation_absent"})

    if not gaps:
        status = "reconstructable"
    elif verified:
        status = "partial"
    else:
        status = "not_reconstructable"
    return {
        "status": status,
        "root_verified": True,
        "gaps": gaps,
        "verified_artifacts": verified,
    }


def make_synthetic_complete(out: Path, att_schema: dict[str, Any], manifest_schema: dict[str, Any]) -> dict[str, Any]:
    root = out / "synthetic"
    root.mkdir(parents=True, exist_ok=True)

    payloads: dict[str, bytes] = {
        "raw_claim": b"Atlas closing time was 0.74 seconds.\n",
        "raw_source": b"Bench test: Atlas closing time 0.74 seconds.\n",
        "claim_gate": canonical_json_bytes({"state": "NOT_NEEDED", "claim": "atlas"}),
        "evidence_gate": canonical_json_bytes({"evidence_world_id": "world:synthetic"}),
        "contract_a": canonical_json_bytes({"contract": "A", "claim": "atlas"}),
        "contract_b": canonical_json_bytes({"contract": "B", "passage": "p1"}),
        "cal_result": canonical_json_bytes({"relation": "supports"}),
        "contract_c": canonical_json_bytes({"contract": "C", "verdict": "supported"}),
        "contract_d": canonical_json_bytes({"contract": "D", "disposition": "clear"}),
    }
    paths: dict[str, Path] = {}
    for name, data in payloads.items():
        p = root / f"{name}.json"
        if name in {"raw_claim", "raw_source"}:
            p = root / f"{name}.txt"
        p.write_bytes(data)
        paths[name] = p

    implementation = {
        "kind": "git",
        "repository": "camerontjs-dot/research-scaffold-harness",
        "commit_sha": "3ed53b13de18e16aa17e71a602218481bad4fc5e",
    }
    empty_authority = [{"kind": "research-control", "id": "synthetic-v1", "immutable_id": "synthetic-v1"}]

    stage_defs = [
        ("claim-gate", "claim_gate", [
            ("causal_input", "raw_claim"),
            ("observed_context", "raw_source"),
        ], "claim_gate"),
        ("evidence-gate", "evidence_gate", [
            ("causal_input", "raw_source"),
            ("observed_context", "raw_claim"),
        ], "evidence_gate"),
        ("evidence-bundler", "evidence_bundler", [
            ("causal_input", "contract_a"),
            ("observed_context", "evidence_gate"),
        ], "contract_b"),
        ("cal", "claim_audit_lab", [
            ("causal_input", "contract_b"),
        ], "contract_c"),
        ("decision", "decision_engine", [
            ("causal_input", "contract_c"),
            ("authority_input", "contract_b"),
        ], "contract_d"),
    ]

    attestations: dict[str, dict[str, Any]] = {}
    for sid, skind, inputs, output_name in stage_defs:
        input_refs = []
        for role, name in inputs:
            input_refs.append({"role": role, "artifact": artifact_ref(name, name, payloads[name])})
        att = {
            "attestation_schema": "cal-pipeline-apparatus-attestation-v1-candidate",
            "stage": {"id": sid, "kind": skind},
            "producer": {"system_id": sid, "implementation": implementation},
            "run": {"run_id": "synthetic-complete-001", "work_id": "synthetic-work-001"},
            "inputs": input_refs,
            "authorities": empty_authority,
            "configuration": {"identities": [artifact_ref("config", f"{sid}-config", f"{sid}:config:v1\n".encode())]},
            "operation": {"name": f"{sid}-operation", "version": "1"},
            "outputs": [artifact_ref(output_name, output_name, payloads[output_name])],
            "execution": {"state": "completed", "reason_code": None},
        }
        sealed = seal_attestation(att)
        Draft202012Validator(att_schema).validate(sealed)
        ap = root / f"attestation-{sid}.json"
        ap.write_bytes(canonical_json_bytes(sealed))
        attestations[sid] = {"object": sealed, "path": ap, "bytes": ap.read_bytes()}

    artifacts: list[dict[str, Any]] = []
    for name, data in payloads.items():
        artifacts.append(artifact_entry(name, name, name, data, paths[name], True))
    for sid, rec in attestations.items():
        artifacts.append(
            artifact_entry(
                f"attestation-{sid}",
                "apparatus-attestation",
                rec["object"]["attestation_id"],
                rec["bytes"],
                rec["path"],
                True,
            )
        )

    required = [a["artifact_id"] for a in artifacts]
    manifest_base = {
        "manifest_schema": "cal-pipeline-run-manifest-v1-candidate",
        "run_id": "synthetic-complete-001",
        "work_id": "synthetic-work-001",
        "root_inputs": ["raw_claim", "raw_source"],
        "artifacts": artifacts,
        "stages": [
            {
                "stage_id": sid,
                "stage_kind": skind,
                "state": "completed",
                "attestation_artifact_id": f"attestation-{sid}",
            }
            for sid, skind, _, _ in stage_defs
        ],
        "authorities": empty_authority,
        "reconstruction": {
            "required_artifact_ids": required,
            "status": "not_evaluated",
            "missing_or_unresolved": [],
            "notes": ["Synthetic positive control only."],
        },
    }
    manifest = seal_manifest(manifest_base)
    Draft202012Validator(manifest_schema).validate(manifest)
    mp = root / "RUN-MANIFEST.json"
    mp.write_bytes(canonical_json_bytes(manifest))
    trusted_root = manifest_digest(manifest)

    positive = evaluate_reconstruction(manifest, manifest_schema, trusted_root, Path("/"))

    # Weak 1: mutate retained bytes without moving the independently pinned commitment.
    original_b = paths["contract_b"].read_bytes()
    paths["contract_b"].write_bytes(original_b + b"mutated\n")
    mutation = evaluate_reconstruction(manifest, manifest_schema, trusted_root, Path("/"))
    paths["contract_b"].write_bytes(original_b)

    # Weak 2: a separately pinned control manifest honestly omits one required locator.
    no_locator_manifest = copy.deepcopy(manifest)
    for a in no_locator_manifest["artifacts"]:
        if a["artifact_id"] == "contract_b":
            a["retention"] = {"state": "locator_absent", "locators": []}
    no_locator_manifest = seal_manifest(no_locator_manifest)
    no_locator_root = manifest_digest(no_locator_manifest)
    no_locator = evaluate_reconstruction(no_locator_manifest, manifest_schema, no_locator_root, Path("/"))

    # Weak 3: attacker moves bytes + manifest commitment + self-hash, but external root stays fixed.
    moved = copy.deepcopy(manifest)
    attacker_bytes = b'{"contract":"B","passage":"ATTACKER"}\n'
    attacker_path = root / "contract_b_attacker.json"
    attacker_path.write_bytes(attacker_bytes)
    for a in moved["artifacts"]:
        if a["artifact_id"] == "contract_b":
            a["commitments"] = [{"scheme": "sha256-bytes", "value": f"sha256:{sha256_bytes(attacker_bytes)}"}]
            a["retention"] = {"state": "retained_verified", "locators": [{"kind": "filesystem", "value": str(attacker_path)}]}
    moved = seal_manifest(moved)
    moving_root_strong = evaluate_reconstruction(moved, manifest_schema, trusted_root, Path("/"))
    moving_root_weak = evaluate_reconstruction(moved, manifest_schema, manifest_digest(moved), Path("/"))

    # Weak 4: role mutation must alter the attestation identity.
    eb = attestations["evidence-bundler"]["object"]
    role_mut = copy.deepcopy(eb)
    role_mut["inputs"][1]["role"] = "causal_input"
    role_mut = seal_attestation(role_mut)
    role_identity_changed = role_mut["attestation_id"] != eb["attestation_id"]

    # Weak 5: removing behaviorally relevant configuration must alter identity.
    cfg_mut = copy.deepcopy(eb)
    cfg_mut["configuration"]["identities"] = []
    cfg_mut = seal_attestation(cfg_mut)
    config_identity_changed = cfg_mut["attestation_id"] != eb["attestation_id"]

    return {
        "positive": positive,
        "mutation_without_commitment_move": mutation,
        "locator_absent": no_locator,
        "moving_root_strong": moving_root_strong,
        "moving_root_weak": moving_root_weak,
        "role_identity_changed": role_identity_changed,
        "config_identity_changed": config_identity_changed,
        "trusted_manifest_sha256": f"sha256:{trusted_root}",
        "manifest": manifest,
    }


def extract_receipt_value(text: str, label: str) -> str:
    pattern = rf"\| {re.escape(label)} \| (.*?) \|"
    m = re.search(pattern, text)
    if not m:
        raise ValueError(f"missing receipt row: {label}")
    return m.group(1)


def parse_sha(text: str) -> str:
    m = re.search(r"sha256:([0-9a-f]{64})", text)
    if not m:
        raise ValueError(f"missing sha256 in: {text}")
    return m.group(1)


def check_public_commit(repo: str, sha: str) -> bool:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    try:
        data = json.loads(fetch_bytes(url).decode("utf-8"))
        return data.get("sha") == sha
    except Exception:
        return False


def make_first_genuine(out: Path, manifest_schema: dict[str, Any]) -> dict[str, Any]:
    root = out / "first-genuine"
    root.mkdir(parents=True, exist_ok=True)
    receipt_bytes = fetch_bytes(PORTABLE_RECEIPT_URL)
    receipt_path = root / "PORTABLE_RECEIPT.md"
    receipt_path.write_bytes(receipt_bytes)
    receipt = receipt_bytes.decode("utf-8")

    source_sha = parse_sha(extract_receipt_value(receipt, "Source payload"))
    b_row = extract_receipt_value(receipt, "Contract B")
    b_bundle_match = re.search(r"bundle `([^`]+)`", b_row)
    if not b_bundle_match:
        raise ValueError("missing Contract B bundle id")
    b_bundle_id = b_bundle_match.group(1)
    b_hash = parse_sha(b_row)
    cal_sha = parse_sha(extract_receipt_value(receipt, "CAL result"))
    c2_sha = parse_sha(extract_receipt_value(receipt, "C2 object"))
    d_sha = parse_sha(extract_receipt_value(receipt, "Contract D output"))
    freeze_sha = parse_sha(extract_receipt_value(receipt, "Freeze manifest"))
    exec_sha = parse_sha(extract_receipt_value(receipt, "Execution receipt"))

    artifacts = [
        {
            "artifact_id": "portable_receipt",
            "kind": "portable-receipt",
            "logical_id": "FIRST-GENUINE-B-SIDE-001",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{sha256_bytes(receipt_bytes)}"}],
            "retention": {"state": "retained_verified", "locators": [{"kind": "github_raw", "value": PORTABLE_RECEIPT_URL}]},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "source_payload",
            "kind": "source-payload",
            "logical_id": "FIRST-GENUINE-B-SIDE-001",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{source_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "contract_b",
            "kind": "contract-b",
            "logical_id": b_bundle_id,
            "commitments": [{"scheme": "contract-b-bundle-hash", "value": f"sha256:{b_hash}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "cal_result",
            "kind": "cal-native-result",
            "logical_id": "FIRST-GENUINE-B-SIDE-001:cal-result",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{cal_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "contract_c2",
            "kind": "contract-c2",
            "logical_id": "FIRST-GENUINE-B-SIDE-001:c2",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{c2_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "contract_d",
            "kind": "contract-d",
            "logical_id": "FIRST-GENUINE-B-SIDE-001:d",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{d_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "freeze_manifest",
            "kind": "freeze-manifest",
            "logical_id": "FIRST-GENUINE-B-SIDE-001:freeze",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{freeze_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
        {
            "artifact_id": "execution_receipt",
            "kind": "execution-receipt",
            "logical_id": "FIRST-GENUINE-B-SIDE-001:execution",
            "commitments": [{"scheme": "sha256-bytes", "value": f"sha256:{exec_sha}"}],
            "retention": {"state": "locator_absent", "locators": []},
            "required_for_reconstruction": True,
        },
    ]

    authorities = [
        {"kind": "git-implementation", "id": "evidence-bundler", "immutable_id": "4e1f6fe00e7c350b28f52bfea14f1f8988847884"},
        {"kind": "git-implementation", "id": "cal-c2-authority", "immutable_id": "8204417f478cfbd891499145a7edec5ee33405ad"},
        {"kind": "git-implementation", "id": "cal-semantic-implementation", "immutable_id": "847cc970642bb648dc994b929c2053b5c9d4648c"},
        {"kind": "git-contract-authority", "id": "contract-c2", "immutable_id": "b42c827acb0a9fe65353354d709add0e27bab307"},
        {"kind": "git-resolver-authority", "id": "cal-policy-resolver", "immutable_id": "1d33e0612befcf8016816197c90c062373796df9"},
        {"kind": "git-contract-authority", "id": "contract-d", "immutable_id": "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"},
        {"kind": "git-implementation", "id": "decision-engine", "immutable_id": "b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55"},
    ]

    authority_checks = {
        "evidence_bundler": check_public_commit("camerontjs-dot/evidence-bundler", "4e1f6fe00e7c350b28f52bfea14f1f8988847884"),
        "cal_c2": check_public_commit("camerontjs-dot/claim-audit-lab", "8204417f478cfbd891499145a7edec5ee33405ad"),
        "cal_semantic": check_public_commit("camerontjs-dot/claim-audit-lab", "847cc970642bb648dc994b929c2053b5c9d4648c"),
        "contract_c2": check_public_commit("camerontjs-dot/apparatus-contracts", "b42c827acb0a9fe65353354d709add0e27bab307"),
        "resolver": check_public_commit("camerontjs-dot/apparatus-contracts", "1d33e0612befcf8016816197c90c062373796df9"),
        "contract_d": check_public_commit("camerontjs-dot/apparatus-contracts", "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"),
        "decision_engine": check_public_commit("camerontjs-dot/decision-engine", "b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55"),
    }

    required = [
        "portable_receipt",
        "source_payload",
        "contract_a",
        "eb_native_package",
        "contract_b",
        "cal_result",
        "contract_c2",
        "contract_d",
        "freeze_manifest",
        "execution_receipt",
    ]
    manifest_base = {
        "manifest_schema": "cal-pipeline-run-manifest-v1-candidate",
        "run_id": "FIRST-GENUINE-B-SIDE-001",
        "work_id": "FIRST-GENUINE-B-SIDE-001",
        "root_inputs": ["source_payload"],
        "artifacts": artifacts,
        "stages": [
            {"stage_id": "evidence-bundler", "stage_kind": "evidence_bundler", "state": "completed", "attestation_artifact_id": None},
            {"stage_id": "cal", "stage_kind": "claim_audit_lab", "state": "completed", "attestation_artifact_id": None},
            {"stage_id": "decision", "stage_kind": "decision_engine", "state": "completed", "attestation_artifact_id": None},
        ],
        "authorities": authorities,
        "reconstruction": {
            "required_artifact_ids": required,
            "status": "not_evaluated",
            "missing_or_unresolved": [],
            "notes": [
                "Derived only from the portable public receipt. No omitted locator or private runtime state was invented.",
                "ClaimGate/EvidenceGate are not added retroactively because this historical run record does not state that they participated."
            ],
        },
    }
    manifest = seal_manifest(manifest_base)
    Draft202012Validator(manifest_schema).validate(manifest)
    mp = root / "FIRST-GENUINE-RUN-MANIFEST-CANDIDATE.json"
    mp.write_bytes(canonical_json_bytes(manifest))
    result = evaluate_reconstruction(manifest, manifest_schema, manifest_digest(manifest), Path("/"))

    return {
        "receipt_sha256": f"sha256:{sha256_bytes(receipt_bytes)}",
        "parsed": {
            "source_payload_sha256": f"sha256:{source_sha}",
            "contract_b_bundle_id": b_bundle_id,
            "contract_b_bundle_hash": f"sha256:{b_hash}",
            "cal_result_sha256": f"sha256:{cal_sha}",
            "contract_c2_sha256": f"sha256:{c2_sha}",
            "contract_d_sha256": f"sha256:{d_sha}",
            "freeze_manifest_sha256": f"sha256:{freeze_sha}",
            "execution_receipt_sha256": f"sha256:{exec_sha}",
        },
        "authority_commit_checks": authority_checks,
        "reconstruction": result,
        "manifest": manifest,
    }


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "provenance-rc0-out").resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    att_schema = json.loads(fetch_bytes(ATT_SCHEMA_URL))
    manifest_schema = json.loads(fetch_bytes(MANIFEST_SCHEMA_URL))
    Draft202012Validator.check_schema(att_schema)
    Draft202012Validator.check_schema(manifest_schema)

    synthetic = make_synthetic_complete(out, att_schema, manifest_schema)
    first_genuine = make_first_genuine(out, manifest_schema)

    phase_a_pass = all([
        synthetic["positive"]["status"] == "reconstructable",
        any(g["reason"] == "digest_mismatch" for g in synthetic["mutation_without_commitment_move"]["gaps"]),
        synthetic["locator_absent"]["status"] in {"partial", "not_reconstructable"},
        synthetic["moving_root_strong"]["root_verified"] is False,
        synthetic["moving_root_weak"]["status"] == "reconstructable",
        synthetic["role_identity_changed"] is True,
        synthetic["config_identity_changed"] is True,
    ])

    first_status = first_genuine["reconstruction"]["status"]
    authority_checks_pass = all(first_genuine["authority_commit_checks"].values())

    if not phase_a_pass:
        disposition = "FALSIFIED_PROVENANCE_SCHEMA_OR_EVALUATOR"
    elif first_status == "reconstructable" and authority_checks_pass:
        disposition = "SUPPORTED_FIRST_GENUINE_RECONSTRUCTABLE"
    elif first_status in {"partial", "not_reconstructable"} and authority_checks_pass:
        disposition = "SUPPORTED_RECONSTRUCTION_ARCHITECTURE_WITH_RETENTION_GAP"
    else:
        disposition = "INCONCLUSIVE_APPARATUS"

    result = {
        "schema": "cal-pipeline-provenance-reconstruction-rc0-result",
        "disposition": disposition,
        "apparatus": {
            "provenance_schema_commit": APPARATUS_COMMIT,
            "portable_receipt_commit": CAL_RECEIPT_COMMIT,
            "attestation_schema_url": ATT_SCHEMA_URL,
            "manifest_schema_url": MANIFEST_SCHEMA_URL,
            "portable_receipt_url": PORTABLE_RECEIPT_URL,
        },
        "phase_a": {
            "passed": phase_a_pass,
            "synthetic_positive_status": synthetic["positive"]["status"],
            "mutation_control": synthetic["mutation_without_commitment_move"],
            "missing_locator_control": synthetic["locator_absent"],
            "moving_root_strong": synthetic["moving_root_strong"],
            "weak_caller_selected_root_accepts": synthetic["moving_root_weak"]["status"] == "reconstructable",
            "role_identity_changed": synthetic["role_identity_changed"],
            "config_identity_changed": synthetic["config_identity_changed"],
            "trusted_manifest_sha256": synthetic["trusted_manifest_sha256"],
        },
        "phase_b": {
            "first_genuine_reconstruction": first_genuine["reconstruction"],
            "authority_commit_checks": first_genuine["authority_commit_checks"],
            "parsed_receipt_identities": first_genuine["parsed"],
            "portable_receipt_sha256": first_genuine["receipt_sha256"],
        },
        "nonclaims": [
            "This is not a clean-room independent reproduction.",
            "The result does not establish semantic correctness of Evidence Bundler, CAL, Contract C2, Decision Engine, or Contract D.",
            "Locator absence in the public/authorized aperture does not prove the historical local bytes were destroyed.",
            "No released Contract A/B/C/D schema is modified or promoted by this result.",
        ],
    }
    (out / "RESULT.json").write_bytes(canonical_json_bytes(result))

    gaps = first_genuine["reconstruction"]["gaps"]
    lines = [
        "# CAL Pipeline provenance reconstruction RC0 result",
        "",
        f"**Disposition:** `{disposition}`",
        "",
        "## Phase A",
        "",
        f"- synthetic complete chain: `{synthetic['positive']['status']}`",
        f"- changed artifact / fixed commitment detected: `{any(g['reason'] == 'digest_mismatch' for g in synthetic['mutation_without_commitment_move']['gaps'])}`",
        f"- missing required locator fails reconstructability: `{synthetic['locator_absent']['status']}`",
        f"- moving bytes + manifest while external root fixed rejected: `{synthetic['moving_root_strong']['root_verified'] is False}`",
        f"- deliberately weak caller-selected root accepts moving world: `{synthetic['moving_root_weak']['status'] == 'reconstructable'}`",
        f"- observed_context -> causal_input changes attestation identity: `{synthetic['role_identity_changed']}`",
        f"- removing configuration identity changes attestation identity: `{synthetic['config_identity_changed']}`",
        "",
        "## Phase B: first genuine run",
        "",
        f"Reconstruction status: `{first_status}`.",
        "",
        "The portable receipt was recovered and parsed. Public Git commit identities named by the receipt were independently resolved. The historical raw artifacts and producer attestations below were not invented when the receipt did not expose a locator or identity.",
        "",
        "### Gaps",
        "",
    ]
    for g in gaps:
        lines.append(f"- `{g['artifact_id']}`: `{g['reason']}`")
    lines += [
        "",
        "## Interpretation",
        "",
        "The candidate provenance layer discriminates a fully retained/reconstructable run from a historical commitment-only record. The first-genuine portable receipt preserves valuable identities, but it is not itself a complete reconstruction package. The next real pipeline execution should emit producer attestations at each stage and a run manifest containing durable locators for every artifact required by the reconstruction policy.",
        "",
        "This RC0 does not claim independent reproduction. A context-free consumer remains a later gate.",
    ]
    (out / "RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if disposition in {
        "SUPPORTED_FIRST_GENUINE_RECONSTRUCTABLE",
        "SUPPORTED_RECONSTRUCTION_ARCHITECTURE_WITH_RETENTION_GAP",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
