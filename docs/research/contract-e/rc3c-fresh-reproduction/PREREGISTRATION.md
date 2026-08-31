# Contract E RC3C — Independent Fresh Reproduction Preregistration

Status: pre-implementation, pre-reveal.
Implementer: Grok 4.6 (xAI), isolated successor run.
Information aperture: TASK.md plus the five hash-verified blobs under `authority_input/`.
Clean base: `548bfa81f65290eda15af658f647497679b840ef`.
Input-aperture commit: `8902fca4e61221cfb40e52ce7abc6c58a1ec42d5`.

This document is recorded **before** implementation. It states how the five blobs will be read, which points are treated as closed rules, which points are left open, what would falsify the reading, and what behavior is predicted. It is not a claim that this reading matches any hidden reference validator.

## 0. Isolation and contamination statement (pre-implementation)

Authorized pre-freeze inputs actually used:

- `TASK.md`
- `authority_input/SPEC-CANDIDATE.json` (git blob `9c1090335d87eb5e4885a755542923b453c45317`)
- `authority_input/SPEC-SHAPES.json` (git blob `c3f293430ae6ddb87523d83ea6e5380b8b832136`)
- `authority_input/SPEC-PARTICIPANT-BOUNDARY.json` (git blob `8b1d292a240300388949d502e7b656e7a23a0b8e`)
- `authority_input/BASIS-BINDING-SPEC.json` (git blob `63c952c9c28f1be2173e69c79976c7dfe5880c10`)
- `authority_input/RC3C-SPEC.json` (git blob `f05feac88128fd693cca2fb25a0b2951654377eb`)

Not used, not searched, not opened:

- any Contract E reproduction branch/PR other than this isolated workspace and the authorized clean base
- RC3A/RC3B/RC3C frozen cases, registries, validators, results, preregistrations, or workflow artifacts
- GitHub, the web, other local repositories, prior conversations, or another model's output

If denied material is observed before freeze, this run is contaminated and stops.

RC3C explicitly supersedes inherited rules on: authority currentness composition; canonical wire cardinality; delegation wire shape; bounded normative reason semantics. Inherited blobs remain authoritative on all points RC3C does not amend.

## 1. Independent interpretation (closed rules)

The consumer is a research-only native evaluator. It consumes JSON objects in the canonical wire shapes. It does not translate hidden-vector aliases, coerce singular/plural forms, or infer authority from semantic payloads.

### 1.1 Evaluation surfaces

The stable API/CLI evaluates five kinds of input:

1. **Authority envelope** plus an **authority-basis registry/resolver**.
2. **Propagation request**.
3. **Delegation parent/child pair**.
4. **Historical authority record** (inspection vs new-exercise recheck).
5. Combined request objects that name one of the above kinds.

Default evaluation mode is `new_exercise` unless the caller names `historical_inspection`.

### 1.2 Decision object

Every evaluation returns a deterministic object:

- `accepted`: boolean
- `primary_reason`: a string when rejected; `null` when accepted
- `reason_is_normative`: true only when `primary_reason` is listed by RC3C `reason_contract` or by RC3B `ordering.reason_precedence`
- `evaluation_kind`: `envelope` | `propagation` | `delegation` | `historical`
- `mode`: `new_exercise` | `historical_inspection`
- `notes`: implementation-local annotations, including ambiguities hit; notes never change `accepted`

RC3C: `decision_is_normative` is true; `single_primary_reason` is true; inherited RC3A reason strings are historical/non-normative unless RC3C relists them. When multiple defects exist, the primary reason is the earliest matching entry in RC3C `whole_envelope_precedence` for envelope evaluation. Delegation- and propagation-specific relisted reasons apply on those surfaces.

Accept has no specified success reason; `primary_reason` is `null`.

### 1.3 Common envelope — required fields

Inherited required envelope keys:

`subject`, `authority_domain`, `operation`, `target`, `jurisdiction`, `authority_basis`, `propagation`, `non_implications`, `evaluated_at`

Participant amendment adds required `participant`.

RC3C canonical wire additionally requires:

- `authority_basis`: JSON array of AuthorityReference, `min_items` 1
- `competence`: JSON array of Qualification, `min_items` 0, **required** (empty array is the only allowed “no competence” form)
- `jurisdiction.scope`: JSON string
- `non_implications`: JSON array of strings
- `evaluated_at`: JSON string, date-time

Subject required inner fields: `id`, `kind`.
Target required inner fields: `class`, `id`, `current_hash`.
Jurisdiction required inner fields: `scope`, `applicable`, `current`.

Missing required keys or required inner keys → `missing_required_field`.

### 1.4 Canonical wire cardinality (no coercion)

RC3C `silent_singular_plural_coercion_forbidden` is treated as a hard rule. The consumer inspects JSON types natively:

| Path | Required JSON type | Wrong-type primary reason |
|---|---|---|
| `authority_basis` | array | `malformed_authority_basis_shape` |
| `competence` | array | `malformed_competence_shape` |
| `jurisdiction.scope` | string | `malformed_jurisdiction_scope_shape` |
| `competence[].scope` | string | `malformed_qualification_scope_shape` |
| `Delegation.operations` | array, min_items 1 | `malformed_delegation_operations_shape` |
| `Delegation.scope` | array, min_items 1 | `malformed_delegation_scope_shape` |

A string is not an array. An array is not a string. A single object is not an array of objects. These are rejects, not conversions.

Empty `authority_basis` (`[]`) is an array, so it is **not** `malformed_authority_basis_shape`. After later checks, it fails as `missing_domain_authority_basis` (no conferring basis that satisfies the domain). Empty delegation `operations`/`scope` arrays violate `min_items: 1` and are treated as the corresponding malformed-shape reasons because RC3C requires malformed cardinality to be rejected and does not list a separate empty-array reason.

Absent `authority_basis` / `competence` keys are `missing_required_field`, not the malformed-shape reasons.

Non-object items inside `authority_basis` or `competence` are treated as the corresponding malformed-shape reason.

### 1.5 Generic authorized boolean

If the envelope object contains a top-level `authorized` key, reject `generic_authorized_forbidden`. The value is irrelevant. Presence is the defect.

### 1.6 Authority domains and operations

Unknown `authority_domain` → `unknown_authority_domain`.
Known domain with `operation` not in that domain’s `operations` list → `domain_operation_mismatch`.
Unknown operation on an unknown domain is still `unknown_authority_domain` (earlier in precedence).

Closed domain table (from SPEC-CANDIDATE):

| Domain | Kind | Operations | Competence required | Warrant allowed | Accepted qualification types | Accepted warrant types |
|---|---|---|---|---|---|---|
| source_access | operational | source.read | no | no | — | — |
| evidence_admission | operational | evidence.admit_passage | no | no | — | — |
| assessment_mandate | mandate | assessment.issue | no | no | — | — |
| numeric_relation | informational | semantic.validate_numeric | yes | yes | numeric_relation_validator | numeric-threshold-v1 |
| source_boundary | informational | semantic.validate_absence | yes | yes | source_boundary_validator | source-boundary-v1 |
| decision_mandate | mandate | decision.make | no | yes | — | decision-policy-v1 |
| citation_use | operational | citation.use | no | no | — | — |
| task_dispatch | operational | task.dispatch | no | no | — | — |
| outcome_verification | informational | outcome.verify | yes | yes | outcome_verifier | postcondition-observation-v1 |

### 1.7 Participant boundary

`participant` must be one of the declared participant ids. Unknown → `unknown_participant`.
Declared participant must list the envelope domain in `accepted_domains` → else `participant_domain_out_of_scope`.
Declared participant must list the envelope operation in `accepted_operations` → else `participant_operation_out_of_scope`.
Participant is **not** inferred from `subject.id` / `subject.kind`.
A positive `result` payload cannot supply or bypass participant declaration.

Closed participant table: evidence-bundler, claim-audit-lab, numeric-validator, source-boundary-validator, decision-engine-policy, citation-agent, task-agent, outcome-verifier, with the accepted domains/operations exactly as in SPEC-CANDIDATE.

### 1.8 Jurisdiction

`jurisdiction.applicable` must be JSON boolean `true`; otherwise `jurisdiction_inapplicable`.
`jurisdiction.current` must be JSON boolean `true`; otherwise `jurisdiction_not_current`.
Non-boolean values fail closed (not true).
Jurisdiction does not imply competence. Competence does not imply jurisdiction.

### 1.9 Authority-basis registry / resolved records

The resolver is a collection of resolved basis records, accepted in any of:

- a JSON object mapping `id` → record
- a JSON object `{"records": [record, ...]}`
- a JSON array of records

Native resolved-record required fields: `id`, `type`, `subject_ids`, `authority_domain`, `operations`, `scopes`, `target_classes`, `current`, `valid_from`, `valid_until`.
Optional: `target_ids`, `parent_authority_id`, `revoked_at`.

RC3C wire types:

- `subject_ids`, `operations`, `scopes`, `target_classes`, `target_ids`: arrays of strings
- `current`: boolean

No coercion of `scopes` ↔ `scope`, `operations` ↔ `operation`, `subject_ids` ↔ `subject_id`.

