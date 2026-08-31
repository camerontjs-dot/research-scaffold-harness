# Contract E fresh reproduction — preregistration

Status: **frozen interpretation, written before implementation**

Date (UTC): 2026-08-31

Input aperture commit: `ca9c00a3a238d449445485fc72974837fee7ac5c`

Authorized inputs (and only these) used to form this interpretation:

- `authority_input/SPEC-CANDIDATE.json` blob `9c1090335d87eb5e4885a755542923b453c45317`
- `authority_input/SPEC-SHAPES.json` blob `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `authority_input/SPEC-PARTICIPANT-BOUNDARY.json` blob `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `authority_input/BASIS-BINDING-SPEC.json` blob `63c952c9c28f1be2173e69c79976c7dfe5880c10`

This document records an independent reading of those four files. It is not Contract E authority. It is not a claim that a universal production evaluator exists. Where the files are silent, this document preserves the silence and labels any local choice as an **implementation assumption**, not specification authority.

Do not amend this file after implementation begins. Record later discoveries as dated deviation notes in a separate file.

---

## 1. Concise description of the contract's purpose

The four files specify a **research** contract for evaluating whether a proposed exercise of authority is warranted by an explicit, typed basis rather than by implication, competence, semantic success, or identity provenance.

An evaluation is an envelope describing:

- who is acting (`subject`);
- which declared participant role is claimed (`participant`);
- which typed authority domain and operation are being exercised;
- against which target;
- under which jurisdiction;
- citing which authority-basis references;
- at which evaluation time;
- with which propagation mode and which declared non-implications.

The common validator's job is to **accept or reject** that exercise using only:

1. envelope structure;
2. participant-boundary rules;
3. domain/operation/warrant/qualification tables;
4. resolved authority-basis records and the basis-binding matching rules;
5. optional warrant and qualification objects when the domain requires or binds them;
6. explicit non-implication and propagation constraints.

The contract's central negative thesis is that several things that look like authority **are not authority**: competence, jurisdiction taken alone, warrants, decisions, execution reports, positive semantic results, supporting artifacts, policy identifiers without bound records, and any field that merely propagated as identity provenance.

The files do **not** specify production architecture, cryptographic trust, a required on-disk registry format, CAL/Decision/Executor runtime behavior, or a generic `authorized: true` flag.

---

## 2. Entities and relations believed to be normative

### 2.1 Evaluation envelope (common envelope)

From `SPEC-CANDIDATE.json#/common_envelope` plus `SPEC-PARTICIPANT-BOUNDARY.json#/common_envelope_additional_required`.

Required envelope fields:

| Field | Nested required fields |
|---|---|
| `subject` | `id`, `kind` |
| `authority_domain` | — |
| `operation` | — |
| `target` | `class`, `id`, `current_hash` |
| `jurisdiction` | `scope`, `applicable`, `current` |
| `authority_basis` | entries with `type`, `id`, `current` |
| `propagation` | mode in `{none, identity_provenance_only, explicit}` |
| `non_implications` | — |
| `evaluated_at` | — |
| `participant` | — (additional required) |

`authority_basis_entry_required` implies `authority_basis` is a sequence of reference objects, not a single opaque string.

### 2.2 Authority domains and operations

Nine named domains, each with `kind`, `operations`, `competence_required`, `warrant_allowed`, and optionally `accepted_qualification_types` / `accepted_warrant_types`.

| Domain | Kind | Operation | Competence | Warrant allowed |
|---|---|---|---|---|
| `source_access` | operational | `source.read` | no | no |
| `evidence_admission` | operational | `evidence.admit_passage` | no | no |
| `assessment_mandate` | mandate | `assessment.issue` | no | no |
| `numeric_relation` | informational | `semantic.validate_numeric` | yes | yes |
| `source_boundary` | informational | `semantic.validate_absence` | yes | yes |
| `decision_mandate` | mandate | `decision.make` | no | yes |
| `citation_use` | operational | `citation.use` | no | no |
| `task_dispatch` | operational | `task.dispatch` | no | no |
| `outcome_verification` | informational | `outcome.verify` | yes | yes |

`kind` is treated as a classification label. The mechanically load-bearing flags are `competence_required`, `warrant_allowed`, accepted type lists, and `domain_basis_requirements`.

### 2.3 Authority-basis reference and resolved record

A reference (`type`, `id`, `current`) must resolve to a record with:

Required: `id`, `type`, `subject_ids`, `authority_domain`, `operations`, `scopes`, `target_classes`, `current`, `valid_from`, `valid_until`

Optional: `target_ids`, `parent_authority_id`, `revoked_at`

Listed basis types: `grant`, `policy`, `credential`, `receipt`, `artifact`, `delegation`.

Authority-conferring types: `grant`, `policy`, `delegation`.

`domain_basis_requirements.any_of` further restricts conferring type per domain (notably `decision_mandate` allows only `policy`).

### 2.4 Qualification (competence)

Required shape: `type`, `id`, `subject_id`, `scope`, `current`.

Qualification is **not** an authority basis by itself. Currentness is required for new exercise.

### 2.5 Warrant

Required shape: `type`, `id`, `authority_domain`, `operation`, `input_artifact_ids`, `target_id`, `target_hash`, `applicable`, `current`.

A warrant must match envelope domain, operation, and target. It must be applicable and current. It is **not** operational permission. Named warrant types license specific effects and declare their own non-implications.

### 2.6 Delegation

Required shape: `id`, `delegator`, `delegate`, `authority_domain`, `operations`, `scope`, `current`, `parent_authority_id`.

