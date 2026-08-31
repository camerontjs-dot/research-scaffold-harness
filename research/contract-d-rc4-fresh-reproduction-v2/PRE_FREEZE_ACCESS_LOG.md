# Pre-Freeze Access Log

All entries are observable access facts. No hidden reasoning is recorded.

| Seq | Repository / local source | Exact path / surface | Exact ref | Expected identity | Observed identity | Source class | Purpose |
|---:|---|---|---|---|---|---|---|
| 1 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4-successor-v1/CONTEXT_FREE_LAUNCH_PACKET.md` | `32ccd9e732907645eab93e7653ad2d926b3840df` | blob `efc5626aeea61db5d405e87671a5c062a4d7d010` | blob `efc5626aeea61db5d405e87671a5c062a4d7d010` | immutable launch authority | Establish complete task instructions and authorized aperture. |
| 2 | `camerontjs-dot/research-scaffold-harness` | `refs/heads/research/contract-d-rc4-fresh-reproduction-v2` (ref-only surface) | ref itself | commit `548bfa81f65290eda15af658f647497679b840ef` | commit `548bfa81f65290eda15af658f647497679b840ef` | isolation preflight | Verify authorized successor surface remained at clean base without inspecting branch contents/history. |
| 3 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/SPEC.md` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `42a9819651ab41efdb154240eab4f7d808887cd6` | blob `42a9819651ab41efdb154240eab4f7d808887cd6` | public authority | Normative Contract D RC4 semantics. |
| 4 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/schema.json` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `b17183038b75f3ee00804e63c2d9b8d7da476f2e` | blob `b17183038b75f3ee00804e63c2d9b8d7da476f2e` | public authority | Structural schema constraints. |
| 5 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/effect-registry.json` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `53df222ca439248a44029e02a662825235db892f` | blob `53df222ca439248a44029e02a662825235db892f` | public authority | Typed effect/version/parameter/default authority. |
| 6 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` | blob `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58` | public authority | Public valid fixture corpus. |
| 7 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` | blob `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc` | public authority | Public invalid fixture corpus. |
| 8 | `camerontjs-dot/apparatus-contracts` | `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json` | `fd6923115116b0ced0f9feb5c005099d2e51ea88` | blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4` | blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4` | public authority | Public applicability conformance expectations. |

## Aperture statement

No other Contract D candidate, apparatus reference, prior reproduction, Decision Engine producer, PR/issue/workflow/search result, project file, project attachment, conversation summary, or memory source was opened before freeze.

## Tooling note

The access ledger was initialized on the authorized successor branch before opening the first allowlisted candidate file. The available GitHub write surface materialized that initialization as commit `9f51301f1a1d8a78d9b766c4a6257476c132d36f`; this is a tooling artifact, not the independent freeze commit. The final prereveal ledger content is frozen together with the implementation and tests in the later independent freeze commit.
