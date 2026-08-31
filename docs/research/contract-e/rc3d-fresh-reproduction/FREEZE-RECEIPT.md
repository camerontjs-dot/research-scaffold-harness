# FREEZE RECEIPT

## Provider/Model Identity
- **Model**: Gemini 3.1 Pro (High)
- **Agent Environment**: Antigravity

## Version Control Hashes
- **Clean Base SHA**: `548bfa81f65290eda15af658f647497679b840ef`
- **Clean Base Tree**: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- **Input-Aperture Commit**: `805579a17c4888bd490fbebc0a2532806f9a3366`
- **Input-Aperture Tree**: `09e8a4aa1d24b44697838795f193bcc691c0d1d5`

## Public Blobs
- `SPEC-CANDIDATE.json`: `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json`: `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json`: `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `BASIS-BINDING-SPEC.json`: `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- `RC3C-SPEC.json`: `f05feac88128fd693cca2fb25a0b2951654377eb`
- `RC3D-INTERFACE-SPEC.json`: `61f46b09d391e7da4aed2491e428ec2ed226fe93`

## Preregistration
- **Commit**: `68c50b3230369d9ddd5dc6df371ce78ae8cc8738`
- **Tree**: `a4c8cf118c56199af7ec8a156dd35acba3afcba8`
- **Blob** (`PREREGISTRATION.md`): `3c2cf28c7a323d900a0bdcef4460460c4cbefab6`

## Implementation & Tests
- **Commit**: `76f63ed48538463487b7336b158745cdf63975d0`
- **Tree**: `87ccd265e4581d7c40a58439603382d81fb445d4`
- **Source Hash** (`consumer.py`): `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`
- **Tests Hash** (`test_rc3d.py`): `1102fc173086c45040da45125de4d138ee495765`

## Test Execution
- **Exact Command**: `python3 test_rc3d.py -v`
- **Counts**: Ran 42 tests in 0.001s
- **Results**: OK (All tests passed, zero authority-relevant false accepts, zero canonical false rejects)

## Recorded Ambiguities/Unknowns
- Native consumption requirements prohibit reliance on `requested_fields` alias mapping, so this was structurally enforced rather than delegated to semantic evaluation.
- `separately_reauthorized` behavior in propagation evaluations was assumed to fail closed if `explicit` is requested but no `fields` are passed or reauthorization is `False`.
- Malformed kind/mode rejections are elevated over inner payload structural rejections, avoiding processing malformed envelopes.

## Deviations
- None.

## Contamination Status
- **CLEAN**. No prior branches, hidden test material, project reasoning, or other external data retrieved or accessed. Pre-freeze aperture completely adhered to.

FRESH_RC3D_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL
