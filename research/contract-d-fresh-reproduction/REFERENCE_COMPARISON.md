# Contract D Fresh Reproduction — Reference Comparison

Status: **post-reference-reveal evidence**

Frozen independent implementation: `43f3acc4e2c8a456e38723ee7031d89e75086529`

Fixed Decision Engine reference head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`

No frozen implementation, test, prediction, fixture, or pre-reveal authority record was modified after reveal.

## Observed semantic agreement

The frozen independent implementation independently recovered these authority-relevant semantics before seeing the reference code:

1. Contract/version identity is required for safe interpretation.
2. Upstream authority kind/id participates in Decision identity.
3. Decision policy id/version participates in Decision identity.
4. Target kind/id plus immutable content identity belongs in the Decision core.
5. Completed policy evaluation and evaluation failure are distinct states.
6. Completed CLEAR and completed HOLD are distinct conclusions.
7. Operation-bearing conclusions require a typed/versioned effect with machine-semantic parameters.
8. Unknown effect type/version must fail closed for an evolution-aware downstream consumer. RC1 explicitly implements this rule.
9. Human-readable explanation/reason material must not acquire downstream Authorization authority.
10. A stored Decision id is not needed to recover the semantic Decision when a canonical identity can be derived.
11. Authorization-only actor/profile/context/approval state is external to Contract D.

This is strong evidence for independent recovery of the **semantic core**.

## Exact reference artifacts revealed

- `run.mjs`, Git blob `43df12ab0a796508b909be79c79ca80c4686b981`
- `run-rc1.mjs`, Git blob `a732ea11c8686e4324604f42b171367d7047ded3`
- `run-rc2.mjs`, Git blob `f4a722c60766e018131798426cb2fba489efc311`
- research workflow, Git blob `4b2975f1bacf2a1e86a113492a126e62c9a9c664`

All were read only after the independent freeze.

## Disagreements and classifications

| ID | Observation | Classification | Authority impact |
| --- | --- | --- | --- |
| D-01 | Reference RC2 uses `D-rc2`, lowercase `clear/hold`, string effect versions, and its own field vocabulary. Frozen consumer chose `0.research-d`, uppercase dispositions, integer effect versions, and a conventional structured envelope. | specification ambiguity + representation-only difference | **Blocks native cross-repository interoperability**, but does not by itself refute the recovered semantic core. |
| D-02 | The public research authority did not publish a normative effect registry/vocabulary. Reference uses `knowledge.add_verified_tag`, `knowledge.cite_as_evidence`, and `task.dispatch`; frozen research vocabulary independently chose `knowledge.tag`, `citation.use`, and `task.dispatch`. | specification ambiguity | **Authority relevant for operation binding.** A consumer cannot safely guess effect identifiers or version semantics. |
| D-03 | Frozen declared-version parser rejects unknown structural fields. Reference RC0/RC1 decoders and RC2 consumer ignore unknown extra fields when reading known semantics. RC1 preregistration explicitly allowed either rule if declared. | specification ambiguity | Fail-closed in frozen implementation; no observed authority leak, but interoperable validation policy is not specified. |
| D-04 | Frozen optional `decision_id`, if supplied, must equal the derived semantic identity. RC2 explicitly demonstrates that an opaque stored `decision_id` is ignored by the consumer. | specification ambiguity / serialization-only rule | No demonstrated Decision-authority disagreement; stored id is redundant in both models. |
| D-05 | Reference canonical helper is recursively key-sorted compact JSON with no trailing newline and hashes the object passed to it. Frozen implementation uses recursively key-sorted compact JSON with one trailing newline and hashes a normative semantic projection for semantic identity. | specification ambiguity + representation-only difference | Exact bytes/hashes cannot conform without a published canonicalization and identity projection. |
| D-06 | RC2 core declares `target.kind`, but its local `consume` request binds only target id + content hash. The frozen consumer binds kind + id + content hash. | reference implementation defect/test gap relative to the declared RC2 core | Potential cross-kind replay is not mechanically excluded by the RC2 local consumer when id/hash collide across namespaces. |
| D-07 | RC2 local consumer checks that upstream authority and policy fields exist, but does not compare them to a separately supplied Authorization policy/profile. Frozen consumer can pin acceptable upstream authority and Decision policy/version. | reference consumer limitation relative to this experiment | A substituted but internally valid upstream authority/policy could remain a candidate in the RC2 local consumer. The field still changes reference Decision identity, so the core binding itself agrees. |
| D-08 | RC1 correctly returns `unknown_effect` for unknown effect type/version. RC2's narrower discriminator consumer has no effect registry and would treat a matching request action as sufficient. | reference harness limitation, not an independent-reproduction defect | RC1 supplies the evolution rule. RC2 cannot serve alone as a complete downstream validator/consumer. |
| D-09 | Frozen consumer separates Authorization `permit`, `deny`, and `cannot_establish`. Reference research consumers stop at `candidate_for_authorization` / `not_candidate` / `unknown_effect` / `invalid_decision`. | scope difference | No contradiction with the seam. Reference research does not implement the separate Authorization policy/profile required by this experiment. |
| D-10 | Reason/explanation placement differs. Reference shapes use reason codes in several locations; frozen representation puts explanation/audit material under metadata. | representation-only difference | Both keep it non-authoritative for downstream Authorization. |

No disagreement was silently repaired.

## Native cross-repository conformance

The exact RC2 `core` specimen from Decision Engine was supplied unchanged to the frozen consumer in `camerontjs-dot/research-scaffold-harness`.

Observed frozen result:

- validation: rejected at `contract_version = D-rc2` because the independently declared serialization version is `0.research-d`;
- downstream result: `invalid_decision / cannot_establish`;
- after **comparison-only** mechanical alignment of contract-version token, disposition casing, and effect-version scalar type, the specimen becomes structurally parseable but still returns `unknown_effect / cannot_establish` because there is no shared published effect registry.

The mechanical alignment is diagnostic only. It is **not** counted as conformance and does not modify the frozen implementation.

Therefore:

`native_cross_repository_conformance = false`

This is preserved as evidence rather than hidden behind a bridge or adapter.

## Reference comparison conclusion

The experiment independently reproduced the semantic core strongly enough to recognize the same Decision/Authorization seam, but the available research authority is not sufficient to make two fresh repositories exchange native Contract D bytes safely.

The main missing shared authorities are:

- one authoritative Contract D serialization/version;
- one canonicalization + semantic identity rule;
- one typed effect registry/version policy, including machine parameter schemas/defaults;
- one validator unknown-field policy;
- explicit downstream applicability requirements for target kind, upstream authority, and policy profile.

The reference RC2 result `SEMANTIC_CORE_SUPPORTED_REPRESENTATION_UNDERDETERMINED` is therefore consistent with this experiment's semantic agreement **and** its native interoperability failure.
