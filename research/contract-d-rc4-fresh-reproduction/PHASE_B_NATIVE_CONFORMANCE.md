# Contract D RC4 Phase B Native Producer Conformance

This record is additive post-reveal machinery. No frozen independent implementation, test, case, weak-consumer, access-log, or prediction file was modified.

## Producer reveal

- repository: `camerontjs-dot/decision-engine`
- commit: `e768cedc891fa0d3280dc55f54b578d149019555`
- path: `research/contract-d-rc4-producer-conformance/emit.mjs`
- expected blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- observed blob: `96d7856493c498080e3e34366654aeebd14db9f4`
- identity: MATCH

Phase B reveal occurred only after `PHASE_A_REFERENCE_COMPARISON.md` had been durably committed.

## Unchanged producer execution

The revealed `emit.mjs` was written byte-for-byte to the local Phase B staging path. Local `git hash-object emit.mjs` returned:

```text
96d7856493c498080e3e34366654aeebd14db9f4
```

Execution command:

```text
node emit.mjs > producer_first_stdout.json
```

Result:

```text
producer_exit=0
producer_first_stdout.json sha256=48c169ce0d5d3eb2a75a473f1594864d07b67ad530e22761315d24759f1d66ca
```

The first stdout is preserved additively as `PHASE_B_PRODUCER_FIRST_STDOUT.json`.

## Decisive native path

The producer's top-level `decisions` members were selected by case name and supplied **as emitted** to the frozen independent consumer from freeze commit `a34fcccf15b752f0870099d18ee8370aae591b04`, implementation blob `5c7ac5a4c821a76d6520412d2dade0cfb0c19021`.

No translation, compatibility adapter, shape normalizer, field rename, version bridge, effect mapper, or default injector was used.

Expected upstream/policy/target/request context came from the prereveal frozen public authority values, not from a repaired or post-reveal schema.

Decisive path:

```text
Decision Engine -> emitted RC4 Decision object -> frozen independent consumer
```

## First native results

| Producer class | Frozen independent outcome | Expected | Direct object | Translation required |
|---|---|---|---|---|
| source-audit CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | yes | no |
| citation-use CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | yes | no |
| task-dispatch CLEAR | `candidate_for_authorization` | `candidate_for_authorization` | yes | no |
| completed HOLD | `hold` | `hold` | yes | no |
| evaluation failure | `evaluation_failed` | `evaluation_failed` | yes | no |

All five producer objects validated under the frozen independent RC4 implementation.

First-result semantic identities:

- source-audit CLEAR: `decision:sha256:9f8a43651f0de365a26161f7951493f9e01370dcca46b6e24ea80d1a9636152f`
- citation-use CLEAR: `decision:sha256:a7593e3dff38d841b99c6ce7a7d33991900b69522ad380f8c1043148d15ee200`
- task-dispatch CLEAR: `decision:sha256:2c57de9b2e78dc4de82455dbd74d0e4bd61bb5c6a45c7d5c0edf89d19b4d3004`
- completed HOLD: `decision:sha256:d6741bea58ad3392b9204aa7498cd9f890976bf32e1b86b71a5e194b640b8716`
- evaluation failure: `decision:sha256:bd71b6852f3166aa8a7994cde913b1558a53cd049685cab3a1863d2f15c239f6`

The machine-readable first native result is preserved as `PHASE_B_NATIVE_FIRST_RESULT.json`; its local SHA-256 at creation was `7ccfa3d5fb21bff153882c1395e4812ee92ab9c1edb1525a33713f69838be055`.

## Diagnostic translation

No diagnostic translation was required or performed.

## Phase B conclusion

Native cross-repository conformance **succeeded** for all three CLEAR classes, completed HOLD, and evaluation failure. The frozen Decision Engine RC4 objects are natively consumable by the frozen independent consumer without a bespoke adapter.
