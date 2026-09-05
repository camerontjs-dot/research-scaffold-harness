# RC2 Preregistration Amendment 3 — CAS Safety vs Dedupe Recovery

Status: **FROZEN BEFORE EVALUATOR CONSTRUCTION OR CANDIDATE EXECUTION**

Parent preregistration: `2cd26654bb082f94597a4a980eeb8e44c65b3c56`

Amendments: `f2a38348e43a5df79fbab496c74fbc23f7c4abc3`, `91fdaf8068b2a8ecc3f6b9ad02e8e4e0c598c3f0`

## Defect found

The original weak control `W-NO-DURABLE-DEDUPE` said removal of durable intent uniqueness MUST demonstrate more than one committed target transition and/or ExecutionRecord.

For the exact RC2 probe, target version/state CAS already makes a second `version 17, ready -> version 18, marked` transition impossible once the first transition commits, even if no intent ledger exists.

Therefore duplicate target mutation is not a valid isolated falsifier for dedupe in this particular probe. Claiming otherwise would confuse two independent mechanisms.

No evaluator has been created and no candidate execution/result has been observed.

## Frozen correction

RC2 distinguishes:

- **target CAS**: prevents applying a transition to a target state other than the exact expected pre-state;
- **intent dedupe/result memory**: lets a retry of the same exact intent resolve a durable prior committed outcome, and lets an intent-ID/digest conflict fail explicitly rather than being misclassified as an ordinary stale-target request.

Replace broken control 3 with:

`W-NO-DURABLE-INTENT-RESULT`

The weak design retains target CAS but omits durable intent/result memory. After an injected response loss following commit, retrying the same exact intent cannot recover the prior committed outcome and instead returns only a stale-target/precondition failure (or otherwise loses exact prior-outcome reconstruction).

The strong candidate must return the original committed outcome with the same ExecutionRecord ID and no second mutation.

The existing concurrent same-intent case still requires exactly one target transition and one durable ExecutionRecord. The evidence attribution is:

- at-most-one target transition: principally supported by serialized target CAS;
- exact same-intent retry reconstruction and ID/digest conflict semantics: supported by the durable intent ledger plus ExecutionRecord.

No scientific case or safety falsifier is removed. This amendment narrows the claimed contribution of dedupe to what the experiment can actually discriminate.