Child must be a subset of parent: no extra operations, no expanded scope, no extended expiry.

### 2.7 Participant declaration

Named participants with `accepted_domains`, `accepted_operations`, `responsibilities`, `excluded_responsibilities`.

Participant is a declared role, not inferred from `subject` identity.

### 2.8 Result / semantic payload

Opaque to the common validator. `positive_status`, `success`, and `confidence` have no authority effect.

### 2.9 Historical record

Required: `evaluated_at`, `authority_was_valid_at_time`, `authority_basis_ids`.

Later currentness may be false. Later revocation does not rewrite `authority_was_valid_at_time`. New exercise still requires a current recheck.

### 2.10 Propagation

Modes: `none`, `identity_provenance_only`, `explicit`.

Identity-provenance fields that may travel: `source_id`, `artifact_id`, `content_hash`, `producer_id`, `policy_id`, `policy_version`.

Never implicit: `competence`, `authority_domain`, `jurisdiction`, `warrant`, `semantic_validity`, `decision_mandate`, `citation_use`, `task_dispatch`, `outcome_verification`.

### 2.11 Relations the validator must enforce

- Envelope domain/operation must be known (else reject).
- Participant must be declared and must accept that domain and operation.
- At least one **conferring** basis must resolve and satisfy all matching rules and the domain's `any_of`.
- Subject, domain, operation, jurisdiction scope, target class, and (when bound) target id must match the record.
- New exercise requires record currentness and `evaluated_at` inside the validity interval.
- Competence, warrant, and jurisdiction are distinct and non-substitutable.
- Supporting artifacts, results, and identity provenance never satisfy an authority requirement.
- Declared non-implications block attempted cross-use; missing non-implications are not inferred from domain semantics.

---

## 3. Distinctions among competence, warrant, authority basis, participant responsibility, jurisdiction, propagation, delegation, currentness, and historical validity

These are **not** synonyms. The files spend most of their normative energy keeping them apart.

### Competence (qualification)

A typed, current, subject-bound skill/role credential (`numeric_relation_validator`, `source_boundary_validator`, `outcome_verifier`).

- Required for domains with `competence_required: true`.
- Does **not** imply jurisdiction (`competence_implies_jurisdiction: false`).
- Is **not** an authority basis.
- Does **not** propagate (`competence` is in `never_implicit`).
- Does **not** create a mandate.

### Warrant

A typed, current, applicable, domain/operation/target-bound license of a named effect (for example `numeric_relation.validity`).

- Allowed only in domains with `warrant_allowed: true`.
- Does **not** imply operational permission.
- Does **not** repair a missing or mismatched authority basis.
- Must match envelope domain, operation, and target.
- Does **not** propagate.

### Authority basis

The conferring record (grant, policy, or delegation; policy-only for `decision_mandate`) that is the actual permission source.

- Must resolve by id.
- Reference type must match record type.
- Reference `current` must not override record currentness.
- Must match subject, domain, operation, scope, target class, and bound target ids.
- Must be current for new exercise and valid at `evaluated_at`.
- A current policy **identifier** without a matching bound record is not authority.

### Participant responsibility

The declared participant's accepted domains/operations and excluded responsibilities.

- Must be an explicit envelope field.
- Must not be inferred from subject identity.
- Cannot be bypassed by a positive semantic result.
- Responsibilities and excluded responsibilities are participant-boundary claims, not authority bases.

### Jurisdiction

Envelope object with `scope`, `applicable`, `current`.

- Scope must be in the resolved record's `scopes`.
- Inapplicable jurisdiction rejects (`inapplicable_behavior: reject`).
- Does **not** imply competence (`jurisdiction_implies_competence: false`).
- Does **not** propagate.

### Propagation

How fields may travel with an artifact or handoff.

- Default: `none`.
- Identity provenance may carry the six listed identity fields and nothing authority-bearing.
- Explicit mode requires an explicit field list; authority fields remain forbidden unless separately reauthorized.
- Propagation is not a substitute for re-establishing competence, domain, jurisdiction, warrant, or the named never-implicit effects.

### Delegation

Both a basis type and a shape with parent-subset constraints.

- Conferring, unlike `credential` / `receipt` / `artifact`.
- Child cannot amplify parent: no added operation, no expanded scope, no extended expiry.
- `parent_authority_id` links to the parent record.
- Delegation does not escape domain/operation/subject/currentness matching.

### Currentness

A present-tense flag on records, references, jurisdiction, qualifications, and warrants.

- Required for **new** exercise of authority (`record_must_be_current_for_new_exercise`, `current_recheck_required_for_new_action`, qualification/warrant current flags).
- Distinct from validity-interval membership.
- Distinct from historical `authority_was_valid_at_time`.
- Later currentness may become false without rewriting history.

### Historical validity

Whether authority **was** valid at `evaluated_at`.

- Required traces: `evaluated_at` and `authority_basis`.
- `evaluated_at` must fall in `[valid_from, valid_until]` (bound inclusivity is an assumption; see §5).
- Later revocation does **not** rewrite `authority_was_valid_at_time`.
- A historically valid exercise does **not** authorize a new action if the basis is no longer current.

---

## 4. What may propagate versus what must be re-established

### May propagate

Only under `identity_provenance_only`, and only these fields:

- `source_id`
- `artifact_id`
- `content_hash`
- `producer_id`
- `policy_id`
- `policy_version`

Under `explicit`, additional **non-authority** fields named in the explicit `fields` list may propagate. Authority fields remain forbidden unless they are separately re-established as first-class envelope/basis/warrant/qualification objects.