### 1.10 Authority references

Each `authority_basis` item is an object requiring `type` (string), `id` (string), `current` (boolean).

Authority-conferring types: `grant`, `policy`, `delegation`.
Non-conferring supporting types: `credential`, `receipt`, `artifact`.
Supporting artifact / credential / receipt references **never** satisfy an authority requirement.

### 1.11 Basis-binding matching (RC3B, unchanged except currentness composition)

For each conferring reference, resolve `id` then apply, in this reason order:

1. id not in resolver → `unresolvable_authority_basis`
2. `reference.type != record.type` → `authority_basis_type_mismatch`
3. currentness conjunction (section 1.12) → `authority_basis_not_current` or `authority_basis_outside_validity_interval`
4. envelope `subject.id` not in `record.subject_ids` → `authority_basis_subject_mismatch`
5. envelope `authority_domain` != `record.authority_domain` → `authority_basis_domain_mismatch`
6. envelope `operation` not in `record.operations` → `authority_basis_operation_mismatch`
7. envelope `jurisdiction.scope` not in `record.scopes` → `authority_basis_scope_mismatch`
8. envelope `target.class` not in `record.target_classes` → `authority_basis_target_class_mismatch`
9. if `record.target_ids` is present and a non-empty array: envelope `target.id` must be in it, else `authority_basis_target_id_mismatch`
10. if `record.target_ids` is absent or `[]`, target-id matching is not applied

Basis binding is checked before warrant or result payload.

### 1.12 Currentness composition (RC3C; supersedes inherited currentness)

Applies to `new_exercise` only.

Required conjunction, all must hold:

1. `authority_reference.current == true` (JSON boolean true)
2. `resolved_basis_record.current == true` (JSON boolean true)
3. `evaluated_at >= resolved_basis_record.valid_from` (inclusive)
4. `evaluated_at <= resolved_basis_record.valid_until` (inclusive)
5. `resolved_basis_record.revoked_at` is absent, **or** `evaluated_at < revoked_at` (strict)

Closed reason mapping:

- reference current is not boolean true → `authority_basis_not_current`
- record current is not boolean true → `authority_basis_not_current`
- `revoked_at` present and `evaluated_at >= revoked_at` → `authority_basis_not_current`
- outside inclusive validity interval → `authority_basis_outside_validity_interval`

Additional closed rules:

- reference `true` cannot override a non-current record
- reference `false` must reject even when the record is current
- reference `false` does not rewrite record state (the consumer does not mutate the registry)
- record `false` must reject even when the reference is current
- `authority_basis_not_current` precedes `authority_basis_outside_validity_interval` when both apply

`historical_inspection` does not apply this conjunction to authorize a new exercise. Later `current=false` or later `revoked_at` does not rewrite a stored `authority_was_valid_at_time` flag. A new exercise that presents a historical record still requires a live currentness recheck against the resolver.

Timestamp comparison: parse ISO-8601 date-time strings (`...Z` allowed). Validity bounds are inclusive. Revocation uses strict less-than relative to `evaluated_at`.

### 1.13 Domain basis-type requirements

After conferring references are bound, at least one **successfully bound** conferring record must have `type` in the domain’s `any_of` list:

| Domain | any_of types | Additional required instruments |
|---|---|---|
| source_access | grant, policy | — |
| evidence_admission | grant, policy | — |
| assessment_mandate | grant, policy | — |
| numeric_relation | grant, policy | qualification `numeric_relation_validator`; warrant `numeric-threshold-v1` |
| source_boundary | grant, policy | qualification `source_boundary_validator`; warrant `source-boundary-v1` |
| decision_mandate | policy | warrant `decision-policy-v1` |
| citation_use | grant, policy | — |
| task_dispatch | grant, policy | — |
| outcome_verification | grant, policy | qualification `outcome_verifier`; warrant `postcondition-observation-v1` |

`delegation` is authority-conferring for binding, but it is **not** in any domain `any_of` list. A delegation record alone does not satisfy `missing_domain_authority_basis`. A grant does **not** satisfy `decision_mandate`.

If no conferring reference fully binds, the primary reason is the earliest binding reason among those failures (not `missing_domain_authority_basis`). If conferring references bind but none have an allowed type, or only non-conferring references are present, the reason is `missing_domain_authority_basis`.

Multiple conferring references: **at least one** must fully bind and have an allowed type. Additional non-conferring supporting references are ignored for satisfaction and do not themselves emit binding failures. Additional conferring references that fail are ignored **if** another conferring reference fully binds and satisfies `any_of`. If none satisfy, all conferring failures compete on envelope precedence.

### 1.14 Cross-domain use

