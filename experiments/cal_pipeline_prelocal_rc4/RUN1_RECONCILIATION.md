# CAL Pipeline pre-local pressure RC4 — Run 1 reconciliation

## Preserved execution

- workflow run: `35052465191`
- job: `104655609665`
- harness head: `28efb4489f5d78be94371a092b967ca2fc66dc89`
- artifact: none; `actions/upload-artifact` rejected Evidence Bundler filenames containing `:` after the scientific run completed
- scientific classification: `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY`

## Observed component evidence

Every independently selected component pressure suite passed:

- ClaimGate exact qualification runbook: `34 passed`, `14 passed`, Ruff PASS;
- Evidence Bundler Contract B integration boundary: `11 passed, 1 skipped`;
- current CAL focused integration/semantic pressure: `38 passed`;
- Contract C2 validator: `9 passed`;
- Decision C2 hostile-control suite: PASS, including stale C2 hash, wrong Contract B, target substitution, wrong C2 authority, strict C1/C2 cross-ingress rejection, replay mismatch, non-deciding safety, and no downgrade;
- Contract E RC3 target-cardinality successor: `65` asserted controls PASS.

The corrected cross-repository successor also completed successfully. The workflow recorded all seven surfaces, including `cross_chain`, as `success`.

## Scientific result

The exact two-lane pressure driver reached current CAL -> Contract C2 and returned:

`BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY`

This is the first pressure run in the campaign to reach a scientific authority boundary after the predecessor apparatus defects were removed.

The current CAL integration candidate advertises semantic implementation:

`847cc970642bb648dc994b929c2053b5c9d4648c`

The frozen Contract C2 producer-policy authority was qualified against CAL RC1:

`a902621e8baea3063dddd7f92ba975aade305464`

The pressure apparatus did not invent a resolver mapping for the new CAL subject. Structural Contract C2 materialization and downstream structural pressure were allowed to continue, but the scientific readiness gate stayed red.

## Evidence-preservation defect

After the scientific classification had been printed, `actions/upload-artifact` attempted to upload the raw 252-file evidence tree and failed because canonical Evidence Bundler passage filenames contain `:`. Example:

`passages/passage:0d57a00d6d9c9c2390b3b0a64fa32cdd.yaml`

This is an artifact-transport portability limitation, not a pipeline or evidence-integrity failure. A successor/final qualification campaign must package the evidence tree inside an archive before upload and record the archive digest.

## Classification

`SCIENTIFIC_BLOCKER_CONFIRMED_WITH_POSTRUN_ARTIFACT_PACKAGING_DEFECT`

The scientific blocker is current-CAL -> Contract-C2 producer authority requalification. The artifact packaging defect is separate and must not be used to weaken or reinterpret that blocker.

## Next justified work

1. requalify current CAL `847cc970...` as a Contract C2 producer against exact C2 head `b42c827...`;
2. establish a truthful successor policy-resolver authority if that requalification supports the same frozen semantic policy, rather than fabricating inheritance from `a902...`;
3. rerun the complete pressure chain with archived evidence transport;
4. only after that seam closes, widen to a bounded heterogeneous cohort before prototype freeze.
