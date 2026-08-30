# Contract D Fresh Independent Reproduction and Cross-Repository Conformance — Terminal Results

## Terminal disposition

`CROSS_REPOSITORY_CONFORMANCE_FAILED`

Secondary finding: the Contract D **semantic core was independently reproduced with representation variance**, but the experiment did not achieve native cross-repository interchange and therefore does not satisfy the requested promotion criteria.

This result does **not** authorize Contract D promotion, production Decision Engine changes, production Authorization, or execution authority.

## 1. Exact repositories and authorities

### `camerontjs-dot/apparatus-contracts`

- live `main` observed before implementation: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Contract D research/registry record: issue #22
- main CI observed green: Actions run `33265643599`

### `camerontjs-dot/decision-engine`

- live `main` observed before implementation: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- promoted Decision / Authorization boundary merge: `f7c3759dfac7ee4be45879b8266b5eb1440530ee`
- Contract D research PR: #19
- fixed PR #19 reference head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- RC0 preregistration: `6d6f003cc705264e4f8ecda24602da1da1820bc0`
- RC0 executed head named in written result: `c6824ecf6a5cb75b165195a39765582481fe6c95`
- RC0 written-results commit: `cc27d766d751dbc1d062e0790f2bee5e04276c23`
- RC0 hosted run: `33289298195`
- RC1 preregistration: `785a407e71797e88c89e81fd164302c05785d9d0`
- RC1 hosted-execution commit: `a31ddd73f417edcbcaf9bb46abfdb48e5ddb5793`
- RC2 preregistration: `bc1cc749bcea5a12aa66f6ac091cc17a8463991c`
- RC2 hosted-execution/current fixed head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- current PR #19 hosted research run observed green: `33316266252`
- current PR #19 repository CI observed green: `33316266272`

Reference implementation files were not opened until after the independent freeze.

### `camerontjs-dot/research-scaffold-harness`

- live `main` used as independent repository base: `548bfa81f65290eda15af658f647497679b840ef`
- research branch: `research/contract-d-fresh-reproduction-rc0`
- independent research PR: #1
- pre-implementation preregistration commit: `3b63269b29488b7ffe45d2933eab0fec0279c5b4`
- frozen implementation commit: `43f3acc4e2c8a456e38723ee7031d89e75086529`
- post-reveal comparison commit: `0a50f01c288634e115091bafa85284672b9f8c43`
- freeze hosted suite run: `33318155700`, success
- post-reveal frozen-suite rerun: `33318332823`, success
- post-reveal conformance comparison: `33318332890`, success as an **execution receipt** for the comparison; the comparison itself records conformance `false`.

## 2. Independence boundary actually observed

Before freeze, the implementation read only the public semantic research authorities: RC0/RC1/RC2 preregistrations, RC0 written results, apparatus-contracts issue #22, promoted seam information, repository/PR metadata, commit metadata, and CI summaries.

Before freeze it did **not** inspect:

- `run.mjs`;
- `run-rc1.mjs`;
- `run-rc2.mjs`;
- their patches/diffs;
- reference validator/decoder/canonicalizer/consumer code;
- workflow logs or generated reference outputs that would expose the algorithm.

The freeze packaging found and corrected a manifest/comment-byte bookkeeping mismatch **before** reference reveal. The branch was still on the preregistration commit while the exact bytes were verified. The final freeze was then created directly from the preregistration parent. No reference code had been opened.

After freeze, reference files were inspected only for comparison. The frozen implementation, frozen tests, frozen predictions, and frozen fixture corpus were not modified.

## 3. Fresh implementation freeze

Label: `FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`

Commit: `43f3acc4e2c8a456e38723ee7031d89e75086529`

Cryptographic record:

- `contract_d.py` SHA-256: `dd6b3bce4d5069bf64c0f71a0f27836915ce210f14a9ea2aacc1f17b7a7a4d80`
- `test_contract_d.py` SHA-256: `f85f7acf6fe29999f042aeeb20aec3ee14226f47f591828ceda246c9c9c3edd1`
- frozen fixture corpus SHA-256: `48d29b0ba59f2978f4e146c6aa91ef3c9bb841938b8b7c818d171e9c92f88fae`

Individual fixture hashes are preserved in `FREEZE_MANIFEST.json`.

## 4. Frozen test matrix and results

Frozen suite: 28 tests, local `OK`, hosted `OK` at run `33318155700`, and unchanged suite re-ran `OK` after reference reveal at run `33318332823`.

Covered and passed:

- three valid effect classes: knowledge audited/verified tagging, citation/evidence use, task dispatch;
- completed CLEAR;
- completed HOLD;
- Decision evaluation failure;
- HOLD distinct from evaluation failure;
- exact target-id replay denial;
- same-id changed-content replay denial;
- policy-version replay denial;
- upstream-authority replay denial;
- cross-operation replay denial;
- known effect/version validation;
- unknown effect type fail-closed;
- unknown effect version fail-closed;
- optional machine parameter with safe default;
- required machine parameter enforcement;
- unknown parameter rejection for a known effect/version;
- Authorization/execution-looking top-level injection rejection;
- the same strings inside explanatory metadata acquiring no authority;
- explanatory reason/explanation/diagnostic invariance;
- strict declared-version unknown structural field handling;
- deterministic canonicalization under object key reordering;
- stored Decision id redundancy/tamper detection;
- producer generation of a hash-bound Decision object.