Using a bound record whose `authority_domain` differs from the envelope domain is `authority_basis_domain_mismatch`.

RC3C relists these as the same reason:

- assessment_mandate used as citation_use → `authority_basis_domain_mismatch`
- decision_mandate used as task_dispatch → `authority_basis_domain_mismatch`

The consumer does **not** infer additional non-implications from domain semantics. It does **not** invent cross-domain reasons other than those relisted or produced by ordinary binding.

### 1.15 Competence / qualification

Qualification objects are inline (not registry-resolved). Required keys: `type`, `id`, `subject_id`, `scope`, `current`. `scope` is a **string**. Qualification is not an authority basis.

When the domain has `competence_required: true`:

1. empty competence array → `missing_required_qualification`
2. no qualification with `type` in the domain’s accepted list → `qualification_type_mismatch`
3. among matching types, none with `current === true` → `qualification_not_current`
4. among those, none with `subject_id == envelope.subject.id` → `qualification_subject_mismatch`
5. among those, none with `scope == envelope.jurisdiction.scope` (string equality) → `qualification_scope_mismatch`

When competence is not required, an empty array is sufficient. Extra qualifications do not create jurisdiction or authority.

### 1.16 Warrant

Warrant is a single inline object (not an array) when present. Required keys: `type`, `id`, `authority_domain`, `operation`, `input_artifact_ids`, `target_id`, `target_hash`, `applicable`, `current`.

Warrant is not operational permission. A valid warrant never repairs a missing/mismatched basis. Basis is checked first.

When the domain requires a warrant:

- missing / non-object warrant → `missing_required_warrant`
- `warrant.authority_domain != envelope.authority_domain` → `warrant_domain_mismatch`
- `warrant.operation != envelope.operation` → `warrant_operation_mismatch`
- `warrant.type` not in the domain’s accepted warrant types → `warrant_type_mismatch`
- `applicable` is not boolean true → `warrant_inapplicable`
- `current` is not boolean true → `warrant_not_current`
- `target_id != envelope.target.id` → `warrant_target_mismatch`
- `target_hash != envelope.target.current_hash` → `warrant_target_hash_mismatch`

When the domain has `warrant_allowed: false` and a `warrant` key is present → `warrant_not_allowed_for_domain` (late; earlier defects still win).

### 1.17 Result payload opacity

If `result` is present, common authority logic does not read it. `status`, `success`, `confidence`, positive/negative/indeterminate content, and any other result fields have **zero** authority effect. Semantic metamorphism of `result` must leave the authority signature (`accepted`, `primary_reason`) unchanged.

### 1.18 Propagation

Envelope `propagation` is required. Accepted native forms:

- string mode: `none` | `identity_provenance_only` | `explicit`
- object with `mode` plus optional `fields` / `separately_reauthorized`

Unknown mode → `unknown_propagation_mode`.

Default / `none`: no authority fields propagate. `allowed_fields` is empty.

`identity_provenance_only` may carry only: `source_id`, `artifact_id`, `content_hash`, `producer_id`, `policy_id`, `policy_version`.

Never implicit (must not ride along unless separately reauthorized): `competence`, `authority_domain`, `jurisdiction`, `warrant`, `semantic_validity`, `decision_mandate`, `citation_use`, `task_dispatch`, `outcome_verification`.

RC3C relisted reasons:

- explicit decision_mandate propagation → `authority_requires_reestablishment`
- explicit task_dispatch propagation → `authority_requires_reestablishment`

`explicit` requires a `fields` collection. Authority fields remain forbidden unless `separately_reauthorized` is boolean true. The consumer treats `separately_reauthorized: true` as the only specified bypass; the blobs do not define a second-envelope reauthorization protocol.

Propagation evaluation is also exposed as its own request surface so tests can attack the mode/field rules directly.

### 1.19 Delegation parent/child

Native delegation object required keys: `id`, `delegator`, `delegate`, `authority_domain`, `operations`, `scope`, `current`, `parent_authority_id`.

RC3C: `operations` is an array of strings, min_items 1; `scope` is an array of strings, min_items 1. This is **not** the jurisdiction string `scope` and **not** the resolved-record `scopes` array. No coercion among those three.

Subset rule: `child.operations` ⊆ `parent.operations` AND `child.scope` ⊆ `parent.scope` (set inclusion; order irrelevant; duplicates ignored for inclusion).

Expiry rule: when both `valid_until` values are present, `child.valid_until <= parent.valid_until`. Additional inherited rule `cannot_extend_parent_expiry`: if parent has `valid_until` and child omits it, treat as expiry amplification (child would be unbounded past parent).

Closed relisted reasons:

