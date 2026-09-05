# Contract E Production Envelope — Authority/Use Linearization RC2 Final Result

Terminal scientific disposition: **SUPPORTED FOR THE BOUNDED AUTHORIZATION/USE LINEARIZATION CLAIM**

Production authorization: **false**

Merge/tag/release/promotion authorization: **false**

## 1. Claim tested

RC2 tested whether, for one reversible non-epistemic single-record mutation in one disposable SQLite store, the following could participate in one explicit serialization order:

- the AuthorityState generation governing the operation;
- exact target version/state;
- exact Decision-derived intent;
- intent result/deduplication state;
- target mutation;
- durable ExecutionRecord.

Decision and AuthorityState origin/authentication were deliberately held fixed as trusted experimental inputs.

The probe operation was research-only:

`envelope_probe.transition@1`

with exact transition:

`fixture-1: version 17 / ready / marker null -> version 18 / marked / marker <intent_id>`

No `knowledge.add_verified_tag@1` semantics were tested or invented.

## 2. Deep Research correction incorporated before execution

The completed CAL Production Authorization Envelope Research Reconnaissance identified that temporal proximity is not sufficient for current-authority safety. A fresh Contract E evaluation can still evaluate a stale AuthorityState.

Inspection of the frozen Contract E RC3 SPEC confirmed that RC3 currentness means valid/unrevoked at the request's `evaluation_time` **within the exact supplied immutable AuthorityState**. `authority_state_id` is content identity, not a latest-generation, causal-freshness, or anti-rollback token.

Inspection of frozen RC1 likewise confirmed that the supplied authority state was evaluated under target/journal locks, but the authority source itself was outside that serialization domain.

RC2 therefore tested the stronger consuming-profile property: **authorization-and-use linearization**, while leaving Contract E itself unchanged and stateless.

## 3. Frozen preregistration lineage

Base preregistration:

- commit `2cd26654bb082f94597a4a980eeb8e44c65b3c56`
- blob `63c494998394626a28a2458dc011cf36cff5afa8`

Pre-result amendments, all frozen before evaluator construction or candidate execution:

1. Distinguish independently originated valid intents from same-intent retries:
   - commit `f2a38348e43a5df79fbab496c74fbc23f7c4abc3`
   - blob `efcb02c1196c386fbd4f5d21cad704ea915424f4`
   - added non-conferring opaque `request_nonce`.
2. Separate standing resource authority from ephemeral intent identity:
   - commit `91fdaf8068b2a8ecc3f6b9ad02e8e4e0c598c3f0`
   - blob `b46977900561102ed5963299fc5916d172e16903`
   - Contract E standing authority targets stable `fixture-1`; exact intent remains PEP-bound and a non-conferring supporting artifact.
3. Separate target-CAS safety from durable retry-result semantics:
   - commit `7978a613a8f73b9187fdf23bb3d8640cbe0b0969`
   - blob `d34ee6b4cc980895a81d40cb4988bc5e0a4fce90`
   - durable intent ledger credited for prior-outcome reconstruction/conflict semantics, not for target CAS already enforcing.
4. Make anti-rollback a PEP-verified store invariant rather than only an installer convention:
   - commit `6741e7011ea112c5d13d733c48702c61054c2d7c`
   - blob `d671c78082b3a388ae9f1787d253a29d10700173`
   - required `authority_current.generation == MAX(authority_history.generation)` for the epoch.

These amendments preserve defects/assumptions discovered during design rather than hiding them after results.

## 4. Frozen scientific surface

Evaluator freeze commit:

- `48f22a50eae49ca241a50739b7e7212617e4e94f`

Freeze receipt:

- `e608bb3d96d04fe74d5112e10ebd05ad2c4e9db7`

Frozen final fixtures:

- path `research/contract_e_authority_use_linearization_rc2/fixtures_rc2_final.py`
- blob `b46fd61e285c6bd9923d638086c593d7aa2a7f6b`
- SHA-256 `d393e64994197160ff48b0be9c6fd12aab7f09f2b70f99b58feb93af890b33be`

Frozen candidate core:

- path `research/contract_e_authority_use_linearization_rc2/candidate_rc2_final.py`
- blob `e3683d0d1f41224b4084c6e3f980eba9ae736276`
- SHA-256 `c3381a1f78e7249f0b38e4eb4299817c0323de159c5e954d06c91f9a9cb119d1`