Under `none`, no fields are treated as propagated.

`policy_id` / `policy_version` as identity provenance are **not** a bound policy record.

### Must be re-established (never implicit)

- `competence`
- `authority_domain`
- `jurisdiction`
- `warrant`
- `semantic_validity`
- `decision_mandate`
- `citation_use`
- `task_dispatch`
- `outcome_verification`

Also, by matching rules and non-implications, operational permission itself must be re-established via a resolved conferring basis. A warrant, result, decision artifact, or supporting artifact cannot stand in.

---

## 5. Ambiguities and missing definitions

Each item is a specification gap, not a prompt to invent hidden rules. Implementation assumptions are listed only where a running validator must pick a branch.

### A1. Is a warrant required or merely allowed?

`warrant_allowed` is not `warrant_required`. `domain_basis_requirements` nevertheless names a warrant type for `numeric_relation`, `source_boundary`, `decision_mandate`, and `outcome_verification`.

Competing readings:

1. Warrant is **required** whenever `domain_basis_requirements` names one.
2. Warrant is **optional**; if present it must be the named type.
3. Warrant is required only when the case **claims** a warrant-licensed effect.

**Assumption W1 (conservative, anti-widening):** if `domain_basis_requirements[domain]` contains `warrant`, a warrant of that exact type is required to accept an exercise of that domain. Distinguishing test: T14.

### A2. How are multiple `authority_basis` entries combined?

The envelope has a list of references. Matching rules speak of "the record". Supporting artifacts may appear without conferring authority.

Competing readings: all entries must independently satisfy; any one conferring match suffices; exactly one conferring entry is allowed.

**Assumption B1:** accept if **at least one** conferring reference fully matches the domain's `any_of` and all matching rules. Non-conferring entries never satisfy and do not, by themselves, poison a separate matching conferring entry. Empty list is `missing_required_basis`. Distinguishing test: T39.

### A3. How is resolution performed?

The files say the frozen registry is a research resolver and that production representation may vary. No resolution protocol is specified.

**Assumption R1:** the evaluator is given an explicit `basis_records` map (id → record). There is no network/registry I/O. Unlisted id is `unresolvable_authority_basis`.

### A4. How is "new exercise" versus historical audit signaled?

The files distinguish the two but do not define the input bit.

**Assumption H1:** evaluation input includes `exercise_kind` ∈ {`new`, `historical`}. Default, if omitted, is `new` (anti-widening: currentness is required unless historical mode is explicit). Distinguishing test: T7/T22.

### A5. Reference `current` versus record `current`

`reference_current_must_not_override_record_currentness` clearly blocks using `reference.current=true` to revive a stale record. It does not say whether `reference.current=false` independently rejects.

**Assumption C1:** for `exercise_kind=new`, currentness is taken from the **record** (`current` flag, and `revoked_at` if present). `reference.current` cannot make a non-current record current. A false reference flag is **not** an independent reject if the record is current (the record is authoritative). Distinguishing test: T21.

### A6. `revoked_at` versus `current` versus validity interval

Optional `revoked_at` is not mentioned in matching rules or reason precedence.

**Assumption C2:** if `revoked_at` is present and `revoked_at <= evaluated_at`, the record is treated as not current for new exercise. Historical audit still uses the validity interval and does not rewrite `authority_was_valid_at_time`. Distinguishing test: T22.

### A7. Validity-interval bound inclusivity and time format

No statement whether `valid_from`/`valid_until` are inclusive, nor the timestamp format.

**Assumption T1:** timestamps are ISO-8601 strings. If both sides parse as datetime, compare as aware/naive UTC datetimes; otherwise compare as Unicode strings. Both bounds **inclusive**. Distinguishing test: T38.

### A8. Envelope `authority_basis` type: list versus object

**Assumption B2:** value must be a list of objects. A single object is malformed, not silently wrapped. Distinguishing test: T35b.

### A9. Qualification `scope` matching

Required to be present; not said to equal jurisdiction scope or record scopes.

**Assumption Q1:** check presence, accepted type, `subject_id == subject.id`, and currentness for new exercise. Do **not** reject solely because `qualification.scope` differs from `jurisdiction.scope`. Distinguishing test: T33b.

### A10. When is a target "stale"?

`stale_target_behavior: reject`. Envelope target has `current_hash` but no current flag. Warrant has `target_hash` and must match envelope target.

**Assumption S1:** reject `stale_target` when a presented warrant/target binding hash differs from `target.current_hash`, or when optional `target.current === false` is supplied. A hash-only envelope with no warrant and no `target.current` is not stale merely for having a hash. Distinguishing test: T25.

### A11. Participant `responsibilities` / `excluded_responsibilities`

No envelope field named `responsibility`. Checking exclusions requires a claimed effect/responsibility.

**Assumption P1:** if the case includes `claimed_responsibilities` or `claimed_effects` that intersect the participant's `excluded_responsibilities`, reject `participant_excluded_responsibility`. If those claims are absent, do not infer responsibilities from subject identity or domain semantics. Distinguishing test: T18b.

### A12. Check order outside basis-binding precedence

Basis binding is checked before warrant or result payload. Overall order among malformed, unknown domain, participant, jurisdiction, and basis is unspecified.

**Assumption O1:** see §6.3. Distinguishing tests report the first reason under that order. If a reference implementation uses a different first-failure, that is disagreement about ordering, not necessarily about the underlying violation set. The outcome object will also include `violations` (all detected) so ordering disagreement is recoverable.

### A13. Delegation parent subset on target classes / target ids / subject

