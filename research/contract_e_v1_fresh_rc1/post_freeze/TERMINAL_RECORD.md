# Contract E v1 Fresh Independent Reproduction RC1 — Post-Freeze Terminal Record

- Execution branch: `research/contract-e-v1-fresh-independent-reproduction-rc1-20260902`
- Frozen implementation commit: `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`
- Frozen implementation blob: `42d2f43ec9222f2409d6066fd599327ce9ba5765`
- Freeze receipt commit: `32b81adc82384a437289c8b034000cbe31951d86`
- Evaluator final seal commit: `ee47670104776f627b7c337c6235dabafe03c874`
- Evaluator blob: `c07d3adbcc108dabe0daa6fc145a6d5dd51b3ec7`
- Hidden-cases blob: `f60f0315f42402a53378b5ce4ce55c1d5ab4e8f3`
- Candidate reference blob: `378cdb7835df3959c82a0fe98068b1434b1b68ec`
- Evaluator case count: `50`
- Normative exact matches: `48/50`
- Normative mismatch IDs: `NEG-SUPPORT-CANNOT-CONFER`, `NEG-STATE-ID`
- False-permit IDs: none
- False-reject IDs: none
- Exception IDs: none
- Preservation-failure IDs: none
- Diagnostic-shape-failure IDs: none
- Evaluator terminal exit code: `1`
- Evaluator scientific state: `FALSIFIED`
- Terminal scientific state: `FALSIFIED`
- Preserved `RESULTS.json` SHA-256: `5ca842b1b9f2e58bcf23081f93dbeae7161efda3dc0c88f74e99cd23ff8dbc7e`

## Contamination and deviations

Contamination: none observed during the post-freeze comparison.

Apparatus deviation: the host environment could not perform a network-backed full Git checkout of the sealed Apparatus repository. The comparison therefore ran from a minimal local layout containing only the authorized files required by `evaluate_fresh.py`, placed at the evaluator's expected paths. Before execution, `evaluate_fresh.py`, `hidden_cases.py`, the candidate `reference.py`, and the frozen `authority_e.py` were each verified byte-for-byte by both their specified Git blob IDs and SHA-256 values. No adapter, shim, field translation, coercion, fallback, diagnostic normalization, or modification of the frozen implementation/tests was introduced. The evaluator completed all 50 cases and generated a valid `RESULTS.json`; its nonzero exit was the sealed evaluator's specified consequence of the `FALSIFIED` state, not an infrastructure failure. The host also emitted a non-fatal `TERM environment variable not set` terminal warning after execution; it did not prevent or alter generation of the comparison result.