Frozen anti-rollback wrapper:

- path `research/contract_e_authority_use_linearization_rc2/candidate_rc2_sealed.py`
- blob `ca07a6a9622da596958e55151dfcac9613036484`
- SHA-256 `bb3087d02a6f8757d5ac226b816bd243b8d0425498fab0abe5b873226d2b7c06`

Frozen independent verifier:

- path `research/contract_e_authority_use_linearization_rc2/verifier_rc2_final.py`
- blob `0e1cc0a058258601014bfdacca42ace201602391`
- SHA-256 `1553dafc83664cdb9410eb44f336cd8ca64b65934b4b2dc8ff6ddbc5d0e4ca1d`

Frozen process worker:

- path `research/contract_e_authority_use_linearization_rc2/worker_rc2_final.py`
- blob `709ef81baaf122f73d00820e247654956c935d24`
- SHA-256 `4d0de86317dec999451bbaac7edda92b6afbb9bbf84f26c7beea3bc1bc6b2b20`

Frozen evaluator:

- path `research/contract_e_authority_use_linearization_rc2/evaluate_rc2.py`
- blob `8ac02df2a5970db34367fbd875123b3524abe24c`
- SHA-256 `bf944af58771afe538389a64874a07b8cd52da5892af707ad1d24b3e03dd0ce4`
- cases `20`
- seeded broken controls `6`

Earlier design drafts remain preserved on the branch but are explicitly outside the frozen scientific surface.

No frozen scientific byte changed after the freeze receipt.

## 5. Exact Contract E authorities

Sealed successor:

- commit `a678c73a661853a3a704666fc6bbf29fa378948f`
- public SPEC blob `8c142c6b86dd2512f1df0c19aa36dbef759d6c18`
- successor reference blob `00d4d8f078073388d751546c24678825b89a6402`

Fresh independent implementation:

- final reproduction seal `9feb44d8c8ea96176f797fe0ef692cc8e4d13656`
- implementation blob `9019abd8ade820988de1f899b2ccef9e57e9a908`

Both exact frozen implementations were executed as research instrumentation for authorization. Any disagreement/error was fail-closed.

## 6. Accepted hosted run

Workflow head:

- `8f2f03498ea5765964fba5d4f8813a55685e2346`

Accepted run:

- run `33941257564`
- job `101239016602`
- conclusion `success`

Evidence artifact:

- artifact ID `9961889922`
- name `contract-e-authority-use-linearization-rc2-8f2f03498ea5765964fba5d4f8813a55685e2346`
- size `6,274` bytes
- digest `sha256:85f42894290ad55be944b2363edf5ce25d293bd798fc85d0d3ba3e1f7bb3323e`

All frozen Git blob checks and external Contract E identity checks passed before science. Exact `rfc8785==0.1.4` was installed and checked before execution.

## 7. Scientific result

- frozen cases: `20/20` passed
- case failures: `0`
- seeded broken controls caught: `6/6`
- missed broken controls: `0`
- production authorization: `false`

Scientific state:

**SUPPORTED_FOR_BOUNDED_AUTHORIZATION_USE_LINEARIZATION_CLAIM**

## 8. Decisive authority-ordering observations

### E serializes before A1

`POS-E-SERIALIZES-BEFORE-A1` established:

- execution acquired the SQLite write-serialization domain while A0/generation 0 was current;
- Contract E authorized under exact A0;
- an attempted competing authority write was observed blocked by the store's write lock while E remained inside the execution transaction;
- E committed the target transition, intent ledger, and ExecutionRecord using recorded authority generation `0`;
- only after E committed did A1 install as generation `1`;
- final state contained target version `18`, one ledger row, one ExecutionRecord, and current authority generation `1`.

This gives an explicit ordering: `E < A1`.

### A1 serializes before E

`NEG-A1-SERIALIZES-BEFORE-E` established:

- A1 installed as generation `1` before execution;
- execution selected generation `1` from the store, not caller-provided A0;
- Contract E returned deny under A1;
- target remained version `17 / ready`;
- no ledger row or ExecutionRecord was created.

`NEG-A1-WINS-BEFORE-TRANSACTION` additionally held the same already-constructed Decision/intent across the A0→A1 update. Starting execution only after A1 still selected generation `1` and denied.

This gives an explicit ordering: `A1 < E`.

### Historical A0 cannot override current A1

