# CAL Pipeline V1 prototype-freeze qualification RC0

**Class:** bounded integration qualification / research infrastructure.

**Status at freeze:** cohort and authorities frozen before runner implementation.

## Objective

Determine whether one exact current CAL Pipeline V1 prototype is sufficiently coherent, deterministic, fail-closed, and reconstructable to freeze for **local smoke and use-driven testing**.

A green result does not authorize production, merge, release, canonical Contract C2 discovery, Contract E production use, execution, MainFrame mutation, or Brain promotion.

## Exact subject manifest

Use `MANIFEST.json` in this directory without substitution. The campaign is invalid if any checked-out subject differs from that manifest.

The current CAL -> Contract C2 producer-policy seam is considered available only through:

- current CAL semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
- hard-bound producer materializer blob `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`;
- exact Contract C2 promotion head `b42c827acb0a9fe65353354d709add0e27bab307`;
- independently frozen resolver authority `1d33e0612befcf8016816197c90c062373796df9`;
- policy digest `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`.

No predecessor resolver fallback is permitted for current CAL.

## Frozen cohort

`COHORT.json` contains exactly ten cases and was committed before the qualification runner.

The cohort covers:

1. frozen ClaimGate `DECLARED` branch, through external Contract A validation and Evidence Bundler;
2. frozen ClaimGate `NOT_NEEDED` branch, then unsupported-family CAL fail-closed through Decision/Contract D;
3. frozen ClaimGate `ABSTAINED` branch, with no authoritative Contract A and no EB execution;
4. raw strict-comparison support, expected CLEAR, with research-only Contract E dry pressure;
5. raw strict-comparison refutation, expected HOLD;
6. raw strict-comparison mixed support/refutation, expected CAL abstention and HOLD;
7. raw strict-comparison no-deciding evidence, expected CAL abstention and HOLD;
8. raw direct-event support, expected CLEAR;
9. raw direct-event refutation, expected HOLD;
10. raw direct-event support plus negative-event unresolved evidence, expected unresolved precedence and HOLD.

For raw semantic cases, ClaimGate must author the Contract A object from the raw request. The harness may supply the explicit typed CAL target because automatic semantic-family typing is outside the frozen ClaimGate/CAL V1 authority. It may not hand-build or replace Contract A, Contract B, CAL relation state, Contract C2, Decision, or Contract D.

## Required observations

### Authority identity

Before behavior is evaluated, exact Git heads/tags and the CAL materializer/resolver blobs must match the manifest. Any mismatch is terminal.

### Determinism

For every EB-executed case, the admitted final EB package must reproduce byte-identically in a second empty output directory.

For every CAL-executed case, the complete CAL output directory must reproduce byte-identically in a second empty output directory.

For every Decision-executed case, two independent invocations over the same exact C2 input must produce byte-identical Contract D output.

The whole ten-case campaign must be executed twice into separate run directories. A canonical summary of behavioral outputs, excluding run-directory paths and timestamps, must be byte-identical across campaign repeats.

### Contract boundaries

Every emitted Contract A must pass the released/exact external Contract A validator used by the frozen integration candidate.

Evidence Bundler must use the frozen 10/3 integration profile and its compatibility carrier. Admission remains explicit harness admission of retained candidates and must be preserved in evidence.

CAL must consume the emitted Contract B world through its canonical `validate-bundle` / `run-bundle` surface.

Contract C2 must be produced only from current CAL's actual `AuditContext` + native result through the exact hard-bound materializer and must pass:

- C2 object validation;
- exact Contract-B-reference validation;
- producer-policy resolution against independently selected resolver authority `1d33e061...`.

Decision must consume that exact C2 object and produce canonical Contract D through the frozen C2 ingress surface.

Contract E is research-only and may be exercised only on the strict-support CLEAR D as non-conferring support. No effect may execute.

## Hostile controls

The qualification must fail closed on at least these mutations:

- Contract A root text/content mutation under stale identity;
- CAL target stale text hash;
- CAL target proposition-ID alias/substitution;
- Contract C2 wrong externally supplied whole-object SHA at Decision ingress;
- Contract C2 wrong expected Contract-B binding at Decision ingress;
- Decision target/content substitution;
- wrong Contract C2 authority directory;
- current CAL C2 object evaluated against the predecessor resolver authority;
- current CAL C2 object with wrong policy digest;
- current CAL C2 object with resolver-commit substitution;
- Contract E dry controls for revoked, expired, wrong target and ambiguous target;
- Contract D support alone must not confer Contract E authorization without valid independent AuthorityState.

No mutation may be silently normalized into acceptance.

## Evidence preservation

The runner must preserve per-case:

- raw request or exact frozen fixture identity;
- ClaimGate receipt and Contract A when emitted;
- EB package, admission decision, Contract B, aperture/candidate history and replay identity;
- typed CAL target;
- native CAL result and replay identity;
- canonical Contract C2 bytes, whole-object hash, resolver authority and validation summary;
- Decision stdout/Contract D and replay identity;
- Contract E dry summary when invoked;
- hostile-control command/stdout/stderr receipts.

Before upload, the complete evidence directory must be packed into a deterministic tar archive using filesystem-safe archive entry names. The archive SHA-256 and a file-hash manifest must be recorded outside the archive. This specifically prevents platform artifact transport from silently dropping evidence because of unsafe filenames.

## Classification rule

`CAL_PIPELINE_V1_PROTOTYPE_CANDIDATE_FROZEN_FOR_LOCAL_SMOKE` requires all of the following:

- all ten preregistered cases reach their expected terminal stage/state;
- every required boundary validation passes;
- all component preflight suites selected by the workflow pass;
- all hostile controls reject or deny as preregistered;
- EB, CAL, Decision and whole-campaign deterministic replay pass;
- exact current CAL producer-policy resolution succeeds only through the frozen successor resolver authority;
- complete evidence archive and hashes are present;
- no semantic/runtime component was changed during the campaign.

Otherwise classify the first causal failure by stage when possible. Apparatus failures must remain distinct from component/seam failures.

## Stop rule

Do not tune retrieval, ClaimGate semantics, CAL semantics, C2 semantics, Decision policy, or Contract E to make RC0 green. Preserve the first red result. A harness-only defect may be repaired only in a separately preregistered RC1 successor that leaves the frozen manifest and cohort byte-identical.
