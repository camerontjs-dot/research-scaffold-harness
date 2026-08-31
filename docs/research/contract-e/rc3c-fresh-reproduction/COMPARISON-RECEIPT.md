# Contract E RC3C Grok successor — post-freeze comparison receipt

Terminal disposition: **FALSIFIED**

authority-relevant false accept

Frozen implementation and pre-reveal tests were not modified.

## Revealed blobs

- `RC3A-FROZEN-CASES.json` git blob `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a` match=True
- `RC3B-AUTHORITY-BASIS-REGISTRY.json` git blob `76ea333ee0460d9614e9899edb69e6865e48eccb` match=True
- `RC3B-FROZEN-BASIS-ATTACKS.json` git blob `c726fb0ef914a850620e545131a70d427f4027bd` match=True
- `RC3B-HARDENING-PREREGISTRATION.md` git blob `1d85e2036d410b3af08d4b2b8926586da8fe6088` match=True
- `RC3C-FROZEN-CASES.json` git blob `17d45524125814478b987bb8e91d23f545fb514e` match=True

## Frozen suite rerun

Command: `python -m pytest tests/contract_e_rc3c -q --tb=no`

Exit: 0

```
........................................................................ [ 49%]
........................................................................ [ 99%]
.                                                                        [100%]
145 passed in 0.05s
```

## Counts by family

| Family | n | outcome match | false accept | false reject | normative reason disagreements |
|---|---:|---:|---:|---:|---:|
| `rc3a_envelope` | 31 | 31 | 0 | 0 | 0 |
| `rc3a_propagation` | 4 | 3 | 1 | 0 | 0 |
| `rc3a_delegation` | 4 | 3 | 0 | 1 | 0 |
| `rc3a_historical` | 2 | 1 | 0 | 1 | 0 |
| `rc3a_negative_controls` | 2 | 2 | 0 | 0 | 0 |
| `rc3b_basis_attacks` | 13 | 13 | 0 | 0 | 0 |
| `rc3b_compatibility_matrix` | 135 | 135 | 0 | 0 | 0 |
| `rc3b_type_mutations` | 18 | 18 | 0 | 0 | 0 |
| `rc3c_currentness` | 9 | 9 | 0 | 0 | 0 |
| `rc3c_wire` | 5 | 5 | 0 | 0 | 0 |
| `rc3c_delegation` | 6 | 5 | 0 | 1 | 3 |
| `rc3c_reason` | 4 | 4 | 0 | 0 | 2 |
| `semantic_metamorphic` | 18 | 18 | 0 | 0 | 0 |

## Material disagreements

- Authority-relevant false accepts: PROP-N01-semantic-authority
- False accepts (all families): PROP-N01-semantic-authority
- False rejects: DEL-P01-narrower-child, HIST-P01-prior-valid-later-revoked, DELWIRE-P01-canonical
- Normative reason disagreements: DELWIRE-N03-operation-amplification, DELWIRE-N04-scope-amplification, DELWIRE-N05-expiry-amplification, REASON-N03-explicit-decision-authority-propagation, REASON-N04-explicit-task-authority-propagation

## Compatibility matrix

135 cells; canonical accepts 9; false accepts 0; false rejects 0.

## Native-consumption / adaptation deviations

- DEL-N01-operation-amplification: RC3A parent object omitted delegator/delegate; passed unmodified
- DEL-N02-scope-amplification: RC3A parent object omitted delegator/delegate; passed unmodified
- DEL-N03-expiry-amplification: RC3A parent object omitted delegator/delegate; passed unmodified
- DEL-P01-narrower-child: RC3A parent object omitted delegator/delegate; passed unmodified
- DELWIRE-N01-operations-singular: source parent omitted delegator/delegate; passed unmodified
- DELWIRE-N02-scope-singular: source parent omitted delegator/delegate; passed unmodified
- DELWIRE-N03-operation-amplification: source parent omitted delegator/delegate; passed unmodified
- DELWIRE-N04-scope-amplification: source parent omitted delegator/delegate; passed unmodified
- DELWIRE-N05-expiry-amplification: source parent omitted delegator/delegate; passed unmodified
- DELWIRE-P01-canonical: source parent omitted delegator/delegate; passed unmodified
- HIST-P01-prior-valid-later-revoked: vector mode 'historical_record' is not a consumer mode; passed unmodified
- RC3A/RC3C propagation vectors use requested_fields; the frozen consumer reads propagation.fields. The vector key was not renamed.
- RC3B registry file wrapper {schema, records: map} is not a native collection for normalize_registry; evaluate() is called with the id-to-record mapping, which is the consumer's native dict-of-records collection. Envelope fields were not rewritten.
- rc3a negative_controls.transitive_chain is a description, not a callable native object; not rewritten into cases

No singular/plural coercion, hidden-case adapter, or field rewrite was applied to make vectors pass.

## Preregistered ambiguity correspondence

- A7/A8: RC3A/RC3C propagation vectors use `requested_fields`; consumer reads `fields`. PROP-N01 therefore accepted (false accept). PROP-N02/N03 and REASON-N03/N04 still rejected, but with local `propagation_forbidden_fields` rather than relisted `authority_requires_reestablishment`.
- A2/A13/delegation required-field plan: RC3A/RC3C parent objects omit `delegator`/`delegate`/`parent_authority_id`. Those objects were not filled. DEL-P01 and DELWIRE-P01 false-reject with `missing_required_field`; amplification cases still reject, but not on the amplification reasons.
- A11: HIST-P01 mode is `historical_record`, which is not a consumer mode. Passed unmodified; `evaluate()` remaps unknown modes to `new_exercise` and false-rejects.
- A16: semantic result mutations (frozen variants plus omitted/success/confidence forms) produced zero authority-signature changes.
- A20/A12 currentness: RC3C currentness vectors matched on accept/reject including inclusive bounds and revocation timing.

## Contamination / deviation status

none observed during post-freeze comparison; first Grok reproduction and reference validators were not inspected

0.1s sandbox prompt-path denial remains an apparatus/setup deviation only

The first 0.1s child-launch sandbox failure is a preserved apparatus/setup deviation. It is not the scientific implementation under comparison.

