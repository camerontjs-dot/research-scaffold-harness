# Source Authority and Contamination Record

## Authorities inspected before freeze

### Apparatus Contracts

- repository: `camerontjs-dot/apparatus-contracts`
- live `main`: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Contract D research/registry issue: #22
- issue #22 is a research coordination record and explicitly authorizes no Contract D version.

### Decision Engine

- repository: `camerontjs-dot/decision-engine`
- live `main`: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- promoted Decision / Authorization boundary merge: `f7c3759dfac7ee4be45879b8266b5eb1440530ee`
- Contract D research PR: #19
- observed PR #19 head before freeze: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- RC0 preregistration: `6d6f003cc705264e4f8ecda24602da1da1820bc0`
- RC0 executed head named in written results: `c6824ecf6a5cb75b165195a39765582481fe6c95`
- RC0 written-results commit: `cc27d766d751dbc1d062e0790f2bee5e04276c23`
- RC1 preregistration: `785a407e71797e88c89e81fd164302c05785d9d0`
- RC1 hosted execution commit: `a31ddd73f417edcbcaf9bb46abfdb48e5ddb5793`
- RC2 preregistration: `bc1cc749bcea5a12aa66f6ac091cc17a8463991c`
- RC2 hosted execution/current observed head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`

## Public artifacts actually read before freeze

- PR #19 `PREREGISTRATION.md`
- PR #19 `RC1-PREREGISTRATION.md`
- PR #19 `RC2-PREREGISTRATION.md`
- PR #19 `RESULTS.md`
- PR #19 metadata and changed filenames
- PR #19 commit metadata/messages, without diffs
- current GitHub Actions run metadata, without logs/artifact contents
- apparatus-contracts issue #22
- live branch metadata and current CI summaries

## Explicitly not inspected before freeze

- `research/contract-d-schema-bakeoff-rc0/run.mjs`
- `run-rc1.mjs`
- `run-rc2.mjs`
- any patch/diff for those files
- implementation-specific reference tests
- reference validators/decoders/canonicalizers/consumer implementation
- GitHub Actions job logs for the Contract D research scripts
- generated reference fixtures/expected outputs not included in the public preregistration/result prose
- workflow artifacts that could disclose those outputs

No pre-freeze contamination is known. If later evidence shows that an inspected public result encoded an implementation-specific algorithm beyond legitimate consumer authority, that will be recorded as an experimental limitation rather than hidden.
