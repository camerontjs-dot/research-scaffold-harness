# Contract C Candidate A RC2 Consumer B — Post-Reveal Terminal Record

**Disposition:** `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE`

**Classification:** Research evidence record only. This does not merge, release, promote, assign an official Contract C version, authorize Decision policy, create Contract E / Authorization semantics, or authorize execution.

## Frozen subject

- aperture start: `07258b47477f8df4151b0ba531809e76a7c5641b`
- candidate implementation commit: `99619c2582a5e632c29a622b878537d10f758698`
- candidate freeze commit: `ba09743b28e57bc87dd1f315046ef79b93f24021`
- consumer blob: `1f0e64d22f11d7dbe620fef209852870e6b5203d`
- prereveal test blob: `54e03ff388974fb3524b164c17b7af9f7cf9870c`
- candidate freeze-receipt blob: `1f57979b23eb37d8611acfb58b288e4952eaa717`

The evaluator recomputed the Git blob identities of all three frozen subject files and matched them exactly. The candidate freeze receipt also matched the exact aperture/candidate identities, reported `contamination_state = clean`, `forbidden_inputs_read = []`, and `FROZEN_CANDIDATE_READY_FOR_REVEAL`.

## Frozen evaluator

- preregistration commit: `dcf65e0b12a5cb84960f443508612a204192f094`
- preregistration blob: `6806e84169707a8021a0682c28cb6a71c96f4001`
- evaluator implementation commit: `1d841e0b36c90983b11eb122e1755b1548c95b72`
- evaluator blob: `6ba7be4b0820500b5634287f4da0e4433575cf18`
- weak-control blob: `3112093ddec1449e4a0899899bcf37fda6f6454c`
- evaluator freeze-receipt commit: `5d1f8b5d9e6d7103e303a6747969dc45378eacaf`
- workflow launch head: `78d54a13c1668459b253d537310dc66b65e3a3f3`

No evaluator-semantic file or frozen candidate file was changed after evaluator freeze; only workflow launch plumbing was added.

## Decisive execution

- GitHub Actions run: `34803321014`
- job: `103850175410`
- workflow conclusion: `success`
- evaluator step: `success`
- preserved-artifact upload: `success`
- scientific-disposition enforcement: `success`
- artifact ID: `10332011261`
- artifact name: `contract-c-consumer-b-postreveal-evaluation`
- artifact digest: `sha256:b0a761d8baf7b3a893146dd20d38049365bd650b6c8b3c24344f0e4909dfb493`
- extracted `EVALUATION.json` SHA-256: `84255a1df9a29ebf4cd4909b96ea9e11b9bc1a69dac3f64c09695cf7684c5ba2`

## Authoritative positives

All four supplied authoritative RC2 handoffs were accepted and returned with exact public object content preserved:

1. independent supports: `supported / categorical_support`, two singleton alternative bases;
2. alternative-joint mixed: `not_checkable / MIXED_RELATIONS`, two two-member alternative joint bases;
3. no-deciding: `not_checkable / no_deciding_relation`, empty basis family;
4. unsupported family: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`, empty basis family.

The independent prereveal suite was rerun unchanged: **38 executed, 38 passed, 0 failures/errors**.

## Post-reveal adversarial result

The evaluator executed **27** preregistered/required adversarial and metamorphic attacks.

**Frozen Consumer B result:** 27/27 rejected via the declared `ConsumerError` fail-closed path; no attack produced an uncaught crash and no attacked object was accepted.

Observed discriminating failure classes included:

- `WHOLE_OBJECT_MISMATCH` for coherent winner deletion, basis flattening, reason aliasing, and coherent local reseal under stale external authority;
- `INVALID_REASON` for case-folded public reasons;
- `TERMINAL_CAUSAL_INCOHERENCE` for relation laundering;
- `BASIS_COVERAGE_MISMATCH` for uncovered causal participants;
- `RESIDUAL_IN_BASIS`;
- `NON_MINIMAL_BASIS_GROUP`;
- `DUPLICATE_BASIS_GROUP` and `DUPLICATE_BASIS_MEMBER`;
- `UNKNOWN_BASIS_PARTICIPANT`;
- `DUPLICATE_PARTICIPANT`;
- `DUPLICATE_KEY`;
- `NON_CANONICAL_BYTES`;
- `INVALID_RESULT_SET_ID`;
- `CONTRACT_B_MISMATCH`;
- `PROPOSITION_DIGEST_MISMATCH`;
- `UNKNOWN_EVIDENCE_REFERENCE`;
- `PRODUCER_MISMATCH` and `RESOLVER_MISMATCH`;
- `UNKNOWN_FIELD` for Authorization/policy injection;
- `EXECUTION_TERMINAL_LAUNDERING`.

## Evaluator discrimination

The deliberately weaker binding/integrity consumer was not a straw-green control. It still enforced profile, exact Contract-B tuple, producer bindings, proposition bindings, retained evidence references, local result-set identity, and external whole-object digest.

It nevertheless accepted **15/27** attacked inputs because it omitted semantic basis/reason/canonical/firewall invariants. Escapes included:

- Authorization injection;
- case-folded `MIXED_RELATIONS` and `UNSUPPORTED_SEMANTIC_FAMILY`;
- uncovered causal participant;
- duplicate basis member/equivalent group;
- duplicate JSON key;
- duplicate participant;
- failed-execution terminal laundering;
- mixed/non-polarized relation laundering;
- non-polarized-to-support laundering;
- noncanonical raw permutation;
- non-minimal strict-superset basis;
- residual participant in basis;
- unknown basis participant.

Therefore the evaluator itself demonstrated useful discrimination and was not accepted merely because both target and weak control shared hash/binding checks.

## Preserved governance deviation

During post-reveal setup, a one-word placeholder `post_reveal/PREREGISTRATION.md` was accidentally written to `main` at commit `dfe5ce90364398c16ec28fd047b2dc8849525884`. It was immediately removed at `3ed53b13de18e16aa17e71a602218481bad4fc5e`.

This happened after the independent candidate freeze, contained no evaluator semantics, and did not alter the frozen candidate. It is retained as a process deviation rather than hidden.

## Research conclusion

The independent-consumer gate for Candidate A RC2 is satisfied for the frozen public specification and tested aperture:

`CAL-authorized public result state -> Candidate A RC2 handoff -> independent downstream Consumer B`

is now supported by both producer-side conformance evidence and a context-free independent consumer that survived a separately frozen post-reveal evaluator.

This result does **not** itself establish production promotion, an official successor Contract C version, compatibility/SemVer class, Decision Engine production conformance, Contract E / Authorization behavior, or execution authority.

The justified next programme action is an explicit Contract C successor promotion/version decision using the accumulated evidence, followed separately by downstream Decision Engine compatibility/conformance work if promotion is authorized.
