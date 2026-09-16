# RC2 Run 1 Reconciliation

## Preserved execution

- workflow run: `35050510484`
- job: `104649628733`
- executed harness head: `4d7157ddf709c93188f2e248a5693466375723b6`
- artifact: `10428149791`
- artifact digest: `sha256:b2df04d03278943f0b1ae8b5cc859983da5785433a74149555f8fd65648191a2`
- workflow conclusion: `failure`

## What passed

All six component pressure suites passed again:

- ClaimGate exact qualification-runbook suites;
- Evidence Bundler integration-boundary suite (`11 passed, 1 skipped`);
- current CAL focused suite;
- Contract C2 validator suite;
- Decision C2 hostile-control suite;
- Contract E RC3 65-control suite.

The exact authority manifest and annotated Contract C1 / Contract D tag identities also passed inside the cross-chain driver. The raw ClaimGate lane again emitted valid authoritative Contract A and the stale-root hostile mutation was rejected.

## Exact apparatus failure

RC2 successfully added `deps/eb/src` to `PYTHONPATH`, so the direct EB subprocess found `evidence_bundler`. It then failed importing `yaml`.

The command receipt shows why:

`/opt/hostedtoolcache/Python/3.11.16/x64/bin/python3.11 .../deps/eb/scripts/run_v1_integration_candidate.py`

The RC1 scientific driver constructs interpreter paths using `Path(.../.venv-*/bin/python).resolve()`. On the hosted runner, each venv Python is a symlink, so `.resolve()` dereferenced it to the system interpreter and discarded the venv site-packages. The EB component suite used the non-resolved `.venv-eb/bin/python` and passed, which discriminates this as harness interpreter plumbing rather than EB behavior.

The same latent issue would affect later helper subprocesses that use the resolved CAL or ClaimGate interpreter paths.

No EB retrieval result was produced by the cross-chain canary, so RC2 still has no scientific result downstream of Contract A.

## Successor correction

RC3 may change only interpreter environment plumbing. Keep the RC1 scientific driver byte-identical and provide the exact installed ClaimGate, EB and CAL venv site-package directories on `PYTHONPATH` so its dereferenced Python executables see the same installed environments already proven by the component suites.

No component bytes, fixtures, semantic expectations, admissions, targets, contract authorities, or readiness criteria may change.

## RC2 disposition

`APPARATUS_FAILURE_BEFORE_EB_CROSS_CHAIN_EXECUTION`