- extra child operation → `delegation_operation_amplification`
- extra child scope token → `delegation_scope_amplification`
- child expiry extends parent → `delegation_expiry_amplification`

Delegation shape checks use the malformed delegation reasons, which are not in `whole_envelope_precedence` because they belong to the delegation surface.

### 1.20 Historical records

Required historical fields: `evaluated_at`, `authority_was_valid_at_time`, `authority_basis_ids`.

Closed rules:

- later currentness may be false
- later revocation does not rewrite `authority_was_valid_at_time`
- new exercise requires current recheck (cannot treat `authority_was_valid_at_time: true` as live authority)

`historical_inspection` of a well-formed historical record is an inspection of a stored fact, not a new permit. `new_exercise` mode with only a historical record and no current conjunction against the resolver rejects.

### 1.21 Non-implications field

`non_implications` must be a JSON array of strings. The consumer may check attempted cross-use against declared lists. It must not infer missing non-implications from domain semantics. A non-array `non_implications` is rejected without coercion. That specific wrong-type reason is **not** listed in `malformed_wire_reasons`; see ambiguities.

### 1.22 Native consumption

The consumer’s public API accepts the canonical JSON objects described above. It will not provide:

- singular/plural converters
- `scope` ↔ `scopes` adapters
- hidden-vector field renaming
- producer-specific envelope translation
- result-derived authority

Any later comparison harness must call this API natively.

## 2. Recorded ambiguities (will not be silently “fixed” toward a guessed reference)

Each item is an underspecification. The planned implementation chooses a fail-closed local behavior and marks `reason_is_normative=false` when it must emit a reason that RC3C/RC3B did not list. These choices are **not** claims of hidden-vector agreement.

A1. **Multiple conferring `authority_basis` entries.** Blobs do not say whether all claimed conferring references must bind, or whether one sufficient reference is enough. Plan: at-least-one sufficient conferring bind + allowed type; ignore extra conferring failures only when another reference fully satisfies. If this causes post-reveal disagreement, it remains an ambiguity, not a repair target.

A2. **Delegation versus domain `any_of`.** `delegation` is authority-conferring, but no domain `any_of` lists it. Plan: bind delegation records, but they never satisfy domain type requirements by themselves. Parent following via `parent_authority_id` is **not** automatic.

A3. **Qualification `scope` comparison target.** Qualification `scope` is a string; jurisdiction `scope` is a string; no blob names the comparison target. Plan: string-equal to `envelope.jurisdiction.scope`.

A4. **Warrant cardinality.** Warrant shape is a single object; envelope warrant field is not in the RC3C canonical_wire block. Plan: `envelope.warrant` is a single object, not an array. Arrays are `missing_required_warrant` when a warrant is required, and `warrant_not_allowed_for_domain` when a warrant is present but disallowed.

A5. **`non_implications` wrong JSON type.** Required array, but no malformed-wire reason is listed. Plan: reject with implementation-local `malformed_non_implications_shape`, `reason_is_normative=false`.

A6. **`evaluated_at` / `valid_from` / `valid_until` / `revoked_at` parse failures.** Format is date-time for `evaluated_at` only. Plan: require parseable ISO-8601; unparseable comparison timestamps reject with implementation-local `unparseable_datetime`, `reason_is_normative=false`. Naive timestamps treated as UTC.

A7. **Envelope `propagation` wire shape.** Modes are named; object-versus-string is not. Plan: accept a mode string or an object with `mode`. Other types: `unknown_propagation_mode` if a string/object mode cannot be read; if a non-string non-object is present, `unknown_propagation_mode`.

A8. **Forbidden identity-provenance / `none` extra fields.** Relisted reestablishment reasons cover only explicit decision_mandate and task_dispatch. Plan: those two emit `authority_requires_reestablishment`. Other never-implicit or `none`-mode extra fields emit implementation-local `propagation_forbidden_fields`, `reason_is_normative=false`.

A9. **Meaning of `separately_reauthorized`.** Named but not protocol-specified. Plan: boolean true on the propagation object is the only bypass.

A10. **`stale_target_behavior: reject`.** Target has `current_hash`, not a current flag. Plan: no extra stale-target reason beyond required fields and warrant hash matching (`warrant_target_hash_mismatch`).

A11. **Historical record schema beyond the three required fields.** Plan: inspection accepts extra fields; it does not interpret them as live authority.

A12. **Boolean-typed fields with non-boolean JSON values.** Plan: fail closed (`== true` fails). Reasons stay the corresponding not-current / inapplicable / not-current jurisdiction reasons rather than a new malformed-boolean reason.