`NEG-CALLER-SUPPLIED-STALE-A0` supplied a genuine historical A0 `authorized=true` receipt after A1 became current.

The candidate:

- ignored the historical material for current authority selection;
- selected store generation `1`;
- denied under A1;
- performed no transition.

## 9. Known-broken authority TOCTOU control

`W-CHECK-THEN-WRITE-AUTHORITY-TOCTOU` deliberately implemented the architecture RC2 is intended to falsify:

1. evaluate A0 outside the mutation transaction;
2. obtain a real `authorized=true` result;
3. install A1 revocation;
4. perform the mutation using the stale allow.

The weak control **did mutate under current generation 1**.

This is direct evidence that “fresh check shortly before write” is a weaker property than the serialization invariant tested by RC2.

## 10. Target-state/concurrency observations

`NEG-STALE-TARGET-VERSION` refused a target already changed to version 99.

`NEG-TARGET-CHANGE-WITHIN-SERIALIZATION-DOMAIN` showed that while E owned the serialization transaction, a competing target write could not acquire the write domain; E committed version 17→18, and the competitor's subsequent CAS changed zero rows.

`NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17` launched two process-isolated valid intents with different request nonces against the same version 17 target:

- one transition committed;
- one competing intent observed version 18/marked and was refused by target precondition;
- final target version `18`;
- ledger count `1`;
- ExecutionRecord count `1`.

`W-NO-TARGET-CAS` deliberately changed the target to a third state and then unconditionally overwrote it. The unsafe overwrite was exposed and the weak control was caught.

## 11. Same-intent retry and ambiguous response observations

`POS-CONCURRENT-SAME-INTENT` launched two process-isolated copies of the same exact intent:

- one performed the transition;
- one returned the exact prior committed outcome;
- both resolved to the same ExecutionRecord ID;
- one target transition, one ledger row, one ExecutionRecord remained.

`POS-AMBIGUOUS-RESPONSE-LOSS` injected response loss after database commit. Retry of the same exact intent:

- performed no second transition;
- returned the prior committed outcome;
- returned the same ExecutionRecord ID;
- left exactly one ledger row and one ExecutionRecord.

`W-NO-DURABLE-INTENT-RESULT` preserved target CAS but omitted durable intent/result memory. After a committed-looking post-state it could not reconstruct the exact prior intent outcome. This control was caught.

The result therefore credits target CAS for at-most-one target transition in this probe, and the durable intent ledger for exact retry/outcome reconstruction and intent conflict semantics.

## 12. Atomic target + dedupe + ExecutionRecord evidence

`NEG-FAIL-BEFORE-COMMIT` injected a failure after the target UPDATE but before ledger/ExecutionRecord insertion and transaction commit.

SQLite rollback left:

- target version `17 / ready / marker null`;
- ledger count `0`;
- ExecutionRecord count `0`.

The accepted positive path commits target mutation, ledger, and ExecutionRecord in the same transaction.

This is evidence for the bounded single-store atomicity property only.

## 13. Independent verification observations

The verifier is a separate process and does not import or call the executor.

`NEG-FORGED-EXECUTOR-SUCCESS` supplied a forged success assertion without state change. The verifier directly observed:

- target still version `17 / ready`;
- no intent ledger;
- no ExecutionRecord;
- `verification_pass=false`.

It explicitly retained:

- `authorization_established=false`;
- `authenticated_actor_established=false`.

`NEG-TARGET-TAMPER-AFTER-COMMIT` first produced a valid committed transition, then externally changed the authoritative target to version `19 / tampered / marker evil`. The independent verifier rejected with `authoritative_target_disagrees` despite the surviving legitimate ExecutionRecord.

This supports evidentiary independence for the tested direct-state path, not general verifier independence.

## 14. Authority lineage and anti-rollback observations

A0 is generation 0. A1 is generation 1 and names the A0 state digest as parent in the consuming-profile authority lineage.

`NEG-AUTHORITY-FORK-WRONG-PARENT` rejected generation 1 installation with an incorrect parent digest. Current authority remained generation 0 and target remained unchanged.

`NEG-AUTHORITY-ROLLBACK-A1-TO-A0` produced two observations:

1. the supported authority installer rejected a requested generation 1→0 rollback with `generation_not_monotonic_successor`;
2. the harness then directly corrupted `authority_current` back to generation 0 while generation 1 remained in history. The sealed candidate detected `current_generation < MAX(installed_generation)` and failed closed with `authority_store_invalid` before reading/mutating the target.

