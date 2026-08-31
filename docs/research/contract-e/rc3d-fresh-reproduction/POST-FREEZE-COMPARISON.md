# Contract E RC3D Gemini — post-freeze comparison

**Terminal disposition: `FALSIFIED`**

The frozen independent Gemini consumer was compared against the seven authorized evaluator artifacts without post-reveal repair. It does not satisfy the promotion gate.

Independent material falsifiers (any one is sufficient):

1. Canonical false rejects on citation/task envelopes whose supporting artifact references are not authority-conferring registry records (`unresolvable_authority_basis`).
2. Native consumption failure on every canonical RC3D `kind=propagation` request: the consumer reads top-level `mode`/`fields` and does not consume the frozen `request` container.
3. Native serialization failure on frozen singular `warrant` objects: iterating the object as a list raises `AttributeError: 'str' object has no attribute 'get'`.
4. Normative RC3C/RC3D reason disagreements on malformed wire and nested propagation cases.

Zero authority-relevant false accepts were observed. That does not license promotion. Several RC3A negatives in warrant-bearing domains never reached their intended checks because evaluation crashed on warrant cardinality first.

Frozen implementation and pre-reveal tests were not modified.

## Frozen integrity

Verified immediately before comparison:

| Item | Value |
|---|---|
| Starting HEAD | `5364837007fe18f9e05eb39e0aa1031e28561290` |
| Frozen tree | `7ad575731f2e7c5786fff74ead02a311007f36ab` |
| Implementation/tests commit | `76f63ed48538463487b7336b158745cdf63975d0` |
| `consumer.py` | `a1275e1e2ddd6c4509ca8b7769b5651c19749f85` |
| `test_rc3d.py` | `1102fc173086c45040da45125de4d138ee495765` |
| Frozen suite rerun | `python3 test_rc3d.py -v` → 42 tests, OK |
| `git diff` on frozen impl/tests | empty |

After comparison, those two file hashes remain unchanged.

## Authorized reveal (Git blob hashes)

| Artifact | Required blob | Match |
|---|---|---|
| RC3A `FROZEN-CASES.json` | `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a` | yes |
| RC3B `AUTHORITY-BASIS-REGISTRY.json` | `76ea333ee0460d9614e9899edb69e6865e48eccb` | yes |
| RC3B `FROZEN-BASIS-ATTACKS.json` | `c726fb0ef914a850620e545131a70d427f4027bd` | yes |
| RC3B `HARDENING-PREREGISTRATION.md` | `1d85e2036d410b3af08d4b2b8926586da8fe6088` | yes |
| RC3C `FROZEN-CASES.json` | `17d45524125814478b987bb8e91d23f545fb514e` | yes |
| RC3D `VECTOR-MATERIALIZATION-SPEC.json` | `5c75e46a8eb4d7346128d84e21c25bdcea454ec4` | yes |
| RC3D `FROZEN-CASES.json` | `728b308d6eca0ebdf384e7de312c8a62b2f25577` | yes |

No other Contract E reference material was used. Reference validators, generated RESULTS, RC3D/R1 preregistration, Apparatus PR #45 reasoning, workflow logs, prior Grok comparisons, the RC3C post-falsification diagnostic, and prior ChatGPT/CAL Pipeline reasoning were not inspected.

## Comparison method

Command:

```text
python3 docs/research/contract-e/rc3d-fresh-reproduction/compare_post_freeze.py
```

The harness is new post-freeze code. It imports `consumer.Consumer.evaluate` unchanged.

Materialization follows `VECTOR-MATERIALIZATION-SPEC.json` independently of consumer output:

- Envelope cases clone the RC3A baseline, apply frozen overlays, pass the full `RegistryDocument` wrapper, mode `new_exercise` unless a frozen case supplies another canonical mode.
- Propagation cases map fixture `requested_fields` → canonical `request.fields` under `{kind: propagation, request: {mode, fields}}`. The alias `requested_fields` is never passed as native wire.
- Delegation cases pass fixture `parent`/`child` byte-for-byte with mode `new_exercise`. Missing parent fields are not invented.
- Historical cases map fixture `historical_record` → canonical `historical_inspection`. HIST-N01 passes the unmapped fixture token `historical_record` as native mode.
- RC3B matrix replaces only the conferring reference; supporting artifacts are preserved.
- RC3B type mutations replace only `type` and preserve `id`.
- Semantic metamorphic cases replace only the opaque `result` payload.

