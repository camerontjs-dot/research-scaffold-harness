from __future__ import annotations

import copy
import json
import math
import os
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

REF = Path(os.environ["REF_DIR"])
NODE_MODULE = Path(os.environ["NODE_MODULE"])
NODE_ADAPTER = Path(os.environ["NODE_ADAPTER"])
sys.path.insert(0, str(REF))

from contract_d_consume import ApplicabilityExpectation, consume as ref_consume
from contract_d_core import ContractDError, canonical_json_bytes, semantic_identity, validate_decision
from contract_d_validate import parse_json_bytes

VALID = json.loads((REF / "fixtures" / "valid.json").read_text(encoding="utf-8"))["fixtures"]
INVALID = json.loads((REF / "fixtures" / "invalid.json").read_text(encoding="utf-8"))["fixtures"]
CONFORMANCE = json.loads((REF / "conformance-cases.json").read_text(encoding="utf-8"))["cases"]

records: list[dict] = []


def node(req: dict) -> dict:
    cp = subprocess.run(
        ["node", str(NODE_ADAPTER), str(NODE_MODULE)],
        input=json.dumps(req, ensure_ascii=True),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(cp.stdout)


def ref_result(fn):
    try:
        return {"status": "accept", "value": fn()}
    except ContractDError as exc:
        return {"status": "reject_controlled", "error": exc.code}
    except RecursionError:
        return {"status": "reject_controlled", "error": "RecursionError-translated-by-harness"}


def add(case_id: str, category: str, ref_value, ind_value, *, authority=True, mismatch_class=None):
    same = ref_value == ind_value
    rec = {
        "id": case_id,
        "category": category,
        "authority_relevant": authority,
        "agreement": same,
        "reference": ref_value,
        "independent": ind_value,
    }
    if not same:
        rec["classification"] = mismatch_class or "AUTHORITY_RELEVANT_DISAGREEMENT"
    records.append(rec)


def validate_ref(decision):
    return ref_result(lambda: (validate_decision(copy.deepcopy(decision)), "accepted")[1])


def validate_node(decision):
    return node({"action": "validate", "decision": decision})


def expectation_for(decision, *, op=None, params_marker="__ABSENT__"):
    e = {
        "input_authority": copy.deepcopy(decision["input_authority"]),
        "policy": copy.deepcopy(decision["policy"]),
        "target": copy.deepcopy(decision["target"]),
        "requested_operation": op or decision.get("effect", {}).get("type", "knowledge.add_verified_tag"),
    }
    if params_marker != "__ABSENT__":
        e["effect_params"] = copy.deepcopy(params_marker)
    return e


def to_ref_expectation(e):
    required = {"input_authority", "policy", "target", "requested_operation"}
    allowed = required | {"effect_params"}
    if not isinstance(e, dict) or not required.issubset(e) or not set(e).issubset(allowed):
        return e
    return ApplicabilityExpectation(
        copy.deepcopy(e["input_authority"]),
        copy.deepcopy(e["policy"]),
        copy.deepcopy(e["target"]),
        e["requested_operation"],
        copy.deepcopy(e.get("effect_params")),
    )


def consume_ref(decision, expectation):
    try:
        return ref_consume(copy.deepcopy(decision), to_ref_expectation(expectation))["outcome"]
    except Exception as exc:
        return f"HARNESS_EXCEPTION:{type(exc).__name__}"


def consume_node(decision, expectation):
    return node({"action": "consume", "decision": decision, "expectation": expectation})["value"]


def identity_ref(decision):
    return ref_result(lambda: semantic_identity(copy.deepcopy(decision)))


def identity_node(decision):
    return node({"action": "identity", "decision": decision})


def canonical_ref(value):
    return ref_result(lambda: canonical_json_bytes(value).decode("utf-8"))


def canonical_node(value):
    return node({"action": "canonical_value", "value": value})


def canonical_decision_ref(decision):
    return ref_result(lambda: canonical_json_bytes(copy.deepcopy(decision)).decode("utf-8"))


def canonical_decision_node(decision):
    return node({"action": "canonical_decision", "decision": decision})


def parse_ref(raw: bytes):
    return ref_result(lambda: canonical_json_bytes(parse_json_bytes(raw)).decode("utf-8"))


def parse_node(raw: bytes):
    return node({"action": "parse_bytes", "hex": raw.hex()})


def f64(bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(bits))[0]


def nested_lists(count: int):
    x = "leaf"
    for _ in range(count):
        x = [x]
    return x


def special_ref(kind: str, base: dict, count: int | None = None):
    def run():
        x = copy.deepcopy(base)
        if kind == "self_cycle":
            cycle = {}
            cycle["self"] = cycle
            x["metadata"]["diagnostics"] = cycle
        elif kind == "mutual_cycle":
            left = []
            right = {"left": left}
            left.append(right)
            x["metadata"]["diagnostics"] = {"cycle": left}
        elif kind == "shared_acyclic":
            shared = {"values": [1, 2, 3]}
            x["metadata"]["diagnostics"] = {"a": shared, "b": shared}
        elif kind == "depth":
            x["metadata"]["diagnostics"] = {"deep": nested_lists(int(count))}
        validate_decision(x)
        return "accepted"
    return ref_result(run)


# A. Structural/state behavior: all public fixtures.
for name in sorted(VALID):
    add(f"validate:valid:{name}", "structural", validate_ref(VALID[name]), validate_node(VALID[name]))
for name in sorted(INVALID):
    add(f"validate:invalid:{name}", "structural", validate_ref(INVALID[name]), validate_node(INVALID[name]))

case_version = copy.deepcopy(VALID["source-audit-clear.json"])
case_version["contract_d_version"] = "0.3.0-RC5"
add("validate:case-varied-version", "structural", validate_ref(case_version), validate_node(case_version))

# Explicit state outcomes beyond the public conformance set.
for name in ["citation-use-clear.json", "task-dispatch-clear.json", "completed-hold.json", "evaluation-failed.json"]:
    d = copy.deepcopy(VALID[name])
    e = expectation_for(d)
    add(f"consume:state:{name}", "state", consume_ref(d, e), consume_node(d, e))

for case in CONFORMANCE:
    d = copy.deepcopy(VALID[case["decision_fixture"]])
    e = copy.deepcopy(case["expect"])
    add(f"conformance:{case['id']}", "applicability", consume_ref(d, e), consume_node(d, e))

base = copy.deepcopy(VALID["source-audit-clear.json"])
substitutions = [
    ("upstream-kind", ("input_authority", "kind"), "task-review"),
    ("upstream-id", ("input_authority", "id"), "other"),
    ("upstream-immutable", ("input_authority", "immutable_id"), "result-set:" + "9" * 64),
    ("policy-id", ("policy", "id"), "other.policy"),
    ("policy-version", ("policy", "version"), "2"),
    ("target-kind", ("target", "kind"), "task"),
    ("target-id", ("target", "id"), "other"),
    ("target-hash", ("target", "content_sha256"), "sha256:" + "2" * 64),
]
for cid, (section, key), value in substitutions:
    e = expectation_for(base)
    e[section][key] = value
    add(f"consume:substitution:{cid}", "applicability", consume_ref(base, e), consume_node(base, e))

e = expectation_for(base, op="task.dispatch")
add("consume:clear-wrong-operation", "applicability", consume_ref(base, e), consume_node(base, e))
for cid, params in [
    ("params-absent", "__ABSENT__"),
    ("params-empty", {}),
    ("params-default-explicit", {"scope": "claim"}),
    ("params-conflict", {"scope": "object"}),
    ("params-unknown-key", {"future": 1}),
]:
    e = expectation_for(base, params_marker=params)
    add(f"consume:{cid}", "requested-params", consume_ref(base, e), consume_node(base, e))

# Malformed expectations.
malformed = []
e = expectation_for(base); del e["target"]["id"]; malformed.append(("missing-nested-key", e))
e = expectation_for(base); e["target"]["extra"] = "x"; malformed.append(("extra-nested-key", e))
e = expectation_for(base); e["policy"]["version"] = 1; malformed.append(("wrong-nested-type", e))
e = expectation_for(base); e["target"]["content_sha256"] = "not-a-sha256"; malformed.append(("malformed-target-hash", e))
e = expectation_for(base); e["requested_operation"] = ""; malformed.append(("empty-operation", e))
e = expectation_for(base); e["effect_params"] = []; malformed.append(("wrong-effect-params-type", e))
e = expectation_for(base); del e["policy"]; malformed.append(("missing-top-key", e))
e = expectation_for(base); e["extra"] = True; malformed.append(("extra-top-key", e))
for cid, e in malformed:
    add(f"consume:malformed:{cid}", "malformed-expectation", consume_ref(base, e), consume_node(base, e))

# Host-only/non-finite/surrogate malformed expectation values exposed by reference tests.
e_base = expectation_for(base)
e = to_ref_expectation(e_base); object.__setattr__(e, "effect_params", {"scope": float("nan")})
r = ref_consume(copy.deepcopy(base), e)["outcome"]
n = node({"action": "consume_nonfinite_param", "decision": base, "expectation": e_base})["value"]
add("consume:malformed:nonfinite-param", "malformed-expectation", r, n)
e = to_ref_expectation(e_base); object.__setattr__(e, "effect_params", {"scope": {"claim"}})
r = ref_consume(copy.deepcopy(base), e)["outcome"]
n = node({"action": "consume_host_only_param", "decision": base, "expectation": e_base})["value"]
add("consume:malformed:host-only-param", "malformed-expectation", r, n)
e = to_ref_expectation(e_base); object.__setattr__(e, "requested_operation", "knowledge.add_verified_tag\ud800")
r = ref_consume(copy.deepcopy(base), e)["outcome"]
n = node({"action": "consume_surrogate_operation", "decision": base, "expectation": e_base})["value"]
add("consume:malformed:surrogate-operation", "malformed-expectation", r, n)

# B. Interoperability hardening.
add("ingress:invalid-utf8", "ingress", parse_ref(b"\xff"), parse_node(b"\xff"))
add(
    "ingress:duplicate-key",
    "ingress",
    parse_ref(b'{"contract_d_version":"0.3.0-rc5","contract_d_version":"0.3.0-rc5"}'),
    parse_node(b'{"contract_d_version":"0.3.0-rc5","contract_d_version":"0.3.0-rc5"}'),
)

sur = copy.deepcopy(base)
sur["metadata"]["diagnostics"] = {"bad": "\ud800"}
sur_raw = json.dumps(sur, ensure_ascii=True, separators=(",", ":")).encode("ascii")
add("ingress:unpaired-surrogate", "unicode", parse_ref(sur_raw), parse_node(sur_raw))

for kind in ["self_cycle", "mutual_cycle", "shared_acyclic"]:
    add(
        f"host:{kind}",
        "container-graph",
        special_ref(kind, base),
        node({"action": kind, "base": base}),
    )
add(
    "depth:128-boundary-accept",
    "depth",
    special_ref("depth", base, 125),
    node({"action": "depth", "base": base, "count": 125}),
)
add(
    "depth:129-reject",
    "depth",
    special_ref("depth", base, 126),
    node({"action": "depth", "base": base, "count": 126}),
)

vectors = [
    ("0000000000000000", "0"), ("8000000000000000", "0"),
    ("0000000000000001", "5e-324"), ("8000000000000001", "-5e-324"),
    ("7fefffffffffffff", "1.7976931348623157e+308"), ("ffefffffffffffff", "-1.7976931348623157e+308"),
    ("4340000000000000", "9007199254740992"), ("c340000000000000", "-9007199254740992"),
    ("4430000000000000", "295147905179352830000"), ("44b52d02c7e14af5", "9.999999999999997e+22"),
    ("44b52d02c7e14af6", "1e+23"), ("44b52d02c7e14af7", "1.0000000000000001e+23"),
    ("444b1ae4d6e2ef4e", "999999999999999700000"), ("444b1ae4d6e2ef4f", "999999999999999900000"),
    ("444b1ae4d6e2ef50", "1e+21"), ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
    ("3eb0c6f7a0b5ed8d", "0.000001"), ("41b3de4355555553", "333333333.3333332"),
    ("41b3de4355555554", "333333333.33333325"), ("41b3de4355555555", "333333333.3333333"),
    ("41b3de4355555556", "333333333.3333334"), ("41b3de4355555557", "333333333.33333343"),
    ("becbf647612f3696", "-0.0000033333333333333333"), ("43143ff3c1cb0959", "1424953923781206.2"),
]
for bits, expected in vectors:
    add(
        f"jcs:number:{bits}",
        "jcs-number",
        canonical_ref({"n": f64(bits)}),
        node({"action": "number_bits", "bits": bits}),
    )

# Byte-ingress integer tokens in the exact RC5 domain.
def decision_bytes_with_number(token: str) -> bytes:
    x = copy.deepcopy(base)
    x["metadata"]["diagnostics"] = {"number": "__NUMBER_TOKEN__"}
    text = json.dumps(x, ensure_ascii=False, separators=(",", ":"))
    return text.replace('"__NUMBER_TOKEN__"', token).encode("utf-8")

for token in ["9007199254740993", "9007199254740992", "295147905179352830000", "100000000000000000000"]:
    raw = decision_bytes_with_number(token)
    add(f"ingress:integer-token:{token}", "number-domain", parse_ref(raw), parse_node(raw))

add(
    "jcs:utf16-key-order",
    "jcs-ordering",
    canonical_ref({"\uffff": 1, "\U0001f4a9": 2}),
    canonical_node({"\uffff": 1, "\U0001f4a9": 2}),
)

# Normative canonical transport bytes for all public valid decisions.
for name in sorted(VALID):
    add(
        f"canonical-decision:{name}",
        "canonical-transport",
        canonical_decision_ref(VALID[name]),
        canonical_decision_node(VALID[name]),
    )

# Normative semantic identities. Empty-schema effects are a prereveal uncertainty.
for name in sorted(VALID):
    hint = None
    if name in {"citation-use-clear.json", "task-dispatch-clear.json"}:
        hint = "PUBLIC_AUTHORITY_AMBIGUITY"
    add(
        f"semantic-identity:{name}",
        "semantic-identity",
        identity_ref(VALID[name]),
        identity_node(VALID[name]),
        mismatch_class=hint,
    )

# Metadata firewall/invariance on an effect whose normalization is unambiguous.
meta = copy.deepcopy(base)
meta["metadata"]["diagnostics"] = {"actor": "root", "approval": True, "n": 1e-6}
add("semantic-identity:metadata-firewall", "metadata-firewall", identity_ref(meta), identity_node(meta))
no_meta = copy.deepcopy(base); no_meta.pop("metadata")
add("semantic-identity:metadata-absent", "metadata-firewall", identity_ref(no_meta), identity_node(no_meta))

# Preserve a host-representation variance exposed by the Python reference tests.
# Python has a distinct float host type; JavaScript Number has no int/float distinction.
for decimal in ["9007199254740992", "295147905179352830000"]:
    r = canonical_ref({"n": float(decimal)})
    n = node({"action": "host_integer_valued_binary64", "decimal": decimal})
    add(
        f"host-representation:integer-valued-binary64:{decimal}",
        "host-representation",
        r,
        n,
        authority=False,
        mismatch_class="NON_AUTHORITY_IMPLEMENTATION_VARIANCE",
    )

# Summaries.
auth = [r for r in records if r["authority_relevant"]]
diffs = [r for r in records if not r["agreement"]]
auth_diffs = [r for r in auth if not r["agreement"]]
class_counts = Counter(r.get("classification", "AGREEMENT") for r in records)
summary = {
    "total_comparisons": len(records),
    "authority_relevant_total": len(auth),
    "authority_relevant_agreements": sum(1 for r in auth if r["agreement"]),
    "authority_relevant_disagreements": len(auth_diffs),
    "difference_classifications": dict(sorted((k, v) for k, v in class_counts.items() if k != "AGREEMENT")),
    "disagreement_case_ids": [r["id"] for r in auth_diffs],
    "all_deviation_case_ids": [r["id"] for r in diffs],
    "records": records,
}
print("DIFFERENTIAL_JSON=" + json.dumps(summary, ensure_ascii=True, sort_keys=True))
