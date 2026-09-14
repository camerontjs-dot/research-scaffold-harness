# Contract E Production Envelope Shadow RC0 — Preregistration

Status: **PREREGISTERED / RESEARCH ONLY / NO LIVE MUTATION**

Production authorization: **false**

This experiment is a bounded successor to the Contract E production-profile `NOT_READY` result. It is not a Contract E semantic successor and does not alter the frozen Contract E RC3 predicate.

## 1. Scientific question

> Can a point-of-use shadow enforcement component bind an exact Contract D candidate effect to an exact immutable execution intent, exact current target pre-state, exact current Contract E authorization, and explicit replay state, then fail closed under stale/replayed/substituted/concurrent conditions **without** treating a prior AuthorizationReceipt as reusable permission and without performing the real mutation?

A positive result would support only the shadow point-of-use envelope ordering and binding discipline tested here.

It would not establish a production consumer, trusted root, authenticated principal, real execution semantics, exactly-once execution, or verification of an actual mutation.

## 2. Exact frozen authorities

### Contract D

Repository: `camerontjs-dot/apparatus-contracts`

Release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

Effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`

Effect under test:

`knowledge.add_verified_tag@1(scope=claim)`

The experiment MUST use a Contract D fixture that validates under the exact released Contract D validator/authority. It MUST NOT invent a new Contract D field or parameter.

### Contract E RC3 research authority

Frozen public SPEC blob: `8c142c6b86dd2512f1df0c19aa36dbef759d6c18`

Frozen sealed successor reference blob: `00d4d8f078073388d751546c24678825b89a6402`

Frozen sealed successor evaluator blob: `5bba49c6a412c689232ea1315df0153455dd316f`

Frozen fresh-independent implementation blob: `9019abd8ade820988de1f899b2ccef9e57e9a908`

The Contract E predicate, schemas, canonicalization, target-cardinality rule, currentness semantics, receipt semantics, and normative projection are immutable inputs.

No Contract E repair is authorized in this experiment.

## 3. Environment boundary

The experiment MUST run only against a disposable fixture root created for the test.

It MUST NOT:

- read or write a live `10_knowledge` target except optional read-only preflight proving the test root is elsewhere;
- modify a live MindGraph database;
- invoke Conduit to launch a mutating agent;
- enable ERS auto-promotion;
- change Claude/Codex hooks;
- change MainFrame runtime configuration;
- install production services;
- modify Contract D or Contract E;
- merge any research PR;
- emit a production authorization claim.

The candidate MUST reject target paths that resolve outside the disposable root.

## 4. Research-only execution-intent profile

RC0 defines one research consuming profile outside Contract D and Contract E.

This profile exists only so an immutable Contract E request reference can bind the exact proposed point-of-use operation without adding fields to Contract D or Contract E.

### 4.1 `ShadowExecutionIntent`

A shadow intent contains exactly:

- `schema = "cal-production-envelope-shadow-intent-rc0"`;
- `intent_id`;
- `contract_d_sha256` — SHA-256 of the exact validated Contract D bytes used by the test;
- `effect_id = "knowledge.add_verified_tag"`;
- `effect_version = "1"`;
- `effect_params = {"scope": "claim"}`;
- `target_root_id` — opaque identifier for the disposable fixture root;
- `target_relative_path` — normalized relative path below that root;
- `target_pre_state_sha256` — SHA-256 over the exact target bytes expected at point of use;
- `idempotency_key` — non-empty opaque key unique to the proposed execution attempt.

No field in this object is Contract D or Contract E authority merely by being present.

### 4.2 Intent identity

`intent_id` is `sha256:` plus SHA-256 over RFC 8785 JCS + one LF byte for the `ShadowExecutionIntent` excluding only `intent_id`.

This mirrors Contract E's canonical-byte discipline for research simplicity. It is a consuming-profile choice, not a new Contract E rule.

### 4.3 Contract E target binding

The AuthorizationRequest MUST contain exactly one validated request reference with:

- `kind = "cal.shadow-execution-intent"`;
- `version = "rc0"`;
- `immutable_id = <exact intent_id>`;
- `identity_sha256` computed exactly as Contract E RC3 requires for request references.

`jurisdiction.target_ref` MUST equal that exact reference identity and therefore resolve to exactly one validated reference under the frozen RC3 target-cardinality rule.

A historical AuthorizationReceipt may be supplied to a test case as evidence, but the candidate MUST NOT use it as standing permission.

## 5. Candidate point-of-use sequence

The candidate shadow PEP MUST use this ordering:

1. validate and canonicalize the research intent;
2. validate the exact Contract D fixture and verify the intent's `contract_d_sha256`, effect ID/version, and parameters against it;
3. resolve and confine the target to the disposable root; reject traversal, symlink escape, missing target, or non-regular target;
4. acquire an exclusive target-file lock where supported by the platform;
5. re-resolve the target after lock acquisition;
6. read the exact current target bytes and verify `target_pre_state_sha256`;
7. re-evaluate the supplied current AuthorityState against the supplied AuthorizationRequest **at point of use** using the exact frozen Contract E semantics;
8. as research instrumentation, run both the sealed successor reference and the frozen fresh-independent implementation; any normative disagreement, exception asymmetry, or inability to execute either implementation is fail-closed and recorded;
9. re-read/re-hash the target immediately after Contract E evaluation and before issuing a shadow allow; any change is fail-closed;
10. atomically reserve the `idempotency_key` in a disposable test journal only if it has not previously been reserved for an allowed intent;
11. emit a `ShadowPEPDecision`;
12. release the lock;
13. an independent verifier process re-opens the target and confirms its bytes were not mutated by RC0 and checks the shadow journal/decision evidence.

Dual Contract E execution in step 8 is **research instrumentation only**. RC0 does not propose dual-engine production authorization as architecture.

## 6. Candidate output

`ShadowPEPDecision` MUST make the following distinctions explicit:

- `shadow_allowed: true | false`;
- `execution_occurred: false` always in RC0;
- exact `intent_id` when valid;
- exact `contract_d_sha256` when valid;
- observed pre-evaluation target SHA-256;
- observed post-evaluation target SHA-256;
- Contract E sealed-reference authorization boolean when evaluable;
- Contract E independent-implementation authorization boolean when evaluable;
- whether the idempotency key was unseen/reserved/replayed;
- machine-readable failure classes;
- diagnostics that are explicitly non-authoritative.

A shadow allow means only: **the preregistered point-of-use preconditions held in this disposable test at this observation point**.

It MUST NOT be called an execution receipt, verification receipt, permit, grant, lease, or production authorization.

## 7. Frozen case matrix

The evaluator MUST include at least these cases before candidate results are observed.

### Positive

- `POS-FRESH-EXACT-UNSEEN`: exact valid Contract D, exact intent, exact target pre-state, exact current AuthorityState/request, unseen idempotency key -> shadow allow.

### Contract E denial / historical-receipt controls

- `NEG-RECEIPT-ONLY-REVOKED-NOW`: historical authorized receipt exists, current AuthorityState is revoked at point of use -> deny.
- `NEG-RECEIPT-ONLY-EXPIRED-NOW`: historical authorized receipt exists, authority is no longer current -> deny.
- `NEG-WRONG-SUBJECT`: exact target/intent but wrong terminal subject -> deny.
- `NEG-WRONG-OPERATION`: authority/request operation mismatch -> deny.
- `NEG-WRONG-TARGET-REF`: request target reference is not the exact shadow intent reference -> deny.
- `NEG-DUPLICATE-TARGET-REFERENCE`: target identity resolves more than once -> deny.
- `NEG-RELEVANT-BLOCKER`: relevant conflict or residue present -> deny.

### Execution-intent substitution controls

- `NEG-DECISION-SUBSTITUTION`: same target but different Contract D bytes/hash -> deny.
- `NEG-EFFECT-SUBSTITUTION`: effect ID/version differs from validated Contract D -> deny.
- `NEG-SCOPE-PARAM-SUBSTITUTION`: effect parameter differs -> deny.
- `NEG-INTENT-ID-FORGERY`: claimed intent identity does not recompute -> deny.

### Target-state / path controls

- `NEG-STALE-PRESTATE`: target bytes differ from intent pre-state before lock/evaluation -> deny.
- `NEG-CONCURRENT-CHANGE-DURING-WINDOW`: target changes after first locked read but before final pre-allow re-read -> deny.
- `NEG-PATH-TRAVERSAL`: relative path escapes disposable root -> deny.
- `NEG-SYMLINK-ESCAPE`: path resolves through a link outside disposable root -> deny.

### Replay / failure controls

- `NEG-REPLAY-IDEMPOTENCY-KEY`: second use of a key already reserved by an allowed intent -> deny.
- `NEG-MALFORMED-AUTHORITY`: malformed or non-canonicalizable AuthorityState -> deny.
- `NEG-MALFORMED-REQUEST`: malformed or non-canonicalizable AuthorizationRequest -> deny.
- `NEG-CONTRACT-E-ENGINE-EXCEPTION`: injected research harness failure in one Contract E engine -> deny.
- `NEG-CONTRACT-E-ENGINE-DISAGREEMENT`: injected research harness disagreement between the two frozen-engine projections -> deny.

No case may be removed or relabeled after observing candidate behavior.

## 8. Weak controls

The evaluator MUST include seeded weak consumers and prove it catches them before the candidate is credited.

At minimum:

1. `W-RECEIPT-AS-PERMIT` — accepts a historical `authorized=true` receipt without fresh point-of-use Contract E evaluation.
2. `W-AUTH-BEFORE-TARGET-CHECK` — evaluates authority before binding/rechecking current target state and does not re-read before allow.
3. `W-NO-PRESTATE-BINDING` — ignores `target_pre_state_sha256`.
4. `W-NO-REPLAY-STATE` — accepts repeated idempotency keys.
5. `W-PATH-TEXT-ONLY` — checks path strings but not resolved path confinement/symlink escape.
6. `W-FAIL-OPEN-ENGINE-ERROR` — converts Contract E exception/unavailability into allow.

A weak control that unexpectedly passes the full adversarial matrix invalidates the evaluator for the claimed property until repaired and requalified before candidate interpretation.

## 9. Measurements

Preserve per case:

- exact input fixture hashes;
- exact Contract D validation result;
- exact intent recomputation result;
- initial and final target hashes;
- path-confinement result;
- lock result;
- sealed-reference Contract E result;
- independent Contract E result;
- idempotency-journal state transition;
- final shadow decision;
- exception/failure class;
- independent verifier result;
- any target-byte change observed.

Preserve all failures and deviations.

## 10. Falsifiers

RC0 is **FALSIFIED** for its bounded claim if any of the following occurs in an accepted run:

- candidate shadow-allows any preregistered negative case;
- candidate uses a historical AuthorizationReceipt as sufficient permission;
- candidate shadow-allows after target pre-state mismatch;
- candidate shadow-allows after a detected concurrent target change;
- candidate accepts replay of a reserved idempotency key;
- candidate allows a path outside the disposable root;
- candidate fail-opens on either Contract E engine error or normative disagreement;
- candidate mutates the disposable target bytes despite `execution_occurred=false`;
- candidate touches live `10_knowledge` or a live MindGraph database;
- evaluator fails to catch one of the seeded weak controls.

RC0 is **INCONCLUSIVE** if apparatus/environment failure prevents the frozen matrix from executing without changing scientific semantics.

RC0 may be **SUPPORTED FOR THE BOUNDED SHADOW CLAIM** only if all candidate cases match the frozen expectations, all weak controls are caught, and the independent no-mutation verifier passes.

## 11. Explicit nonclaims

Even a fully supported RC0 does not establish:

- production-ready Contract E;
- legitimacy/authentication of AuthorityState origin;
- authenticated user/workload identity;
- selection of SPIFFE, PKI, OAuth, macaroons, capabilities, ACLs, or another trust mechanism;
- the production component that owns enforcement;
- a concrete representation for `knowledge.add_verified_tag@1` in Markdown/frontmatter;
- a live MainFrame mutation;
- exactly-once execution;
- crash-safe mutation recovery;
- rollback;
- a signed execution receipt;
- independent verification of an actual effect;
- security against a malicious process with unrestricted same-user filesystem access;
- safe production merge/tag/release/promotion.

## 12. Stop rule

Stop after:

1. frozen implementation and evaluator identities are recorded;
2. weak-control qualification passes;
3. the complete frozen case matrix executes in a disposable root;
4. candidate output and independent no-mutation verification are frozen;
5. failures/deviations are preserved;
6. a terminal scientific disposition is recorded.

Do not proceed from shadow allow to a real file mutation in this RC.

A real write requires a separately preregistered successor experiment and, before production promotion, a separate operator/governance decision on trusted origin, authenticated principal, production owner, concrete effect representation, recovery, and verification.