The consumer's `permit` token is classified as accept without renaming fields inside the consumer.

The harness does not flatten nested propagation, does not coerce singular/plural warrant or competence, and does not extract `RegistryDocument.records` before the call. Unexpected exceptions are recorded as execution errors, not remapped to accept/reject.

## Counts by family

| Family | n | outcome match | false accept | false reject | normative reason Δ | non-normative reason Δ | native consume Δ | native serial Δ | exec error | semantic Δ | materializer fail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rc3a_envelope` | 31 | 16 | 0 | 2 | 0 | (see JSON) | 0 | 13 | 13 | 0 | 0 |
| `rc3a_propagation` | 4 | 3 | 0 | 1 | 0 | 3 | 4 | 0 | 0 | 0 | 0 |
| `rc3a_delegation` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `rc3a_historical` | 2 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `rc3b_basis_attacks` | 13 | 12 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `rc3b_compatibility_matrix` | 135 | 129 | 0 | 2 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |
| `rc3b_type_mutations` | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `rc3c_currentness` | 9 | 5 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `rc3c_wire` | 5 | 4 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 |
| `rc3c_delegation` | 6 | 6 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 0 |
| `rc3c_reason` | 4 | 4 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| `rc3d_interface` | 18 | 17 | 0 | 1 | 3 | 0 | 4 | 0 | 0 | 0 | 0 |
| `rc3d_materializer` | 4 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `semantic_metamorphic` | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 9 | 0 | 0 |
| **overall** | **262** | **224** | **0** | **11** | **8** | **12** | **11** | **29** | **27** | **0** | **0** |

Outcome-match counts include reject/reject pairs whose primary reason disagreed. Those are not hidden: they appear in the reason-Δ and native-consumption columns.

## Clustered root causes

Do not collapse these into a single “mostly agrees” story.

### 1. Supporting artifact treated as required resolvable authority basis (9 canonical false rejects)

The consumer resolves every `authority_basis` entry against `registry.records`. Citation and task baselines carry a supporting `artifact` reference (`decision:typed-citation-001`, `decision:typed-task-001`) that is not an authority-conferring registry record.

Observed reason: `unresolvable_authority_basis`.

Cases: `P07-citation`, `P08-task`, `BASIS-P01-canonical-task-grant`, `MATRIX-citation_ok--grant:citation-use`, `MATRIX-task_ok--grant:task-dispatch`, `CUR-P01-canonical-current`, `CUR-P02-revoked-after-evaluation`, `CUR-P03-valid-from-inclusive`, `CUR-P04-valid-until-inclusive`.

RC3B matching rules state that a supporting artifact must not satisfy the authority requirement. They do not authorize rejecting a canonical envelope because that artifact is absent from the conferring registry.

### 2. Nested RC3D propagation container not consumed (11 native-consumption disagreements)

Canonical request:

```json
{"kind": "propagation", "request": {"mode": "...", "fields": [...]}}
```

The frozen consumer inspects top-level `mode` / `fields` / `requested_fields`. On the canonical object it returns `missing_required_field`.

Cases: all four RC3A propagation cases; RC3C `REASON-N03`, `REASON-N04`; RC3D `PROP-P01-native-fields`, `PROP-N01-requested-fields-alias`, `PROP-N02-explicit-missing-fields`, `PROP-N03-unknown-mode`; materializer `MAT-PROP-01`.

`PROP-P01-native-fields` is a canonical false reject (expected accept). Several negatives still reject, but for the wrong normative reason. That is not independent agreement.

The harness did not flatten the container to make the consumer pass.

### 3. Singular warrant object iterated as a list (27 execution errors)

Frozen RC3A warrant-bearing envelopes store `warrant` as a JSON object. The consumer does `for w in env.get("warrant", [])`, which iterates dict keys and then calls `.get` on a string.

Exception: `AttributeError: 'str' object has no attribute 'get'`.

Cases include positives `P04-numeric`, `P05-source-boundary`, `P06-decision`, `P09-verify`, the four matching matrix cells, `WIRE-P01-competence-array`, and all nine semantic-metamorphic evaluations.

The harness did not wrap warrant in an array.

### 4. Silent singular/plural coercion on delegation wire (2 normative reason disagreements)

`DELWIRE-N01-operations-singular` expected `malformed_delegation_operations_shape`; observed `delegation_operation_amplification` (string iterated as characters).

`DELWIRE-N02-scope-singular` expected `malformed_delegation_scope_shape`; observed `delegation_scope_amplification`.

Outcome is reject/reject. The reason is not the frozen RC3C malformed-wire reason. Recorded as native serialization incompatibility.

### 5. Qualification scope cardinality not distinguished (1 normative reason disagreement)

`WIRE-N04-qualification-scope-array` expected `malformed_qualification_scope_shape`; observed `qualification_scope_mismatch`.

### 6. Semantic-result metamorphic family not actually exercised

All nine semantic cases (3 bases × 3 frozen variants) raised the warrant `AttributeError` before a decision. Baseline and variant signatures are both `(None, None)`, so `authority_signature_changed` is vacuously false. That is not evidence of opaque-result invariance. Count of completed signature comparisons: 0.

Materializer audits: `MAT-DEL-01`, `MAT-HIST-01`, and `MAT-REG-01` passed their mapping assertions. `MAT-PROP-01` applied `requested_fields → fields` correctly; the subsequent native call still failed consumption of the `request` container.

## RC3D R1 native interface (18)

Agreed on kind/mode, registry wrapper, delegation parent-authority semantics, and historical mode tokens:

- `KIND-N01` `unknown_evaluation_kind`
- `MODE-N01` `unknown_evaluation_mode`
- `REG-P01` permit with intact wrapper
- `REG-N01` / `REG-N02` `malformed_registry_document`
- `DEL-P01` through `DEL-N05` including `delegation_parent_mismatch`, `delegation_not_current`, amplification reasons
- `HIST-P01` inspection token permit
- `HIST-N01` fixture token `historical_record` → `unknown_evaluation_mode`
- `HIST-N02` new-exercise → `authority_basis_not_current`

Disagreed on the entire native propagation surface (`PROP-P01` false reject; `PROP-N01`–`N03` wrong reason because the container was not read).

## Preregistered ambiguities

These are the three choices Gemini recorded before reveal. The implementation was not changed after seeing the answers.

### 1. Registry map-key versus `record.id` consistency

Preregistered choice: enforce `map_key == record.id` natively.

Frozen evaluator: `REG-N02-record-key-id-mismatch` must reject `malformed_registry_document`.

Observed: reject `malformed_registry_document`.

**Status: agreed.**

### 2. Explicit propagation when `fields` are absent and/or `separately_reauthorized=false`

Preregistered choice: fail closed if `explicit` is requested but no `fields` are passed, or reauthorization is false.

Frozen native requests place `mode`/`fields` under `request`. The consumer never inspects that container, so the inner fail-closed rule was **not exercised on the authorized native surface**.

`PROP-N02-explicit-missing-fields` rejected `missing_required_field` rather than `malformed_propagation_request`. `PROP-P01-native-fields` was a false reject. Child pre-reveal tests used a non-canonical flattened shape; those tests are not counted as independent agreement.

**Status: not exercised on canonical RC3D wire; native-consumption disagreement prevents scoring the inner choice. Remains underdetermined as a semantic rule, and is disagreed as an interface.**

### 3. Wrapper kind/mode validation versus inner payload validation

Preregistered choice: malformed kind/mode rejections are elevated over inner payload structural rejections.

Frozen evaluator: `KIND-N01` `unknown_evaluation_kind`; `MODE-N01` envelope mode `historical_record` → `unknown_evaluation_mode`.

Observed: both match.

**Status: agreed** on the two frozen interface cases that exercise this choice.

## Contamination

`CLEAN` for this comparison aperture.

- Seven authorized blobs only, hash-verified before use.
- Frozen consumer imported natively; not edited, aliased, or wrapped with a semantic adapter.
- Prior Grok implementations/comparisons were not imported.
- Reference validators and RESULTS were not inspected.
- `CHILD-PROMPT.txt` remains untracked orchestrator bootstrap and is not part of the comparison commit.

## Promotion gate

| Gate | Result |
|---|---|
| Zero authority-relevant false accepts | held (0) |
| Zero canonical false rejects | **failed** (10 listed canonical false rejects plus `PROP-P01-identity-provenance`) |
| Native canonical consumption | **failed** (propagation `request` container) |
| Agreement on normative RC3B/RC3C/RC3D reasons | **failed** (8 normative reason disagreements) |
| Zero semantic-result authority-signature changes | vacuous; family did not complete |
| No semantic repair by the materializer | held |
| No contamination | held |
| No post-reveal repair | held |

**Disposition: `FALSIFIED`.**

A disagreement is evidence. A later diagnostic repair of this consumer must not be counted as independent agreement.