A13. **Empty delegation arrays.** `min_items: 1` versus malformed reason text `*_not_array`. Plan: empty arrays use the malformed delegation shape reasons.

A14. **Resolved-record `scopes`/`operations`/`subject_ids` wrong JSON type.** No malformed-record reasons listed. Plan: a conferring record whose array fields are not arrays cannot match membership tests and fails the corresponding mismatch reason (fail closed), without coercion.

A15. **Unknown `authority_basis[].type`.** Plan: not conferring, not supporting-known; treated as conferring-unknown that must resolve and type-match, then still cannot satisfy domain `any_of` unless the record type is in `any_of` (which requires type match, so the record type would have to equal the unknown reference type — therefore it cannot satisfy listed `any_of` values). Practically: unknown types cannot satisfy domain requirements.

A16. **`generic_authorized` nested inside `result`.** Plan: only a top-level envelope `authorized` key is `generic_authorized_forbidden`. Nested copies inside opaque `result` are ignored.

A17. **Order among equal-precedence defects.** Single primary reason; list order is total for listed reasons. Relisted reasons absent from `whole_envelope_precedence` (`authority_requires_reestablishment`, delegation amplification reasons, malformed delegation reasons) apply on their surfaces. If an envelope also contains explicit forbidden decision_mandate propagation, envelope-listed reasons still win if they appear earlier; `unknown_propagation_mode` is last among listed envelope reasons; `authority_requires_reestablishment` is emitted for that envelope only when no earlier listed envelope reason applies.

A18. **Competence items missing required inner keys.** Plan: after shape checks, missing inner keys on present qualification objects are `missing_required_field` when those objects are inspected during the missing-field pass.

A19. **Registry record missing required resolved fields.** Plan: treat as unusable resolution: `unresolvable_authority_basis` (fail closed), because a non-record cannot bind.

A20. **`valid_from` after `valid_until`.** Plan: interval is still applied as written; a new exercise cannot satisfy inclusive membership.

A21. **Child delegation `current: false` on the delegation surface.** No delegation-current reason is listed. Plan: for `new_exercise`, reject with `authority_basis_not_current` (relisted as RC3C currentness reason). For shape-only subset tests, currentness is still applied in `new_exercise`.

A22. **Whether `identity_provenance_only` fields must appear, or may appear.** Plan: may appear, must not include anything outside the allowed list.

These ambiguities are preserved in the freeze evidence. They will not be “resolved” after hidden-vector reveal.

## 3. Falsifiers

The implementation/reading is **FALSIFIED** (as a recoverable common authority boundary) if any of the following occur against the five blobs’ closed rules, independent of hidden vectors:

F1. New exercise accepted when `authority_reference.current` is not true.
F2. New exercise accepted when `resolved_basis_record.current` is not true, even if the reference is current.
F3. New exercise accepted when `evaluated_at >= revoked_at` for a present `revoked_at`.
F4. New exercise accepted when `evaluated_at` is strictly outside `[valid_from, valid_until]`.
F5. Inclusive bound rejected at `evaluated_at == valid_from` or `evaluated_at == valid_until` **and** that rejection is treated as a closed-rule requirement of the blobs (the blobs say inclusive; rejecting the bound would be an implementation error against the blobs).
F6. A non-array `authority_basis` or `competence`, or a non-string `jurisdiction.scope` / qualification `scope`, is coerced and then accepted.
F7. A string delegation `scope` or string `operations` is coerced to a one-element array and then accepted as a subset check.
F8. A supporting `artifact`/`credential`/`receipt` reference, alone, authorizes a domain exercise.
F9. A grant authorizes `decision_mandate` (domain `any_of` is policy only).
F10. A warrant or qualification without a matching domain `any_of` basis authorizes an exercise.
F11. A positive/negative/indeterminate `result` payload changes `accepted` or `primary_reason`.
F12. `authorized: true` on the envelope is accepted.
F13. Unknown domain or unknown participant is accepted.
F14. Child delegation with a superset operation or scope is accepted.
F15. Child `valid_until` later than parent `valid_until` (both present) is accepted.
F16. Explicit decision_mandate or task_dispatch propagation without separate reauthorization is accepted.
F17. Historical `authority_was_valid_at_time` is rewritten because a later `revoked_at` exists.
F18. Historical inspection of a prior valid record is treated as a live new-exercise permit without currentness recheck.
F19. Competence is treated as jurisdiction, or jurisdiction as competence.
F20. A current policy identifier that does not resolve to a matching bound record is accepted as authority.
F21. Reference `current: true` overrides a non-current record.
F22. An RC3C-listed malformed-wire reason is independently unrecoverable (wrong-type inputs accepted).
F23. Implementation requires a hidden-vector translation adapter to consume canonical envelopes.

