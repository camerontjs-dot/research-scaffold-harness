# Local Agent Brief — CAL Provenance RC1

Execute the prepared provenance run series in:

`research/cal_pipeline_provenance_run_series_rc1/`

Read `RUN-SERIES.json` and `README.md` first. Treat their exact Git/release identities as frozen authority for this run.

## Objective

Run the five prepared cases with the pinned CAL Pipeline machinery while adding only observational provenance capture:

1. exact historical first-genuine B-side replay, if its frozen local bytes are recoverable;
2. Health Canada Ozempic full-pipeline case;
3. Rimebridge simple-support full-pipeline case;
4. Amberbraid temporal-supersession full-pipeline case;
5. Wick missing-decisive full-pipeline case.

Do not change retrieval, Gate, CAL, Contract C2, Decision, or policy behavior to improve outcomes.

## Execution boundary

Use disposable worktrees/checkouts at the exact pinned commits. Preserve native outputs exactly.

For each full run:

`Gate V1 -> Contract A -> EB 10/3 -> Contract B 1.2 -> CAL -> C2 -> Decision Engine -> Contract D`

Emit stage attestations using the candidate schema, retain every reconstruction-required artifact as bytes, and seal one candidate RunManifest.

Use the supplied helpers for benchmark packet materialization, deterministic directory snapshots, attestation/manifest sealing, and later reconstruction verification.

Benchmark gold is forbidden from the causal path. Do not inspect/use it until terminal outputs for that case are frozen.

## Most important provenance rule

Classify inputs truthfully:

- `causal_input`
- `authority_input`
- `compatibility_input`
- `observed_context`
- `diagnostic_input`

Do not upgrade something merely visible to the apparatus into causal or authority state.

## Historical replay

Locate the exact local frozen record using the identities in `RUN-SERIES.json`.

If exact historical bytes cannot be recovered, stop only that case as:

`BLOCKED_HISTORICAL_BYTES_UNAVAILABLE`

Do not rebuild substitute packets.

## Stop point

After each run has a sealed `RUN-MANIFEST.candidate.json`, report its digest in `CANDIDATE-ROOT.txt`, but do **not** treat it as trusted.

The series stops at:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

Do not perform the final context-free reconstruction using a self-selected root.

## Report back

Return:

- exact run directory for every case;
- exact checkout SHA for every component;
- terminal state of every stage;
- identities/hashes for native outputs and A/B/C2/D;
- each candidate manifest SHA-256;
- retention verification result;
- any deviation, missing byte, failed attestation, or unexpected semantic result;
- confirmation that no release/promotion/authorization occurred.

Preserve failures and awkward results. Do not repair them inside this run series.
