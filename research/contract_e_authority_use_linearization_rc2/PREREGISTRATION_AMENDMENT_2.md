# RC2 Preregistration Amendment 2 — Stable Resource Authority vs Exact Intent Binding

Status: **FROZEN BEFORE EVALUATOR CONSTRUCTION OR CANDIDATE EXECUTION**

Parent preregistration: `2cd26654bb082f94597a4a980eeb8e44c65b3c56`

Amendment 1: `f2a38348e43a5df79fbab496c74fbc23f7c4abc3`

## Defect found

The initial fixture/candidate profile set Contract E `jurisdiction.target_ref` equal to the exact ephemeral ExecutionIntent reference.

Contract E RC3 standing authority has one exact `target_ref`. Therefore A0 could authorize only one exact intent identity. The preregistered case `NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17` requires two distinct valid intents to be independently authorized for the same stable target resource and then compete on target version 17.

Minting a new standing AuthorityState for every intent would collapse standing resource authority into a one-intent permit and would test a different architecture.

No evaluator has been created and no candidate execution/result has been observed.

## Frozen correction

For RC2 only, standing Contract E authority targets the **stable probe resource**, not the ephemeral intent.

Define immutable stable target reference:

```json
{
  "kind": "cal.envelope-probe-record",
  "version": "rc2",
  "immutable_id": "fixture-1"
}
```

Its exact Contract E reference identity is used as:

- A0/A1 authority record `target_ref`;
- AuthorizationRequest `jurisdiction.target_ref`.

Each AuthorizationRequest contains exactly two validated references:

1. `ref_id="target"` for the stable probe resource, which is the jurisdiction target and authority target;
2. `ref_id="intent"` for the exact immutable ExecutionIntent.

The exact intent reference is included in `supporting_artifacts` as non-conferring evidence. Contract E therefore authorizes actor + operation + stable resource under standing authority, while the PEP/executor separately validates and binds the exact Decision-derived intent before invoking Contract E.

This does **not** weaken intent binding at the mutation boundary. The candidate must still reject any Decision/intent mismatch before mutation, and the ExecutionRecord must preserve the exact intent ID/digest.

## Consequence

Two different valid intents with different `request_nonce` values can now both be authorized under the same A0 standing authority for `fixture-1` while remaining distinct dedupe identities. Their competition is resolved by target version/state serialization, not by silently making one intent unauthorized due only to its unique request identity.

No frozen case, falsifier, or weak-control expectation is removed or weakened.