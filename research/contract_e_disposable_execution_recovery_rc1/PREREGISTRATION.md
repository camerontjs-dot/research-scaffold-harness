# Contract E Production Envelope — Disposable Execution/Recovery RC1 Preregistration

Status: **PREREGISTERED / RESEARCH ONLY / DISPOSABLE STATE ONLY**

Production authorization: **false**

This is a new experiment following the supported bounded shadow result in Research Scaffold Harness Draft PR #22. It does not modify Contract D or Contract E and does not define the production serialization of `knowledge.add_verified_tag@1`.

## 1. Scientific question

> Can a disposable point-of-use executor extend the supported RC0 ordering into one exact byte-for-byte state transition while remaining fail-closed across retry/replay and simulated crash windows, requiring fresh current Contract E authorization before any **new** mutation, preserving ambiguity when a post-state is observed after an interrupted write, and separating execution evidence from independent post-state verification?

The experiment is deliberately narrower than a production executor.

It tests one exact preregistered byte replacement on a temporary file. The replacement bytes are research fixture data and carry no `verified`-tag semantics.

## 2. Prior evidence treated as input, not re-proved

### Contract D 1.0.0

Repository: `camerontjs-dot/apparatus-contracts`

- release commit `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- core blob `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- validator blob `c03ef6c6f059cd03addf5e69b01025bb9a6af8d2`
- applicability consumer blob `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- effect registry blob `a40f4f4447470654bdc16d852f5927189ae30cc5`

The executor MUST require exact released Contract D applicability outcome `candidate_for_authorization` before any new mutation.

### Contract E RC3

- sealed successor commit `a678c73a661853a3a704666fc6bbf29fa378948f`
- public SPEC blob `8c142c6b86dd2512f1df0c19aa36dbef759d6c18`
- sealed successor reference blob `00d4d8f078073388d751546c24678825b89a6402`
- fresh-independent seal commit `9feb44d8c8ea96176f797fe0ef692cc8e4d13656`
- fresh-independent implementation blob `9019abd8ade820988de1f899b2ccef9e57e9a908`

Contract E receipt semantics remain unchanged: a historical receipt is evidence of a past evaluation, not standing permission.

### Production-envelope shadow RC0

Research Scaffold Harness Draft PR #22:

- candidate freeze commit `b9d8e93ac414d37bb3288669526aab9bc28a9f5a`
- candidate blob `bd60ba1da3e1098d4d1a82d6b99bae6255843529`
- evaluator freeze commit `96a5ef58b199fad22bfe46875b6074f6aab36f71`
- evaluator blob `b274b963603612ed3ff2993f76c067fa7c09ec31`
- accepted run `33939307886`
- artifact `9961243481`
- digest `sha256:ea7fb2e4bc499d6c7e083043f2d3cbd754b8acfd59fbfe693b980be2e6762833`
- result `26/26`, six weak controls caught `6/6`
- scientific state `SUPPORTED_FOR_BOUNDED_SHADOW_CLAIM`

RC0 supports point-of-use binding/order only. Its replay reservation does not establish execution recovery or exactly-once behavior and MUST NOT be silently promoted into this experiment as an execution protocol.

## 3. Environment boundary

Every test MUST create its own temporary root outside live MainFrame state.

The candidate MUST refuse a root unless it contains the exact regular-file marker:

`.contract-e-execution-rc1-disposable`

with exact bytes:

`CONTRACT_E_EXECUTION_RC1_DISPOSABLE\n`

The experiment MUST NOT:

- read or write live `10_knowledge` targets;
- mutate live MindGraph databases;
- invoke Conduit or an agent to perform a mutation;
- enable ERS promotion;
- change local hooks/runtime configuration;
- implement a production `verified` tag;
- merge/tag/release/promote any Contract E artifact.

The disposable marker is only an experiment safety condition, not a production trust mechanism.

## 4. Research-only `DisposableExecutionPlan`

The exact plan contains:

- `schema = "cal-disposable-execution-plan-rc1"`;
- `operation_id`;
- `contract_d_sha256`;
- `contract_d_target_kind`;
- `contract_d_target_id`;
- `effect_id = "knowledge.add_verified_tag"`;
- `effect_version = "1"`;
- `effect_params = {"scope":"claim"}`;
- `target_root_id`;
- `target_relative_path`;
- `expected_pre_sha256`;
- `expected_post_sha256`;
- `post_bytes_b64`;
- `authorization_subject_id`;
- `authorization_domain`;
- `authorization_operation`;
- `authorization_scope`;
- `authorization_target_class = "cal.disposable-execution-plan"`.

`operation_id` is `sha256:` + SHA-256 over RFC 8785 JCS + one LF byte for the plan excluding `operation_id`.

The evaluator MUST verify that decoded `post_bytes_b64` hashes exactly to `expected_post_sha256`.

The plan binds exact bytes. It does not claim those bytes are the correct production representation of the Contract D effect.

## 5. Contract E request binding

The AuthorizationRequest MUST contain exactly one validated immutable reference:

- `kind = "cal.disposable-execution-plan"`;
- `version = "rc1"`;
- `immutable_id = operation_id`;
- exact Contract E `identity_sha256`.

`jurisdiction.target_ref` MUST resolve to exactly that one validated reference.

Before every **new mutation attempt**, the executor MUST freshly evaluate current AuthorityState/AuthorizationRequest at point of use.

A prior `authorized=true` receipt or a prior journal `PREPARED` event is insufficient permission for a later new mutation.

## 6. Durable research journal

The candidate uses one append-only JSONL journal inside the disposable root, protected by an exclusive journal lock and fsynced after each event.

Events have at least:

- schema/version;
- operation ID;
- monotonically increasing local sequence number;
- event type;
- exact target hash observed at that phase;
- Contract E receipt ID when applicable;
- `authority_conferring=false` for recorded Contract E receipt evidence;
- previous-event SHA-256;
- event SHA-256.

Allowed event types for RC1:

- `PREPARED` — current Contract D applicability and fresh current Contract E authorization succeeded; target matched exact pre-state; no mutation yet;
- `APPLIED` — this invocation completed the atomic replacement and observed the exact post-state immediately afterward;
- `RECOVERED_POSTSTATE` — a later invocation found exact post-state after an earlier `PREPARED` but no durable `APPLIED`; the current invocation did **not** perform the write and attribution of the intervening write is unknown;
- `ABORTED` — fail-closed terminal observation for a prepared operation that cannot safely continue under the observed state/current authority.

A journal event is evidence generated by this research executor. It is unsigned and does not establish a real-world authenticated actor.

## 7. Candidate execution ordering

For each invocation:

1. validate the plan, exact post bytes/hash, Contract D bytes, exact released Contract D applicability, and Contract D target/effect bindings;
2. resolve the disposable root/marker and target path; reject traversal, symlink escape, missing/nonregular target;
3. acquire the operation journal lock;
4. inspect valid journal history for this exact operation ID;
5. acquire the target lock and re-resolve/re-stat target;
6. read exact current target bytes/hash;
7. if a verified terminal post-state is already present, do not write again;
8. if history contains `PREPARED` but no `APPLIED`/`RECOVERED_POSTSTATE`:
   - if current target == exact post-state: append `RECOVERED_POSTSTATE`, explicitly mark execution attribution `unknown`, and perform no new mutation;
   - if current target == exact pre-state: require a **fresh current Contract E evaluation** before a new mutation may proceed;
   - otherwise append/refuse with `ABORTED` because state is neither exact pre nor exact post;
9. if there is no prior `PREPARED`, require exact pre-state and fresh current Contract E evaluation;
10. before every new mutation, run both frozen Contract E implementations as research instrumentation; disagreement/error is fail-closed;
11. append/fsync `PREPARED` containing the non-conferring authorization evidence;
12. re-read/re-hash target immediately before replacement; mismatch is fail-closed;
13. create same-directory temporary file, write exact post bytes, fsync it, preserve intended file mode, and atomically `os.replace` it;
14. fsync the parent directory where supported;
15. reopen and hash the target; require exact post-state;
16. append/fsync `APPLIED` only after step 15 succeeds;
17. return an execution observation that distinguishes whether this invocation performed the write, observed a recovered post-state, or refused;
18. release locks.

The evaluator may inject a controlled exception immediately after a named durable phase to simulate process interruption. This is failure-injection testing, not proof of power-loss durability.

## 8. Independent verifier

A separate verifier program/process MUST consume only:

- the immutable execution plan;
- the target file;
- the journal.

It MUST NOT call the executor and MUST NOT rely on the executor's returned success boolean.

It verifies:

- plan identity and exact post-byte hash;
- journal parseability and hash-chain consistency;
- operation-ID consistency;
- event-state ordering;
- current target hash;
- whether exact post-state is present;
- whether an `APPLIED` event exists;
- whether only `RECOVERED_POSTSTATE` exists after an interrupted prepared state;
- whether execution attribution is established by the journal or remains unknown.

Its output is a **post-state verification record**, not authorization and not proof of authenticated actor identity.

## 9. Frozen case matrix

At minimum, freeze these cases before candidate observation.

### Normal path

- `POS-NORMAL-APPLY-VERIFY`: fresh authority + exact pre-state -> one atomic write, durable `PREPARED` then `APPLIED`, independent verifier exact post-state PASS.
- `POS-RETRY-AFTER-VERIFIED`: invoke again after normal completion -> no additional target write, no new mutation authorization required solely to observe already-completed exact state; verifier remains PASS.

### Crash/recovery

- `POS-CRASH-AFTER-PREPARED-RETRY-AUTH-CURRENT`: inject interruption after durable `PREPARED` and before write; retry with still-current authority must freshly authorize, execute once, and verify.
- `NEG-CRASH-AFTER-PREPARED-RETRY-AUTH-REVOKED`: same interruption, but current authority revoked before retry -> no write; historical receipt/PREPARED may not confer permission.
- `POS-CRASH-AFTER-REPLACE-BEFORE-APPLIED`: interrupt after atomic post-state is installed but before durable `APPLIED`; retry must not rewrite, must record `RECOVERED_POSTSTATE`, and must preserve `execution_attribution = unknown`.
- `POS-CRASH-AFTER-APPLIED-BEFORE-VERIFY`: interrupt after durable `APPLIED`; independent verifier can verify exact post-state without another write.

### State/concurrency

- `NEG-PRESTATE-CHANGED-BEFORE-FIRST-AUTH`: target not exact pre-state before first authorization -> no write.
- `NEG-PRESTATE-CHANGED-AFTER-PREPARED`: prepared state exists, target changed to neither pre nor post before retry -> no write and ABORT/refusal.
- `NEG-CHANGE-BETWEEN-AUTH-AND-REPLACE`: injected external target change after fresh authorization/PREPARED but before replace -> no candidate replacement over changed bytes.
- `NEG-POSTSTATE-TAMPER-BEFORE-VERIFY`: normal apply then external tamper -> independent verifier FAIL.

### Binding/path/failure

- `NEG-DECISION-DIGEST-SUBSTITUTION`
- `NEG-CONTRACT-D-NOT-CANDIDATE`
- `NEG-PLAN-ID-FORGERY`
- `NEG-TARGET-ID-SUBSTITUTION`
- `NEG-POST-BYTES-HASH-MISMATCH`
- `NEG-PATH-TRAVERSAL`
- `NEG-SYMLINK-ESCAPE`
- `NEG-NONDISPOSABLE-ROOT`
- `NEG-CONTRACT-E-ENGINE-ERROR`
- `NEG-CONTRACT-E-ENGINE-DISAGREEMENT`

### Journal/evidence

- `NEG-JOURNAL-TAMPER`: alter a durable journal event -> independent verifier FAIL.
- `NEG-JOURNAL-FORGED-APPLIED-PRESTATE`: forged/hash-consistent-looking `APPLIED` while target remains pre-state -> verifier FAIL.
- `NEG-AMBIGUOUS-RECOVERY-MUST-NOT-CLAIM-ATTRIBUTION`: post-state is present after PREPARED without APPLIED -> recovery/verifier may verify post-state, but candidate must not claim it proved this executor performed the interrupted write.

No case may be removed or weakened after candidate observation.

## 10. Seeded weak controls

The evaluator MUST demonstrate that it rejects/catches at least these weak designs:

1. `W-PREPARED-AS-PERMIT` — after a PREPARED interruption, retries a new write after authority revocation without fresh authorization.
2. `W-REWRITE-POSTSTATE` — writes again whenever no APPLIED record exists, even when exact post-state is already present.
3. `W-CLAIM-ATTRIBUTION-ON-RECOVERY` — claims the executor performed the write merely because exact post-state is observed after PREPARED.
4. `W-NO-PRESTATE-CAS` — overwrites a third-state concurrent change.
5. `W-APPLIED-BEFORE-STATE` — writes an APPLIED event before the target reaches exact post-state.
6. `W-SELF-VERIFY` — treats executor return status as independent verification without rereading target/journal in a separate verifier process.

A weak control that survives its discriminating case invalidates the evaluator for the claimed property.

## 11. Falsifiers

RC1 is **FALSIFIED** for its bounded claim if an accepted run shows any of:

- a new write proceeds after current authority was revoked following PREPARED;
- an exact post-state is rewritten during recovery/replay;
- a third-state target is overwritten;
- candidate reports `APPLIED` before exact post-state is durably observed;
- candidate or verifier claims known executor attribution in the interrupted post-state-without-APPLIED recovery case;
- journal tamper is accepted by the verifier;
- verifier passes a forged APPLIED record while target remains pre-state;
- verifier passes a tampered post-state;
- Contract D/plan/path/Contract E binding negative is allowed;
- live MainFrame state is touched;
- a seeded weak control is not caught.

RC1 is **INCONCLUSIVE** if apparatus failure prevents the frozen matrix from running without scientific changes.

RC1 may be **SUPPORTED FOR THE BOUNDED DISPOSABLE EXECUTION/RECOVERY CLAIM** only if every frozen case and every weak-control qualification passes.

## 12. Explicit nonclaims

Even full support would not establish:

- production `knowledge.add_verified_tag@1` representation or semantics;
- a real MainFrame production consumer;
- trusted/authenticated AuthorityState origin;
- authenticated workload/principal identity;
- global filesystem mediation against unrestricted same-user writers;
- cryptographically signed execution evidence;
- real power-loss durability across arbitrary filesystems;
- distributed locking;
- exactly-once execution in a distributed system;
- that a recovered post-state was caused by this executor when APPLIED evidence is absent;
- production rollback policy;
- production ownership/change authority;
- production merge/tag/release/promotion.

## 13. Stop rule

Stop after:

1. candidate/verifier/evaluator are frozen;
2. weak controls are qualified;
3. all frozen cases run on disposable roots;
4. all interruption/deviation evidence is preserved;
5. terminal scientific disposition is recorded.

Do not move from disposable exact-byte mutation to live MainFrame mutation in this RC.
