# Contract E Production Envelope — Disposable Execution/Recovery RC1 Final Result

Terminal scientific disposition: **SUPPORTED FOR THE BOUNDED DISPOSABLE EXECUTION/RECOVERY CLAIM**

Production authorization: **false**

Merge/tag/release/promotion authorization: **false**

## Frozen lineage

Preregistration:

- commit `997ea4696bf1b5de24c2187eeb72c76bcb1ed5c4`
- blob `e64eabfdfa79f220ff352c21608fa3d1aec7e67e`

Candidate:

- freeze commit `a69c3ac13ec0c0fd7f72fb77c1987c2bc5306588`
- blob `2f7f4678f6f92de1e7ced733d324fa9b234e95fc`
- SHA-256 `bba1adb67fbbefdb71c78993a3436b9818235489a0802fb2995cf08f100eae74`

Independent verifier:

- freeze commit `23732a1adec7a63f7a52f277ff53c5b0914fce95`
- blob `18e59803ba2e316b16564d1fe26d839c71b82ff7`
- SHA-256 `a5ae0c2fd56fec37bead1d750b64879d0422a54acff922ddece777dc08c90078`

Evaluator:

- freeze commit `ad2da092a041750a55e06cdf97657dc9112300e9`
- blob `db6ce20ef9a1f8fe83336d670306de3307524812`
- SHA-256 `5c5eea58d34ee3e55013d2b5b7297b8eb2881503bcb72d54a6c081ae5b212df0`
- frozen cases `23`
- frozen weak controls `6`

Freeze receipt:

- commit `a9cba052bedacea5829ea513afb2742c1d8bab52`

Accepted workflow head:

- `e3a665e2a81d6ed20c8c428a3000594b32fbf7ba`

No candidate, verifier, or evaluator byte changed after freeze.

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

Prior point-of-use evidence:

- Research Scaffold Harness Draft PR #22
- accepted RC0 run `33939307886`
- artifact `9961243481`
- digest `sha256:ea7fb2e4bc499d6c7e083043f2d3cbd754b8acfd59fbfe693b980be2e6762833`
- RC0 result `26/26`, weak controls `6/6`

## Accepted hosted run

- run `33939733370`
- job `101234666188`
- head `e3a665e2a81d6ed20c8c428a3000594b32fbf7ba`
- conclusion `success`

Evidence artifact:

- artifact ID `9961390590`
- name `contract-e-disposable-execution-recovery-rc1-e3a665e2a81d6ed20c8c428a3000594b32fbf7ba`
- size 5,213 bytes
- digest `sha256:5514fb8202b414f089e56d9bb8dfcde4ae31ee829724a17a0f721d09fb802632`

The hosted run verified all frozen Git blob identities and installed exact `rfc8785==0.1.4` before science.

## Scientific result

- case count `23`
- exact case passes `23/23`
- case failures `0`
- weak controls caught `6/6`
- missed weak controls `0`
- scientific state `SUPPORTED_FOR_BOUNDED_DISPOSABLE_EXECUTION_RECOVERY_CLAIM`

## Important observed behaviors

### Normal exact-byte execution

The normal disposable path:

1. required exact released Contract D applicability `candidate_for_authorization`;
2. freshly evaluated both frozen Contract E implementations;
3. durably recorded `PREPARED` with non-conferring receipt evidence;
4. rechecked exact pre-state immediately before replacement;
5. installed exact post bytes using a same-directory fsynced temp file + atomic `os.replace`;
6. observed exact post-state;
7. durably recorded `APPLIED`;
8. was independently reread by a separate verifier process.

The verifier returned `verification_pass=true`, exact post-state, valid journal chain, and explicitly returned:

- `authorization_established=false`;
- `authenticated_actor_established=false`.

Thus post-state verification did not silently become Authorization or actor authentication.

### Retry after completed operation

A retry after durable `APPLIED` and exact post-state:

- performed no additional write;
- performed no fresh authorization solely to observe the already-completed exact state;
- left the target inode and journal bytes unchanged;
- remained independently verifiable.

This is bounded replay avoidance, not a distributed exactly-once guarantee.

### Crash after PREPARED before write

With authority still current on retry:

- first invocation left target at exact pre-state and one durable `PREPARED`;
- retry performed a **fresh current Contract E evaluation**;
- journal sequence became `PREPARED -> PREPARED -> APPLIED`;
- exactly one candidate replacement occurred;
- independent verification passed.

With authority revoked before retry:

- the historical `PREPARED` receipt evidence did not confer permission;
- retry freshly evaluated current authority and was denied;
- target remained exact pre-state;
- journal became `PREPARED -> ABORTED`;
- `authority_conferring=false` remained explicit on recorded receipt evidence.