The delegation shape forbids extra operations, expanded scope, and extended expiry. Target-class/id subset and subject transfer (`delegator`/`delegate` vs `subject_ids`) are not fully specified.

**Assumption D1:** also require child `operations ⊆ parent.operations`, child `scope` ∈ parent `scopes` (or equal if parent has a singular scope), child `valid_until <= parent.valid_until`, child `valid_from >= parent.valid_from`. If both have `target_classes`/`target_ids`, child must be subset. Envelope subject must be in child `subject_ids` (ordinary subject matching). Do not additionally require envelope subject to equal `delegate` unless `delegate` is present; if present, require `subject.id == delegate` **or** `subject.id in subject_ids` (prefer `subject_ids` as binding, `delegate` as informational if they conflict, reject as amplification/malformed delegation). Simpler choice: if `delegate` present, `subject.id` must equal `delegate` and also be in `subject_ids`. Distinguishing test: T16.

### A14. `input_artifact_ids` matching

Required on warrants; no matching rule against the envelope.

**Assumption W2:** require the field to be present and a list; do not match contents against other ids unless a warrant-type `required_bindings` check needs presence. Distinguishing test: T34b.

### A15. Envelope `non_implications` versus warrant-type `non_implications`

Both exist. Equality is not required.

**Assumption N1:** attempted cross-use is checked against the **union** of envelope `non_implications` and, if a warrant is used, that warrant type's `non_implications`. The validator does **not** invent additional non-implications from domain semantics. Distinguishing test: T26/T27.

### A16. `generic_authorized_boolean_forbidden`

Does a present `authorized` field make the case malformed, or is the field ignored?

**Assumption G1:** if `authorized` (or `generic_authorized`) is present on the envelope or result, reject `generic_authorized_boolean_forbidden`. Do not use its value. Distinguishing test: T31.

### A17. Unknown extra envelope fields

Silent.

**Assumption X1:** ignore unknown fields except the forbidden generic authorized boolean and except treating `result` / `success` / `confidence` as non-authorizing. Do not treat extra fields as authority.

### A18. Domain `kind` as a constraint

No matching rule uses `kind`.

**Assumption K1:** `kind` is documentary. It does not produce a distinct reason. Mandate-ness is enforced via `any_of` and participant/domain tables, not via `kind`.

### A19. Historical record `authority_was_valid_at_time` conflicting with recomputation

**Assumption H2:** in `exercise_kind=historical`, recompute whether the basis matched at `evaluated_at` ignoring later currentness. If the historical record claims `authority_was_valid_at_time=true` but recomputation says it was not valid then, reject `historical_validity_claim_false`. If it claims false, the evaluator reports the recomputation and does not "repair" the claim. Later revocation is not applied as a rewrite of that past bit.

### A20. Missing qualification type lists / warrant type lists

If `competence_required` is true but `accepted_qualification_types` is missing, the domain table still names types via `domain_basis_requirements.qualification`.

**Assumption Q2:** required qualification type is `domain_basis_requirements[domain].qualification` if present, else the `accepted_qualification_types` list. Same for warrant.

### A21. Whether `credential` with otherwise perfect fields confers authority

Listed as a basis type but not as conferring.

**Assumption B3:** `credential`, `receipt`, and `artifact` never satisfy an authority requirement (`supporting_artifact_reference_never_satisfies_authority_requirement`). Reason: `supporting_artifact_not_authority` (after type match / resolve). If the reference type is conferring but the record type is not, that is `authority_basis_type_mismatch` first if types differ, else the supporting-artifact reason.

### A22. `inapplicable_behavior`

Could apply to jurisdiction, warrant, or both.

**Assumption I1:** `jurisdiction.applicable !== true` → `jurisdiction_inapplicable`. `warrant.applicable !== true` (when warrant is present or required) → `warrant_inapplicable`. Both are rejects.

### A23. Evaluator totality

The files do not say that every possible JSON document has a specified outcome.

**Assumption U1:** structurally malformed inputs reject with `malformed_envelope` / `malformed_basis_record` / `malformed_warrant` / `malformed_qualification`. The evaluator does not return "unknown" for listed reject behaviors. It does not invent domain semantics for unlisted domains: unlisted domain is `unknown_domain`.

---

## 6. Validator outcomes / reason taxonomy

Derived from the files. Reasons in backticks are either copied from `reason_precedence` or constructed by mechanically turning a named rule into a stable identifier.

### 6.1 Outcome

```text
outcome ∈ {accept, reject}
```

No generic `authorized` boolean is emitted as the sole result. The machine-readable object is:

```text
{
  "outcome": "accept" | "reject",
  "primary_reason": <reason code or "ok">,
  "violations": [<reason codes in check order>],
  "notes": [<implementation-assumption tags if a branch was taken>],
  "spec_version": <loaded spec versions>
}
```

`accept` uses `primary_reason: "ok"` and empty `violations`.

### 6.2 Reason codes

**Structural**

- `malformed_envelope`
- `malformed_basis_reference`
- `malformed_basis_record`
- `malformed_warrant`
- `malformed_qualification`
- `malformed_delegation`
- `malformed_historical_record`
- `generic_authorized_boolean_forbidden`

**Domain / operation**

- `unknown_domain`
- `unknown_operation`

**Participant** (`SPEC-PARTICIPANT-BOUNDARY.json`)

- `participant_not_declared`
- `participant_domain_not_accepted`
- `participant_operation_not_accepted`
- `participant_excluded_responsibility`
- `participant_inferred_from_subject` (reject if a case asks to infer and omit `participant`)