The known-broken `W-NO-AUTHORITY-ANTI-ROLLBACK` used the same direct pointer rollback against the core candidate without the highest-generation invariant. It selected generation `0`, regained A0 authorization, and **committed the target transition**.

This demonstrates why content integrity and installer correctness alone do not establish current trusted configuration; bounded anti-rollback state is independently material.

## 15. Receipt semantics

`NEG-HISTORICAL-RECEIPT-ONLY` confirmed that a genuine historical A0 allow receipt had zero effect after A1 became current.

`W-RECEIPT-AS-PERMIT` deliberately used that historical receipt as permission after A1 and performed the forbidden transition. The weak control was caught.

RC2 therefore reinforces the existing Contract E invariant that AuthorizationReceipt is evidence, not reusable permission.

## 16. Bounded conclusion

Within this one-host, one-SQLite-store, non-epistemic probe, the evidence supports:

> Current standing authority, exact target pre-state, exact Decision-derived intent, target transition, durable intent-result memory, and durable ExecutionRecord can be placed in one explicit serialization domain while Contract E remains a pure evaluator. Concurrent authority revocation and execution can be forced into an observable order: if E serializes first it may commit under the recorded A0 generation; if A1 serializes first E selects A1 and refuses. A historical receipt or caller-held A0 cannot override the store's current generation. Exact target CAS prevents stale-state overwrite, same-intent retries can reconstruct a prior committed outcome, and a separate direct-state verifier can detect missing or contradictory execution state.

The known-broken check-then-write control demonstrates the corresponding unsafe behavior when authority evaluation is outside that serialization order.

This is evidence for the **authorization/use linearization mechanism**, not for a full production deployment.

## 17. Preserved limitations and inconvenient evidence

- Decision origin/authentication is held fixed as an experimental trust assumption.
- AuthorityState origin/authentication is held fixed as an experimental trust assumption.
- The authority epoch/generation/parent-digest wrapper is a research consuming profile, not Contract E semantics.
- The experiment uses one SQLite write-lock/transaction domain. It does not establish a safe distributed approximation when authority and target live in different services/stores.
- The final stable-resource authority design was a pre-result correction. The earlier idea of binding standing authority directly to one ephemeral intent was rejected because it prevented multiple valid independently originated intents against the same resource without minting standing authority per request.
- Request nonce exists only to distinguish independently originated research intents. It confers no authority.
- Target CAS, not the intent ledger alone, is what prevents a second version-17 transition in this probe. The intent ledger is credited for exact prior-outcome reconstruction and conflict semantics.
- Anti-rollback detects rollback relative to history in the same database. It does not protect against an attacker who can rewrite/destroy the entire database and its history.
- The independent verifier reads the same authoritative database as the executor, but through a separate process and direct query path. It does not prove independence from compromise of that database.
- Contract E evaluation time remains the frozen RC3 timestamp semantic. RC2 does not establish trusted wall-clock sourcing.
- SQLite `BEGIN IMMEDIATE` and transaction behavior were exercised on hosted Linux. Production filesystem/store behavior remains untested.
- No live MainFrame path was touched.

## 18. Explicit nonclaims

RC2 does **not** establish:

- authenticated Decision producer identity;
- authenticated AuthorityState origin;
- production trust-root or PKI requirements;
- remote/multi-host authority freshness;
- Zanzibar/ReBAC architecture or semantics;
- SPIFFE/SPIRE suitability;
- production MainFrame consumer/owner;
- production `knowledge.add_verified_tag@1` representation or semantics;
- general operation-schema safety;
- multi-object atomic execution;
- distributed exactly-once execution;
- partition behavior between separate authority/resource services;
- cryptographic resistance to host/root compromise;
- production rollback/recovery on the eventual actual target store;
- production merge/tag/release/promotion.

## 19. Terminal classification

**TERMINAL: SUPPORTED FOR THE BOUNDED AUTHORIZATION/USE LINEARIZATION CLAIM**

Production profile remains **NOT_READY**.

Further progress requires a **NEW EXPERIMENT and/or OPERATOR/GOVERNANCE DECISION** tied to actual production facts: the real consumer and target store, concrete operation representation, source/principal trust model, bypass-resistance threat boundary, and whether the real topology can supply an equivalent authority/target consistency contract.
