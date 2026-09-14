# Contract E Production Envelope — Authority/Use Linearization RC2 Preregistration

Status: **PREREGISTERED / RESEARCH ONLY / DISPOSABLE TRANSACTIONAL STORE ONLY**

Production authorization: **false**

This is a new bounded experiment informed by:

- Contract E RC3 and its fresh independent reproduction;
- RSH Draft PR #22 (shadow point-of-use binding/order);
- RSH Draft PR #23 (disposable execution/recovery/post-state verification);
- the completed CAL Production Authorization Envelope Research Reconnaissance supplied on 2026-09-04.

It does not modify Contract E, does not create a production authorization service, and does not define the production semantics of `knowledge.add_verified_tag@1`.

## 1. Correction motivating RC2

Contract E RC3 answers whether the **supplied exact AuthorityState** authorizes an exact request at an exact `evaluation_time`.

Its `authority_state_id` is an exact content identity. RC3 does not establish that the supplied AuthorityState is the latest authoritative generation, causally fresh relative to a revocation, or protected against rollback.

RC0 and RC1 freshly re-evaluated supplied AuthorityState and strongly bound target state, but they did not serialize the authority source itself with the mutation.

Therefore the unresolved question is not “can Authorization run immediately before execution?” It is:

> Can CAL establish an authorization-and-use linearization point at which the authority generation that governs the operation, the exact target version, intent deduplication, the target transition, and the durable ExecutionRecord participate in one explicit serialization order?

## 2. Scientific claim under test

> For one reversible, non-epistemic, single-object transition in one disposable transactional store, with Decision and authority origin accepted as trusted experimental inputs, no target transition occurs unless the exact Decision-derived intent is authorized under the AuthorityState generation that is current in the store at the execution transaction's serialization point, the target is still at the exact expected version/state, and the same intent has not already committed a transition; the target mutation, dedupe fact, and ExecutionRecord commit atomically, and an independent verifier can directly observe the resulting authoritative state without treating AuthorizationReceipt or executor return status as permission or proof.

This is a bounded single-host/single-store claim only.

## 3. Research-only probe operation

RC2 deliberately does **not** use `knowledge.add_verified_tag@1` because that operation's name overlaps CAL epistemic semantics and its production persistence semantics are undefined.

The only operation is:

`envelope_probe.transition@1`

with exact semantics:

- target kind: `cal.envelope-probe-record`;
- one record identified by `target_id`;
- required pre-state: `version = 17`, `state = "ready"`, `marker = null`;
- committed post-state: `version = 18`, `state = "marked"`, `marker = <exact intent_id>`.

The transition is reversible in the research fixture by discarding/recreating the disposable database. RC2 defines no production operation or migration.

## 4. Frozen Decision fixture

Define a research-only deterministic Decision object:

```json
{
  "schema": "cal-envelope-probe-decision-rc2",
  "decision_id": "<recomputed sha256 identity>",
  "target": {
    "kind": "cal.envelope-probe-record",
    "id": "fixture-1",
    "expected_version": 17
  },
  "effect": {
    "type": "envelope_probe.transition",
    "version": "1",
    "params": {
      "from_state": "ready",
      "to_state": "marked"
    }
  }
}
```

`decision_id` is `sha256:` + SHA-256 over RFC 8785 JCS + LF of the object excluding `decision_id`.

The Decision is held fixed as a trusted experimental input. Its content hash proves exact bytes only, not authenticated producer origin.

## 5. Research-only ExecutionIntent

The exact intent contains:

- `schema = "cal-envelope-probe-intent-rc2"`;
- `intent_id`;
- `decision_id`;
- `decision_sha256`;
- `actor = "agent:probe-executor"`;
- `operation = "envelope_probe.transition"`;
- `operation_version = "1"`;
- `target_kind = "cal.envelope-probe-record"`;
- `target_id = "fixture-1"`;
- `expected_target_version = 17`;
- `params = {"from_state":"ready","to_state":"marked"}`.