**Jurisdiction / applicability / target**

- `jurisdiction_inapplicable`
- `jurisdiction_not_current`
- `stale_target`

**Propagation**

- `unknown_propagation_mode`
- `propagation_forbidden_field`
- `explicit_propagation_missing_fields`

**Basis binding** (copied from `reason_precedence`, this order)

1. `unresolvable_authority_basis`
2. `authority_basis_type_mismatch`
3. `authority_basis_not_current`
4. `authority_basis_subject_mismatch`
5. `authority_basis_domain_mismatch`
6. `authority_basis_operation_mismatch`
7. `authority_basis_scope_mismatch`
8. `authority_basis_target_class_mismatch`
9. `authority_basis_target_id_mismatch`
10. `authority_basis_outside_validity_interval`

Additional basis reasons from named rules / non-implications:

- `missing_required_basis`
- `supporting_artifact_not_authority`
- `authority_basis_type_not_allowed_for_domain` (record type not in domain `any_of`)
- `policy_identifier_without_bound_record` (alias of unresolvable when only an identity policy id is offered)

**Competence / warrant**

- `missing_required_qualification`
- `qualification_not_current`
- `qualification_type_mismatch`
- `qualification_subject_mismatch`
- `qualification_is_not_authority_basis`
- `missing_required_warrant`
- `warrant_not_allowed_for_domain`
- `warrant_type_mismatch`
- `warrant_domain_mismatch`
- `warrant_operation_mismatch`
- `warrant_target_mismatch`
- `warrant_not_current`
- `warrant_inapplicable`
- `warrant_is_not_operational_permission`

**Delegation**

- `delegation_parent_unresolvable`
- `delegation_operation_added`
- `delegation_scope_expanded`
- `delegation_expiry_extended`
- `delegation_not_subset_of_parent`

**Non-implication / result / history / payload**

- `non_implication_cross_use`
- `positive_result_self_authorizes`
- `semantic_payload_authority_effect`
- `decision_used_as_execution_permission`
- `historical_validity_rewritten`
- `historical_validity_claim_false`

### 6.3 Check order (Assumption O1)

1. Structural envelope / forbidden generic boolean / unknown propagation mode.
2. Unknown domain; unknown operation relative to the domain table.
3. Participant declared / accepts domain / accepts operation.
4. Jurisdiction applicable (and current, if `exercise_kind=new`).
5. Propagation forbidden-field checks.
6. Basis presence; then for candidate conferring references, **basis-binding matching in the spec's `reason_precedence` order**; supporting-artifact / `any_of` type allowance; validity interval; delegation parent subset.
7. Qualification if required.
8. Warrant if required or present (present but disallowed is `warrant_not_allowed_for_domain`).
9. Stale target.
10. Claimed effects vs non-implications and excluded responsibilities.
11. Result/semantic payload offered as authority.
12. Historical-record rewrite / false historical claim.

Basis binding is completed before warrant or result, matching `basis_binding_checked_before_warrant_or_result_payload`.

Among basis reasons, the spec list is the precedence for `primary_reason` of a single reference. If several conferring references exist and none fully match, `primary_reason` is taken from the conferring reference whose first failure is **earliest in `reason_precedence`**; ties go to earlier list position. This tie-break is Assumption O2.

---

## 7. Adversarial / metamorphic tests to implement

Minimum required probes from the task packet are marked **[required]**. Additional probes from the files are marked **[extra]**. Predicted `primary_reason` uses this interpretation, including labeled assumptions.

Shared happy-path fixture unless a test names otherwise: `exercise_kind=new`; participant `evidence-bundler`; domain `source_access`; operation `source.read`; subject `sub-1`; jurisdiction `{scope: "org-a", applicable: true, current: true}`; matching grant record current and in interval; propagation `none`; `non_implications` as an explicit list; no warrant; no qualification; no result.

Informational/mandate tests substitute the corresponding participant, domain, operation, basis type, qualification, and warrant.

### T01 subject/principal substitution **[required]**

Envelope `subject.id` replaced with `sub-2`. Record `subject_ids` remains `["sub-1"]`.

Predict: `reject` / `authority_basis_subject_mismatch`.

### T02 authority-domain substitution **[required]**

Envelope domain/operation/participant remain `source_access` / `source.read` / `evidence-bundler`. Record `authority_domain` set to `evidence_admission`.

Predict: `reject` / `authority_basis_domain_mismatch`.

(A variant T02b that also changes the envelope domain to `evidence_admission` while leaving a `source_access` grant is the same reason, after participant/operation checks if those also fail. T02 isolates the basis rule.)

### T03 typed-operation substitution **[required]**

Envelope domain `source_access`, operation `evidence.admit_passage`.

Predict: `reject` / `unknown_operation` (operation not in domain table).

T03b: envelope stays `source.read` but record `operations` is `["evidence.admit_passage"]`.

Predict: `reject` / `authority_basis_operation_mismatch`.

### T04 scope substitution **[required]**

Envelope `jurisdiction.scope="org-b"`; record `scopes=["org-a"]`.

Predict: `reject` / `authority_basis_scope_mismatch`.

### T05 target-class substitution **[required]**

Envelope `target.class="passage"`; record `target_classes=["document"]`.

Predict: `reject` / `authority_basis_target_class_mismatch`.

### T06 exact-target substitution **[required]**

Record `target_ids=["tgt-1"]`; envelope `target.id="tgt-2"`.

Predict: `reject` / `authority_basis_target_id_mismatch`.

