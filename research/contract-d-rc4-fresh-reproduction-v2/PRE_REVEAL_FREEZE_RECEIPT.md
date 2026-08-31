# Contract D RC4 Independent Pre-Reveal Freeze Receipt

Freeze recorded before any denied/reference reveal.

- Clean base: `548bfa81f65290eda15af658f647497679b840ef`
- Authorized branch: `research/contract-d-rc4-fresh-reproduction-v2`
- Ref-only preflight: PASS; the authorized branch initially pointed exactly to the clean base.
- Independent freeze commit: `79e94e7f3795472e31620cdbc4279dc399882ed5`
- Independent freeze tree: `96f7d44fb2a1d82550377322bac7903f029bd91f`
- Freeze-record timestamp: `2026-08-31T00:57:02Z`
- Order: independent implementation/tests/predictions/access ledger were completed and locally tested; freeze commit/tree were created and the authorized branch was advanced to the freeze commit; this receipt was then created; no denied/reference source had been opened at receipt creation.

## Frozen file identities

| Frozen file | Blob |
|---|---|
| `contract_d_independent.py` | `bf4ea3eb9a5cf379d5923198225fed542cc6345e` |
| `test_independent.py` | `19a9a780b5fe90f9e43f6387f5b639edf13dd541` |
| `weak_consumers.py` | `fdbc9374f842c6f3b8c56e4b681217f3b1cd40cf` |
| `generated_cases.json` | `6ae56233f7a2f9ef4c20c39105187c066659f5da` |
| `PREDICTIONS.md` | `6a52e508574127c9dbaf9924519f3b1deeee9b71` |
| `PRE_FREEZE_ACCESS_LOG.md` | `6b8895d59256d1eeff9c2cb57e720669745538a9` |

Self-generated case/fixture identity: the self-generated inventory is the single frozen `generated_cases.json` blob `6ae56233f7a2f9ef4c20c39105187c066659f5da`; additional mutation/metamorphic/cycle/weak-consumer cases are generated directly in the frozen test code. No separate fixture directory/tree was created. The enclosing independent freeze tree is `96f7d44fb2a1d82550377322bac7903f029bd91f`.

## Public authority aperture

All six authorized authority files were opened only at `camerontjs-dot/apparatus-contracts@fd6923115116b0ced0f9feb5c005099d2e51ea88`, and every observed blob matched the packet:

| Path | Observed blob |
|---|---|
| `research/contract-d-independent-authority-rc4/candidate/SPEC.md` | `42a9819651ab41efdb154240eab4f7d808887cd6` |
| `research/contract-d-independent-authority-rc4/candidate/schema.json` | `b17183038b75f3ee00804e63c2d9b8d7da476f2e` |
| `research/contract-d-independent-authority-rc4/candidate/effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` |
| `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json` | `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` |
| `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json` | `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` |
| `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json` | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` |

Launch packet itself was opened at exact ref/path and matched blob `efc5626aeea61db5d405e87671a5c062a4d7d010`. The implementation-repository branch was checked only through its exact ref surface before candidate access.

## Denied surfaces and contamination

`NO PRE-FREEZE DENIED MATERIAL OBSERVED`

No apparatus reference implementation/test, prior Contract D reproduction/result/receipt/packet, Decision Engine producer, repository-wide/code/issue/PR search, workflow/check output, project governance attachment, project-context retrieval, conversation summary, or memory source was opened before freeze.

## Frozen local test

Exact command:

`cd /mnt/data/research-scaffold-harness/research/contract-d-rc4-fresh-reproduction-v2 && python3 -m unittest -v`

Result immediately before freeze construction: all 8 frozen parameterized test methods passed; `Ran 8 tests in 0.004s`; `OK`.

The parameterized methods cover the public conformance/state controls, all seven required requested-operation/parameter discriminators, authority sensitivity and replay/substitution, unknown/future fail-closed behavior, finite-JSON ingress and decoded-host cycle/shared-acyclic behavior, canonicalization/identity invariance, and every required weak-consumer control.

`HOSTED TEST: NOT REQUESTED BY LAUNCH PACKET`

## Pre-reveal ambiguities/deviations

1. `PREDICTIONS.md` records the prereveal finite-number canonical lexical underspecification and the independent implementation's standard-library finite-number serialization choice. Current authority-bearing RC4 fields and registered machine-semantic parameters exercised here are strings, so the ambiguity does not alter the prereveal Decision identity cases.
2. `PREDICTIONS.md` records that the public authority does not expressly specify extra keys in the external expected upstream/policy/target binding objects; the independent API requires those expected objects to contain exactly the specified binding keys and treats malformed external expectations as `cannot_establish`.
3. Unknown/malformed externally requested effect-parameter constraints are treated as nonmatching (`not_applicable`), never as registry-default constraints.
4. Tooling deviation: the available GitHub contents write used to satisfy the required pre-candidate access-ledger creation materialized the initial ledger as commit `9f51301f1a1d8a78d9b766c4a6257476c132d36f` on the authorized branch. It had clean-base parent `548bfa81f65290eda15af658f647497679b840ef`. The final ledger content and all independent evidence were subsequently frozen together in the independent freeze commit above. No denied material was exposed by that write.
5. No separate self-generated fixture directory/tree was necessary; the frozen case inventory plus frozen tests generate the required cases deterministically.
