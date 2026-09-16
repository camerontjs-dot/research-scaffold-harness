# CAL Pipeline pre-local pressure successor RC1

## Classification

Successor Research Infrastructure experiment after RC0 run `35049854474` terminated `APPARATUS_INVALID_FOR_FULL_INTEROPERABILITY_CONCLUSION`.

RC0 evidence remains immutable in GitHub Actions/artifact history and `../cal_pipeline_prelocal_rc0/RUN1_RECONCILIATION.md`.

No production component semantics are changed by RC1.

## Exact corrections from RC0

1. ClaimGate pressure uses the exact qualification-runbook test subset rather than the whole repository pytest surface.
2. Released Contract C1 and Contract D checkouts include their annotated release tags because Decision authority verification explicitly binds them.
3. The invalid out-of-profile strict-comparison ClaimGate canary is removed.
4. The experiment is split into two lanes without weakening either component:
   - a true raw-claim fail-closed lane beginning at ClaimGate;
   - an explicitly test-only downstream positive-control lane beginning from a valid Contract A `not_decomposed` object emitted through the Contract A emitter, not claimed as a ClaimGate semantic decision.

Everything else, including exact component SHAs and the current-CAL-to-C2 producer-authority discriminator, remains fixed.

## Lane A: true raw-claim fail-closed E2E

Input claim:

`Valve Cerulean was inactive.`

This is a ClaimGate-supported single-proposition shape and should emit authoritative Contract A `not_decomposed`.

The exact Contract A object flows through EB 10/3 and Contract B 1.2. The explicit CAL test adapter classifies it as `assertion_scope`, which is outside CAL's two deciding families. CAL must therefore fail closed as `NOT_CHECKABLE / UNSUPPORTED_SEMANTIC_FAMILY`.

That result is structurally materialized to Contract C2 and consumed by Decision, which must HOLD. The true pipeline lane stops there. Contract E is not invoked from a HOLD decision.

## Lane B: downstream positive control

A valid Contract A `not_decomposed` object is emitted by the frozen Contract A emitter for:

`Women had a higher rate than Men.`

with an exact matching supplied source.

This is an explicit test fixture for the downstream boundary. It is not evidence that ClaimGate can semantically authorize this sentence.

The fixture flows through EB 10/3, Contract B 1.2, a strict-comparison typed target, current CAL, Contract C2 structural materialization, Decision CLEAR, canonical Contract D 1.0 and Contract E research-only dry authorization pressure.

## Producer-authority discriminator

Both lanes test the same critical seam:

- current CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`;
- frozen Contract C2 qualified CAL producer identity: `a902621e8baea3063dddd7f92ba975aade305464`.

RC1 may prove structural materialization and downstream consumer behavior with the current object, but it must not fabricate or self-select a new producer resolver entry. If the independently frozen C2 resolver does not authorize `847cc970...`, the terminal scientific disposition remains:

`BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY`

Downstream structural pressure may continue after recording that blocker, but it cannot erase it.

## Required hostile controls

- stale Contract A root/hash;
- EB rejects invalid A and preserves exact 10/3/replay;
- CAL stale text hash, aliased proposition ID and non-empty output refusal;
- unsupported-family state remains distinct from no-deciding/mixed;
- C2 structural validation and exact B references;
- Decision stale C2 hash, wrong B binding, target substitution, wrong C2 authority, C1/C2 separation;
- Contract E 65-control suite;
- actual positive-lane Contract D supplied to Contract E as non-conferring support while revoked/expired/wrong/ambiguous target cases deny;
- exact repository identities and deterministic replay.

## Terminal classes

- `SUPPORTED_FOR_LOCAL_PIPELINE_SMOKE_WITH_BOUNDS`
- `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY`
- `INCONCLUSIVE_PRELOCAL_PRESSURE`
- `FALSIFIED_PRELOCAL_INTEROPERABILITY_CLAIM`
- `APPARATUS_FAILURE_BEFORE_SCIENTIFIC_COMPARISON`

A scientific blocker is not an apparatus failure. The evidence artifact must be uploaded before the readiness gate is evaluated.
