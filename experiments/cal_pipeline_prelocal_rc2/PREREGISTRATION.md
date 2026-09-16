# CAL Pipeline pre-local pressure apparatus successor RC2

## Predecessor

RC1 run `35050244828` executed all six component pressure suites successfully but the cross-chain lane stopped before Evidence Bundler semantics because the direct EB script subprocess could not import the checked-out `src/evidence_bundler` package.

Preserved RC1 evidence:

- run `35050244828`;
- artifact `10428358814`;
- digest `sha256:795ab06ff37288e28a98ee5b17afabeac6046d192f93157d02d5b737b105d695`;
- reconciliation: `../cal_pipeline_prelocal_rc1/RUN1_RECONCILIATION.md`;
- disposition: `APPARATUS_FAILURE_BEFORE_EB_CROSS_CHAIN_EXECUTION`.

## Exact RC2 delta

RC2 changes no scientific subject, fixture, semantic expectation, test adapter, contract authority, admission decision, or component checkout.

The only execution changes are:

1. prepend the exact checked-out `deps/eb/src` directory to `PYTHONPATH` for direct Evidence Bundler subprocesses;
2. preserve the component-suite log directory across the unchanged RC1 cross-chain driver's output-directory reset;
3. copy the resulting evidence tree into an RC2-named artifact directory and bind it to the RC2 manifest.

The corrected two-lane scientific design from RC1 is reused byte-for-byte.

## Stop rule

Any later failure is interpreted at the first newly reached boundary. Do not repair a component inside this apparatus successor. If another harness-only defect occurs, preserve RC2 and create a successor.
