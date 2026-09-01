# Contract E Semantic Recoverability Audit — Cohort Comparison Terminal Record

Status: **TERMINAL**

Primary research disposition: **FALSIFIED**

This disposition falsifies the broad semantic-recoverability claim for the current frozen resolved artifact. It does **not** falsify the Contract E architecture, the domain separation model, or the many rules on which readers converged. It does not authorize Contract E amendment, promotion, release, implementation, or production behavior.

## Frozen question under review

Preregistered claim:

> Given one provenance-traceable resolved normative artifact and no prior Contract E reasoning, independent competent readers derive materially the same authority semantics, including explicit underdetermination where the artifact does not decide.

Frozen authority:

- apparatus-contracts content freeze: `3e522b79208f5b918d51d903b4fcc0623145923d`
- apparatus-contracts PR #47 frozen head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`
- materialized resolved-contract SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- semantic-question blob: `867dfe4d1be40344bc07b651c060c78b5e9307d7`
- question-task blob: `52dd27a23bde3cd0b465cd8cdc93347fd1bdba5d`
- question count: 51

The frozen apparatus was not changed after reader observations.

## Primary durable reader cohort

### Reader 1 — GitHub Copilot CLI

Draft evidence PR: `research-scaffold-harness#8`

- frozen interpretation commit: `a3c2ea532e5d4ba42bec404760509058198bec62`
- interpretation SHA-256: `73ca20406b07df6981079ff98a6501378edfea62aca54b77551747ff5bd879bd`
- same-session semantic-answer commit: `e64ac67112998fd2e886438919c4ece5bfc1ab51`
- semantic-answer SHA-256: `53f1cdd678f82f107a65256a1f47b4bed952f53f4c1904f6890ac720da6100c1`
- reported question counts: PERMIT 5 / REJECT 45 / UNDERDETERMINED 1

### Reader 2 — Grok CLI

Draft evidence PR: `research-scaffold-harness#10`

- CLI: `grok 1.0.13 (5e9a58528b76)`
- runtime model: `grok-4.6-build`; session summary `grok-4.6`
- session: `f6a9e985-4d54-48c5-a0cb-d5b679b256fc`
- interpretation SHA-256: `5e1d0b7c86297f5b67fa132718304fdc806c9b54682f72f5265f59422b01ea20`
- semantic-answer SHA-256: `40f26fc68fd56e45eb4356e3fdccd6f5d3b58fb644cf4cf2cb591da20eb16d1b`
- counts: PERMIT 3 / REJECT 45 / UNDERDETERMINED 3
- phase 2 used exact `--resume` of the phase-1 session

### Reader 3 — Gemini CLI

Draft evidence PR: `research-scaffold-harness#11`

- CLI: `gemini 0.46.0`
- session: `16fd5a48-84c7-491c-b804-107f9eaa805f`
- successful runtime calls used `gemini-3-flash-preview`
- failed initial call used `gemini-3.1-pro-preview-customtools`
- reader-authored model metadata says `gemini-2.0-flash-exp`; this conflict is preserved and not repaired
- interpretation SHA-256: `717746bb32bcf9e2ec625a0160ffd99436dce46d4b30367ad1fcdb36578d8444`
- semantic-answer SHA-256: `071e34fe642815ba813957f382b037dd47d3e307d2ff91036b80f8e91b14563f`
- counts: PERMIT 4 / REJECT 45 / UNDERDETERMINED 2
- phase 2 resumed the same session UUID

## Durable question-level agreement

Across the three GitHub-durable readers:

- unanimous outcomes: **48 / 51 = 94.12%**
- Copilot ↔ Gemini exact outcome agreement: **50 / 51 = 98.04%**
- Copilot ↔ Grok exact outcome agreement: **48 / 51 = 94.12%**
- Grok ↔ Gemini exact outcome agreement: **49 / 51 = 96.08%**

The three disputed question IDs are:

| Question | Copilot | Grok | Gemini | Classification |
| --- | --- | --- | --- | --- |
| `Q-BASIS-08` | PERMIT | UNDERDETERMINED | UNDERDETERMINED | Copilot reader-error candidate against explicit source-set underdetermination |
| `Q-PROP-03` | REJECT | UNDERDETERMINED | REJECT | Grok phase-2 reader-error candidate; absence of separate reauthorization is stated in the scenario |
| `Q-HIST-01` | PERMIT | REJECT | PERMIT | semantic-question polarity defect candidate; reasons converge on the same historical rule |

### Q-BASIS-08

The frozen resolved artifact states:

`/effective_contract/authority_basis/registry_resolution_of_nonconferring_supporting_artifacts = UNDERDETERMINED_BY_SOURCE_SET`

The frozen reader task also instructs readers not to choose a preferred answer for an explicitly underdetermined item. Grok and Gemini returned `UNDERDETERMINED`; Copilot returned `PERMIT`. The Copilot outcome is therefore a reader-error candidate before any contract change is considered.

### Q-PROP-03

The frozen resolved artifact states that explicit propagation authority fields remain forbidden unless separately reauthorized. The scenario explicitly says there is no separate reauthorization. Copilot and Gemini returned `REJECT`; Grok returned `UNDERDETERMINED`.

Grok's phase-1 interpretation correctly identified that the *procedure or evidence sufficient to establish* separate reauthorization is itself underdetermined. That uncertainty does not decide the presented case because the question explicitly fixes separate reauthorization as absent. The Grok phase-2 `UNDERDETERMINED` is therefore a reader-error candidate rather than evidence that this scenario is underdetermined.

### Q-HIST-01

All reader reasons recover the same underlying historical rule: later revocation does not rewrite `authority_was_valid_at_time` for historical inspection.

The answer-label split arises because the prompt asks a yes/no proposition — whether later revocation rewrites history — while the allowed vocabulary is `PERMIT | REJECT | UNDERDETERMINED`. `PERMIT` can be read as permitting the historical validity conclusion; `REJECT` can be read as rejecting the proposition that later revocation rewrites it.

This is classified as a **semantic-question apparatus polarity defect candidate**, not a demonstrated Contract E semantic disagreement.

## Decisive falsifier: qualification subject/scope matching is not normatively specified

The broad recoverability claim is nevertheless falsified by a different observation that is more important than the 48/51 question agreement.

The frozen resolved artifact defines Qualification only as requiring:

- `type`
- `id`
- `subject_id`
- `scope`
- `current`

and requires currentness for new exercise. It contains no qualification matching-rules object and no normative predicate relating:

- `Qualification.subject_id` to envelope `subject.id`; or
- `Qualification.scope` to `jurisdiction.scope` or another scope source.

The reason precedence list contains `qualification_subject_mismatch` and `qualification_scope_mismatch`, but a reason token does not itself define the missing comparison predicate.

This gap was identified **before question reveal** by Grok as:

`U-QUALIFICATION-MATCHING-PREDICATES`

> What are the exact predicates for qualification subject and scope matching?

Grok's frozen interpretation states that the mismatch reasons are listed but no qualification matching-rules object is given.

The hidden question `Q-QUAL-04` later asks for an outcome when a valid `outcome_verifier` qualification is for a different subject. All three durable phase-2 readers returned `REJECT`, but that agreement requires an unstated subject-binding assumption. The question set therefore exposes a case whose intended rejection is plausible from reason naming but is not mechanically recoverable from an explicit normative predicate in the resolved artifact.

Agreement among readers does not turn an unstated rule into normative text.

This satisfies the preregistered falsification concern that authority-relevant questions may require an unstated assumption. Therefore the current resolved artifact is not fully semantically recoverable as claimed.

## Additional phase-1 underdeterminations preserved by Grok

Grok's pre-question interpretation identified further unresolved areas beyond the two explicitly frozen source-set questions, including:

- aggregation semantics for multiple `authority_basis` references;
- whether `delegation` can satisfy per-domain `any_of` basis requirements that list only grant/policy;
- treatment of surplus qualifications and warrants;
- exact qualification subject/scope matching predicates;
- semantic obligations for `Warrant.input_artifact_ids`;
- what constitutes separate reauthorization and the exact authority-field set;
- delegation historical-currentness semantics;
- the required shape of the common-envelope `propagation` field;
- inherited propagation-rule closure;
- several malformed-wire/reason-precedence edge cases.

These findings are evidence records, not automatically accepted new Contract E requirements. They should be discriminated before semantic amendment.

## Supplemental ChatGPT witness

A separate fresh ChatGPT GPT-5.6 Sol reader was executed by the operator after a prior contaminated launch was discarded before semantic interpretation.

The clean run reported:

- model: GPT-5.6 Sol
- resolved-contract SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- question counts: PERMIT 3 / REJECT 45 / UNDERDETERMINED 3
- four-reader unanimous outcomes: 47 / 51

Its phase-1 interpretation independently identified several of the same extra gaps as Grok, including authority-basis aggregation, delegation-as-basis semantics, qualification subject/scope matching, warrant input-artifact binding, separate-reauthorization semantics, delegation historical currentness, envelope propagation shape, and inherited propagation-rule closure.

At the time of this terminal record, this ChatGPT witness is preserved in the operator conversation but does not have an immutable GitHub output SHA/PR. It is therefore **supplemental corroboration**, not the sole basis of the primary disposition.

## Deviations

Preserved reader/apparatus deviations include:

1. Grok strict/read-only sandbox profiles failed to launch because of the Docker socket symlink; workspace sandbox plus read-tool/path restrictions was used.
2. Filesystem isolation was working-directory + isolated CLI homes + tool/permission limits rather than kernel-strict confinement.
3. Bundled Grok skills were present in the isolated home but not in the tool allowlist.
4. Gemini sandbox flag was not applied.
5. Gemini runtime telemetry and reader-authored model identity disagree; telemetry shows successful `gemini-3-flash-preview` calls while the reader wrote `gemini-2.0-flash-exp`.
6. Gemini's isolated environment exposed both `GOOGLE_API_KEY` and `GEMINI_API_KEY`; the CLI used `GOOGLE_API_KEY`.
7. Pretty-printed frozen JSON was extracted from fenced model output while lossless raw CLI wrappers were retained locally.
8. Phase-1 reader-task/schema files remained present after question reveal.
9. Gemini attempted `run_shell_command` during phase 1; it failed with no semantic output from that attempt.

None of these observed deviations establishes cross-reader or prior-project semantic contamination. They remain part of the evidence quality record.

## What is supported

The cohort strongly supports recoverability of a large bounded core, including:

- domain/operation separation;
- basis binding by type, subject, domain, operation, scope, target class/id;
- fail-closed currentness and inclusive validity bounds;
- participant domain/operation boundaries;
- typed warrant domain/operation/target binding;
- default non-propagation;
- delegation no-amplification rules;
- historical validity not being rewritten by later revocation;
- result payload non-authority;
- reason precedence for the cases directly stated.

## What is not supported

This audit does not establish:

- full semantic recoverability of the current resolved Contract E artifact;
- Contract E 1.0.0;
- production authorization behavior;
- implementation correctness;
- evaluator correctness;
- that majority reader agreement can substitute for a missing normative rule;
- that every additional Grok/ChatGPT underdetermination is a real required Contract E rule.

## Terminal disposition

**FALSIFIED** — the full semantic-recoverability claim for the present resolved artifact does not survive because at least one authority-relevant outcome requires an unstated qualification-binding predicate, while additional pre-question interpretation gaps remain live.

The narrower claim that the frozen artifact contains a **highly recoverable core with a small but material unresolved semantic boundary** is supported.

## Next authority

No Contract E semantic amendment is authorized by this result.

A successor experiment may test only the smallest independently surfaced gaps, starting with qualification subject/scope binding and authority-basis aggregation. It should use explicit candidate rules and falsifiers rather than treating majority reader behavior as a normative answer.

Any choice of new normative defaults is a new semantic decision and requires separate authority.