Hidden vectors that depend on producer-specific semantics **absent from the five blobs** do not falsify the blobs; they falsify *independent recoverability of those vectors* and must be recorded as such rather than patched.

## 4. Predicted behavior (pre-implementation)

### 4.1 Predicted accepts

An envelope is predicted to be accepted only when all of the following hold:

- JSON types match RC3C canonical wire
- no top-level `authorized` key
- all required envelope/inner fields present
- domain and operation known and paired
- participant declared and in-scope for both domain and operation
- jurisdiction `applicable` and `current` are boolean true
- at least one conferring reference fully binds under RC3B matching and RC3C currentness conjunction
- that record’s type is in the domain `any_of`
- qualifications and warrant present and matching when the domain requires them
- no disallowed warrant on a domain that forbids warrants
- propagation mode known and not an unreauthorized explicit decision_mandate/task_dispatch export
- `result`, if any, ignored

Predicted positive informational baselines: well-formed `numeric_relation`, `source_boundary`, and `outcome_verification` envelopes with grant-or-policy basis, current matching qualification, and current matching warrant.

Predicted positive operational baselines: well-formed `source_access`, `evidence_admission`, `citation_use`, `task_dispatch` with grant or policy.

Predicted positive mandate baselines: `assessment_mandate` with grant or policy; `decision_mandate` with **policy** plus `decision-policy-v1` warrant.

### 4.2 Predicted rejects (normative reasons)

| Attack | Predicted primary reason | Normative? |
|---|---|---|
| `authority_basis` object/string | malformed_authority_basis_shape | yes (RC3C) |
| `competence` object/string | malformed_competence_shape | yes (RC3C) |
| `jurisdiction.scope` array | malformed_jurisdiction_scope_shape | yes (RC3C) |
| qualification `scope` array | malformed_qualification_scope_shape | yes (RC3C) |
| top-level `authorized` | generic_authorized_forbidden | yes (RC3C list) |
| omitted `participant` | missing_required_field | yes (RC3C list) |
| domain `not-a-domain` | unknown_authority_domain | yes (RC3C list) |
| `source_access` + `citation.use` | domain_operation_mismatch | yes (RC3C list) |
| participant `no-such-agent` | unknown_participant | yes (RC3C list) |
| evidence-bundler + citation_use | participant_domain_out_of_scope | yes (RC3C list) |
| evidence-bundler + source_access + citation.use (if domain were accepted) | participant_operation_out_of_scope | yes (RC3C list) |
| `jurisdiction.applicable: false` | jurisdiction_inapplicable | yes (RC3C list) |
| `jurisdiction.current: false` | jurisdiction_not_current | yes (RC3C list) |
| unknown basis id | unresolvable_authority_basis | yes (RC3B/RC3C) |
| reference type grant vs record type policy | authority_basis_type_mismatch | yes (RC3B/RC3C) |
| reference.current false | authority_basis_not_current | yes (RC3C currentness) |
| record.current false | authority_basis_not_current | yes (RC3C currentness) |
| evaluated_at >= revoked_at | authority_basis_not_current | yes (RC3C currentness) |
| subject id not in record.subject_ids | authority_basis_subject_mismatch | yes (RC3B/RC3C) |
| assessment record used on citation_use | authority_basis_domain_mismatch | yes (relisted) |
| operation not in record.operations | authority_basis_operation_mismatch | yes (RC3B/RC3C) |
| jurisdiction.scope not in record.scopes | authority_basis_scope_mismatch | yes (RC3B/RC3C) |
| target.class not in record.target_classes | authority_basis_target_class_mismatch | yes (RC3B/RC3C) |
| target.id not in nonempty record.target_ids | authority_basis_target_id_mismatch | yes (RC3B/RC3C) |
| evaluated_at < valid_from or > valid_until | authority_basis_outside_validity_interval | yes (RC3C) |
| only artifact references | missing_domain_authority_basis | yes (RC3C list) |
| grant on decision_mandate (bound) | missing_domain_authority_basis | yes (interpretation of any_of) |
| numeric_relation with empty competence | missing_required_qualification | yes (RC3C list) |
| wrong qualification type | qualification_type_mismatch | yes (RC3C list) |
| qualification.current false | qualification_not_current | yes (RC3C list) |
| qualification.subject_id mismatch | qualification_subject_mismatch | yes (RC3C list) |
| qualification.scope != jurisdiction.scope | qualification_scope_mismatch | yes (RC3C list; A3) |
| missing warrant on numeric_relation | missing_required_warrant | yes (RC3C list) |
| warrant domain mismatch | warrant_domain_mismatch | yes (RC3C list) |
| warrant operation mismatch | warrant_operation_mismatch | yes (RC3C list) |
| wrong warrant type | warrant_type_mismatch | yes (RC3C list) |
| warrant.applicable false | warrant_inapplicable | yes (RC3C list) |
| warrant.current false | warrant_not_current | yes (RC3C list) |
| warrant.target_id mismatch | warrant_target_mismatch | yes (RC3C list) |
| warrant.target_hash mismatch | warrant_target_hash_mismatch | yes (RC3C list) |
| warrant present on source_access | warrant_not_allowed_for_domain | yes (RC3C list) |
| propagation mode `telepathy` | unknown_propagation_mode | yes (RC3C list) |
| explicit decision_mandate propagation | authority_requires_reestablishment | yes (relisted) |
| explicit task_dispatch propagation | authority_requires_reestablishment | yes (relisted) |
| child extra operation | delegation_operation_amplification | yes (relisted) |
| child extra scope | delegation_scope_amplification | yes (relisted) |
| child later valid_until | delegation_expiry_amplification | yes (relisted) |
| delegation operations string | malformed_delegation_operations_shape | yes (RC3C malformed) |
| delegation scope string | malformed_delegation_scope_shape | yes (RC3C malformed) |

