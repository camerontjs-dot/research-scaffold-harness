# Contract D RC3 Independent Freeze Receipt

Status: PRE-REVEAL RECEIPT. The independent object named below was frozen before any Phase A/B denied answer-bearing source was opened.

## Isolation identity

- repository: `camerontjs-dot/research-scaffold-harness`
- branch: `research/contract-d-rc3-fresh-reproduction-2`
- clean starting base: `548bfa81f65290eda15af658f647497679b840ef`
- initial ref-only observed target: `548bfa81f65290eda15af658f647497679b840ef`
- initial isolation gate: PASS

## Independent freeze identity

- implementation freeze commit: `af15722cc52372e79abb097c587efec5eab5ff13`
- freeze root tree: `4d38222cbd0b2024ca93477a387e97b6d2969095`
- freeze commit timestamp: `2026-08-30T23:11:20Z`
- freeze commit parent: `cf759f9c6cb792cec91caf188da06b6cd0b31367`

### Frozen implementation / evaluator identities

- `research/contract-d-rc3-fresh-reproduction-2/contract_d.py` blob: `ce7ba21008c7c557229a028634e614a4c8f3379e`
- `research/contract-d-rc3-fresh-reproduction-2/test_contract_d.py` blob: `527a6968d5aec6865f54b7c3bd0b9f0ba470f984`
- `research/contract-d-rc3-fresh-reproduction-2/weak_consumers.py` blob: `7d854ecc31c558fdabdc7565865dc995f2525100`
- `research/contract-d-rc3-fresh-reproduction-2/self_generated_cases.json` blob: `e558ea0352514892ce02b68ed459357dc696fec4`
- `research/contract-d-rc3-fresh-reproduction-2/PREDICTIONS.md` blob: `dc0df712558c40b4b19deee015f0deca6c51da5c`
- `research/contract-d-rc3-fresh-reproduction-2/PRE_FREEZE_ACCESS_LOG.md` blob: `64a25daa6406faec31265e8bfef8c96aac5f15ae`

Self-generated fixture/case identity: the independent mutation/metamorphic corpus is the single frozen `self_generated_cases.json` blob `e558ea0352514892ce02b68ed459357dc696fec4`; no separate self-generated fixture directory was created. Programmatic mutations and weak-consumer cases are additionally frozen in `test_contract_d.py` and `weak_consumers.py` above.

## Exact allowed pre-freeze sources opened

All were opened only at `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`:

1. `research/contract-d-independent-authority-rc3/candidate/SPEC.md` — expected/observed blob `a91a9f171a3b5f3241b5970d7c0415e00f0477d7`
2. `research/contract-d-independent-authority-rc3/candidate/schema.json` — expected/observed blob `41481aa7941a789534c974ed7b368fddead6ce5a`
3. `research/contract-d-independent-authority-rc3/candidate/effect-registry.json` — expected/observed blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc3/candidate/fixtures/valid.json` — expected/observed blob `f823936c9945ea551943c40bee1e956faf1d834d`
5. `research/contract-d-independent-authority-rc3/candidate/fixtures/invalid.json` — expected/observed blob `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6`
6. `research/contract-d-independent-authority-rc3/candidate/conformance-cases.json` — expected/observed blob `229f2898f756f9ca078086cfc99d2a6a2edd2a73`

The five packet-authorized durable governance files were unavailable through this task aperture. They were not substituted with conversation history, memory, other attachments, GitHub narrative, or reconstructed text.

## Denied-surface statement

No pre-freeze denied Contract D reference implementation/test, Decision Engine implementation/output, prior reproduction material, PR/issue content, predecessor branch surface, broad GitHub search, web search, conversation history, user memory, assistant memory, or project-history material was opened or used before the freeze.

**NO PRE-FREEZE DENIED MATERIAL OBSERVED**

## Local deterministic test receipt

Exact command:

`cd /tmp/contract_d_rc3_repro && python -m unittest -v`

Result immediately before freeze upload verification:

- tests run: 12
- failures: 0
- errors: 0
- result: `OK`

The uploaded implementation, weak-control module, test suite, self-generated case record, and predictions were then verified by Git blob identity to exactly match the locally tested files before the access ledger was sealed.

Hosted status query for freeze commit returned no statuses.

**HOSTED TEST: NOT AVAILABLE ON CLEAN BASE**

## Deviations / bounded notes

- The five durable governance files named by the packet were unavailable; execution continued under the narrower aperture because the packet itself supplied the exact clean-room gates and research protocol needed for this run.
- No repository-wide CI/workflow/configuration file was added or modified.
- No separate self-generated fixture directory was needed; cases were frozen as one JSON corpus plus programmatic tests.
- The pre-reveal implementation selected and froze explicit interpretations for zero-parameter effect normalization, requested safe-default normalization, and HOLD/failed applicability ordering in `PREDICTIONS.md`.

## Order statement

The independent freeze commit `af15722cc52372e79abb097c587efec5eab5ff13` and tree `4d38222cbd0b2024ca93477a387e97b6d2969095` existed before any Phase A reference implementation or tests were revealed. This receipt is additive and does not modify the frozen independent object.
