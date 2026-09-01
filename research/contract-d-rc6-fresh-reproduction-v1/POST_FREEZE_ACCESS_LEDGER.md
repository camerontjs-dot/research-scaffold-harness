# Contract D RC6 Fresh Independent Consumption Reproduction v1 — Post-Freeze Access Ledger

## Scope

This ledger begins only after successful freeze verification. It does not rewrite or amend the frozen prereveal `ACCESS_LEDGER.md` or `FREEZE_RECEIPT.md`.

Post-freeze reference authority was opened only after verifying:

- branch head before post-freeze record work: `e1d436cd9813eefc84aec5129afa0bef4594ed72`;
- immutable freeze commit: `f5ce28cef76808e390e016d63dec3d50a28fbda2`;
- freeze tree: `805c3b229922a605b16990a699ffa03f3a2e6250`;
- frozen implementation blob: `26058b7901347c6e7e3c207de2195a0ab529aa08`;
- frozen test blob: `c4f733088fe25f482b07b24fe2685d7a524d1e20`;
- prereveal test-log blob: `f4f1864e78166d8c0ec58ed0c2c90b2fa952c9ce`;
- durable freeze-receipt blob: `47ed7bf0632c8d36a52de380b2ca226e46e51d9a`;
- final prereveal access-ledger blob: `cd80c34d513786cd8ee8b02c5b46250f0dae3398`.

The frozen implementation and test files were re-fetched from the freeze commit, reconstructed locally, and verified with Git blob hashing to the exact frozen blob identities before post-reveal execution. They were not modified.

## Authorized reference material opened

All apparatus-contracts paths below were read at commit `bb656fc50806c344fda1ddeaf08a9878f5cb460e` unless a different commit is stated.

| Path | Immutable identity | Purpose |
|---|---|---|
| `research/contract-d-independent-authority-rc6/RC6_CHANGE_NOTE.md` | blob `2eeb6e719ef4c5efac3adad0c3edc8d43454e364` | RC6 clarification scope |
| `research/contract-d-independent-authority-rc6/candidate/contract_d_core.py` | blob `473f3c65ef838f9d4f03ee01b497e7263a6d2da7` | reference core behavior |
| `research/contract-d-independent-authority-rc6/candidate/contract_d_validate.py` | blob `8cc6d81515d7c5b0a86df163a38d1c12931f897f` | reference byte-ingress validation |
| `research/contract-d-independent-authority-rc6/candidate/contract_d_consume.py` | blob `42536aaac5acd953f150a87891a70e9c194b7aaf` | reference consumer behavior |
| `research/contract-d-independent-authority-rc6/candidate/requirements.txt` | blob `9bc3e4b733b2963a79a756a696eeafc92b532634` | pinned dependency |
| `research/contract-d-independent-authority-rc6/candidate/tests/` | tree `520e13eb378e0a23736fb3c3b102ed8a1e8de377` | reference test suite |
| `.../tests/test_rc6_expectation_hardening.py` | blob `9d02b269fe83ba79ded16d154f59fed0267e87c5` | reference tests |
| `.../tests/test_rc6_jcs_vectors.py` | blob `35a01f918fc4b993e5367d7878e5b11a90bcd428` | reference tests |
| `.../tests/test_rc6_normalized_effect_shape.py` | blob `e16d12efcc847bdab9754c7192c3614bda015993` | reference tests |
| `.../tests/test_rc6_regression.py` | blob `1f8470b4f6efea5bec3260cd575a626e8242c045` | reference tests |

The authorized RC6 candidate subtree was verified as tree `5151e2c30235784d4ae594db454ac24c1e3868b4`.

## Public authority reread