## 5. Mutation and metamorphic results

### Authorization invariance

For one fixed frozen Decision, changing only:

- actor A -> actor B;
- authorization profile trust/allow-list;
- human approval absent -> present;
- restricted -> permissive context;

changed Authorization outcome across `deny`, `permit`, and `cannot_establish` while the Decision bytes and semantic identity stayed unchanged.

### Decision sensitivity

For fixed Authorization context, independent changes to:

- upstream authority id;
- policy id;
- policy version;
- target id;
- target immutable content hash;
- CLEAR -> HOLD disposition;
- effect type;
- effect version;
- machine-semantic effect parameter;

changed Decision identity when the mutated Decision remained valid. Invalid known-effect parameter substitutions were rejected rather than normalized into authority.

### Explanation versus authority

Changing reason codes, human explanation, or diagnostic metadata changed transport bytes where metadata was present but did not change the semantic Decision identity or Authorization result.

## 6. Field-ablation findings

| Field/family | Finding | Semantic capability lost |
| --- | --- | --- |
| contract version | semantically required | safe interpretation/version selection |
| upstream authority kind | semantically required | authority namespace/type binding |
| upstream authority id | semantically required | exact upstream authority binding |
| policy id | semantically required | exact policy provenance/applicability |
| policy version | semantically required | revision replay protection |
| target kind | semantically required | target namespace/class binding |
| target id | semantically required | logical target binding |
| immutable target content/version identity | semantically required | stale same-id content replay protection |
| evaluation state | semantically required | completed conclusion vs evaluation failure distinction |
| disposition on completed evaluation | semantically required | established policy conclusion |
| effect type | semantically required for operation-bearing conclusion | operation/effect class binding |
| effect version | semantically required | evolution/future-semantics fail-closed behavior |
| required machine-semantic effect parameters | semantically required per effect | complete machine constraint/meaning |
| optional machine parameter with declared safe default | semantic capability required, field presence not always required | deterministic default semantics |
| empty `params` container | required by frozen serialization, not demonstrated as universally semantic | current representation shape only |
| reason/basis codes | explanatory/audit metadata by default | explanation/audit detail only |
| human explanation | explanatory metadata | human-readable explanation only |
| diagnostics | explanatory metadata | diagnostics only |
| stored Decision id | redundant/convenience | no authority capability if semantic identity is derivable |
| Authorization/execution-looking fields | must not become Decision authority | no legitimate Decision semantic capability |

## 7. Reference comparison

Reference reveal files at fixed head `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`:

- `run.mjs`, blob `43df12ab0a796508b909be79c79ca80c4686b981`
- `run-rc1.mjs`, blob `a732ea11c8686e4324604f42b171367d7047ded3`
- `run-rc2.mjs`, blob `f4a722c60766e018131798426cb2fba489efc311`
- workflow, blob `4b2975f1bacf2a1e86a113492a126e62c9a9c664`

Authority-relevant semantic agreement was strong on upstream/policy/target-content identity, evaluation state, HOLD/failure separation, typed/versioned effects, machine parameters, unknown-effect fail-closed behavior from RC1, non-authoritative explanations/reasons, and external Authorization context.

The full disagreement table is preserved in `REFERENCE_COMPARISON.md`.

## 8. Every disagreement

1. **Serialization/version vocabulary differs**: specification ambiguity + representation-only difference, but it blocks native interoperability.
2. **Effect registry/vocabulary differs**: specification ambiguity, authority-relevant for operation binding.
3. **Unknown structural fields**: frozen parser rejects; reference consumers ignore. Specification ambiguity expressly left open by RC1.
4. **Stored Decision id validation**: frozen implementation integrity-checks if present; RC2 ignores opaque stored id. Serialization ambiguity; no demonstrated authority disagreement.
5. **Canonical bytes/identity**: both deterministic but use different byte terminator/projection rules. Specification ambiguity + representation variance.
6. **Target-kind applicability**: frozen consumer checks kind/id/content hash; RC2 local consumer checks request id/content hash only. Reference implementation defect/test gap relative to the RC2 declared core, with potential cross-kind replay.
7. **Upstream/policy applicability against Authorization profile**: frozen consumer pins them; RC2 local consumer checks presence but not separately supplied profile. Reference consumer limitation for this experiment.
8. **Unknown effect/version handling across reference stages**: RC1 fails closed correctly; RC2 narrower discriminator has no registry. Reference-harness limitation; RC1 is required to recover the evolution rule.
9. **Authorization outcome scope**: frozen consumer returns permit/deny/cannot-establish; reference research stops at candidate/not-candidate/unknown/invalid. Scope difference, not a seam contradiction.
10. **Reason/explanation placement**: representation-only difference; both keep it non-authoritative.

No disagreement was repaired after reveal.

