"""Fresh clean-room implementation of Contract C successor RC1."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from typing import Any

VERSION = "research-contract-c-successor-rc1"
H40 = re.compile(r"^[0-9a-f]{40}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
CID = re.compile(r"^contribution:[0-9a-f]{64}$")
RID = re.compile(r"^result-set:[0-9a-f]{64}$")


class DuplicateKey(ValueError):
    pass


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKey(f"duplicate JSON object key: {key!r}")
        out[key] = value
    return out


def _constant(text):
    raise ValueError(f"non-finite JSON number: {text}")


def canonical_bytes(value: dict) -> bytes:
    if not isinstance(value, dict):
        raise TypeError("canonical_bytes requires a JSON object")
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def result_set_identity(value: dict) -> str:
    if not isinstance(value, dict):
        raise TypeError("result_set_identity requires a JSON object")
    reduced = copy.deepcopy(value)
    reduced.pop("result_set_id", None)
    return "result-set:" + hashlib.sha256(canonical_bytes(reduced)).hexdigest()


def _add(errors, path, msg):
    errors.append(f"{path}: {msg}")


def _exact(value, keys, path, errors):
    if not isinstance(value, dict):
        _add(errors, path, "must be an object")
        return False
    actual = set(value)
    missing, extra = keys - actual, actual - keys
    if missing:
        _add(errors, path, "missing field(s): " + ", ".join(sorted(missing)))
    if extra:
        _add(errors, path, "unknown field(s): " + ", ".join(sorted(extra)))
    return not missing and not extra


def _nonempty(value):
    return isinstance(value, str) and bool(value)


def _finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and (not isinstance(value, float) or math.isfinite(value))


def _assessment(value, path, errors):
    if not isinstance(value, dict):
        _add(errors, path, "must be an object")
        return
    state = value.get("state")
    if state == "performed":
        if _exact(value, {"state", "value"}, path, errors) and value.get("value") not in {"unknown", "adverse"}:
            _add(errors, path + ".value", "unknown assessment value")
    elif state in {"not_performed", "not_applicable", "failed"}:
        _exact(value, {"state"}, path, errors)
    else:
        _add(errors, path + ".state", "unknown assessment state")
        _exact(value, {"state"}, path, errors)


def _prop_execution(value, path, errors):
    if not isinstance(value, dict):
        _add(errors, path, "must be an object")
        return
    state = value.get("state")
    if state == "completed":
        if _exact(value, {"state", "completion"}, path, errors) and value.get("completion") not in {"assessed", "not_checkable"}:
            _add(errors, path + ".completion", "unknown completion")
    elif state in {"failed", "incomplete"}:
        _exact(value, {"state"}, path, errors)
    else:
        _add(errors, path + ".state", "unknown proposition execution state")
        _exact(value, {"state"}, path, errors)


def _index(index, errors):
    keys = {"contract_version", "bundle_id", "bundle_hash", "propositions", "passages"}
    exact = _exact(index, keys, "contract_b_index", errors)
    if not isinstance(index, dict):
        return False
    ok = exact
    if not _nonempty(index.get("contract_version")):
        _add(errors, "contract_b_index.contract_version", "must be non-empty")
        ok = False
    if not _nonempty(index.get("bundle_id")):
        _add(errors, "contract_b_index.bundle_id", "must be non-empty")
        ok = False
    if not isinstance(index.get("bundle_hash"), str) or not SHA.fullmatch(index["bundle_hash"]):
        _add(errors, "contract_b_index.bundle_hash", "invalid sha256 binding")
        ok = False
    props = index.get("propositions")
    if not isinstance(props, dict):
        _add(errors, "contract_b_index.propositions", "must be an object")
        ok = False
    else:
        for key, digest in props.items():
            if not _nonempty(key) or not isinstance(digest, str) or not H64.fullmatch(digest):
                _add(errors, f"contract_b_index.propositions[{key!r}]", "invalid proposition index entry")
                ok = False
    passages = index.get("passages")
    if not isinstance(passages, dict):
        _add(errors, "contract_b_index.passages", "must be an object")
        ok = False
    else:
        for key, passage in passages.items():
            path = f"contract_b_index.passages[{key!r}]"
            if not _nonempty(key) or not _exact(passage, {"source_id", "passage_sha256"}, path, errors):
                ok = False
                continue
            if not _nonempty(passage.get("source_id")) or not isinstance(passage.get("passage_sha256"), str) or not SHA.fullmatch(passage["passage_sha256"]):
                _add(errors, path, "invalid passage index entry")
                ok = False
    return ok


def _validate(value, errors, index):
    top = {"contract_c_version", "input", "producer", "execution", "propositions", "result_set_id"}
    if not _exact(value, top, "$", errors) and not isinstance(value, dict):
        return
    if value.get("contract_c_version") != VERSION:
        _add(errors, "$.contract_c_version", "wrong exact research version")

    inp = value.get("input")
    cb = None
    if _exact(inp, {"contract_b"}, "$.input", errors):
        cb = inp["contract_b"]
        if _exact(cb, {"contract_version", "bundle_id", "bundle_hash"}, "$.input.contract_b", errors):
            if not _nonempty(cb.get("contract_version")) or not _nonempty(cb.get("bundle_id")):
                _add(errors, "$.input.contract_b", "version and bundle_id must be non-empty")
            if not isinstance(cb.get("bundle_hash"), str) or not SHA.fullmatch(cb["bundle_hash"]):
                _add(errors, "$.input.contract_b.bundle_hash", "invalid sha256 binding")

    producer = value.get("producer")
    policy = None
    if _exact(producer, {"semantic_implementation_sha", "policy"}, "$.producer", errors):
        if not isinstance(producer.get("semantic_implementation_sha"), str) or not H40.fullmatch(producer["semantic_implementation_sha"]):
            _add(errors, "$.producer.semantic_implementation_sha", "must be 40 lowercase hex")
        policy = producer.get("policy")
        if _exact(policy, {"canonical", "sha256"}, "$.producer.policy", errors):
            if not isinstance(policy.get("canonical"), dict):
                _add(errors, "$.producer.policy.canonical", "must be an object")
            if not isinstance(policy.get("sha256"), str) or not H64.fullmatch(policy["sha256"]):
                _add(errors, "$.producer.policy.sha256", "must be 64 lowercase hex")

    execution = value.get("execution")
    if _exact(execution, {"state"}, "$.execution", errors) and execution.get("state") not in {"completed", "failed", "incomplete"}:
        _add(errors, "$.execution.state", "unknown state")

    props = value.get("propositions")
    if not isinstance(props, list):
        _add(errors, "$.propositions", "must be an array")
        props = []
    elif isinstance(execution, dict) and execution.get("state") == "completed" and not props:
        _add(errors, "$.propositions", "completed result set must be non-empty")

    rsid = value.get("result_set_id")
    if not isinstance(rsid, str) or not RID.fullmatch(rsid):
        _add(errors, "$.result_set_id", "invalid result-set identity syntax")

    seen_props = set()
    for i, prop in enumerate(props):
        pp = f"$.propositions[{i}]"
        keys = {"proposition", "execution", "assessments", "contributions", "measurement", "conclusion"}
        if not _exact(prop, keys, pp, errors) and not isinstance(prop, dict):
            continue

        binding = prop.get("proposition")
        pid = text_sha = None
        if _exact(binding, {"proposition_id", "text_sha256"}, pp + ".proposition", errors):
            pid, text_sha = binding.get("proposition_id"), binding.get("text_sha256")
            if not _nonempty(pid):
                _add(errors, pp + ".proposition.proposition_id", "must be non-empty")
                pid = None
            elif pid in seen_props:
                _add(errors, pp + ".proposition.proposition_id", "duplicate proposition ID")
            else:
                seen_props.add(pid)
            if not isinstance(text_sha, str) or not H64.fullmatch(text_sha):
                _add(errors, pp + ".proposition.text_sha256", "must be 64 lowercase hex")
                text_sha = None

        pexec = prop.get("execution")
        _prop_execution(pexec, pp + ".execution", errors)
        assessments = prop.get("assessments")
        slots = {"eligibility", "semantic_validity", "aperture_completeness", "temporal_applicability"}
        if _exact(assessments, slots, pp + ".assessments", errors):
            for slot in slots:
                _assessment(assessments[slot], pp + ".assessments." + slot, errors)

        contributions = prop.get("contributions")
        if not isinstance(contributions, list):
            _add(errors, pp + ".contributions", "must be an array")
            contributions = []
        cids, refs = set(), {}
        for j, contribution in enumerate(contributions):
            cp = pp + f".contributions[{j}]"
            if not _exact(contribution, {"contribution_id", "channel", "evidence_ref"}, cp, errors) and not isinstance(contribution, dict):
                continue
            cid = contribution.get("contribution_id")
            if not isinstance(cid, str) or not CID.fullmatch(cid):
                _add(errors, cp + ".contribution_id", "invalid contribution ID")
                cid = None
            elif cid in cids:
                _add(errors, cp + ".contribution_id", "duplicate contribution ID")
            else:
                cids.add(cid)
            if contribution.get("channel") not in {"support", "counterevidence", "non_deciding"}:
                _add(errors, cp + ".channel", "unknown channel")
            ref = contribution.get("evidence_ref")
            if _exact(ref, {"source_id", "passage_id", "passage_sha256"}, cp + ".evidence_ref", errors):
                if not _nonempty(ref.get("source_id")) or not _nonempty(ref.get("passage_id")):
                    _add(errors, cp + ".evidence_ref", "source_id and passage_id must be non-empty")
                if not isinstance(ref.get("passage_sha256"), str) or not SHA.fullmatch(ref["passage_sha256"]):
                    _add(errors, cp + ".evidence_ref.passage_sha256", "invalid passage hash")
                if cid is not None:
                    refs[cid] = ref

        measurement = prop.get("measurement")
        if measurement is not None and _exact(measurement, {"kind", "value", "basis_contribution_ids"}, pp + ".measurement", errors):
            if not _nonempty(measurement.get("kind")):
                _add(errors, pp + ".measurement.kind", "must be non-empty")
            if measurement.get("value") is not None and not _finite_number(measurement.get("value")):
                _add(errors, pp + ".measurement.value", "must be finite number or null")
            basis = measurement.get("basis_contribution_ids")
            if not isinstance(basis, list) or not basis:
                _add(errors, pp + ".measurement.basis_contribution_ids", "must be non-empty array")
            else:
                seen = set()
                for cid in basis:
                    if not isinstance(cid, str) or not CID.fullmatch(cid) or cid not in cids:
                        _add(errors, pp + ".measurement.basis_contribution_ids", "invalid contribution reference")
                    if cid in seen:
                        _add(errors, pp + ".measurement.basis_contribution_ids", "duplicate contribution reference")
                    seen.add(cid)

        conclusion = prop.get("conclusion")
        state = pexec.get("state") if isinstance(pexec, dict) else None
        completion = pexec.get("completion") if isinstance(pexec, dict) else None
        if state in {"failed", "incomplete"} and conclusion is not None:
            _add(errors, pp + ".conclusion", "failed/incomplete proposition requires null conclusion")
        if state == "completed" and conclusion is None:
            _add(errors, pp + ".conclusion", "completed proposition requires conclusion")

        if conclusion is not None:
            ck = {"reported_verdict", "terminal_branch", "causal_form", "basis_members", "residual_contribution_ids", "rule_roles"}
            if _exact(conclusion, ck, pp + ".conclusion", errors):
                verdict = conclusion.get("reported_verdict")
                if not _nonempty(verdict) or not _nonempty(conclusion.get("terminal_branch")):
                    _add(errors, pp + ".conclusion", "verdict and terminal_branch must be non-empty")
                if completion == "not_checkable" and verdict != "not_checkable":
                    _add(errors, pp + ".conclusion.reported_verdict", "not_checkable completion requires matching verdict")
                if completion == "assessed" and verdict == "not_checkable":
                    _add(errors, pp + ".conclusion.reported_verdict", "assessed completion cannot report not_checkable")
                form = conclusion.get("causal_form")
                forms = {"single_necessary", "independent_sufficient_alternatives", "jointly_sufficient", "redundant_non_deciding"}
                if form not in forms:
                    _add(errors, pp + ".conclusion.causal_form", "unknown causal form")

                basis = conclusion.get("basis_members")
                if not isinstance(basis, list):
                    _add(errors, pp + ".conclusion.basis_members", "must be an array")
                    basis = []
                seen_basis, causal_cids, causal_rules = set(), set(), set()
                for member in basis:
                    bp = pp + ".conclusion.basis_members"
                    if not _exact(member, {"namespace", "id"}, bp, errors) and not isinstance(member, dict):
                        continue
                    ns, ident = member.get("namespace"), member.get("id")
                    if ns not in {"contribution", "rule", "state"}:
                        _add(errors, bp, "unknown namespace")
                    if not _nonempty(ident):
                        _add(errors, bp, "basis id must be non-empty")
                        continue
                    pair = (ns, ident)
                    if pair in seen_basis:
                        _add(errors, bp, "duplicate (namespace,id) pair")
                    seen_basis.add(pair)
                    if ns == "contribution":
                        if not CID.fullmatch(ident) or ident not in cids:
                            _add(errors, bp, "invalid causal contribution reference")
                        else:
                            causal_cids.add(ident)
                    elif ns == "rule":
                        if not ident.startswith("rule-role:"):
                            _add(errors, bp, "rule basis id must begin rule-role:")
                        else:
                            causal_rules.add(ident)
                    elif ns == "state" and not ident.startswith("state:"):
                        _add(errors, bp, "state basis id must begin state:")

                if form == "single_necessary" and len(basis) != 1:
                    _add(errors, pp + ".conclusion.basis_members", "single_necessary requires one member")
                if form in {"independent_sufficient_alternatives", "jointly_sufficient"} and len(basis) < 2:
                    _add(errors, pp + ".conclusion.basis_members", "causal form requires at least two members")
                if form == "redundant_non_deciding" and basis:
                    _add(errors, pp + ".conclusion.basis_members", "redundant_non_deciding requires zero members")

                residuals = conclusion.get("residual_contribution_ids")
                if not isinstance(residuals, list):
                    _add(errors, pp + ".conclusion.residual_contribution_ids", "must be an array")
                    residuals = []
                residual_set = set()
                for cid in residuals:
                    if not isinstance(cid, str) or not CID.fullmatch(cid) or cid not in cids:
                        _add(errors, pp + ".conclusion.residual_contribution_ids", "invalid residual reference")
                    if cid in residual_set:
                        _add(errors, pp + ".conclusion.residual_contribution_ids", "duplicate residual reference")
                    residual_set.add(cid)
                if causal_cids & residual_set:
                    _add(errors, pp + ".conclusion", "causal/residual contribution overlap")
                if causal_cids | residual_set != cids:
                    _add(errors, pp + ".conclusion", "every retained contribution must be classified exactly once")

                roles = conclusion.get("rule_roles")
                if not isinstance(roles, list):
                    _add(errors, pp + ".conclusion.rule_roles", "must be an array")
                    roles = []
                role_map = {}
                for role in roles:
                    rp = pp + ".conclusion.rule_roles"
                    if not _exact(role, {"rule_id", "code", "terminal_role"}, rp, errors) and not isinstance(role, dict):
                        continue
                    rule_id = role.get("rule_id")
                    if not isinstance(rule_id, str) or not rule_id.startswith("rule-role:") or rule_id == "rule-role:":
                        _add(errors, rp, "invalid rule_id")
                        continue
                    if rule_id in role_map:
                        _add(errors, rp, "duplicate rule_id")
                    role_map[rule_id] = role.get("terminal_role")
                    if not _nonempty(role.get("code")) or role.get("terminal_role") not in {"causal", "residual"}:
                        _add(errors, rp, "invalid rule role")
                for rule_id in causal_rules:
                    if role_map.get(rule_id) != "causal":
                        _add(errors, pp + ".conclusion.rule_roles", "rule basis requires declared causal role")
                for rule_id, terminal_role in role_map.items():
                    if terminal_role == "residual" and rule_id in causal_rules:
                        _add(errors, pp + ".conclusion.rule_roles", "residual rule may not be causal basis")

        if index is not None and isinstance(index, dict):
            iprops, ipassages = index.get("propositions"), index.get("passages")
            if pid is not None and text_sha is not None and isinstance(iprops, dict):
                if pid not in iprops or iprops[pid] != text_sha:
                    _add(errors, pp + ".proposition", "does not exactly bind Contract-B proposition index")
            if isinstance(ipassages, dict):
                for ref in refs.values():
                    found = ipassages.get(ref.get("passage_id"))
                    if not isinstance(found, dict) or found.get("source_id") != ref.get("source_id") or found.get("passage_sha256") != ref.get("passage_sha256"):
                        _add(errors, pp + ".contributions", "evidence reference does not exactly bind Contract-B passage index")

    if index is not None and isinstance(index, dict) and isinstance(cb, dict):
        for field in ("contract_version", "bundle_id", "bundle_hash"):
            if field in index and cb.get(field) != index.get(field):
                _add(errors, "$.input.contract_b." + field, "does not exactly match Contract-B index")

    if isinstance(policy, dict) and isinstance(policy.get("canonical"), dict) and isinstance(policy.get("sha256"), str):
        try:
            if hashlib.sha256(canonical_bytes(policy["canonical"])).hexdigest() != policy["sha256"]:
                _add(errors, "$.producer.policy.sha256", "policy hash mismatch")
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            _add(errors, "$.producer.policy.canonical", f"cannot canonicalize: {exc}")

    if isinstance(rsid, str):
        try:
            if rsid != result_set_identity(value):
                _add(errors, "$.result_set_id", "result-set identity mismatch")
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            _add(errors, "$.result_set_id", f"cannot compute identity: {exc}")


def validate_contract_c_bytes(raw: bytes, *, expected_sha256: str | None = None, contract_b_index: dict | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(raw, bytes):
        return ["$: raw input must be bytes"]
    if expected_sha256 is not None:
        if not isinstance(expected_sha256, str):
            _add(errors, "expected_sha256", "must be a string")
        else:
            digest = expected_sha256[7:] if expected_sha256.startswith("sha256:") else expected_sha256
            if not H64.fullmatch(digest):
                _add(errors, "expected_sha256", "invalid digest syntax")
            elif hashlib.sha256(raw).hexdigest() != digest:
                _add(errors, "expected_sha256", "exact-byte digest mismatch")
    if contract_b_index is not None:
        _index(contract_b_index, errors)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        _add(errors, "$", f"invalid UTF-8: {exc}")
        return errors
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except (DuplicateKey, json.JSONDecodeError, ValueError) as exc:
        _add(errors, "$", f"invalid JSON: {exc}")
        return errors
    if not isinstance(value, dict):
        _add(errors, "$", "top-level JSON must be an object")
        return errors
    try:
        if raw != canonical_bytes(value):
            _add(errors, "$", "received bytes are not normative canonical bytes")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        _add(errors, "$", f"cannot canonicalize: {exc}")
        return errors
    _validate(value, errors, contract_b_index)
    return errors
