# CAL Pipeline pre-local pressure RC3 — Run 1 reconciliation

## Preserved execution

- workflow run: `35052292513`
- job: `104655083751`
- harness head: `432d54ca4585a765472831b22cd9072ba05f36b1`
- artifact: `10429730724`
- artifact digest: `sha256:3c2a1424a9023125c8e04d26eb46af70fb67ef861831983d5852a4d13ae0062b`

## Observed component evidence

All six independently selected component pressure suites passed before the cross-chain driver:

- ClaimGate exact qualification-runbook suites: PASS (`34 + 14` pytest cases and Ruff);
- Evidence Bundler integration boundary: PASS (`11 passed, 1 skipped`);
- current CAL focused pressure suite: PASS (`38 passed`);
- Contract C2 validator pressure suite: PASS (`9 passed`);
- Decision C2 ingress hostile-control suite: PASS, including stale hash, wrong Contract B, target substitution, wrong authority, C1/C2 cross-ingress, replay mismatch, and no-downgrade controls;
- Contract E RC3 target-cardinality successor: PASS (`65` asserted controls).

## Cross-chain failure

The RC3 wrapper imported `experiments/cal_pipeline_prelocal_rc2/run_pressure.py` under the generic module name `run_pressure`. RC2 then prepended the RC1 directory and performed `import run_pressure`, which resolved to the already-loaded RC2 module. This recursively re-entered `rc2.main()` until Python raised `RecursionError`.

No ClaimGate → EB → CAL → C2 scientific cross-chain result was produced, and no `RESULT.json` was preserved in the RC3 artifact.

## Classification

`APPARATUS_FAILURE_BEFORE_SCIENTIFIC_CROSS_CHAIN_EXECUTION`

This run does not falsify any pipeline component or seam. It does falsify the RC3 wrapper composition strategy.

## Successor constraint

A successor may change only module-loading apparatus: load the already frozen RC1 scientific driver by a unique explicit module identity, while retaining RC3's exact interpreter-environment repair. No component, fixture, admission, typed target, contract authority, semantic expectation, hostile control, or scientific readiness criterion may change.