## 9. Cross-repository conformance

The exact Decision Engine RC2 `core` specimen was copied post-reveal with provenance and supplied unchanged to the already-frozen consumer in the separate `research-scaffold-harness` repository.

Native outcome:

- frozen validation: rejected because reference declares `contract_version = D-rc2` while the independent serialization declared `0.research-d`;
- downstream outcome: `invalid_decision / cannot_establish`;
- native conformance: `false`.

For diagnosis only, aligning the version token exposed additional representation differences in disposition casing and effect-version scalar type. After those representation-only changes, the object became parseable but the frozen consumer still returned `unknown_effect / cannot_establish` because no shared published effect registry exists.

No bridge/adapter result is counted as conformance.

Therefore the requested chain:

`Decision Engine -> Contract D -> independent consumer -> Authorization evaluation`

was **not** achieved natively from the published research authority.

## 10. Falsifiers tested

- **Immutable target binding unavailable**: not observed in semantic core; content identity is present and frozen replay tests passed.
- **Generic eligibility permits cross-operation replay**: falsified as safe design; negative control failed in the intended direction and frozen consumer denied replay.
- **Unknown effect accidentally treated as authority**: frozen consumer did not; RC1 reference also failed closed. RC2 alone is too narrow to provide this guarantee.
- **Authorization context changes Contract D identity**: not observed; metamorphic invariant passed.
- **Reasons become hidden permission logic**: not observed; reason/explanation changes did not change Authorization.
- **HOLD collapses with evaluation failure**: not observed; states remained distinct.
- **Fresh implementations cannot agree without inspecting implementation**: **partially triggered at wire level**. The semantic core was independently recovered, but native bytes/effect vocabulary did not interoperate.
- **Core contains fields with no demonstrated semantic function**: stored Decision id was classified redundant; reasons explanatory; the remaining core fields had demonstrated semantic functions.
- **Necessary semantics exist only in prose and cannot be validated mechanically**: **partially triggered for shared consumption**. This experiment could implement mechanical rules, but no authoritative apparatus Contract D schema/validator/canonicalizer/effect registry existed for two repositories to share.
- **Authorization requires undocumented Decision Engine knowledge**: native consumer did not require Decision Engine internals, but interoperability requires specification details that are currently unpublished/underdetermined, especially serialization and effect registry.
- **Authorization must reinterpret Contract C epistemic semantics**: not observed; consumer treated upstream authority as an opaque exact identity.

These failures weaken promotion readiness but do not falsify the conceptual Decision/Authorization seam itself.

## 11. Terminal disposition

`CROSS_REPOSITORY_CONFORMANCE_FAILED`

Why this outcome rather than `INDEPENDENT_REPRODUCTION_FAILED`: the semantic core was independently reconstructed before reveal and mostly agreed with the reference research. The decisive failure is native downstream interchange across repositories.

Why this outcome rather than `CONTRACT_D_HYPOTHESIS_FALSIFIED`: the authority seam remained intact in the frozen implementation, and the failures are principally missing shared contract artifacts/representation/effect-registry authority plus reference-consumer coverage gaps.

## 12. Exact promotion recommendation

**No Contract D promotion is justified by this experiment.**

The smallest justified next step is research-only contract hardening in `apparatus-contracts`, not production promotion:

1. publish one authoritative candidate Contract D serialization/version;
2. publish a normative validator and unknown-field rule;
3. publish canonicalization and semantic-identity projection rules;
4. publish the typed effect registry, effect-version evolution rule, parameter schemas, and safe defaults;
5. require exact target kind/id/content binding and define downstream policy/upstream-authority applicability checks;
6. publish frozen native fixtures intended for downstream consumption;
7. rerun a fresh independent reproduction in a repository that did not participate in choosing those rules.

Only after that new experiment achieves native cross-repository conformance with no unresolved authority-relevant disagreement should the smallest Contract D artifact be considered for promotion.

Do **not** promote Authorization machinery as part of Contract D.

## 13. Durable evidence links

- Apparatus Contract D registry: https://github.com/camerontjs-dot/apparatus-contracts/issues/22
- Decision Engine research PR #19: https://github.com/camerontjs-dot/decision-engine/pull/19
- Independent reproduction PR #1: https://github.com/camerontjs-dot/research-scaffold-harness/pull/1
- Freeze commit: https://github.com/camerontjs-dot/research-scaffold-harness/commit/43f3acc4e2c8a456e38723ee7031d89e75086529
- Post-reveal comparison commit: https://github.com/camerontjs-dot/research-scaffold-harness/commit/0a50f01c288634e115091bafa85284672b9f8c43
- Freeze CI: https://github.com/camerontjs-dot/research-scaffold-harness/actions/runs/33318155700
- Post-reveal frozen-suite CI: https://github.com/camerontjs-dot/research-scaffold-harness/actions/runs/33318332823
- Post-reveal comparison CI: https://github.com/camerontjs-dot/research-scaffold-harness/actions/runs/33318332890

RC0, RC1, and RC2 evidence remains preserved. This experiment adds evidence; it does not rewrite the earlier research record.
