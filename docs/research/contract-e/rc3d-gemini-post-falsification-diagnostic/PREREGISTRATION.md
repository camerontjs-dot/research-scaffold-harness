# Contract E RC3D Gemini post-falsification diagnostic — preregistration

## Status

Research diagnostic only. This experiment cannot change the terminal disposition of PR #5, which remains **FALSIFIED**.

## Frozen subject under diagnosis

- repository: `camerontjs-dot/research-scaffold-harness`
- terminal Gemini comparison parent: `bc1ebd8e61fb884787b85155baf93d57773b6ff8`
- immutable pre-reveal Gemini freeze: `5364837007fe18f9e05eb39e0aa1031e28561290`
- frozen implementation blob: `consumer.py` `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`
- frozen pre-reveal test blob: `test_rc3d.py` `1102fc173086c45040da45125de4d138ee495765`

The diagnostic must not edit either frozen file.

## Exact causal question

The Gemini comparison exposed five clustered failures. Three appear to contradict explicit frozen public wire requirements and are not candidates for specification repair in this diagnostic:

1. canonical RC3D propagation uses nested `request`, but Gemini reads top-level `mode`/`fields`;
2. RC3C forbids silent singular/plural coercion for delegation operations/scope, but Gemini coerces strings;
3. RC3C requires `Qualification.scope` to be a string and freezes a malformed-shape reason, but Gemini reports a semantic mismatch for an array.

This diagnostic asks only whether the other two clusters are causally explained by residual specification ambiguity:

A. **Warrant cardinality** — inherited `warrant_shape` defines the warrant object but does not freeze whether the envelope field is singular or an array. The frozen evaluator corpus supplies a singular object; Gemini independently implemented list iteration.

B. **Supporting-artifact basis resolution** — RC3A allows artifact references in `authority_basis`; RC3B distinguishes authority-conferring types (`grant`, `policy`, `delegation`) and states that a supporting artifact may be part of the basis chain without itself satisfying the authority requirement, but the public text does not mechanically state whether non-conferring supporting references must resolve through the authority-conferring registry.

## Hypotheses

### W0 — frozen Gemini interpretation

A singular warrant object is passed unchanged. Prediction: warrant-bearing reference cases continue to raise the observed iteration `AttributeError`.

### W1 — singular normative warrant, plural internal representation

Diagnostic-only transformation: when and only when canonical `envelope.warrant` is an object, present `[warrant]` to the frozen consumer.

This is a post-reveal causal adapter and **must never be counted as independent agreement or native conformance**.

Prediction if warrant cardinality alone caused the cluster:

- warrant-cardinality execution errors collapse substantially or completely;
- the intended warrant-domain/type/current/target checks become reachable;
- the semantic-result metamorphic family completes rather than crashing;
- no new authority-relevant false permits are introduced by this transformation.

### B0 — frozen Gemini interpretation

Every `authority_basis` reference must resolve through `RegistryDocument.records`.

Prediction: citation/task/currentness positives carrying supporting artifact references continue to reject `unresolvable_authority_basis`.

### B1 — conferring-only registry resolution

Diagnostic-only transformation: before calling the frozen consumer, retain in resolver-facing `authority_basis` only references whose type is one of `grant`, `policy`, or `delegation`. Non-conferring references are not converted into grants and no registry records are invented.

This transformation emulates the alternative interpretation that supporting artifacts can remain part of the evidence/basis chain but are outside the authority-conferring registry resolver. It is not native-conformance evidence.

Prediction if resolution policy alone caused the cluster:

- canonical citation/task/currentness false rejects caused by unresolved artifact references collapse;
- the 9×15 authority-conferring compatibility matrix does not gain non-canonical false permits;
- negative authority-binding cases remain rejected for their actual conferring-basis defect.

## Factorial design

For every eligible envelope request, evaluate four diagnostic conditions without modifying `consumer.py`:

1. `W0+B0` — original frozen request, control;
2. `W1+B0` — warrant object wrapped only;
3. `W0+B1` — non-conferring basis refs excluded from resolver-facing input only;
4. `W1+B1` — both causal probes.

The control must reproduce the relevant terminal comparison failures before transformed results are interpreted.

## Eligible corpus

Reconstruct from the already-authorized revealed artifacts and frozen materialization rules:

- all RC3A envelope cases;
- RC3B direct basis attacks;
- the full 9×15 compatibility matrix;
- RC3C currentness cases;
- RC3C envelope wire cases;
- RC3C envelope reason cases;
- RC3C semantic-result metamorphic bases/variants.

Propagation, delegation, and historical requests are not transformed by this diagnostic.

## Required measurements

For each condition and relevant subset record:

- outcome match / false accept / false reject / execution error;
- observed decision/reason or exception;
- whether warrant transformation applied;
- whether supporting-reference transformation applied;
- newly recovered canonical positives;
- newly introduced false permits;
- compatibility-matrix canonical accepts, false accepts, false rejects;
- completed semantic metamorphic comparisons and authority-signature changes.

Also report cluster-specific paired transitions from control to each treatment.

## Explicit falsifiers

### Warrant-cardinality ambiguity hypothesis is weakened/falsified if

- wrapping the singular warrant does not remove the relevant execution errors; or
- major authority outcome disagreements persist after those errors disappear; or
- wrapping introduces authority-relevant false permits; or
- semantic metamorphic evaluations complete but authority signatures change with result payload alone.

### Supporting-artifact resolution ambiguity hypothesis is weakened/falsified if

- conferring-only resolution does not recover the unresolved-artifact canonical positives; or
- it introduces non-canonical matrix false permits; or
- it repairs cases whose expected rejection depends on a missing/mismatched conferring authority source.

## Nonclaims

Even a perfect diagnostic recovery:

- does not change PR #5 from FALSIFIED;
- does not establish independent Gemini agreement;
- does not authorize a repaired Gemini implementation;
- does not automatically justify RC3E;
- does not excuse the three explicit public-wire implementation failures left untouched;
- does not establish Contract E 1.0.0 or production policy.

## Decision rule after diagnostic

- If one or both ambiguous clusters collapse cleanly with no unsafe collateral effect, treat that as causal evidence for a narrowly scoped future specification clarification.
- If they do not, do not add specification text merely to fit the implementation; preserve the failure as implementation or deeper semantic disagreement.
- Do not launch another independent reproduction automatically.
