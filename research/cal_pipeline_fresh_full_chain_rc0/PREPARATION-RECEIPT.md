# CAL Fresh Full-Chain RC0 — Hosted Preparation Receipt

**Status:** `READY_FOR_LOCAL_PAIRED_EXECUTION`

**Classification:** Draft Research preparation evidence only.

## Exact preparation authority

Terminal hosted preparation head:

`d4fc62d6f90633dbfbce98dd7c0bc1498cc8905d`

Decisive workflow evidence:

- run: `35348868081`
- job: `105611895739`
- conclusion: `success`
- artifact: `10548936420`
- artifact digest: `sha256:5ac3078a7d8732a88792c85f5adf651da7e488ea86394ad5c0f0f69c965d5773`
- deterministic inner snapshot ZIP: `sha256:527d8192bd75571b1e157b78ebae9c786135707532a65f90ad9cff7f3604b61a`

The artifact includes `PREFLIGHT-SUMMARY.json`, `FULL-CHAIN-PREFLIGHT-SUMMARY.json`, and the complete deterministic preflight snapshot.

## Hosted result

All four prepared packets passed:

- exact Gate V1.0.0 execution;
- exact released Contract A 2.0.0 external validation;
- frozen Evidence Bundler V1 10/3 execution and Contract B 1.2 projection.

The three single-proposition cases additionally passed:

- exact CAL target binding;
- canonical CAL B1.2 execution;
- saved CAL result byte reproduction before C2 materialization;
- exact Contract C2 validation and independently selected resolver authority;
- exact Decision Engine C2 ingress;
- exact released Contract D 1.0.0 canonical validation.

No Authorization or downstream action was executed.

## Single-proposition full-chain observations

### not-needed-single

- Gate: `NOT_NEEDED`
- Contract A handoff: `sha256:a6312bec9812cb9f2eef0df6bec67979b81321504192c23f194d70ed941559f7`
- EB native package: `sha256:9e5910f6801525bff334202e925d1df51f93ee4b01feb4b3a838d7e390d9b2ce`
- Contract B: `sha256:0adcb350465cb193a6b06a9bb9bca526384d889e9486a873cac143fe1feac569`
- CAL result: `sha256:b314fca4d02fc40d5b1c1a15c74c9772236d9ab4619672ec0c1f096fb662674d`
- CAL: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- CAL saved-result byte reproduction before C2: `true`
- C2: `sha256:03e89ae58bc942811a7a23832d8956b6fdb60f4e8f6cdebcb3d970bdca3c9e1e`
- C2 terminal: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- Contract D: `sha256:4b8d295adf3d7e73ad5824c38ba8504bfed3b296b25dc6e7966584b2d022a19a`
- Decision: `completed / hold`
- reason: `contract_c_unsupported_semantic_family_not_supported`

### health-canada-text-representation

- Gate: `NOT_NEEDED`
- Contract A handoff: `sha256:840b910543e68991bfd6af00a517510032908fc36bf87e5dcb5dbe2a0203d2c9`
- EB native package: `sha256:57c9efaac6a1d6fd8d172d16612e49835d0ce5767a4467eaf923707442bffff3`
- Contract B: `sha256:24c80500252448ed853cd261a87dee8df1570551e7e1edf05d5197a36353c9b1`
- CAL result: `sha256:2b7dba8e1e86f2785fa3474cd73f509ea7c416f8765088b68694364928ede497`
- CAL: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- CAL saved-result byte reproduction before C2: `true`
- C2: `sha256:300ee4610b13bf3e9e36db5f555bd752acda0357eb97c6917f20941ebfc88967`
- C2 terminal: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- Contract D: `sha256:f5fb9f3607e4bda801135233c6aae00829e49cec1d253859045f998305072cfc`
- Decision: `completed / hold`
- reason: `contract_c_unsupported_semantic_family_not_supported`

### valve-temporal-status

- Gate: `NOT_NEEDED`
- Contract A handoff: `sha256:9d2e1f3334891efd36266c3c04f2215686ee34ab0d1a0bdd6f7b0a1d19edb8a7`
- EB native package: `sha256:7d8b559441ecef722adf3229af9929895440d0f50b1c779ae2d1d31d1ef06bc9`
- Contract B: `sha256:377381598c2ac9c31edc3178bdea1cf4bbe286eb2e1c3314e3ff6f212310cc5a`
- CAL result: `sha256:2dac6a75bdd617b6a7f7553271ec0aa02095d58197e3389160c9aaf62906975b`
- CAL: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- CAL saved-result byte reproduction before C2: `true`
- C2: `sha256:af1f6512975aeda8d3f1ff816361c6481540d1383ccdc5f9e6850430d880b921`
- C2 terminal: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`
- Contract D: `sha256:8834c08a3e81acc136aeb9ef860d153e1614e1b99c951472d61f0bfb652ec166`
- Decision: `completed / hold`
- reason: `contract_c_unsupported_semantic_family_not_supported`

These outcomes are legitimate fail-closed results for the frozen `semantic_family: unsupported` targets. They are plumbing/conformance evidence, not semantic-accuracy evidence.

## Decomposition boundary probe

`declared-all-of` passed Gate → released Contract A → EB/B:

- Gate: `DECLARED`
- Contract A handoff: `sha256:182c455571f82ddff0083015c7b00b7013b9f205d0785fdc9c93c6a90a7b5348`
- EB native package: `sha256:f5da1fa885a866af5bb61973424d8f7c7a9d38f6fc7a44db461da71266ed79cc`
- Contract B: `sha256:7057954f217a92ab7990f86a84f8397f7dca3c9c2d9539b14da4146c4d385d8e`

Hosted downstream execution was intentionally not performed. Current canonical CAL `run-bundle` consumes one typed Contract B claim at a time, and this preparation does not assume or invent a root-level `all_of` aggregator.

## Preserved apparatus deviations

The preparation lineage preserves five non-scientific failures rather than erasing them:

1. initial workflow YAML orchestration error before case execution;
2. transient frozen-predecessor HTTPS bootstrap reset;
3. GitHub artifact transport rejection of a legitimate Contract B filename containing `::`, corrected by deterministic ZIP packaging;
4. shallow Contract D checkout could not resolve the required annotated release tag;
5. exact Contract D validator dependency `rfc8785==0.1.4` was initially absent from the hosted environment.

The last two failures occurred after CAL byte reproduction and C2 validation had already succeeded. Their successors changed only hosted authority/dependency apparatus, not causal inputs, component pins, semantic targets, policies, or domain outputs.

## Why the next step is local

Hosted preparation has established the exact ordinary pipeline path. The remaining scientific question is **provenance non-interference** under paired control/instrumented execution with reconstruction-required bytes retained in the MainFrame output area.

That requires the local governed artifact store and exact local run directories.

A second local-only observation also remains: the private RC1 overall receipt contains four metadata aliases and one authority alias whose exact rows are not available through public GitHub. They should be reported after the paired run, without modifying the candidate schemas.

## Allowed next disposition

The next local run may reach:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

only if the control and instrumented authoritative/native outputs are identical under the frozen comparison burden and the instrumented run retains the complete provenance package.

## Nonclaims

This preparation does not establish retrieval recall, evidence completeness, CAL semantic accuracy, Decision correctness, production readiness, Authorization, or automatic action.

Immutable Gate V1.0.0 is not modified or reinterpreted. Its post-release Contract A producer-conformance defect remains separately recorded in proposition-authoring issue #52 and Draft PR #50.

No merge, release, promotion, Authorization, or downstream action is authorized by this receipt.