`intent_id` is `sha256:` + SHA-256 over RFC 8785 JCS + LF excluding `intent_id`.

The Decision does **not** freeze a particular AuthorityState generation. The PEP/executor reads the store's current authority generation at use.

## 6. Authority lineage profile outside Contract E

RC2 adds a consuming-profile wrapper around immutable Contract E AuthorityStates. This wrapper is **not** a Contract E change.

The disposable store holds exactly one authority epoch and one current generation pointer.

Metadata for each installed authority generation contains:

- `authority_epoch = "probe-authority-epoch-1"`;
- integer `generation >= 0`;
- `authority_state_id`;
- `authority_state_sha256`;
- `parent_authority_state_sha256` (`null` only for generation 0);
- exact canonical AuthorityState JSON bytes.

Frozen fixtures:

- **A0 / generation 0**: actor `agent:probe-executor` is authorized for `envelope_probe.transition`, scope `record`, target class `cal.envelope-probe-record`, exact probe-intent target reference; unrevoked and current at evaluation time.
- **A1 / generation 1**: successor of A0 in the consuming-profile lineage and semantically revoked/denying for the same actor/operation at the frozen Contract E evaluation time.

The authority installer is part of the experiment store and MUST:

- serialize updates with execution transactions using the same SQLite write-lock domain;
- require `new_generation == current_generation + 1`;
- require `parent_authority_state_sha256 == current authority_state_sha256`;
- reject attempts to install an older/equal generation;
- reject a fork with the wrong parent.

This is bounded anti-rollback/lineage machinery for the experiment. It is not authenticated remote provenance.

## 7. Contract E request semantics

The execution transaction constructs an exact Contract E AuthorizationRequest from:

- the current store-selected AuthorityState generation;
- exact actor/operation/scope/target class;
- exactly one immutable reference to the exact ExecutionIntent;
- frozen deterministic `evaluation_time` for the case.

The candidate MUST evaluate both the frozen sealed Contract E successor and the frozen fresh-independent implementation as research instrumentation. Any normative disagreement or error is fail-closed.

A historical AuthorizationReceipt may be supplied as inert evidence in negative tests but MUST NOT influence eligibility.

## 8. Serialization mechanism under test

Use one disposable SQLite database per case.

The authority metadata/current pointer, target record, intent dedupe row, and ExecutionRecord all reside in that database.

Execution begins with `BEGIN IMMEDIATE` (or an equivalent write-serializing transaction established by the candidate before reading authority/target state).

Within the same transaction the candidate MUST:

1. validate Decision and ExecutionIntent identities/bindings;
2. inspect the intent ledger:
   - same `intent_id` + identical intent digest + committed prior outcome -> return prior outcome with no new mutation;
   - same `intent_id` + different intent digest -> hard integrity failure;
3. read the **current authority generation and exact AuthorityState bytes from the store**;
4. validate generation metadata/lineage relation to the store's current pointer;
5. read current target version/state;
6. require exact expected target version and `from_state`;
7. construct and freshly evaluate Contract E using that store-selected AuthorityState;
8. require exact allow from both frozen Contract E engines;
9. at an injectable barrier, remain inside the same serialization transaction;
10. conditionally update target only where exact `target_id`, version 17, state `ready`, marker null still match;
11. require exactly one row changed;
12. insert the intent dedupe fact with unique `intent_id` and exact intent digest;
13. insert a durable ExecutionRecord containing at least:
    - `intent_id`;
    - exact intent digest;
    - Decision ID/digest;
    - authority epoch;
    - authority generation used;
    - AuthorityState ID/digest used;
    - target ID;
    - target before version/state;
    - target after version/state;
    - committed outcome;
14. commit target mutation + dedupe + ExecutionRecord atomically.

An authority update transaction must use the same write-serialization domain. Therefore a concurrent execution E and authority update A1 must have one observable order:

