# Contract D RC3 fresh independent reproduction — pre-reveal freeze receipt

## Isolation

- Repository: `camerontjs-dot/research-scaffold-harness`
- Starting base commit: `548bfa81f65290eda15af658f647497679b840ef`
- Starting base tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- Branch: `research/contract-d-rc3-fresh-reproduction`
- Exact branch-existence search before creation returned no branch with this name.
- Implementation freeze commit: `7e64784761dc52f881d5c8ab522e8dea9348b841`
- Implementation freeze tree: `d4202a8c1df675d0d85c1c4ee650d6ba9f593336`
- Freeze commit timestamp: `2026-08-30T17:31:49Z`

## Frozen implementation/test/prediction identities

- `research/contract-d-rc3-fresh-reproduction/contract_d_rc3.py` — blob `7132e96c635c841daff375faafb05b5fe3bbedca`
- `research/contract-d-rc3-fresh-reproduction/test_contract_d_rc3.py` — blob `8d60de4c69e8b3a94eb3c817e2660d2f8affa07d`
- `research/contract-d-rc3-fresh-reproduction/fixtures/self_generated.json` — blob `e6bf0591a7aa9625d383265b8f69a4314a3961f0`
- `research/contract-d-rc3-fresh-reproduction/fixtures/metamorphic_cases.json` — blob `c377a37dfdb0e5e86d915d2d7e6773a3ebb87265`
- Combined self-generated fixture/case tree: `f93644b5f634e7fccc934039a056a8ab4bfa4318`
- `research/contract-d-rc3-fresh-reproduction/PREDICTIONS.md` — blob `ad34757614b13be895533cb870b7fcaeb2ed7575`

## Pre-freeze Contract D authority actually opened

All reads below were path-and-ref constrained to `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`:

1. `research/contract-d-independent-authority-rc3/candidate/SPEC.md` — blob `a91a9f171a3b5f3241b5970d7c0415e00f0477d7`
2. `research/contract-d-independent-authority-rc3/candidate/schema.json` — blob `41481aa7941a789534c974ed7b368fddead6ce5a`
3. `research/contract-d-independent-authority-rc3/candidate/effect-registry.json` — blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc3/candidate/fixtures/valid.json` — blob `f823936c9945ea551943c40bee1e956faf1d834d`
5. `research/contract-d-independent-authority-rc3/candidate/fixtures/invalid.json` — blob `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6`
6. `research/contract-d-independent-authority-rc3/candidate/conformance-cases.json` — blob `229f2898f756f9ca078086cfc99d2a6a2edd2a73`

No other `apparatus-contracts` path was opened pre-freeze.

## Durable governance files

The packet listed five durable governance filenames but did not supply a repository/ref locator for them. A single conservative exact-path lookup for `CONTEXT-FREE-EXECUTION-PROTOCOL(1).md` at the supplied research-scaffold-harness base returned 404. No repository-wide search was used to compensate, and no governance file content was imported. Execution continued under the narrower packet-defined aperture because those files were not necessary to preserve the stated isolation, freeze, or contamination rules.

## Administrative pre-freeze reads / deviations

- An exact branch-name search was used solely to establish that `research/contract-d-rc3-fresh-reproduction` did not already exist.
- A metadata read of supplied base commit `548bfa81f65290eda15af658f647497679b840ef` exposed its unrelated MLX test diff. This was outside the Contract D answer-bearing surfaces and did not contain prior Contract D reproduction material. It is recorded as a non-answer-bearing aperture deviation, not hidden.
- A Git commit-object metadata read of the same supplied base was used to obtain base tree `191976638bbf8b7153e3f2c94945a2f15cd640ad` for an exact tree-based freeze commit.

## Test receipt before freeze

Local command executed against the exact bytes later frozen:

`cd /tmp/contract-d-rc3-fresh && python -m unittest -v`

Result: `Ran 66 tests in 0.022s` / `OK`.

Coverage includes the required positive/state controls; authority-sensitive mutations; metadata and Authorization-only invariance; replay/substitution; future/unknown fail-closed behavior; Authorization/execution-looking injections; canonicalization and duplicate-key handling; safe-default normalization; and the nine intentionally weak consumer controls listed in the task packet.

Hosted test: not executed before freeze. No PR or branch-wide workflow enumeration was introduced pre-freeze.

## Contamination statement

Before implementation freeze commit `7e64784761dc52f881d5c8ab522e8dea9348b841`, none of the packet's pre-freeze-denied Contract D reference implementation files, RC3 preregistration/freeze/results files, apparatus PR/issue narrative, Decision Engine Contract D implementations/results/logs, prior independent reproduction material, prior reproduction PR, or surrounding Contract D conversation/history were opened or used.

No pre-freeze-denied material was exposed. Independence claim remains live at this freeze point.

## Order marker

- Freeze commit created: `2026-08-30T17:31:49Z`.
- This receipt was prepared after that freeze and before any permitted post-freeze reference/producer reveal.
- Local receipt preparation clock immediately before writing this receipt: `2026-08-30T17:32:25Z`.
- At this point, post-freeze reveal has not yet occurred.

The frozen implementation/tests/fixtures/predictions must not be modified in response to subsequent reference behavior.
