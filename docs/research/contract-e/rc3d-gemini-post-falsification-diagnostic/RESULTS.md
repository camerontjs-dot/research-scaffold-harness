# Contract E RC3D Gemini post-falsification diagnostic — results

## Terminal disposition

**FALSIFIED** for the preregistered hypothesis that the two disputed clusters can both be explained as safe, representation-only ambiguity repairs.

This result does not change the frozen Gemini reproduction in PR #5, which remains **FALSIFIED**.

## Integrity

Frozen subject remained unchanged:

- pre-reveal freeze: `5364837007fe18f9e05eb39e0aa1031e28561290`
- terminal comparison parent: `bc1ebd8e61fb884787b85155baf93d57773b6ff8`
- `consumer.py`: `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`
- `test_rc3d.py`: `1102fc173086c45040da45125de4d138ee495765`
- unchanged frozen suite: 42/42 OK

## Apparatus history

### First run — INCONCLUSIVE apparatus failure

- run: `33438328587`
- job: `99640111612`
- artifact: `9775243768`
- failure: diagnostic semantic-variant parser assumed every non-omission variant used a `result` wrapper and raised `KeyError: 'result'` before treatment evaluation.

R1 preregistered an apparatus-only parser correction. No scientific hypothesis or treatment changed.

### R1 accepted scientific diagnostic execution

- diagnostic branch head: `6335eada7566b41aba5da87331727b3688a4e0b9`
- run: `33438557293`
- job: `99640856174`
- artifact: `9775325969`
- artifact digest: `sha256:4b8ab34b6258c4f4e6f4f920f5621b3db97c6f1ae75cc48d7bfab827494b1a9e`
- control correspondence mismatches: `0`
- eligible envelope cases: `207`
- evaluations: `828` (`207 × 4` conditions)

The R1 workflow intentionally concluded failure because a preregistered treatment introduced authority-relevant false permits.

## Four diagnostic conditions

| Condition | Match | False reject | False accept | Execution error |
|---|---:|---:|---:|---:|
| W0+B0 control | 168 | 9 | 0 | 30 |
| W1 warrant-wrap only | 193 | 9 | **5** | 0 |
| B1 conferring-only resolution | 177 | 0 | 0 | 30 |
| W1+B1 combined | 202 | 0 | **5** | 0 |

## Hypothesis A — warrant cardinality

### Observed

94 eligible requests carried a singular warrant object.

Diagnostic one-element wrapping changed them as follows:

- 25 `execution_error → match`
- 5 `execution_error → false_accept`
- 64 `match → match`

The five newly exposed authority-relevant false permits were:

1. `N03-wrong-qualification`
2. `N07-jurisdiction-inapplicable`
3. `N08-target-stale`
4. `N09-participant-domain-substitution`
5. `N22-correct-semantics-wrong-responsibility`

These are not hidden-dialect-only rules. The frozen public authority explicitly requires, among other things:

- competence/qualification where the domain requires it;
- inapplicable jurisdiction to reject;
- stale target to reject;
- participant domain/operation responsibility bounds.

Therefore the warrant exception had been masking deeper implementation omissions.

### Positive causal evidence

The cardinality mismatch was nevertheless causal for the crash cluster:

- all 30 control execution errors disappeared under W1;
- four warrant-bearing canonical matrix positives became reachable;
- the semantic metamorphic family became executable.

Under W1, semantic metamorphism completed 9 frozen variant comparisons with **0 authority-signature changes**.

### Interpretation

**Warrant cardinality remains a real specification gap, but it is not a sufficient or safely isolated explanation of Gemini's warrant-bearing disagreement.**

A future public contract may still need to freeze `warrant` cardinality explicitly. However, merely adapting singular warrant objects into Gemini's list representation would produce unsafe false permits because the implementation also omitted independent qualification/jurisdiction/staleness/participant checks.

The preregistered “harmless cardinality clarification” hypothesis is therefore **FALSIFIED**.

## Hypothesis B — supporting-artifact registry resolution

### Observed

58 eligible requests carried at least one non-authority-conferring basis reference.

Under the diagnostic conferring-only resolver interpretation:

- 9 `false_reject → match`
- 49 `match → match`
- **0 false accepts**
- no new execution errors.

Recovered canonical positives:

- `P07-citation`
- `P08-task`
- `BASIS-P01-canonical-task-grant`
- `MATRIX-citation_ok--grant:citation-use`
- `MATRIX-task_ok--grant:task-dispatch`
- `CUR-P01-canonical-current`
- `CUR-P02-revoked-after-evaluation`
- `CUR-P03-valid-from-inclusive`
- `CUR-P04-valid-until-inclusive`

`N18-generic-authorized-flag` remained rejected, while its primary reason shifted from `unresolvable_authority_basis` to the downstream `missing_domain_authority_basis`, showing that removing the non-conferring resolver obligation did not manufacture authority.

### Compatibility-matrix safety

| Condition | Canonical accepts | Canonical false rejects | Canonical execution errors | Noncanonical false accepts | Noncanonical rejects |
|---|---:|---:|---:|---:|---:|
| Control | 3/9 | 2 | 4 | 0 | 126/126 |
| W1 only | 7/9 | 2 | 0 | 0 | 126/126 |
| B1 only | 5/9 | 0 | 4 | 0 | 126/126 |
| W1+B1 | 9/9 | 0 | 0 | 0 | 126/126 |

B1 alone recovered exactly the two artifact-bearing canonical matrix false rejects while preserving all 126 noncanonical rejects.

### Interpretation

**SUPPORTED WITH BOUNDS as a causal specification ambiguity.**

The evidence strongly favors explicitly distinguishing:

- references that may appear in the broader basis/provenance chain; from
- authority-conferring references that must resolve through the authority registry.

A supporting artifact does not need to become a registry authority record merely because it is present in `authority_basis`.

This diagnostic does not by itself establish the final production representation or whether the broader field should later be split into distinct `authority_basis` and supporting-artifact/provenance collections.

## Explicit implementation failures left untouched

The diagnostic deliberately did not repair or rescore:

1. nested RC3D propagation `request` container not consumed;
2. singular delegation operations/scope silently coerced rather than rejected as malformed wire;
3. array-valued `Qualification.scope` reported as semantic mismatch instead of malformed wire.

Those remain direct disagreements with explicit frozen public authority.

## Scientific interpretation

The five original Gemini clusters now separate into:

| Cluster | Result |
|---|---|
| supporting artifact resolution | **specification ambiguity strongly supported** |
| warrant singular vs list | **real cardinality gap, but not sufficient; unsafe implementation omissions revealed** |
| nested propagation request | explicit implementation disagreement |
| delegation singular/plural handling | explicit implementation disagreement |
| qualification scope cardinality | explicit implementation disagreement |

The diagnostic therefore argues against a broad RC3E rewrite. If a successor specification is later authorized, the smallest evidence-justified clarification is the authority-conferring resolver rule, with warrant cardinality frozen separately only if desired for interoperability. It should not add prose to compensate for the three explicit implementation mistakes or the five unsafe checks Gemini omitted.

## Nonclaims

- PR #5 remains FALSIFIED.
- No repaired Gemini implementation is independent evidence.
- No Contract E promotion is authorized.
- No successor reproduction is automatically authorized.
- The semantic opacity result under W1 is diagnostic-only because W1 is a post-reveal adapter.
