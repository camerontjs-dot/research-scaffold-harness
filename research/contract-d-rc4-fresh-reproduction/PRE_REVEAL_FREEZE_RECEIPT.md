# Contract D RC4 Independent Pre-Reveal Freeze Receipt

## Isolation identity

- implementation repository: `camerontjs-dot/research-scaffold-harness`
- branch: `research/contract-d-rc4-fresh-reproduction`
- clean base: `548bfa81f65290eda15af658f647497679b840ef`
- mandatory ref-only preflight: PASS; the authorized successor ref pointed exactly to the clean base before any candidate content was opened
- independent freeze commit: `a34fcccf15b752f0870099d18ee8370aae591b04`
- independent freeze tree: `8a9ba686ac737f096c8ee37b47eb17972f28b93f`
- freeze commit timestamp from Git object: `2026-08-31T00:21:25Z`

## Frozen artifact identities

| Artifact | Blob/tree |
|---|---|
| `contract_d_independent.py` | `5c7ac5a4c821a76d6520412d2dade0cfb0c19021` |
| `test_rc4_independent.py` | `d48b8d26b42979750dc6ca9ab705e6d9ad9fc89c` |
| `weak_consumers.py` | `d380e1f96f91c94ec76aa3cd9d573da418cf0055` |
| `PREDICTIONS.md` | `691332aa05f2198cbeb8e5226446c70a26b5cfa1` |
| `PRE_FREEZE_ACCESS_LOG.md` | `b7dd2b2f7a63e5dfa108529ac3e641c41856ff9b` |
| `RUN.md` | `14dc32299eb594bbd4020fe590cfe86349eb4067` |
| `self_generated_cases.json` | `5b65ef441380e616be96c981a3e2ef25f456b283` |
| `self_generated/cases.json` | `5b65ef441380e616be96c981a3e2ef25f456b283` |
| `self_generated/` case corpus tree | `f22a4d236db6b7bbcb40d033840a60a8a41d3397` |

The root and directory case manifests are byte-identical; the directory copy exists so the frozen self-generated case corpus has an explicit Git tree identity.

## Frozen public authority aperture

All public authority files were opened only at `camerontjs-dot/apparatus-contracts@ca9302243ed99e69c603d82b3c9abd424a5bb38a` and all observed blobs matched the launch packet:

| Path | Observed blob |
|---|---|
| `research/contract-d-independent-authority-rc4/candidate/SPEC.md` | `42a9819651ab41efdb154240eab4f7d808887cd6` |
| `research/contract-d-independent-authority-rc4/candidate/schema.json` | `b17183038b75f3ee00804e63c2d9b8d7da476f2e` |
| `research/contract-d-independent-authority-rc4/candidate/effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` |
| `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json` | `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` |
| `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json` | `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` |
| `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json` | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` |

Immutable launch packet:

- ref: `16182c1c1f8e44116c66eefa30267553a0d59b19`
- path: `research/contract-d-independent-authority-rc4/CONTEXT_FREE_LAUNCH_PACKET.md`
- observed blob: `5996e81486534370fca2f7db81f9c6c70a5cd393`

Allowed durable governance files were not opened because the experiment did not require them; the narrower aperture was retained.

## Denied surfaces

NO PRE-FREEZE DENIED MATERIAL OBSERVED.

Before this freeze, no hidden/reference RC4 implementation/test, prior Contract D material, Decision Engine producer, repository-wide/code search, PR, issue, workflow result, sibling reproduction branch, branch history, or other denied answer-bearing surface was opened.

## Test receipt

Environment: `Python 3.13.5`

Exact command from `research/contract-d-rc4-fresh-reproduction/`:

```text
python3 -m unittest -v test_rc4_independent.py
```

Final prereveal result recorded at `2026-08-31T00:21:39Z`:

```text
Ran 57 tests in 0.006s

OK
exit=0
```

The suite includes public conformance controls, mutation/metamorphic/replay/substitution/invariance/parser tests, all twelve required RC4 discriminators, authority sensitivity, future/unknown behavior, canonicalization/identity distinctions, and every required weak-consumer class.

HOSTED TEST: NOT AVAILABLE ON CLEAN BASE. No hosted-runner surface was authorized or exposed inside the permitted clean-base aperture; repository-wide workflows were deliberately not inspected.

## Prereveal interpretation preserved

The independent implementation normalizes registered zero-parameter effects to include `params: {}`. This was recorded in `PREDICTIONS.md` before reveal and must not be repaired after reference reveal. Any authority-relevant disagreement on this point must be preserved and classified.

## Deviations

- No protocol-authority deviation.
- The self-generated case manifest is duplicated byte-for-byte at the target root and inside `self_generated/` solely to provide an explicit case-corpus tree identity.
- No repository-wide CI/config/workflow modification was made.

## Freeze-before-reveal order

1. Ref-only isolation preflight passed.
2. Access ledger was created.
3. Six allowlisted authority files were opened and blob-verified.
4. Independent implementation, tests, weak consumers, cases, predictions, and run record were created.
5. Final prereveal local suite passed.
6. Independent freeze commit `a34fcccf15b752f0870099d18ee8370aae591b04` existed at `2026-08-31T00:21:25Z`.
7. Final exact prereveal test receipt was recorded at `2026-08-31T00:21:39Z`.
8. This additive receipt is created before any hidden/reference RC4 material or Decision Engine producer is revealed.