### 4.3 Predicted currentness composition matrix (new exercise)

Let R = reference.current, C = record.current, I = evaluated_at in inclusive interval, V = revoked_at absent or evaluated_at < revoked_at.

Accept iff R ∧ C ∧ I ∧ V.

| R | C | I | V | predicted |
|---|---|---|---|---|
| T | T | T | T | accept |
| F | T | T | T | reject not_current |
| T | F | T | T | reject not_current |
| T | T | F | T | reject outside_validity_interval |
| T | T | T | F | reject not_current |
| T | F | F | T | reject not_current (precedence) |
| F | F | F | F | reject not_current |

Equal-boundary predictions:

- `evaluated_at == valid_from` → interval holds
- `evaluated_at == valid_until` → interval holds
- `evaluated_at == revoked_at` → revocation reached, not_current
- `evaluated_at == revoked_at == valid_until` → not_current (precedence over interval)

### 4.4 Predicted metamorphic invariance

For any accepted or rejected envelope, replacing `result` with each of `{omitted, {status:"positive"}, {status:"negative"}, {status:"indeterminate"}, {success:true,confidence:1}, {success:false}}` must preserve `accepted` and `primary_reason`.

## 5. Adversarial test plan (self-designed; no hidden vectors)

Tests will be original and will include at least:

1. Native happy path per domain (9 domains).
2. Wire cardinality attacks: scalar/array swaps on authority_basis, competence, jurisdiction.scope, qualification.scope, delegation.operations, delegation.scope, resolved-record array fields.
3. Currentness conjunction and boundary timestamps, including revocation equality.
4. Each RC3B matching failure in isolation, and mixed failures for precedence.
5. Non-conferring types alone and mixed with a valid grant.
6. decision_mandate × grant vs policy.
7. Cross-domain assessment_mandate-as-citation_use and decision_mandate-as-task_dispatch.
8. Participant unknown / domain / operation.
9. Qualification and warrant attack suite for the three informational domains plus decision_mandate warrant.
10. Propagation none / identity / explicit / unknown / decision / task.
11. Delegation subset, amplification, expiry, malformed cardinality.
12. Historical inspection vs new-exercise recheck.
13. Result metamorphism on at least one positive informational baseline and one reject.
14. generic `authorized` presence.
15. Unknown domain/operation.
16. Empty authority_basis array.
17. Registry miss and type mismatch.
18. CLI smoke on each evaluation kind.

Test counts will be recorded after they exist. No test will be edited after freeze to match revealed vectors.

## 6. Implementation constraints

- Language: Python, native dict/list/bool/str checks, no Pydantic envelope coercion.
- Package: `research_scaffold_harness.contract_e_rc3c` (research-only; production harness behavior unchanged).
- CLI: `python -m research_scaffold_harness.contract_e_rc3c` and console script `contract-e-rc3c`.
- Spec tables copied into implementation constants with blob hashes cited; runtime does not fetch denied artifacts.
- Fail closed on unknowns that would otherwise permit.
- Do not optimize toward an imagined reference.

## 7. Planned freeze contents

After implementation and self-tests, freeze will record:

- input-aperture SHA/tree
- this preregistration SHA
- implementation SHA/tree
- test corpus hashes and counts
- contamination status
- exact marker `FRESH_RC3C_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL`

No reference reveal and no post-freeze repair in this run.