This directly falsifies the seeded `W-PREPARED-AS-PERMIT` design.

### Crash after replace before APPLIED

The first invocation installed exact post-state but was interrupted before durable `APPLIED`.

On retry:

- the candidate observed exact post-state;
- performed **no rewrite**;
- performed no new mutation authorization because no new mutation occurred;
- appended `RECOVERED_POSTSTATE`;
- set `execution_attribution="unknown"`;
- independent verifier passed exact post-state and preserved attribution as `unknown`.

This result intentionally refuses the stronger claim that the surviving state proves which actor/process performed the interrupted write.

### Crash after APPLIED before verification

After durable `APPLIED`, a separate verifier process could independently establish exact current post-state and journal-chain consistency without another execution.

### Concurrent/stale-state pressure

The candidate correctly refused:

- a changed target before first authorization;
- a third-state target after PREPARED;
- an external target change between fresh authorization/PREPARED and atomic replace.

The authorization-window change case preserved `PREPARED -> ABORTED` and did not overwrite the third-state bytes.

### Verification catches post-execution tamper

After a successful execution, externally changing the target before verification caused the independent verifier to fail with `current_target_not_exact_poststate` even though the executor had previously returned success.

This directly falsifies `W-SELF-VERIFY`.

### Adversarial journal controls

The verifier rejected:

- a tampered journal event whose hash no longer recomputed;
- a hash-consistent-looking forged `APPLIED` journal while the actual target remained pre-state.

The latter is important: journal consistency alone is insufficient; verifier success also requires the real current target to equal exact post-state.

## Weak-control qualification

All six seeded weak designs were caught:

1. `W-PREPARED-AS-PERMIT`
2. `W-REWRITE-POSTSTATE`
3. `W-CLAIM-ATTRIBUTION-ON-RECOVERY`
4. `W-NO-PRESTATE-CAS`
5. `W-APPLIED-BEFORE-STATE`
6. `W-SELF-VERIFY`

Each control was constructed so the unsafe shortcut appeared attractive on its discriminating case; the strong candidate/verifier behavior distinguished it.

## Bounded conclusion

Within this temporary, single-host, exact-byte experiment, evidence supports:

> A point-of-use executor can extend the supported RC0 ordering into a bounded exact state transition with fail-closed current-authority reevaluation before every new mutation, atomic local replacement, replay-aware recovery, durable phase evidence, and independent post-state verification. It can avoid re-execution when exact post-state is already observed, deny a new write when authority was revoked after PREPARED, and preserve unknown execution attribution when post-state survives but APPLIED evidence does not.

The result supports the distinction among:

- current Authorization for a **new mutation**;
- execution evidence from the local executor;
- recovery observation when causation is ambiguous;
- independent verification of current post-state.

## Preserved limitations and inconvenient evidence

- Interruption was injected at named program phases; this is not a real power-loss/fs crash campaign.
- `fsync` + `os.replace` behavior was exercised on the hosted Linux filesystem, not proven across arbitrary production filesystems.
- The journal is hash-chained but unsigned. An attacker able to rewrite the entire journal can recompute the chain.
- `APPLIED` attribution is still a claim from the executor process, not cryptographically authenticated actor provenance.
- A surviving exact post-state after PREPARED but without APPLIED is deliberately treated as causally ambiguous.
- The independent verifier verifies current state/evidence consistency. It does not establish Authorization and explicitly says so.
- The experiment uses exact fixture bytes. It does not define what `knowledge.add_verified_tag@1` should mean in Markdown/frontmatter or another production store.
- The local MainFrame archaeology still found no actual Contract E production consumer.

## Explicit nonclaims

RC1 does **not** establish:

- production `knowledge.add_verified_tag@1` representation or semantics;
- a real MainFrame production consumer;
- trusted/authenticated AuthorityState origin;
- authenticated actor/workload identity;
- global mediation against unrestricted same-user file writers;
- cryptographically signed execution evidence;
- real power-loss durability across arbitrary filesystems;
- distributed locking or distributed exactly-once execution;
- causal attribution after interrupted post-state without APPLIED evidence;
- production rollback policy;
- production ownership/change authority;
- safe production merge/tag/release/promotion.

## Terminal classification

**TERMINAL: SUPPORTED FOR THE BOUNDED DISPOSABLE EXECUTION/RECOVERY CLAIM**

Further progress is a **NEW EXPERIMENT or OPERATOR/GOVERNANCE DECISION**, not an extension of this RC.

The remaining production-profile questions are now concentrated in areas this RC deliberately did not choose: the real consumer/owner, concrete effect representation, authenticated origin/principal/trust root, stronger production threat model, and production operational ownership/change policy.
