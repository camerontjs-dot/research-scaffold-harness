# Frozen Field-Ablation Predictions

Status: **pre-reference-reveal**

The classification asks what semantic capability is lost, not merely whether the parser currently rejects the object.

| Field/family | Frozen prediction | Capability lost if removed |
| --- | --- | --- |
| `contract_version` | semantically required | consumer cannot select/interpret the declared contract semantics safely |
| `input_authority.kind` | semantically required | authority namespace/type substitution cannot be detected |
| `input_authority.id` | semantically required | exact upstream authority/input substitution cannot be detected |
| `policy.id` | semantically required | Decision policy provenance/applicability cannot be established |
| `policy.version` | semantically required | policy-revision replay/substitution cannot be detected |
| `target.kind` | semantically required | target namespace/class ambiguity or cross-kind replay is possible |
| `target.id` | semantically required | exact logical target cannot be bound |
| `target.content_hash` | semantically required as a capability; mechanism may vary | changed content under the same logical id can receive stale Decision authority |
| `evaluation_state` | semantically required | completed HOLD and evaluation failure can collapse |
| `disposition` on completed evaluation | semantically required | consumer cannot recover the established policy conclusion |
| `effect.type` | semantically required for operation-bearing conclusion | cross-operation replay becomes possible |
| `effect.version` | semantically required | future semantic changes can be misinterpreted as known authority |
| each required machine effect parameter | semantically required for that effect | machine constraint/meaning becomes incomplete or ambiguous |
| optional machine effect parameter with declared safe default | semantically required capability, presence not always required | consumer needs deterministic default semantics; omission may be equivalent to explicit default |
| reason/basis codes | explanatory/audit metadata by default | explanation/audit detail only; Authorization capability should remain intact |
| human-readable explanation | explanatory metadata | human explanation only |
| diagnostic metadata | explanatory metadata | diagnostics only |
| stored `decision_id` | redundant/convenience | no semantic capability if deterministic semantic hash can be recomputed |
| authorization-looking fields | forbidden as Decision authority | no legitimate Decision capability; accepting them as authority contaminates the seam |
| execution-looking fields | forbidden as Decision authority | no legitimate Decision capability; accepting them as authority contaminates the seam |

Serialization-specific strictness may make some explanatory fields syntactically disallowed or optional. Such parser behavior is not itself evidence that a field is semantically required.
