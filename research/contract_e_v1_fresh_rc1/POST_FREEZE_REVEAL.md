# POST-FREEZE REVEAL AUTHORIZED — Contract E v1 Fresh Independent Reproduction RC1

The pre-freeze implementation has been externally verified as frozen and clean.

This file authorizes only the post-freeze comparison phase described below. It does not authorize modifying the frozen implementation or tests.

## 1. Verified fresh freeze

Repository: `camerontjs-dot/research-scaffold-harness`

Execution branch: `research/contract-e-v1-fresh-independent-reproduction-rc1-20260902`

Clean base: `548bfa81f65290eda15af658f647497679b840ef`

Frozen pre-freeze aperture head: `5a31c2c17dc4b63dd8235f98dd9a3e8e7921e98b`

Implementation/test freeze commit: `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`

Freeze receipt commit: `32b81adc82384a437289c8b034000cbe31951d86`

Frozen implementation:

- path: `research/contract_e_v1_fresh_rc1/authority_e.py`
- Git blob: `42d2f43ec9222f2409d6066fd599327ce9ba5765`
- SHA-256: `7f2c2359a4553edb8adcf9ef9cee6ce624a5e5a1cbd3f67f5ade71be53338ad7`

Frozen prereveal tests:

- path: `research/contract_e_v1_fresh_rc1/test_authority_e.py`
- Git blob: `99cf8901017480b1b55035c174c7667a9811cb73`
- SHA-256: `4a5b430b6194dd970b9d830674dc200f8fd98cb48deeb92c1168c29de56bbe32`
- recorded result: `PASS: 25 tests ran; OK; exit code 0`

Contamination status: `CLEAN_PRE_FREEZE_APERTURE`.

External verification confirmed that `32b81adc82384a437289c8b034000cbe31951d86` is exactly one metadata commit after the freeze and adds only `FREEZE_RECEIPT.json`; the implementation and test Git blobs at the receipt head remain the frozen blobs above.

## 2. Immutable post-freeze rule

From this point forward, do not edit, replace, regenerate, repair, or reinterpret `authority_e.py` or `test_authority_e.py` in response to evaluator behavior.

Any disagreement with the sealed evaluator is evidence. A repaired implementation would require a separately named successor reproduction and cannot be counted as this RC1 run.

## 3. Sealed evaluator authority

The evaluator was qualified and sealed before any fresh implementation existed.

Repository: `camerontjs-dot/apparatus-contracts`

Exact final evaluator seal commit:

`ee47670104776f627b7c337c6235dabafe03c874`

Final seal receipt:

`sealed/contract-e-v1-fresh-rc1/qualification/FINAL_SEAL_RECEIPT.json`

Sealed evaluator files at that exact commit:

- `sealed/contract-e-v1-fresh-rc1/evaluate_fresh.py`
  - Git blob: `c07d3adbcc108dabe0daa6fc145a6d5dd51b3ec7`
  - SHA-256: `4d91cddba1861d653c03c86b083aabb9c8274cb8bd83b854a49c796fb488ab36`
- `sealed/contract-e-v1-fresh-rc1/hidden_cases.py`
  - Git blob: `f60f0315f42402a53378b5ce4ce55c1d5ab4e8f3`
  - SHA-256: `6340670f01844893d89a8df6c5a6150e53c60a0ed63b9dc8e5e3c6e59f39fc31`
- `sealed/contract-e-v1-fresh-rc1/qualification/QUALIFICATION-CONTRACT.md`
  - Git blob: `3c945580e53d28f8eff1afd1de0737542ba75514`
  - SHA-256: `64fb5338329747b5e617027bf0b81654fbcbf43f592aa4b6f7e7acfd8f10edac`

Frozen candidate reference used by that evaluator:

- candidate freeze commit: `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`
- `docs/research/contract-e/v1-closure-20260902/candidate/reference.py`
- Git blob: `378cdb7835df3959c82a0fe98068b1434b1b68ec`
- SHA-256: `2b9ddbc5f6e51fffedcca1bcc33983113dbff995a476afe0608d7bf1dc58b643`

The final seal records:

- hidden cases: 50;
- reference normative exact matches: 50/50;
- diagnostic-content invariance: supported;
- weak controls caught: 7/7;
- qualification failures: none;
- `fresh_implementation_existed_at_seal=false`.

Diagnostic string content is intentionally non-normative. The evaluator compares the sealed normative receipt projection and requires diagnostic shape, not exact diagnostic wording.

## 4. Authorized reveal aperture

You may now inspect only the exact sealed evaluator/candidate files required to execute and understand the comparison at the commits named above, plus your own already-frozen implementation, tests, and freeze receipt.

Do not use broader Contract E history or unrelated project context to reinterpret your frozen implementation before comparison.

The purpose of reveal is comparison, not repair.

## 5. Required comparison

Execute the exact sealed `evaluate_fresh.py` from `ee47670104776f627b7c337c6235dabafe03c874` against the frozen `authority_e.py` blob `42d2f43ec9222f2409d6066fd599327ce9ba5765` from freeze commit `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`.

The evaluator requires the fresh implementation to expose:

`evaluate(authority_state: dict, request: dict) -> dict`

Do not insert adapters, field renames, coercions, fallback defaults, reason normalization, cardinality repair, semantic shims, or compatibility patches between the frozen implementation and evaluator.

Run the evaluator in an exact checkout of the sealed Apparatus commit so its frozen reference path resolves within that checkout.

Preserve the evaluator-generated `RESULTS.json` verbatim.

## 6. Required post-freeze evidence record

After comparison, create only post-freeze evidence under:

`research/contract_e_v1_fresh_rc1/post_freeze/`

At minimum preserve:

- `RESULTS.json` exactly as generated by the sealed evaluator;
- `TERMINAL_RECORD.md` stating exact evaluator seal, exact frozen implementation commit/blob, result counts, mismatching case IDs if any, contamination/deviation status, and terminal scientific state.

Do not alter the frozen implementation/test files.

Terminal scientific state for this reproduction must follow the sealed evaluator result:

- `SUPPORTED` only if the sealed evaluator returns its supported state with no normative mismatches, exceptions, preservation failures, or diagnostic-shape failures;
- otherwise `FALSIFIED`;
- use `INCONCLUSIVE` only for an apparatus/contamination failure that prevents a valid comparison from occurring.

A narrow disagreement must remain a disagreement. Do not relabel a sealed-gate failure as a pass merely because safety direction agrees.

## 7. Required return

Return only a compact post-freeze comparison record containing:

- execution branch;
- frozen implementation commit/blob;
- freeze receipt commit;
- evaluator final seal commit;
- evaluator case count;
- normative exact matches;
- normative mismatch IDs;
- false-permit IDs;
- false-reject IDs;
- exception IDs;
- preservation-failure IDs;
- diagnostic-shape-failure IDs;
- terminal scientific state;
- exact commit(s) preserving `RESULTS.json` and `TERMINAL_RECORD.md`;
- any post-freeze apparatus deviation or contamination.

Then stop.

Do not modify the frozen implementation after reporting the result. Do not promote Contract E, create a production tag/release, or reinterpret a failed comparison as production authorization.