T06b: `target_ids` absent/empty; envelope `target.id="tgt-2"`.

Predict: `accept` (no exact-target binding). Assumption: empty/absent `target_ids` means unbound.

### T07 current vs stale/revoked **[required]**

Record `current=false`; `exercise_kind=new`.

Predict: `reject` / `authority_basis_not_current`.

T07b: same record, `exercise_kind=historical`, `evaluated_at` inside interval, `authority_was_valid_at_time=true`.

Predict: `accept` (later currentness may be false). Assumption H1/H2.

### T08 validity interval / historical validity **[required]**

`evaluated_at` after `valid_until`.

Predict: `reject` / `authority_basis_outside_validity_interval`.

T08b: `exercise_kind=historical` with later `revoked_at` and a historical claim that the past bit must be rewritten to false.

Predict: `reject` / `historical_validity_rewritten` if the case asserts rewrite; recomputation does not itself rewrite.

### T09 authority reference type mismatch **[required]**

Reference `type="grant"`; record `type="policy"`.

Predict: `reject` / `authority_basis_type_mismatch`.

### T10 unresolvable authority basis **[required]**

Reference id not in `basis_records`.

Predict: `reject` / `unresolvable_authority_basis`.

### T11 competence present but mandate absent **[required]**

Domain `decision_mandate` / `assessment_mandate`; a qualification object is present; no conferring policy/grant.

Predict: `reject` / `missing_required_basis` (qualification is not a basis). Must not accept.

T11b: numeric qualification offered as the sole `authority_basis` entry of type `credential`.

Predict: `reject` / `supporting_artifact_not_authority` or `missing_required_basis`.

### T12 mandate present but required competence absent **[required]**

`numeric_relation` with matching grant, no qualification.

Predict: `reject` / `missing_required_qualification`.

### T13 valid warrant with wrong/missing mandate **[required]**

Well-formed `numeric-threshold-v1` warrant; missing or domain-mismatched basis.

Predict: `reject` / `missing_required_basis` or `authority_basis_domain_mismatch`. Warrant does not repair.

T13b: `decision-policy-v1` warrant plus a **grant** (not policy) for `decision_mandate`.

Predict: `reject` / `authority_basis_type_not_allowed_for_domain`.

### T14 valid mandate with wrong/missing warrant where warrant is required **[required]**

`decision_mandate` with matching current policy; warrant missing.

Predict under W1: `reject` / `missing_required_warrant`.

T14b: same, warrant type `numeric-threshold-v1`.

Predict: `reject` / `warrant_type_mismatch` (or domain mismatch on the warrant object).

If reference reveal shows T14 should accept, assumption W1 is falsified.

### T15 semantic/result payload mutation **[required]**

Happy-path `source_access` with `result={status:"fail", success:false, confidence:0}`. Mutate to `{status:"pass", success:true, confidence:1}` and alter free-text payload.

Predict: **same** `accept`. Result is opaque and has no authority effect.

T15b: no basis; only `result.success=true`.

Predict: `reject` / `positive_result_self_authorizes` (and `missing_required_basis` in `violations`).

### T16 delegation amplification **[required]**

Parent grant operations `["source.read"]`; child delegation operations `["source.read","task.dispatch"]`.

Predict: `reject` / `delegation_operation_added`.

T16b: child `valid_until` after parent.

Predict: `reject` / `delegation_expiry_extended`.

T16c: child scope not in parent scopes.

Predict: `reject` / `delegation_scope_expanded`.

T16d: child is a true subset.

Predict: `accept` if all other rules pass.

### T17 authority propagation versus re-establishment **[required]**

T17a: `propagation="identity_provenance_only"` and `propagated_fields` includes `competence` or `authority_domain`.

Predict: `reject` / `propagation_forbidden_field`.

T17b: `propagation="none"` and `propagated_fields` nonempty.

Predict: `reject` / `propagation_forbidden_field`.

T17c: authority re-established as first-class envelope + basis; `propagation="identity_provenance_only"` with only `source_id`/`content_hash`.

Predict: `accept`.

T17d: `propagation="explicit"` listing `warrant` without a first-class warrant object.

Predict: `reject` / `propagation_forbidden_field`.

### T18 participant responsibility / effect-domain substitution **[required]**

`participant="evidence-bundler"` with domain `decision_mandate`.

Predict: `reject` / `participant_domain_not_accepted`.

T18b: `participant="claim-audit-lab"` with `claimed_responsibilities=["decision_mandate"]`.

Predict: `reject` / `participant_excluded_responsibility`.

T18c: omit `participant`, leave `subject.kind="evidence-bundler"`.

Predict: `reject` / `malformed_envelope` or `participant_not_declared`. Must not infer.

### T19 malformed / unknown domain or operation **[required]**

T19a: `authority_domain="frobnicate"`.

Predict: `reject` / `unknown_domain`.

T19b: `source_access` + `source.write`.

Predict: `reject` / `unknown_operation`.

T19c: missing `target.current_hash`.

Predict: `reject` / `malformed_envelope`.

### T20 supporting artifact as sole basis **[extra]**

`authority_basis=[{type:"artifact", id:"art-1", current:true}]` with a fully filled artifact record.

Predict: `reject` / `supporting_artifact_not_authority`.

### T21 reference current cannot override record **[extra]**

Reference `current=true`; record `current=false`.

Predict: `reject` / `authority_basis_not_current`.

### T22 historical valid, later revoked, new exercise **[extra]**

Record `current=false`, `revoked_at` after original `evaluated_at`; interval covered the original time.

T22a `exercise_kind=historical` at the original time: `accept`.

