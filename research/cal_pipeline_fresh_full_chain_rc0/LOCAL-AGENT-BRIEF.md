# Local Agent Brief — CAL Fresh Full-Chain RC0

Execute the prepared run series in:

`research/cal_pipeline_fresh_full_chain_rc0/`

Read `RUN-SERIES.json` and `README.md` first.

## Goal

For the three prepared single-proposition full-chain cases, run the exact frozen pipeline twice:

1. **control** — ordinary pipeline execution with no provenance sidecars;
2. **instrumented** — exact same causal inputs/configuration plus the already-qualified provenance attestation/retention/RunManifest layer.

Pipeline target:

`Gate V1.0.0 → Contract A 2.0.0 → EB 10/3 → Contract B 1.2 → CAL → C2 → Decision → D`

Do not update component commits, tune retrieval, invent admissions, repair CAL outcomes, or modify Decision policy.

## Required cases

- `not-needed-single`
- `declared-all-of`
- `health-canada-text-representation`
- `valve-temporal-status`

Also run `declared-all-of` as the prepared decomposition-boundary probe.

Use only the frozen packets in `cases/`.

The Health Canada packet is a new explicit text-representation successor. Do not substitute the older `text/html` packet; its failure is preserved separately.

## Contract A gate

Before EB runs, validate each emitted Contract A against exact released Contract A 2.0.0 authority:

`529c92b49a34d5c610618551a8737f019f9fa332`

If external validation fails, preserve it and stop that case as `BLOCKED_AT_CONTRACT_A_CONFORMANCE`.

## EB admission

Omit `--admission` unless an exact, pre-existing, independently justified admission artifact already belongs to the case.

Do not manually accept passages merely to force CAL to assess them.

## CAL target boundary

Use the exact frozen typed targets under `targets/` for:

- `not-needed-single`
- `health-canada-text-representation`
- `valve-temporal-status`

These targets explicitly use `semantic_family: unsupported`. Do not retag them as a supported family to obtain a favorable CAL verdict. The purpose is to exercise canonical B intake and the fail-closed CAL → C2 → Decision path truthfully.

For `declared-all-of`, do not invent a root-level all_of aggregation. The current canonical CAL surface consumes one exact Contract B claim at a time. Preserve the decomposition/child boundary and report where execution legitimately stops or fans out.

## Pair comparison

After control and instrumented runs, compare exact bytes/hashes for:

- Contract A;
- EB native package;
- Contract B;
- CAL native result;
- C2;
- D.

If provenance instrumentation changes any authoritative/native semantic artifact, record:

`FAILED_PROVENANCE_NONINTERFERENCE`

Do not repair or rerun with changed semantics.

Run-local path-only receipt differences may be classified separately if they do not change domain/semantic artifacts.

## Provenance

For instrumented runs, reuse the helpers from:

`research/cal_pipeline_provenance_run_series_rc1/`

Retain all reconstruction-required bytes and emit stage attestations plus a candidate RunManifest.

Do not self-authorize candidate manifest roots.

Stop successful instrumented cases at:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

## Output root

`20_live/cal-pipeline/cal-v1-studies/full-chain-rc0/`

Keep control and instrumented outputs separate under each case.

## Report back

Return:

- exact component/worktree SHAs;
- per-case Gate/A/EB/CAL/C2/Decision terminal states;
- A/B/C2/D and native-output identities;
- control vs instrumented byte/hash comparison;
- any path-only/non-semantic differences;
- candidate manifest roots;
- retention results;
- every failure/deviation;
- confirmation that no merge, release, promotion, Authorization, or downstream action occurred.