- `E < A1`: E may commit using A0, then A1 installs; or
- `A1 < E`: A1 installs first and E must read/evaluate A1 and refuse.

“E checked A0 shortly before A1” is not an accepted consistency claim.

## 9. Independent verifier

A separate verifier process MUST consume only:

- correlation information (`intent_id`, target ID);
- the authoritative disposable SQLite database.

It MUST NOT import/call the executor or use executor return status as proof.

It directly verifies:

- current target row;
- target version/state/marker;
- intent-ledger row;
- ExecutionRecord row;
- agreement among target marker, intent ID, target before/after versions, Decision digest, and recorded authority generation;
- that a successful ExecutionRecord and target transition either both exist or neither exists under the experiment's atomicity claim.

The verifier does not establish Authorization source legitimacy or authenticated actor identity.

## 10. Frozen adversarial case matrix

### Positive / ordering

1. `POS-A0-T0-COMMIT` — A0 current + T0 version 17 + exact intent -> one commit to T1 version 18, dedupe + ExecutionRecord atomic, verifier PASS.
2. `POS-E-SERIALIZES-BEFORE-A1` — E begins write-serializing transaction under A0 and pauses after Contract E allow; A1 installer starts concurrently and must not become current until E commits; E commits under recorded generation 0, then A1 becomes generation 1.
3. `NEG-A1-SERIALIZES-BEFORE-E` — install A1 first, then execute exact intent -> store-selected A1 denies, no target transition.
4. `NEG-A1-WINS-BEFORE-TRANSACTION` — construct/hold the same Decision+intent while A0 is current, install A1 before execution transaction starts, then execute -> no stale A0 reuse; deny.
5. `NEG-CALLER-SUPPLIED-STALE-A0` — current store generation is A1 but caller supplies historical A0/receipt material as optional evidence -> candidate ignores it for current authority selection and denies.

### Target state / CAS

6. `NEG-STALE-TARGET-VERSION` — target externally advanced/changed before execution -> no mutation.
7. `NEG-TARGET-CHANGE-WITHIN-SERIALIZATION-DOMAIN` — competing target update serializes before E -> E observes new version/state and denies; if E owns serialization first, competitor waits until E commits. No lost update.
8. `NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17` — two distinct valid intents expect version 17; at most one target transition commits, the other fails/rejects on version/state.

### Replay / ambiguity

9. `POS-RETRY-SAME-INTENT-AFTER-COMMIT` — same exact `intent_id`/digest returns prior committed outcome with no second target transition and no second ExecutionRecord.
10. `NEG-SAME-INTENT-ID-DIFFERENT-BYTES` — same ID with altered canonical intent bytes/digest -> hard integrity failure.
11. `POS-CONCURRENT-SAME-INTENT` — two workers race same exact intent; exactly one transition/ExecutionRecord, other resolves prior committed result.
12. `POS-AMBIGUOUS-RESPONSE-LOSS` — inject failure after database commit but before response; retry same intent reconstructs prior committed result, no duplicate transition.

### Atomicity / verification

13. `NEG-FAIL-BEFORE-COMMIT` — inject exception after target UPDATE but before transaction commit -> rollback leaves target, dedupe, ExecutionRecord all absent/unchanged.
14. `NEG-FORGED-EXECUTOR-SUCCESS` — executor success assertion without database transition/ExecutionRecord -> independent verifier FAIL.
15. `NEG-TARGET-TAMPER-AFTER-COMMIT` — alter authoritative target after legitimate commit -> verifier reports disagreement/failure.

### Binding / receipt

16. `NEG-DECISION-SUBSTITUTION` — Decision digest/ID mismatch -> no mutation.
17. `NEG-INTENT-SUBSTITUTION` — operation/target/version/params mutation relative to Decision -> no mutation.
18. `NEG-HISTORICAL-RECEIPT-ONLY` — genuine prior allow receipt supplied while current A1 denies -> receipt has zero effect; no mutation.