T22b `exercise_kind=new` at "now": `reject` / `authority_basis_not_current`.

### T23 cross-domain warrant **[extra]**

`source_boundary` exercise presenting `numeric-threshold-v1`.

Predict: `reject` / `warrant_type_mismatch` or `warrant_domain_mismatch`.

### T24 jurisdiction inapplicable **[extra]**

`jurisdiction.applicable=false`.

Predict: `reject` / `jurisdiction_inapplicable`.

### T25 stale target hash **[extra]**

Warrant `target_hash` ≠ envelope `target.current_hash`.

Predict: `reject` / `stale_target` or `warrant_target_mismatch`. Primary: `warrant_target_mismatch` if warrant matching runs before stale-target; `stale_target` if hash divergence is classified as staleness. **Prediction: `warrant_target_mismatch` as primary, `stale_target` also in `violations`.**

### T26 non-implication cross-use **[extra]**

`numeric_relation` with valid basis+qualification+warrant; `claimed_effects` includes `source_boundary.validity`.

Predict: `reject` / `non_implication_cross_use`.

### T27 non-implication not inferred **[extra]**

Same as T26 but `claimed_effects` includes an effect string that is **not** on any declared non-implication list (for example `unrelated.foo`). Envelope still carries the listed numeric-warrant non-implications.

Predict: do **not** reject for `non_implication_cross_use`. (May still accept if other rules pass.) This falsifies an over-inferring validator.

### T28 grant used for decision_mandate **[extra]**

Matching grant, domain `decision_mandate`.

Predict: `reject` / `authority_basis_type_not_allowed_for_domain`.

### T29 identity policy_id without bound record **[extra]**

`propagation="identity_provenance_only"` with `policy_id`; `authority_basis` empty.

Predict: `reject` / `missing_required_basis`. Must not treat `policy_id` as authority.

### T30 jurisdiction current false on new exercise **[extra]**

Predict: `reject` / `jurisdiction_not_current`.

### T31 generic authorized boolean **[extra]**

Happy-path except envelope `authorized=true` and, in a variant, missing basis plus `authorized=true`.

Predict: `reject` / `generic_authorized_boolean_forbidden`. Value is irrelevant.

### T32 qualification cannot substitute for basis **[extra]**

`numeric_relation` with valid qualification and warrant; `authority_basis` empty.

Predict: `reject` / `missing_required_basis`. Notes may include `qualification_is_not_authority_basis`.

### T33 qualification subject mismatch **[extra]**

Valid numeric case; `qualification.subject_id` ≠ `subject.id`.

Predict: `reject` / `qualification_subject_mismatch`.

T33b: `qualification.scope` ≠ `jurisdiction.scope`.

Predict under Q1: **accept** (scope not specified as a match key). Distinguishes Q1.

### T34 warrant operation mismatch **[extra]**

Numeric warrant with `operation="semantic.validate_absence"`.

Predict: `reject` / `warrant_operation_mismatch`.

### T35 empty authority_basis list **[extra]**

Predict: `reject` / `missing_required_basis`.

T35b: `authority_basis` as a single object rather than a list.

Predict under B2: `reject` / `malformed_envelope`.

### T36 unknown propagation mode **[extra]**

`propagation="inherit_all"`.

Predict: `reject` / `unknown_propagation_mode`.

### T37 evaluated_at exactly on bounds **[extra]**

`evaluated_at == valid_from` and a sibling case `== valid_until`.

Predict under T1: both `accept` if otherwise valid.

### T38 metamorphic: irrelevant payload fields **[extra]**

Happy-path plus extra `comment`, `narrative`, `result.confidence` mutation, `subject.display_name`.

Predict: still `accept`. These fields must not affect common authority validation.

### T39 mixed artifact + matching grant **[extra]**

`authority_basis` contains a non-conferring artifact reference and a matching grant.

Predict under B1: `accept`. Distinguishes AND-combination.

### T40 delegation without parent **[extra]**

Delegation record with unresolvable `parent_authority_id`.

Predict: `reject` / `delegation_parent_unresolvable`.

---

## 8. Explicit falsifiers of this interpretation

This interpretation is **wrong** (and should be reported as such at reveal, not patched pre-reveal) if any of the following hold in the specification's intended meaning:

1. **F1.** A valid warrant plus competence, without a conferring grant/policy/delegation, is accepted as operational permission.
2. **F2.** A positive semantic result or `success=true` accepts a case that otherwise lacks a conferring basis.
3. **F3.** `credential` / `receipt` / `artifact` references satisfy authority requirements.
4. **F4.** Unknown domain or operation is accepted, ignored, or given a default domain.
5. **F5.** Participant can be inferred from `subject.kind` or omitted without reject.
6. **F6.** Identity-provenance `policy_id` satisfies `decision_mandate` or any other domain without a bound record.
7. **F7.** Delegation children may add operations, expand scope, or extend expiry and still accept.
8. **F8.** Later revocation rewrites `authority_was_valid_at_time` for a past `evaluated_at`.
9. **F9.** New exercise of a non-current but in-interval record is accepted.
10. **F10.** `competence_required` domains accept without a matching qualification.
11. **F11.** Exact `target_ids` binding is ignored when nonempty.
12. **F12.** Envelope `reference.current=true` makes a `record.current=false` basis current.
13. **F13.** Cross-use of a warrant license (`numeric_relation.validity` used as `source_boundary.validity`) is accepted despite being listed in `non_implications`.
14. **F14.** The common validator inspects result payload values to decide authority (except to refuse self-authorization attempts).
15. **F15.** `grant` satisfies `decision_mandate` despite `any_of: ["policy"]`.
16. **F16.** Propagation mode `none` still carries competence/jurisdiction/warrant.
17. **F17.** A generic `authorized` boolean is honored.
18. **F18.** Historical validity without `evaluated_at` is accepted as exercised authority.

