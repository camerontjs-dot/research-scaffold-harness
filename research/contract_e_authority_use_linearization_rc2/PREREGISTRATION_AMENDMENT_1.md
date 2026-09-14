# RC2 Preregistration Amendment 1 — Distinct Valid Intent Identity

Status: **FROZEN BEFORE EVALUATOR CONSTRUCTION OR CANDIDATE EXECUTION**

Parent preregistration commit: `2cd26654bb082f94597a4a980eeb8e44c65b3c56`

Initial fixture-semantics commit: `e9c82d1accbcc2bff3aef08a22332cd92014df05`

## Defect found

The parent preregistration includes both:

- retry/concurrency of the **same exact intent**, and
- concurrency of **two distinct valid intents** against the same target version 17.

The initial `ExecutionIntent` semantic fields were entirely determined by Decision, actor, target, operation, version and parameters. Therefore there was only one valid canonical intent for the probe operation, making the distinct-intent case impossible to instantiate without altering operation semantics.

No evaluator has been created and no candidate execution/result has been observed.

## Frozen correction

Add exactly one required non-empty opaque string field to the research-only intent:

`request_nonce`

The nonce:

- participates in `intent_id` recomputation;
- does not change Decision semantics;
- does not confer authority;
- is not interpreted by Contract E except indirectly through the exact immutable intent identity;
- exists only to distinguish independently originated requests for the same semantic transition.

Frozen base fixture uses:

`request_nonce = "probe-request-1"`

The `NEG-CONCURRENT-DISTINCT-INTENTS-SAME-V17` case uses a second otherwise identical valid intent with:

`request_nonce = "probe-request-2"`

The same-intent retry/concurrency cases continue to reuse byte-identical `probe-request-1`.

No case expectation or falsifier is weakened.