### Authority lineage / anti-rollback

19. `NEG-AUTHORITY-ROLLBACK-A1-TO-A0` — after A1 current, attempt to install generation 0/A0 -> installer rejects; current remains A1.
20. `NEG-AUTHORITY-FORK-WRONG-PARENT` — attempt successor with wrong parent digest/generation -> installer rejects; current unchanged.

No case may be removed, weakened, or relabelled after candidate observation.

## 11. Seeded known-broken controls

The evaluator MUST prove sensitivity to at least these broken designs:

1. `W-CHECK-THEN-WRITE-AUTHORITY-TOCTOU` — read/evaluate A0 outside the mutation transaction; pause; install A1; resume and mutate using stale allow. The frozen interleaving MUST expose the unauthorized transition.
2. `W-NO-TARGET-CAS` — authorize valid intent, change target to another version/state, then unconditionally write anyway. The stale-target case MUST expose overwrite/lost-update behavior.
3. `W-NO-DURABLE-DEDUPE` — run duplicate/concurrent same intent without unique durable intent ledger. The control MUST demonstrate more than one committed version transition and/or ExecutionRecord.
4. `W-RECEIPT-AS-PERMIT` — after A1 denial, execute based solely on historical `authorized=true` receipt. The control MUST false-allow.
5. `W-EXECUTOR-SELF-VERIFY` — claim verification from executor return status while authoritative database contradicts it. Independent verifier MUST catch it.
6. `W-NO-AUTHORITY-ANTI-ROLLBACK` — install previously valid A0 after A1 and regain permission. The rollback case MUST expose it.

A broken control that survives its discriminating case invalidates the evaluator for the corresponding claimed property.

## 12. Falsifiers

RC2 is **FALSIFIED** for its bounded claim if an accepted run shows any of:

- A1 serializes before E but E commits using A0;
- E claims current-authority safety without recording the exact store-selected authority generation;
- a caller-provided/historical AuthorityState overrides the store's current generation;
- stale target version/state is overwritten;
- more than one qualifying target transition commits for one `intent_id`;
- the same intent ID with different bytes is treated as the original request;
- target transition commits without its dedupe row and ExecutionRecord, or successful ExecutionRecord commits without the target transition;
- a historical AuthorizationReceipt changes execution eligibility;
- independent verifier accepts executor assertion when authoritative database contradicts it;
- authority rollback/fork is accepted by the bounded store profile;
- any seeded broken control is not caught.

RC2 is **INCONCLUSIVE** if apparatus failure prevents the frozen matrix from determining authoritative database state without changing scientific semantics.

RC2 may be **SUPPORTED FOR THE BOUNDED AUTHORIZATION/USE LINEARIZATION CLAIM** only if all 20 frozen cases and all six broken controls behave as preregistered.

## 13. Explicit nonclaims

Even a pass does not establish:

- authenticated Decision producer identity;
- authenticated remote AuthorityState origin;
- a production trust root or PKI requirement;
- secure multi-host authority propagation;
- Zanzibar/ReBAC semantics;
- SPIFFE/SPIRE suitability;
- production MainFrame consumer ownership;
- production `knowledge.add_verified_tag@1` semantics;
- arbitrary operation-schema safety;
- multi-object transactions;
- distributed exactly-once execution;
- partition behaviour across authority/resource services;
- wall-clock correctness beyond frozen Contract E case semantics;
- cryptographic protection against host/root compromise;
- production rollback/recovery on the eventual actual store;
- production merge/tag/release/promotion.

## 14. Stop rule

Stop after:

1. Decision/intent/A0/A1 fixtures and authority-lineage profile are frozen;
2. candidate, independent verifier, and evaluator are frozen;
3. all 20 cases and six broken controls execute in disposable databases;
4. every forced interleaving/failure is preserved;
5. terminal disposition is recorded.

Do not proceed to live MainFrame mutation or production trust/identity machinery in RC2.
