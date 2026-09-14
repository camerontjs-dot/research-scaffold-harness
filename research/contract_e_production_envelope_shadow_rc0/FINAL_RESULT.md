# Contract E Production Envelope Shadow RC0 — Final Result

Terminal disposition: **SUPPORTED FOR THE BOUNDED SHADOW CLAIM**

Production authorization: **false**

Merge/tag/release/promotion authorization: **false**

## Frozen lineage

Preregistration:

- base commit `d879dddb07e0c4f4f1b6588cebddefa662e15829`
- amendment 1 `038702cb5aacfbb42e6fee0848d98eb8d7cb6d1a`
- amendment 2 `436edca34a88d7ad85057c6c800ebc3f339a518c`
- amendment 3 `baff5409bc08ca2a513f7917f1061ec09134b5dd`

Frozen candidate:

- implementation freeze commit `b9d8e93ac414d37bb3288669526aab9bc28a9f5a`
- blob `bd60ba1da3e1098d4d1a82d6b99bae6255843529`
- SHA-256 `620688889de5acdffee648ad131355389bbf8d93eec45a34c8f9a58fd3e0ef37`

Frozen evaluator:

- evaluator freeze commit `96a5ef58b199fad22bfe46875b6074f6aab36f71`
- blob `b274b963603612ed3ff2993f76c067fa7c09ec31`
- SHA-256 `f10a23c9086fe5e9d6b6669cc95debdfb4198b46a947e6124274ef54e2be1265`
- frozen cases: 26
- frozen weak controls: 6

Freeze receipt commit:

- `4480438a8069e5d040ad9221c05be52e63c94f04`

Accepted workflow head:

- `93bd21ce3dd4335a1db670271decabcf0cd18003`

No candidate or evaluator byte changed after freeze.

## Exact external authorities

Contract D 1.0.0:

- release commit `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- core blob `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- validator blob `c03ef6c6f059cd03addf5e69b01025bb9a6af8d2`
- applicability consumer blob `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- effect registry blob `a40f4f4447470654bdc16d852f5927189ae30cc5`

Contract E RC3:

- sealed successor commit `a678c73a661853a3a704666fc6bbf29fa378948f`
- public SPEC blob `8c142c6b86dd2512f1df0c19aa36dbef759d6c18`
- successor reference blob `00d4d8f078073388d751546c24678825b89a6402`
- fresh-independent seal `9feb44d8c8ea96176f797fe0ef692cc8e4d13656`
- fresh-independent implementation blob `9019abd8ade820988de1f899b2ccef9e57e9a908`

## Accepted hosted run

Workflow run:

- run `33939307886`
- job `101233414092`
- conclusion `success`
- head `93bd21ce3dd4335a1db670271decabcf0cd18003`

Evidence artifact:

- artifact ID `9961243481`
- name `contract-e-production-envelope-shadow-rc0-93bd21ce3dd4335a1db670271decabcf0cd18003`
- size 5,928 bytes
- digest `sha256:ea7fb2e4bc499d6c7e083043f2d3cbd754b8acfd59fbfe693b980be2e6762833`

The hosted run verified all frozen Git blob identities and installed exact `rfc8785==0.1.4` before science.

## Scientific result

- case count: 26
- exact case passes: 26/26
- false allows: none
- positive failures: none
- target-integrity failures: none
- `execution_occurred` flag failures: none
- weak controls: 6/6 caught
- missed weak controls: none

Positive behavior:

- exact released Contract D applicability outcome `candidate_for_authorization`;
- exact immutable shadow intent;
- exact Contract D target kind, ID, and content hash bound to the disposable point-of-use target;
- exact current target pre-state;
- exact Contract E request-reference binding;
- sealed successor Contract E `authorized=true`;
- fresh-independent Contract E `authorized=true`;
- no normative Contract E disagreement;
- target unchanged across point-of-use authorization window;
- unseen idempotency key atomically reserved;
- `shadow_allowed=true`;
- `execution_occurred=false`.

Negative controls correctly denied:

- historical authorized receipt with current revocation;
- historical authorized receipt with current expiry;
- wrong subject;
- wrong operation;
- wrong intent reference;
- duplicate target reference;
- relevant blocker;
- Contract D byte substitution;
- effect substitution;
- scope-parameter substitution;
- forged intent identity;
- Contract D target-ID substitution;
- stale target pre-state;
- target content changed during the authorization window;
- path traversal;
- symlink escape;
- missing disposable-root marker;
- replayed idempotency key;
- malformed AuthorityState;
- malformed AuthorizationRequest;
- Contract E engine exception;
- Contract E normative disagreement;
- Contract D `hold`;
- Contract D not-applicable consumer result;
- Contract D evaluation failure.

## Weak-control qualification

All six seeded weak consumers were caught because each false-allowed its targeted negative:

1. `W-RECEIPT-AS-PERMIT`
2. `W-AUTH-BEFORE-TARGET-CHECK`
3. `W-NO-PRESTATE-BINDING`
4. `W-NO-REPLAY-STATE`
5. `W-PATH-TEXT-ONLY`
6. `W-FAIL-OPEN-ENGINE-ERROR`

## What RC0 supports

Within this disposable, no-live-mutation experiment, the evidence supports the following bounded claim:

> A point-of-use shadow enforcement component can mechanically bind an exact released Contract D candidate-for-authorization Decision to an exact immutable consuming intent, exact Contract D target identity and content pre-state, exact current Contract E authority/request, target path confinement, current file state, and explicit replay state; it can fail closed on the preregistered stale/replayed/substituted/concurrent/error conditions without treating a historical AuthorizationReceipt as reusable permission and without mutating the protected target.

The experiment also supports the ordering choice tested here:

1. exact Contract D applicability;
2. exact execution-intent binding;
3. disposable-root/path confinement;
4. target lock and current pre-state observation;
5. fresh point-of-use Contract E evaluation;
6. target re-observation after authorization;
7. replay-key reservation;
8. shadow decision.

This is evidence for a bounded envelope ordering, not a production architecture authorization.

## Preserved observations and limitations

- No apparatus failure occurred in the accepted run.
- The concurrent-change negative deliberately injected an external target mutation during the authorization window. The candidate detected it and denied. That injected change is test stimulus, not candidate execution.
- Some malformed/substitution cases fail before Contract E is invoked because the consuming profile itself detects the mismatch. This is intended fail-closed composition, not evidence that Contract E independently detects every consuming-profile error.
- Dual Contract E execution is research instrumentation only. It is not proposed as a production requirement.
- The disposable marker prevents accidental invocation against an unmarked root but is not a production trust control.
- The replay journal establishes only the local RC0 reservation behavior tested here. It does not establish crash recovery or exactly-once execution.

## Explicit nonclaims

RC0 does **not** establish:

- a real production Contract E consumer;
- trusted or authenticated AuthorityState origin;
- authenticated actor/workload identity;
- production trust-root choice;
- production ownership/change authority;
- concrete serialization semantics for `knowledge.add_verified_tag@1`;
- a live MainFrame knowledge mutation;
- crash-safe execution/recovery;
- exactly-once execution;
- rollback;
- an authenticated/signed execution receipt;
- independent verification that a real downstream effect occurred;
- safety against a malicious same-user process with unrestricted filesystem authority;
- production promotion, merge, tag, or release.

## Deep Research reconciliation status

The user reported that the September 4 Production Authorization Envelope Deep Research pass is complete in a separate ChatGPT project/thread. The current supervisor context can locate the prompt but cannot retrieve the completed response through the available cross-conversation retrieval surface. An older report has not been substituted.

Therefore this RC0 result is supported by the frozen CAL/Contract authorities, live GitHub reconnaissance, the operator-provided local MainFrame archaeology, and the separately recorded narrow standards cross-check. Any additional conclusions unique to the completed Deep Research report remain unreconciled until its actual contents are available in this execution context.

## Terminal classification

**TERMINAL: SUPPORTED FOR THE BOUNDED SHADOW CLAIM**

Further progress requires a **NEW EXPERIMENT**.

The smallest successor should test execution/receipt/verification mechanics on disposable state without inventing the production semantics of the `knowledge.add_verified_tag@1` representation. Production trust-root, authenticated-principal, ownership, and concrete effect-representation choices remain later governance gates.