| Commit | Path | Blob |
|---|---|---|
| `bb656fc50806c344fda1ddeaf08a9878f5cb460e` | `research/contract-d-independent-authority-rc6/candidate/SPEC.md` | `6ff21ae57b4ae57f1d76ba34c41052b7966df7c5` |
| same | `.../candidate/schema.json` | `c7c9f6b7a5874e08cbe3b3ce06c126a2b889e900` |
| same | `.../candidate/effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` |
| same | `.../candidate/fixtures/valid.json` | `14c9259ce327f6a52f4a0d5e14260c0f92ad5fa2` |
| same | `.../candidate/fixtures/invalid.json` | `08b69594e94cae6573e2afd882ef78d9c70629dc` |
| same | `.../candidate/conformance-cases.json` | `29825bfa89b2b91bfa9e457c001e2c869a3649a4` |
| `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8` | `research/contract-d-independent-authority-rc5/candidate/SPEC.md` | `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c` |

The original RC6 launch packet was not reread because it was not needed after the supplied packet and public authority resolved the comparison questions.

## External dependency and standards material consulted

- PyPI `rfc8785` release `0.1.4`, to confirm the pinned release is a pure-Python package, Python >=3.8, and published release identities. Published wheel SHA-256: `520d690b448ecf0703691c76e1a34a24ddcd4fc5bc41d589cb7c58ec651bcd48`; sdist SHA-256: `e545841329fe0eee4f6a3b44e7034343100c12b4ec566dc06ca9735681deb4da`.
- `trailofbits/rfc8785.py` tag `v0.1.4`, resolving to commit `4d9b161f6054301d98d0566e813d020fb019ee10`. Material source files used locally: `src/rfc8785/__init__.py` blob `5a1f9d919643fa3bcaa0999ea66d9c535568c42a`, `src/rfc8785/_impl.py` blob `3137d3326b98938affadb1be711ee411eb2ab86e`.
- RFC 8785, JSON Canonicalization Scheme, RFC Editor HTML, especially sections 3.2.2.3 and Appendix B, to check the bounded JCS numeric vectors and ECMAScript/IEEE-754 framing.

No unrelated standards or runtime documentation was needed.

## Accidental exposures

- No answer-bearing denied reference content was opened post-freeze.
- The authorized RC6 `SPEC.md` and `RC6_CHANGE_NOTE.md` themselves contain identifiers and summary statements referring to earlier RC5 reproduction history. Those statements are part of the explicitly authorized files. No referenced historical implementation, final record, adversarial harness, promotion record, or producer/consumer implementation was opened.
- The prereveal non-answer-bearing candidate-tree metadata exposure remains exactly as recorded in the frozen receipt. No new evidence reclassifies it as answer-bearing.

## Deviations and environment/tooling events

1. Direct network access from the local execution container to GitHub/PyPI raw endpoints was unavailable (DNS/network failure). No reference behavior was inferred from that failure.
2. The pinned `rfc8785==0.1.4` package was not preinstalled and no local package cache was available. Instead of substituting versions, the exact `v0.1.4` source was fetched through the GitHub connector, locally reconstructed, and Git-blob verified before use. This is a dependency-acquisition deviation, not a dependency-version deviation.
3. An attempted alternate MainFrame Conduit runtime lookup failed with an MCP 404 and exposed no project content. It was abandoned; no Conduit agent was created.
4. One initial GitHub tag endpoint attempt was rejected before content retrieval; the exact `refs/tags/v0.1.4` endpoint was then used successfully.
5. The outer command environment emitted `TERM environment variable not set` after completed local test commands. This occurred outside pytest/Node test behavior and did not change exit status or test results.
6. The connector text-transfer surface could not safely carry the 25,138-byte orchestrator and full per-case result corpus as single plain-text writes. Their exact bytes were therefore preserved in deterministic gzip/tar+gzip envelopes. Uncompressed content identities are recorded in the terminal/execution records and the result manifest; no experiment input, output, or classification was changed.

## Denied material status

No RC3/RC4 material, prior RC5 independent implementation/tests/final record, adversarial-harness artifact, Decision Engine production implementation, promotion/EDR record, surrounding project conversation, user memory, prior ChatGPT reasoning, or broad expected-outcome search was retrieved.
