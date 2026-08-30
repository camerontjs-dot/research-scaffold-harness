import json
import sys
import contract_d as cd

H = "sha256:" + "1" * 64
RS = lambda c: "result-set:" + c * 64
EXPECT = {
    "source-audit-clear": {
        "expected_input_authority": {"kind":"contract-c","id":"c1","immutable_id":RS("a")},
        "expected_policy": {"id":"mainframe.source-audit","version":"1"},
        "expected_target": {"kind":"knowledge","id":"k1","content_sha256":H},
        "requested_operation":"knowledge.add_verified_tag",
        "requested_effect_params":{"scope":"claim"},
    },
    "citation-use-clear": {
        "expected_input_authority": {"kind":"contract-c","id":"c2","immutable_id":RS("b")},
        "expected_policy": {"id":"mainframe.citation-use","version":"1"},
        "expected_target": {"kind":"knowledge","id":"k2","content_sha256":H},
        "requested_operation":"knowledge.cite_as_evidence",
        "requested_effect_params":{},
    },
    "task-dispatch-clear": {
        "expected_input_authority": {"kind":"task-review","id":"r1","immutable_id":"task-review:"+"c"*64},
        "expected_policy": {"id":"mainframe.task-dispatch","version":"1"},
        "expected_target": {"kind":"task","id":"t1","content_sha256":H},
        "requested_operation":"task.dispatch",
        "requested_effect_params":{},
    },
    "completed-hold": {
        "expected_input_authority": {"kind":"contract-c","id":"c3","immutable_id":RS("d")},
        "expected_policy": {"id":"mainframe.source-audit","version":"1"},
        "expected_target": {"kind":"knowledge","id":"k3","content_sha256":H},
        "requested_operation":"knowledge.add_verified_tag",
        "requested_effect_params":{"scope":"claim"},
    },
    "evaluation-failed": {
        "expected_input_authority": {"kind":"contract-c","id":"c4","immutable_id":RS("e")},
        "expected_policy": {"id":"mainframe.source-audit","version":"1"},
        "expected_target": {"kind":"knowledge","id":"k4","content_sha256":H},
        "requested_operation":"knowledge.add_verified_tag",
        "requested_effect_params":{"scope":"claim"},
    },
}

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/decision_engine_rc3_native.json"
payload = json.load(open(path, encoding="utf-8"))
results = {}
for name, expectation in EXPECT.items():
    decision = payload["decisions"][name]
    results[name] = {
        "outcome": cd.consume(decision, **expectation),
        "semantic_identity": cd.semantic_identity(decision),
    }
print(json.dumps(results, indent=2, sort_keys=True))
