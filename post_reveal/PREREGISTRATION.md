# Contract C Candidate A RC2 Consumer B — Post-Reveal Evaluator Preregistration

**Classification:** Draft Research Evaluation. This record is created only after the independent Consumer B freeze at `ba09743b28e57bc87dd1f315046ef79b93f24021`. It does not authorize merge, release, promotion, Contract C version assignment, Decision policy, Contract E / Authorization, or execution.

## Frozen subject

- aperture start: `07258b47477f8df4151b0ba531809e76a7c5641b`
- candidate implementation commit: `99619c2582a5e632c29a622b878537d10f758698`
- final candidate freeze commit: `ba09743b28e57bc87dd1f315046ef79b93f24021`
- consumer blob: `1f0e64d22f11d7dbe620fef209852870e6b5203d`
- prereveal test blob: `54e03ff388974fb3524b164c17b7af9f7cf9870c`
- freeze receipt blob: `1f57979b23eb37d8611acfb58b288e4952eaa717`

The subject files are immutable for this evaluation. Any subject mutation invalidates the evaluation.

## Question

Can the independently frozen consumer faithfully enforce the frozen public Candidate A RC2 consumer specification on supplied valid handoffs and on post-reveal adversarial/metamorphic cases, while a plausible weaker consumer is discriminated by the same evaluator?

## Acceptance

Support requires all of the following:

1. exact subject blob identities match the frozen receipt;
2. all four supplied authoritative handoffs are accepted and preserve exact public reasons/basis families;
3. the frozen prereveal suite remains green;
4. adversarial cases required by the public spec fail closed when evaluated under the appropriate unchanged external authority;
5. structural semantic attacks are also tested with internally coherent canonical resealing where doing so does not improperly replace out-of-band authority;
6. canonical-permutation/noncanonical-byte attacks are rejected;
7. exact Contract-B/proposition/evidence/producer/policy/resolver bindings are enforced;
8. destination-policy / Authorization injection is rejected;
9. at least one plausible weak consumer control is killed by the evaluator;
10. no evaluator expectation requires the consumer to know hidden producer history or infer semantics absent from the frozen public specification.

## Preregistered adversarial families

The post-reveal evaluator will include, at minimum:

- delete one alternative basis from the authoritative alternative-joint handoff while retaining original external authority;
- flatten the two alternative joint bases into one strict-superset / pseudo-joint basis;
- choose an arbitrary unique winner from independent sufficient supports;
- relabel a `non_polarized` participant as `supports` or `refutes`;
- alias `UNSUPPORTED_SEMANTIC_FAMILY` to `no_deciding_relation`;
- case-fold/substitute `MIXED_RELATIONS` and `UNSUPPORTED_SEMANTIC_FAMILY`;
- stale local `result_set_id`;
- coherent local reseal with stale external whole-object authority;
- wrong exact Contract-B tuple;
- proposition substitution;
- evidence reference absent from exact Contract B;
- wrong semantic implementation, policy, or resolver authority;
- residual participant placed in a basis;
- causal participant omitted from basis-family coverage;
- non-minimal strict-superset basis group;
- duplicate equivalent basis group;
- destination-policy / Authorization field injection;
- canonical semantic permutation that must normalize to canonical order, paired with raw noncanonical bytes that must be rejected;
- failed/incomplete execution laundering into terminal semantic state.

## Weak-control requirement

The evaluator must exercise at least one deliberately weaker, superficially plausible consumer which performs basic parsing, profile/binding/hash checks but omits one or more semantic invariants such as full basis-family preservation, exact reason identity, or policy-field firewall. The evaluator is invalid if it cannot distinguish that weak control from the frozen candidate.

## Falsifiers

Disposition is `FALSIFIED` if any required authoritative positive is rejected, any required semantic distinction is lost, any preregistered fail-closed attack is accepted by the frozen candidate under the specified authority conditions, or the evaluator cannot kill the weak control.

Disposition is `INCONCLUSIVE_EVALUATOR_INVALID` if evaluator plumbing, fixtures, authority construction, or weak-control design is shown to be inconsistent with the frozen public specification.

Only if no falsifier fires may disposition be `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE`.

## Governance deviation preserved

Before this branch existed, an evaluator-plumbing mistake created a one-word placeholder `post_reveal/PREREGISTRATION.md` on `main` at commit `dfe5ce90364398c16ec28fd047b2dc8849525884`. It was immediately removed from `main` by commit `3ed53b13de18e16aa17e71a602218481bad4fc5e`. The placeholder contained no evaluator semantics and occurred after the independent candidate freeze, so it does not contaminate Consumer B. It is preserved here as a process deviation rather than erased from the record.
