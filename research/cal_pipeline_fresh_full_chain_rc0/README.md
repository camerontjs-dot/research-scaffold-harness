# CAL Pipeline Fresh Full-Chain RC0

Status: prepared research run series. No merge, release, promotion, Authorization, or production permission.

## Question

Can three known-authorable, released-Contract-A-valid single propositions traverse the frozen CAL Pipeline through Decision, while a fourth declared/all_of case exposes the current decomposition boundary, and does already-qualified provenance instrumentation leave authoritative/native pipeline outputs unchanged?

This series separates two questions:

1. **fresh full-chain execution**: Gate → A → EB → B → CAL → C2 → Decision → D;
2. **provenance non-interference**: exact same causal run with and without attestation/RunManifest sidecars.

## Exact machinery

See `RUN-SERIES.json`.

Important pins:

- Gate V1.0.0: `c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`
- Contract A 2.0.0 lock: `529c92b49a34d5c610618551a8737f019f9fa332`
- Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- EB profile: `eb-v1-integration-10x3-rc0`
- Contract B 1.2 lock: `c314e53bd91c0736aa4370a364673b069aceb43e`
- CAL C2 authority: `8204417f478cfbd891499145a7edec5ee33405ad`
- CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- Contract C2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- resolver: `1d33e0612befcf8016816197c90c062373796df9`
- Decision Engine: `b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55`
- Contract D authority: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- provenance candidate schemas: `1a5929295e735e351320cbd8c966dc43afed2859`
- provenance terminal research state: `SUPPORTED_PROVENANCE_RECONSTRUCTION_V1_RC1`

## Cases

### not-needed-single

Known Gate fixture lineage. Expected Gate state `NOT_NEEDED`, Contract A `not_decomposed`.

### declared-all-of

Known Gate fixture lineage. Expected Gate state `DECLARED`, Contract A `declared/all_of`.

### health-canada-text-representation

Successor representation of the Health Canada case. The consumed source representation is explicitly `text/plain; charset=utf-8`, which is valid under released Contract A 2.0.0.

The earlier `text/html` failure remains frozen separately in Proposition Authoring Draft PR #50 and must not be reinterpreted.

### valve-temporal-status

Single-proposition successor of the qualified Gate representative fixture. Expected Gate state `NOT_NEEDED`, Contract A `not_decomposed`. The two supplied representations are explicit UTF-8 text representations valid under released Contract A 2.0.0.

### declared-all-of

This case remains in the series as a decomposition-boundary probe. Gate/A/EB are expected to run, but the canonical CAL `run-bundle` surface consumes one typed Contract B claim at a time and no separately qualified root-level `all_of` aggregator is being assumed here.

Do not fabricate a root Decision by composing child results ad hoc. Preserve the exact child-claim boundary if that is where the current pipeline stops.

## Paired execution

For each case marked as a fresh single-proposition full-chain run:

### A. Control

Run the exact frozen pipeline without generating provenance attestations or a RunManifest.

Retain all ordinary component/native outputs and hashes.

### B. Instrumented

Run again from the exact same packet, component commits, configuration, compatibility carrier, admission state, and policies.

Add only:

- stage attestations;
- reconstruction-required artifact retention;
- deterministic directory snapshots where needed;
- candidate RunManifest;
- candidate manifest root.

Provenance state must not feed back into Gate, EB, CAL, C2, or Decision.

## Equality burden

Compare control vs instrumented for each stage that actually executes:

- Contract A;
- EB native package;
- Contract B;
- CAL native result;
- Contract C2;
- Contract D.

Require byte equality where the underlying apparatus is deterministic.

If a wrapper/receipt differs only because it records an output path or other run-local non-semantic metadata, preserve both values and classify that difference explicitly. Do not broaden the exception to domain or semantic outputs.

A difference in an authoritative/native semantic artifact caused by provenance instrumentation is:

`FAILED_PROVENANCE_NONINTERFERENCE`

## Evidence Bundler admission rule

Do not invent admission judgments for these cases.

Omit `--admission` unless a pre-existing frozen, independently justified admission artifact already belongs to the exact case.

Retained candidates therefore remain `needs-review` by default. That may lead CAL to `not_checkable` and Decision to HOLD; those are legitimate results.

The experiment requires the machinery to execute faithfully, not a favorable verdict.

## Output layout

Use:

`20_live/cal-pipeline/cal-v1-studies/full-chain-rc0/`

Recommended layout:

```
<case-id>/
  control/
    gate/
    eb/
    cal/
    decision/
    hashes.json
  instrumented/
    gate/
    eb/
    cal/
    decision/
    provenance/
      *.attestation.json
      RUN-MANIFEST.candidate.json
      CANDIDATE-ROOT.txt
      RETENTION-CHECK.json
    hashes.json
  PAIR-COMPARISON.json
  OBSERVATIONS.md
```

Preserve actual native filenames when they differ.

## Contract A external validation

Before any Contract A is passed to EB, validate it against exact released Contract A 2.0.0 authority at `529c92b...`.

Do not rely solely on Gate's internal bundle verifier.

## Provenance

Reuse the already-qualified provenance helpers inherited from:

`research/cal_pipeline_provenance_run_series_rc1/`

The instrumented run may produce a candidate manifest digest but must not treat it as its own trusted root.

Stop after candidate roots are produced at:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

A later independent step will freeze roots and reconstruct packages.

## Terminal outcomes

- `READY_FOR_INDEPENDENT_ROOT_FREEZE`
- `BLOCKED_AT_GATE`
- `BLOCKED_AT_CONTRACT_A_CONFORMANCE`
- `BLOCKED_AT_EB`
- `BLOCKED_AT_CAL_C2_AUTHORITY`
- `FAILED_PROVENANCE_NONINTERFERENCE`
- `FAILED_PIPELINE`

Preserve the smallest true outcome. Do not repair a case inside the run series.

## Nonclaims

This series does not establish retrieval recall, evidence completeness, CAL semantic accuracy, Decision correctness, Authorization, production readiness, or permission to publish Gate V1.0.0.


## Frozen CAL targets

The three single-proposition full-chain cases have exact typed target files under `targets/`.

They deliberately use `semantic_family: unsupported` because these status-style claims are outside CAL V1's two deciding semantic families. This is not a shortcut around CAL. It is an explicit, typed fail-closed path through the canonical Contract B intake.

A terminal `UNSUPPORTED_SEMANTIC_FAMILY` / `not_checkable` result is therefore a legitimate expected class for these cases and still exercises B → CAL → C2 → Decision mechanically.

Do not change the target family merely to obtain SUPPORT/REFUTE.
