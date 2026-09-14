# Contract C 2.0 Promotion Compatibility + Adversarial RC0

Classification: Draft Research / final pre-merge compatibility and fail-closed evidence. Do not merge for production behavior.

## Decision sentence

Record `SUPPORTED_C2_MAJOR_COMPATIBILITY_AND_ADVERSARIAL_GATE` only if, against exact Contract C 2.0 promotion head `b42c827acb0a9fe65353354d709add0e27bab307`:

1. released strict Contract C 1.0 accepts its exact released fixture unchanged;
2. strict C1 rejects each of the four authoritative C2 handoffs;
3. exact production C2 accepts each authoritative C2 handoff and rejects the exact C1 fixture;
4. external expected-profile selection cannot be overridden by artifact contents;
5. the closed C1 grammar rejects attempted injection of the tested C2-only public semantic surfaces (`terminal`, participant `role`, `basis_groups`, `non_polarized` participation), so no silent in-band downgrade is available through C1's existing vocabulary;
6. the exact previously frozen post-reveal evaluator reruns unchanged and Consumer B again rejects all 27 attacks while its weak control is killed;
7. no frozen Consumer B/evaluator/weak-control blob changes.

Any failed compatibility assertion attributable to the exact C2 candidate, any adversarial escape through frozen Consumer B, or any failure of the weak control to demonstrate evaluator discrimination is `FALSIFIED` for the claimed gate. Harness faults are `INCONCLUSIVE_EVALUATOR_INVALID`.

## Exact authorities

### Production subject

- Apparatus Draft PR #98;
- exact locally-qualified head `b42c827acb0a9fe65353354d709add0e27bab307`;
- candidate compatibility version `2.0.0`;
- frozen wire profile `contract-c-successor-candidate-a-rc2-research`;
- local promotion run `34804396671` green on Python 3.11/3.12/3.13;
- exact CAL producer production-profile gate: CAL #109 `SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE`;
- exact frozen Consumer B production-profile gate: RSH #32 `SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE`.

### Released C1 authority

- validator blob `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`;
- canonical registry blob `6e805e274f8b1f491bf0c10735a46962ab91d2d4`;
- exact valid C1 fixture blob `38b2271fc31ffa7683c09a486a8919572fc2f1a4`;
- C1 remains canonical during this pre-merge gate.

### Frozen independent evaluator authority

This branch starts from terminal RSH PR #31 commit `1f3a3a186222be6c14c1442023c5970967fc5868`.

Unchanged required blobs:

- Consumer B `candidate/consumer.py`: `1f0e64d22f11d7dbe620fef209852870e6b5203d`;
- Consumer B prereveal tests: `54e03ff388974fb3524b164c17b7af9f7cf9870c`;
- Consumer B freeze receipt: `1f57979b23eb37d8611acfb58b288e4952eaa717`;
- post-reveal evaluator: `6ba7be4b0820500b5634287f4da0e4433575cf18`;
- weak control: `3112093ddec1449e4a0899899bcf37fda6f6454c`;
- evaluator freeze receipt: `cd59b28e27a49456a8c438e8e9536aa964bb5113`.

The old evaluator must be executed as-is. This gate may read its output but must not patch its attack generator, acceptance rule, weak-control threshold, or frozen subject.

## Compatibility matrix

The compatibility evaluator must establish:

- `C1 -> strict C1 = ACCEPT` for the exact released fixture;
- `C2 -> strict C1 = REJECT` for all four authoritative C2 handoffs;
- `C2 -> exact production C2 = ACCEPT` for all four authoritative C2 handoffs;
- `C1 -> exact production C2 = REJECT`;
- externally selected C1/C2 profile remains authoritative; object contents cannot select another validator;
- public candidate version `2.0.0` remains external to integrity-bearing C2 wire profile during pre-merge qualification.

## Tested no-downgrade boundary

Do not claim universal mathematical impossibility of every future translation.

Test the smaller current-contract claim instead: C1's closed normative grammar cannot preserve the following C2 public surfaces in-band without becoming invalid C1:

1. proposition `terminal.verdict/reason` state;
2. participant `role = causal | residual` separate from relation polarity;
3. canonical family of `basis_groups` rather than a single C1 conclusion basis form;
4. `non_polarized` evidence participation, including `UNSUPPORTED_SEMANTIC_FAMILY` and no-deciding residual evidence.

For each surface, inject a representative C2-only field/value into an otherwise exact valid C1 object, recompute the C1 local identity where possible, and require strict C1 rejection because its schema is closed.

Also preserve earlier Apparatus #86 as historical evidence that a prior in-band successor could be made C1-validator-valid only by deleting/relabeling semantics. This RC0 does not replay those obsolete candidate-specific downgrade functions as if they were RC2 translators.

## Adversarial/evaluator gate

Rerun exact frozen `post_reveal/evaluator.py` unchanged.

Require:

- subject identity clean;
- prereveal regression 38/38 PASS;
- all four authoritative positives accepted;
- attacks total = 27;
- frozen Consumer B rejects 27/27 through `ConsumerError`;
- weak control is killed by the frozen evaluator's preregistered rule;
- weak control accepts at least the original required semantic/canonical attack classes, demonstrating discrimination rather than ceremonial all-red inputs.

The evaluator's preserved governance deviation (one-word placeholder on RSH main, immediately reverted after candidate freeze) remains part of the record.

## Stop boundary

This gate does not modify Contract C, assign canonical C2 discovery, merge/release/tag C2, change Decision Engine, or authorize Contract E/execution.

If supported, the remaining Contract C pre-merge gate is release-artifact/package reproducibility. Only after that may the promotion branch make an atomic canonical-discovery switch and rerun its full local gate.