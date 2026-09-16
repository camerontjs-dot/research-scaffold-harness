# CAL Pipeline pre-local pressure apparatus successor RC4

## Predecessor

RC3 preserved all six component pressure suites as PASS but failed before scientific cross-chain execution because the RC3 wrapper loaded RC2 under the generic module name `run_pressure`. RC2 then resolved its intended RC1 import back to itself and recursed until `RecursionError`.

Preserved RC3 evidence:

- run `35052292513`;
- job `104655083751`;
- artifact `10429730724`;
- artifact digest `sha256:3c2a1424a9023125c8e04d26eb46af70fb67ef861831983d5852a4d13ae0062b`;
- reconciliation: `../cal_pipeline_prelocal_rc3/RUN1_RECONCILIATION.md`;
- disposition: `APPARATUS_FAILURE_BEFORE_SCIENTIFIC_CROSS_CHAIN_EXECUTION`.

## Exact RC4 delta

RC4 changes no component, fixture, admission, typed target, contract authority, semantic expectation, hostile control, or scientific readiness criterion.

It retains RC3's interpreter-environment repair, but removes wrapper-on-wrapper module resolution. RC4:

1. discovers the exact installed site-packages directories for `.venv-cg`, `.venv-eb`, and `.venv-cal`;
2. prepends those site-packages plus exact checked-out source roots to `PYTHONPATH`;
3. loads `experiments/cal_pipeline_prelocal_rc1/run_pressure.py` directly with `importlib.util.spec_from_file_location` under a unique module name;
4. invokes that frozen scientific driver's `main()` with the same root and inputs;
5. preserves RC4 component logs and copies the frozen driver's complete evidence tree into an RC4-named artifact.

This is an apparatus-only successor. No scientific expectation is changed after observing RC3.

## Scientific stop rule

If RC4 reaches a genuine pipeline seam, preserve the result even if red. In particular, if current CAL structurally materializes valid Contract C2 but the independently frozen C2 producer-policy resolver rejects current CAL semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`, classify the run as `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY` rather than manufacturing authority.

No production component may be repaired from inside this campaign.
