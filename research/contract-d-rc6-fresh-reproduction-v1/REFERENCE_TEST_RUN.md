# Contract D RC6 Reference Test / Run Record

## Reference identities

Reference commit: `bb656fc50806c344fda1ddeaf08a9878f5cb460e`  
Candidate subtree: `5151e2c30235784d4ae594db454ac24c1e3868b4`  
Reference tests tree: `520e13eb378e0a23736fb3c3b102ed8a1e8de377`

Reference implementation blobs:

- `contract_d_core.py`: `473f3c65ef838f9d4f03ee01b497e7263a6d2da7`
- `contract_d_validate.py`: `8cc6d81515d7c5b0a86df163a38d1c12931f897f`
- `contract_d_consume.py`: `42536aaac5acd953f150a87891a70e9c194b7aaf`
- `requirements.txt`: `9bc3e4b733b2963a79a756a696eeafc92b532634`

Reference test blobs:

- `test_rc6_expectation_hardening.py`: `9d02b269fe83ba79ded16d154f59fed0267e87c5`
- `test_rc6_jcs_vectors.py`: `35a01f918fc4b993e5367d7878e5b11a90bcd428`
- `test_rc6_normalized_effect_shape.py`: `e16d12efcc847bdab9754c7192c3614bda015993`
- `test_rc6_regression.py`: `1f8470b4f6efea5bec3260cd575a626e8242c045`

All reconstructed local reference files were checked with `git hash-object` and matched these identities exactly before execution.

## Runtime / dependency environment

- Python: `3.13.5`
- pytest: `9.0.2`
- Node present for the independent side: `v22.16.0`
- pinned requirement: `rfc8785==0.1.4`
- normal package installation/cache: unavailable in the execution container
- exact dependency source used: `trailofbits/rfc8785.py@v0.1.4`, tag commit `4d9b161f6054301d98d0566e813d020fb019ee10`
- dependency source blobs used: `5a1f9d919643fa3bcaa0999ea66d9c535568c42a` and `3137d3326b98938affadb1be711ee411eb2ab86e`

No alternate canonicalization library or version was substituted.

## Reference suite execution

Command equivalent:

```text
PYTHONPATH=<reference>/vendor pytest -q <reference>/tests
```

Observed result:

```text
.......................................................................  [100%]
71 passed in 0.15s
exit_status=0
```

- failed: 0
- skipped: 0
- test warnings: 0 observed
- dependency/runtime failures affecting reference behavior: 0

Local full-run log SHA-256: `f3259c307f424824445b3aa79ddc7333e66aa3b69aed24d6d20076445c4d0e95`.

The outer shell/tool environment emitted `TERM environment variable not set` after pytest completed. It was not a pytest warning and did not affect exit status.

## Frozen independent rerun verification

The frozen evidence files were reconstituted byte-for-byte and verified before execution:

- implementation: `26058b7901347c6e7e3c207de2195a0ab529aa08`
- tests: `c4f733088fe25f482b07b24fe2685d7a524d1e20`

Post-reveal rerun result, without modification:

```text
67 passed, 0 failed, 67 total
exit_status=0
```

This rerun does not replace the frozen prereveal evidence; it only verifies that the frozen objects still execute consistently in Node `v22.16.0`. Local rerun-log SHA-256: `4972ae93862497df252be59b1edab8f8699cbeddba49432b005774dfbd0927cb`.

## Reference-test defect preserved

`test_rc6_regression.py` contains a duplicate-key parser test whose raw duplicate `contract_d_version` values are both the old string `0.3.0-rc5`. That is a reference-test input defect in an RC6 suite. The duplicate-key hook rejects the input before Contract D version validation, so the test still exercises and passes its stated duplicate-key behavior. Classification: `EVALUATOR_OR_HARNESS_DEFECT`, non-authority-relevant, with no observed effect on the 71-test result or differential outcome.
