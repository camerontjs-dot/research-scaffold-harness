# Contract D Fresh Independent Reproduction RC0 — Preregistration

Status: frozen before independent implementation

This is a fresh contract-reproduction / downstream-consumer conformance experiment. It does **not** authorize Contract D promotion, production Decision Engine changes, production Authorization, or automatic execution.

## Live authority established before implementation

- Apparatus Contracts `main`: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Decision Engine `main`: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- Decision Engine Contract D research PR: #19, branch `research/contract-d-schema-bakeoff-rc0`, observed head `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- RC0 preregistration freeze: `6d6f003cc705264e4f8ecda24602da1da1820bc0`
- RC0 written results commit: `cc27d766d751dbc1d062e0790f2bee5e04276c23`; executed head `c6824ecf6a5cb75b165195a39765582481fe6c95`; hosted run `33289298195`
- RC1 preregistration commit: `785a407e71797e88c89e81fd164302c05785d9d0`
- RC1 hosted-execution commit: `a31ddd73f417edcbcaf9bb46abfdb48e5ddb5793`
- RC2 preregistration commit: `bc1cc749bcea5a12aa66f6ac091cc17a8463991c`
- RC2 hosted-execution / current PR head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- Cross-repository Contract D research registry: `camerontjs-dot/apparatus-contracts` issue #22
- Promoted Decision / Authorization boundary: Decision Engine PR #17, merge `f7c3759dfac7ee4be45879b8266b5eb1440530ee`

The RC0 written report exists. At preregistration time no separate written RC1/RC2 terminal results report was visible on PR #19; green hosted execution is treated only as an execution receipt, not as authorization to infer hidden outputs.

## Independence boundary

### Allowed before freeze

- PR #19 `PREREGISTRATION.md`, `RC1-PREREGISTRATION.md`, `RC2-PREREGISTRATION.md`, and written `RESULTS.md`;
- apparatus-contracts issue #22;
- promoted public Decision / Authorization boundary information;
- public apparatus-contract authority necessary to understand seam ownership.

### Forbidden before freeze

The independent implementer will not inspect:

- `research/contract-d-schema-bakeoff-rc0/run.mjs`;
- `run-rc1.mjs`;
- `run-rc2.mjs`;
- their diffs/patches;
- workflow logs or hosted artifacts that disclose generated reference objects/expected outputs;
- reference validators, decoders, canonicalizers, consumer implementations, or implementation-specific tests.

If contamination occurs, it will be recorded rather than concealed.

## Candidate semantic authority used

RC2 preregisters a representation-independent core:

1. contract version;
2. upstream/input authority `{kind,id}`;
3. Decision policy `{id,version}`;
4. target `{kind,id,immutable content/version identity}`;
5. evaluation state distinguishing completed from failed;
6. disposition only where evaluation established a conclusion;
7. typed/versioned effect with machine-semantic parameters.

Reason/basis/explanation is initially non-normative metadata unless it is explicitly promoted into typed machine-semantic effect state. Serialization nesting is not treated as experimentally established.

## Independent representation prediction

The independent implementation will use a conventional structured envelope because the research artifacts explicitly leave flat versus nested representation underdetermined. Representation is therefore a design choice, not a recovered semantic requirement.

Predictions frozen before reference reveal:

- semantic reproduction should succeed even if exact JSON bytes differ from the reference representation;
- deterministic key-sorted compact UTF-8 JSON with one trailing newline will be used for this implementation, but exact canonical byte rules are predicted to be under-specified by the Contract D research artifacts;
- semantic identity will hash the normative semantic projection, excluding explanatory/audit metadata and any stored convenience `decision_id`;
- strict unknown-field rejection will be used for the declared research contract version, while unknown future effect type/version remains structurally parseable and fails closed at Authorization consumption;
- completed HOLD and evaluation failure will remain distinct;
- Authorization-only actor/profile/context/approval state will be separate inputs and cannot mutate Decision bytes or semantic identity;
- a known effect version may define a safe default for an optional machine parameter; omitted versus explicit default may have different transport bytes but the same semantic identity;
- failed evaluation will carry no disposition and no effect in this independent candidate. This is a prediction, not an established representation requirement.

## Frozen effect registry for the independent experiment

The independent implementation will define three research-only known effect families solely to exercise the semantic obligations:

- `knowledge.tag` v1 -> operation class `knowledge.apply_tag`, machine parameter `tag=audited_verified`;
- `citation.use` v1 -> operation class `citation.use`, optional machine parameter `scope` with safe default `same_target`;
- `task.dispatch` v1 -> operation class `task.dispatch`, machine parameter `dispatch_class`.

These names are independent test vocabulary, not proposed canonical Contract D vocabulary.

## Required independent consumer outcomes

The downstream consumer will distinguish:

- `candidate_for_authorization`;
- `not_applicable`;
- `unknown_effect`;
- `invalid_decision`;
- Authorization `permit`;
- Authorization `deny`;
- Authorization `cannot_establish`.

Contract D itself never returns execution success and never makes actor authorization a Decision property.

## Test families frozen before implementation

- valid knowledge tagging, citation-use, and task-dispatch Decisions;
- completed CLEAR, completed HOLD, evaluation failure;
- upstream/policy/target/content/disposition/effect/version/parameter substitutions;
- Authorization-looking and execution-looking field injection;
- known and unknown effect evolution;
- explanatory metadata invariance;
- strict unknown-field handling;
- cross-operation replay;
- same-id changed-content replay;
- policy-version replay;
- Authorization invariance metamorphics;
- Decision sensitivity metamorphics;
- field-family ablation and semantic-loss classification;
- stored Decision id redundancy/tamper detection.

## Freeze rule

Before any reference implementation or generated reference output is inspected, commit:

- independent implementation;
- tests;
- predictions;
- generated fixtures/canonical outputs;
- file hashes and source-authority list.

That commit will be identified externally as:

`FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`

It will not be amended or rewritten after reveal. Post-reveal comparison evidence may be added only in later commits.