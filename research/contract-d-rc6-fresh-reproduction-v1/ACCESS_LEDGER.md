# Contract D RC6 Fresh Reproduction v1 — Access Ledger

Contamination status: **CLEAN for answer-bearing information**. No denied reference/change-note/test/dependency/prior-result content was intentionally accessed before freeze.

One exact candidate-subtree identity verification returned Git tree metadata that included the already-denied file names plus their blob/tree identities. No denied blob contents were opened. This exposure is recorded below as non-answer-bearing metadata and did not determine implementation architecture or edge-case outputs.

This ledger records repository/path accesses for the prereveal clean-room reproduction. The immutable launch packet was treated as the sole task authority.

## Clean-base verification

- `camerontjs-dot/apparatus-contracts` @ `f759b0ba502e0158c190b53435d6aae588bd9b9e` — `research/contract-d-independent-authority-rc6/CONTEXT_FREE_LAUNCH_PACKET.md` — verified blob `47392bb18b4ceec6dc6dc689a1444ccd9de0fce9`.
- `camerontjs-dot/research-scaffold-harness` — exact ref `refs/heads/research/contract-d-rc6-fresh-reproduction-v1` — verified head `548bfa81f65290eda15af658f647497679b840ef` without branch enumeration.
- `camerontjs-dot/research-scaffold-harness` — exact commit `548bfa81f65290eda15af658f647497679b840ef` — verified tree `191976638bbf8b7153e3f2c94945a2f15cd640ad`.
- `camerontjs-dot/research-scaffold-harness` — exact tree `191976638bbf8b7153e3f2c94945a2f15cd640ad` path-name inspection only — no `contract-d` implementation/reproduction paths found.

## Post-clean-base intentional repository accesses

### Authoritative repository

- `camerontjs-dot/apparatus-contracts` — exact candidate commit metadata `bb656fc50806c344fda1ddeaf08a9878f5cb460e`.
- `camerontjs-dot/apparatus-contracts` — exact candidate subtree object `5151e2c30235784d4ae594db454ac24c1e3868b4`.
  - Non-answer-bearing denied-file metadata exposed by that tree response: `contract_d_consume.py` blob `42536aaac5acd953f150a87891a70e9c194b7aaf`; `contract_d_core.py` blob `473f3c65ef838f9d4f03ee01b497e7263a6d2da7`; `contract_d_validate.py` blob `8cc6d81515d7c5b0a86df163a38d1c12931f897f`; `requirements.txt` blob `9bc3e4b733b2963a79a756a696eeafc92b532634`; `tests` tree `520e13eb378e0a23736fb3c3b102ed8a1e8de377`. No content from those objects was fetched.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/SPEC.md` — blob `6ff21ae57b4ae57f1d76ba34c41052b7966df7c5`.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/schema.json` — blob `c7c9f6b7a5874e08cbe3b3ce06c126a2b889e900`.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/effect-registry.json` — blob `53df222ca439248a44029e02a662825235db892f`.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/fixtures/valid.json` — blob `14c9259ce327f6a52f4a0d5e14260c0f92ad5fa2`.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/fixtures/invalid.json` — blob `08b69594e94cae6573e2afd882ef78d9c70629dc`.
- RC6 public authority: `research/contract-d-independent-authority-rc6/candidate/conformance-cases.json` — blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4`.
- Explicitly incorporated inherited public authority: `research/contract-d-independent-authority-rc5/candidate/SPEC.md` @ `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8` — blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`.
- The allowed RC6 SPEC itself contains historical rationale text and a prior-result reference. That text was encountered only because it is embedded in the expressly allowed public authority. The referenced prior result was not opened.
- No RFC/web/runtime documentation was consulted. Node.js `v22.16.0` built-ins were used directly.

### Execution repository

- `research/contract-d-rc6-fresh-reproduction-v1/ACCESS_LEDGER.md` — created immediately after clean-base verification.
- Write-mechanics note: an initial GitHub contents write was rejected before mutation; an unattached tree `b9dbda9aaf9cfea4cdcb929e29ec331ed51bc0b4` and unattached commit `bbfc8f8e90321fc03238e14ba7e423ab745e9065` were then created while testing an alternate write path, but the ref update was rejected. Neither object became the reproduction branch head. The ledger was subsequently created through the contents API.
- `research/contract-d-rc6-fresh-reproduction-v1/contract_d_rc6_consumer.mjs` — independent implementation written after authority read; frozen blob `26058b7901347c6e7e3c207de2195a0ab529aa08`.
- `research/contract-d-rc6-fresh-reproduction-v1/test_contract_d_rc6_consumer.mjs` — independent prereveal tests; frozen blob `c4f733088fe25f482b07b24fe2685d7a524d1e20`.
- `research/contract-d-rc6-fresh-reproduction-v1/PREREVEAL_TEST_LOG.md` — preserved intermediate/final prereveal test record; frozen blob `f4f1864e78166d8c0ec58ed0c2c90b2fa952c9ce`.
- Exact reproduction branch ref re-read after freeze candidate creation; it resolved to `f5ce28cef76808e390e016d63dec3d50a28fbda2`.
- Exact freeze commit `f5ce28cef76808e390e016d63dec3d50a28fbda2` read; verified freeze tree `805c3b229922a605b16990a699ffa03f3a2e6250`.
- Frozen implementation/test/log paths re-read at exact freeze commit only to verify their blob identities; no modifications followed.

## Prereveal test execution

- Run 1: `66 passed, 1 failed, 67 total`; failure preserved in `PREREVEAL_TEST_LOG.md` and corrected solely from allowed public authority.
- Run 2 / freeze-candidate result: `67 passed, 0 failed, 67 total`.

## Denied-material statement

Before the implementation/test freeze, no RC6 reference implementation blob, RC6 reference tests, RC6 requirements content, RC6 change-note content, any non-authorized RC5 file content, RC3/RC4 material, prior Contract D final record, adversarial-harness artifact, Decision Engine implementation/producer code, or promotion/EDR record was intentionally accessed. No post-freeze reference reveal was performed.
