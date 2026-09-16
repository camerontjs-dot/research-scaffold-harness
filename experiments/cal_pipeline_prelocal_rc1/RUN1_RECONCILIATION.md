# RC1 Run 1 Reconciliation

## Preserved execution

- workflow run: `35050244828`
- job: `104648837374`
- executed harness head: `c0d8147b4759288c8afd4fbfb8d3a93cff630896`
- artifact: `10428358814`
- artifact digest: `sha256:795ab06ff37288e28a98ee5b17afabeac6046d192f93157d02d5b737b105d695`
- workflow conclusion: `failure`

## What RC1 successfully discriminated

All exact authority checkouts succeeded, including the required annotated Contract C1 and Contract D tags.

Every component pressure suite passed:

- ClaimGate exact qualification-runbook suites: PASS;
- Evidence Bundler integration-boundary suite: PASS;
- current CAL focused suite: PASS;
- Contract C2 validator suite: PASS;
- Decision C2 ingress hostile-control suite with release tags: PASS;
- Contract E RC3 successor 65-control suite: PASS.

This confirms the two RC0 wrapper corrections were apparatus corrections rather than product repairs. No component candidate changed.

## Sole RC1 cross-chain blocker reached

The corrected raw lane successfully reached ClaimGate and emitted the expected authoritative `NOT_NEEDED / not_decomposed` Contract A. External Contract A validation passed and the stale-root mutation was rejected.

The next EB seed subprocess failed before EB semantics because Python could not import `evidence_bundler` when invoking the repository script directly:

`ModuleNotFoundError: No module named 'evidence_bundler'`

This occurred despite the focused EB pytest suite passing. The editable/minimal environment plus direct script invocation did not place `deps/eb/src` on that subprocess's import path. No Evidence Bundler retrieval result was produced by the cross-chain lane, so no downstream scientific result exists for that lane.

## Additional apparatus observation

The cross-chain driver recreated `build/cal_pipeline_prelocal_rc1/` and thereby removed the component log directory generated earlier in the job. GitHub step conclusions still preserve the component outcomes, but RC2 will preserve those logs in the uploaded artifact as intended.

## Successor correction

RC2 may change only pressure-harness plumbing:

1. explicitly expose the exact checked-out EB `src/` directory to direct EB subprocesses through `PYTHONPATH`;
2. preserve existing component logs instead of deleting their parent output directory.

No claim fixture, component SHA, semantic expectation, admission decision, CAL typing, C2 materialization rule, Decision policy, Contract E rule, or scientific gate may change because of this failure.

## RC1 disposition

`APPARATUS_FAILURE_BEFORE_EB_CROSS_CHAIN_EXECUTION`
