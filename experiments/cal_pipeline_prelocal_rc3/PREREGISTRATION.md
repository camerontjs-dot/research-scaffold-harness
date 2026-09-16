# CAL Pipeline pre-local pressure apparatus successor RC3

## Predecessor

RC2 run `35050510484` preserved all six component pressure suites as PASS but the cross-chain lane again stopped before Evidence Bundler semantics because the frozen RC1 driver dereferenced `.venv-*/bin/python` symlinks with `Path.resolve()`, causing helper subprocesses to run under the system interpreter without the installed venv site-packages.

Preserved RC2 evidence:

- run `35050510484`;
- job `104649628733`;
- artifact `10428149791`;
- artifact digest `sha256:b2df04d03278943f0b1ae8b5cc859983da5785433a74149555f8fd65648191a2`;
- reconciliation: `../cal_pipeline_prelocal_rc2/RUN1_RECONCILIATION.md`;
- disposition: `APPARATUS_FAILURE_BEFORE_EB_CROSS_CHAIN_EXECUTION`.

## Exact RC3 delta

RC3 changes no component, fixture, admission, typed target, contract authority, semantic expectation, hostile control, or scientific readiness criterion.

It reuses the exact RC1 scientific driver through the RC2 wrapper and changes only interpreter environment plumbing:

1. discover the exact installed site-packages directories for `.venv-cg`, `.venv-eb`, and `.venv-cal`;
2. prepend those three site-packages directories to `PYTHONPATH` before invoking the frozen successor chain;
3. preserve RC3 component logs around predecessor output-directory recreation;
4. copy the predecessor evidence tree into an RC3-named artifact and bind it to the RC3 manifest.

This makes a system interpreter reached through symlink dereference see exactly the packages already installed and independently exercised by the passing component suites. It does not alter import precedence for the checked-out source trees, which remain explicitly pinned.

## Stop rule

If RC3 reaches a scientific seam, preserve that result even if red. No production component may be repaired from inside this campaign.