Assumption-level falsifiers (interpretation branches, not core negatives):

19. **F-W1.** Domains that list a warrant in `domain_basis_requirements` accept with no warrant. (Falsifies W1; would support reading 2 or 3.)
20. **F-B1.** A matching grant plus a leftover artifact is rejected. (Falsifies B1 any-of combination.)
21. **F-Q1.** Qualification scope must equal jurisdiction scope. (Falsifies Q1.)
22. **F-T1.** Bound instants `valid_from`/`valid_until` are exclusive. (Falsifies T1.)
23. **F-H1.** There is no historical/new distinction; currentness is always required, or always ignored in favor of the interval only.
24. **F-B2.** A single basis object (not list) is accepted.

---

## 9. Fields / payload content that must not affect common authority validation

Unless they are themselves structurally forbidden (generic `authorized`) or offered as a substitute for a basis, the following must not change the accept/reject decision:

- `result.status`, `result.success`, `result.confidence`, and any other result payload field (`result_shape.opaque_to_common_validator`)
- free-text semantic bodies, scores, rationales, narratives, comments, display names
- `subject.kind` as a participant/domain inference key
- identity-provenance fields (`source_id`, `artifact_id`, `content_hash`, `producer_id`, `policy_id`, `policy_version`) used as if they conferred authority
- supporting artifact content
- warrant licenses as operational permission
- qualification content as operational permission
- later `current=false` when evaluating a historical `evaluated_at` (must not rewrite the past bit)
- unlisted extra JSON fields other than the forbidden generic authorized boolean

These **may** affect validation, and should:

- subject id, participant, domain, operation, target class/id/hash, jurisdiction scope/applicable/current
- authority-basis type/id/current and the resolved record's matching fields
- `evaluated_at` versus validity interval / revoked_at
- qualification type/subject/current when competence is required
- warrant type/domain/operation/target/applicable/current when required or present
- propagation mode and propagated field names
- declared non-implications versus claimed effects
- delegation parent subset fields
- presence/absence of conferring basis

---

## 10. Behavioral predictions under named mutation classes

### Cross-domain

Changing envelope `authority_domain` away from the bound record's domain rejects (`authority_basis_domain_mismatch` and/or participant/unknown-domain reasons). A warrant from domain A does not authorize domain B. Non-implication lists block claimed cross-use; the validator will not invent further blocks.

### Cross-operation

An operation not in the domain table rejects `unknown_operation`. An operation in the table but not in `record.operations` rejects `authority_basis_operation_mismatch`. Delegation cannot add operations.

### Cross-target

Target class must be in `record.target_classes`. If `record.target_ids` is nonempty, envelope `target.id` must be a member. Warrant `target_id`/`target_hash` must match envelope target. Hash mismatch is not repaired by a positive result.

### Stale / revoked

New exercise of `current=false` or `revoked_at <= evaluated_at` rejects `authority_basis_not_current`. Stale jurisdiction rejects. Stale warrant/qualification rejects when those objects are required or presented. Reference `current=true` cannot revive a stale record.

### Delegation

Valid subset delegation with a resolvable parent and matching subject/domain/operation/scope/current/interval can accept. Any amplification rejects. Unresolvable parent rejects. Delegation is conferring, unlike artifact/receipt/credential.

### Warrant

Warrant never supplies operational permission. Where W1 applies, missing/wrong warrant rejects even if the mandate/basis is valid. Valid warrant with missing/wrong basis still rejects. Warrant/envelope domain-operation-target mismatch rejects.

### Semantic-payload mutations

Mutations of result/success/confidence/narrative on an otherwise valid operational envelope leave the outcome unchanged. The same mutations cannot rescue a missing or mismatched basis. If a case explicitly offers the payload as authority, reject.

### Propagation mutations

Moving competence, domain, jurisdiction, warrant, or the named never-implicit effects into propagated fields rejects. Re-stating them as first-class envelope/basis/qualification/warrant objects is the only path. `policy_id` in provenance is not a bound policy.

### Participant / effect-domain mutations

Wrong participant for the domain/operation rejects even if the subject holds a matching grant. Excluded responsibilities reject when claimed. Positive results cannot bypass participant declaration.

---

## 11. Implementation plan (non-authoritative)

Language: Python 3.11, standard library plus pytest already in this repository. No project-specific downloads.

Layout (to be created after this file is committed):

```text
research/contract_e_fresh_reproduction/
  PREREGISTRATION.md          # this file
  spec_loader.py              # load/validate the four JSON surfaces
  models.py                   # typed views of envelope, records, warrants
  reasons.py                  # outcome/reason constants
  validator.py                # evaluator
  cli.py                      # stdin/file JSON → JSON outcome
  tests/test_preregistered.py # T01–T40
  fixtures/                   # case JSON documents
```

The validator will load the four files at runtime and will not hard-code fixture IDs or expected hidden-case answers.

---

## 12. Contamination statement at preregistration

No `AUTHORITY-BASIS-REGISTRY.json`, frozen attack corpora, RC3A/RC3B validators, RESULTS files, PR narratives, or other withheld materials were consulted. No web or GitHub search was performed. No other reproduction's implementation was read. This interpretation uses only the four authorized files plus `TASK.md`.
