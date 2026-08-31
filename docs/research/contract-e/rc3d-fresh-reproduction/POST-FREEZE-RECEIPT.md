# POST-FREEZE RECEIPT — Contract E RC3D Gemini independent reproduction

Terminal disposition: **`FALSIFIED`**

The frozen Gemini consumer produced canonical false rejects, failed native consumption of RC3D propagation requests, and raised uncaught exceptions on frozen singular warrant objects. It was not repaired after reveal.

## Frozen SHA / tree

- Immutable pre-reveal HEAD: `5364837007fe18f9e05eb39e0aa1031e28561290`
- Frozen tree: `7ad575731f2e7c5786fff74ead02a311007f36ab`
- Clean base: `548bfa81f65290eda15af658f647497679b840ef`
- Input-aperture: `805579a17c4888bd490fbebc0a2532806f9a3366`
- Preregistration: `68c50b3230369d9ddd5dc6df371ce78ae8cc8738`
- Implementation/tests: `76f63ed48538463487b7336b158745cdf63975d0`
- Freeze marker: `FRESH_RC3D_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL`

## Seven verified reveal blobs

| File | Git blob |
|---|---|
| `revealed/RC3A-FROZEN-CASES.json` | `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a` |
| `revealed/RC3B-AUTHORITY-BASIS-REGISTRY.json` | `76ea333ee0460d9614e9899edb69e6865e48eccb` |
| `revealed/RC3B-FROZEN-BASIS-ATTACKS.json` | `c726fb0ef914a850620e545131a70d427f4027bd` |
| `revealed/RC3B-HARDENING-PREREGISTRATION.md` | `1d85e2036d410b3af08d4b2b8926586da8fe6088` |
| `revealed/RC3C-FROZEN-CASES.json` | `17d45524125814478b987bb8e91d23f545fb514e` |
| `revealed/RC3D-VECTOR-MATERIALIZATION-SPEC.json` | `5c75e46a8eb4d7346128d84e21c25bdcea454ec4` |
| `revealed/RC3D-FROZEN-CASES.json` | `728b308d6eca0ebdf384e7de312c8a62b2f25577` |

## Comparison harness

- Path: `docs/research/contract-e/rc3d-fresh-reproduction/compare_post_freeze.py`
- Pre-commit blob: `cb8369736419f21c0235ac33e5829c01ca1fe8f3`
- Consumer modified: no
- Adapter used: no

## Unchanged frozen implementation / tests

- `consumer.py` `a1275e1e2ddd6c4509ca8b7769b5651c19749f85` (matches freeze receipt and commit `76f63ed`)
- `test_rc3d.py` `1102fc173086c45040da45125de4d138ee495765` (matches freeze receipt and commit `76f63ed`)
- `git diff HEAD -- consumer.py test_rc3d.py` empty after comparison

## Frozen suite rerun

```text
python3 test_rc3d.py -v
Ran 42 tests in 0.001s
OK
```

## Comparison command

```text
python3 docs/research/contract-e/rc3d-fresh-reproduction/compare_post_freeze.py
```

Machine record: `docs/research/contract-e/rc3d-fresh-reproduction/COMPARISON-RESULTS.json`

## Complete counts

| Metric | Count |
|---|---:|
| Total cases | 262 |
| Outcome matches | 224 |
| Outcome disagreements | 11 |
| False accepts / false permits | 0 |
| Authority-relevant false accepts | 0 |
| False rejects | 11 |
| Canonical false rejects | 10 listed in results plus `PROP-P01-identity-provenance` |
| Normative reason matches | (see JSON `reason_class=reason_match`) |
| Normative reason disagreements | 8 |
| Non-normative reason differences | 12 |
| Native consumption incompatibilities | 11 |
| Native serialization/interface incompatibilities | 29 |
| Execution errors | 27 |
| Semantic-payload authority-signature changes | 0 (vacuous; 9/9 semantic cases crashed) |
| Materializer audit failures | 0 |

## Every disagreement class

Canonical false rejects (`unresolvable_authority_basis` on supporting artifacts):

- `P07-citation`
- `P08-task`
- `BASIS-P01-canonical-task-grant`
- `MATRIX-citation_ok--grant:citation-use`
- `MATRIX-task_ok--grant:task-dispatch`
- `CUR-P01-canonical-current`
- `CUR-P02-revoked-after-evaluation`
- `CUR-P03-valid-from-inclusive`
- `CUR-P04-valid-until-inclusive`

Canonical false reject (nested propagation not consumed):

- `PROP-P01-native-fields`
- `PROP-P01-identity-provenance`

Native consumption (all `kind=propagation` canonical requests → `missing_required_field`):

- RC3A: `PROP-P01-identity-provenance`, `PROP-N01-semantic-authority`, `PROP-N02-decision-mandate`, `PROP-N03-task-dispatch`
- RC3C: `REASON-N03-explicit-decision-authority-propagation`, `REASON-N04-explicit-task-authority-propagation`
- RC3D: `PROP-P01-native-fields`, `PROP-N01-requested-fields-alias`, `PROP-N02-explicit-missing-fields`, `PROP-N03-unknown-mode`
- Materializer: `MAT-PROP-01`

Execution / warrant serialization (`AttributeError` on singular warrant object):

- Envelope positives/negatives: `P04-numeric`, `P05-source-boundary`, `P06-decision`, `P09-verify`, `N03`–`N09`, `N20`, `N22`
- Matrix canonical cells: `MATRIX-numeric_ok--grant:numeric-validation`, `MATRIX-source_boundary_ok--policy:source-boundary`, `MATRIX-decision_ok--policy:decision-v1`, `MATRIX-verify_ok--grant:verify`
- `WIRE-P01-competence-array`
- All 9 semantic-metamorphic cases

Normative reason disagreements with outcome match:

- `WIRE-N04-qualification-scope-array` (`malformed_qualification_scope_shape` vs `qualification_scope_mismatch`)
- `DELWIRE-N01-operations-singular` (`malformed_delegation_operations_shape` vs `delegation_operation_amplification`)
- `DELWIRE-N02-scope-singular` (`malformed_delegation_scope_shape` vs `delegation_scope_amplification`)
- `PROP-N01` / `PROP-N02` / `PROP-N03` interface and RC3C reason-propagation cases (wrong reason because container unread)

## Clustered root causes

1. Supporting `artifact` references treated as required resolvable basis records.
2. Canonical propagation `request` container unread (top-level mode/fields API).
3. Singular `warrant` object iterated as a list → uncaught `AttributeError`.
4. Singular delegation `operations`/`scope` coerced by `set(str)` instead of malformed-wire reject.
5. Qualification `scope` array treated as semantic mismatch rather than malformed shape.

## Preregistered ambiguity resolution

1. Registry map-key vs `record.id`: **agreed** (`REG-N02`).
2. Explicit propagation without fields / not reauthorized: **not exercised** on canonical nested `request`; **disagreed** as native interface (`missing_required_field`). Inner fail-closed rule remains underdetermined on the authorized wire.
3. Wrapper kind/mode vs inner payload: **agreed** (`KIND-N01`, `MODE-N01`).

## Contamination status

`CLEAN` for the comparison aperture. Seven reveal blobs only. Frozen consumer unmodified. Prior Grok comparison not imported.

## Terminal disposition

`FALSIFIED`

Do not merge this PR as a promotion. Do not repair the frozen Gemini implementation on this branch. A post-reveal repair, if later authorized, is a separate diagnostic and must never be counted as independent agreement.
