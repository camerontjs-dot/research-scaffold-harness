# Contract D RC4 Phase A Comparison

This record was created after the independent freeze and pre-reveal freeze receipt, and before any Decision Engine producer reveal.

Frozen independent object:
- commit `79e94e7f3795472e31620cdbc4279dc399882ed5`
- tree `96f7d44fb2a1d82550377322bac7903f029bd91f`

## Reveal order and identity

All sources below were revealed only at `camerontjs-dot/apparatus-contracts@fd6923115116b0ced0f9feb5c005099d2e51ea88`, in the packet-mandated order. Every identity matched.

| Order | Path | Expected/observed blob | Result |
|---:|---|---|---|
| 1 | `research/contract-d-independent-authority-rc4/candidate/contract_d_core.py` | `589e3f1c31a21d305402e5750605d25be682a336` | MATCH |
| 2 | `research/contract-d-independent-authority-rc4/candidate/contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` | MATCH |
| 3 | `research/contract-d-independent-authority-rc4/candidate/contract_d_consume.py` | `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4` | MATCH |
| 4 | `research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py` | `8bece62cc9d4734af0f6ebee75bb39a0221ce397` | MATCH |

## Frozen reference tests

The four exact revealed reference files were materialized locally with their Git blob identities rechecked, together with only the already-authorized public `effect-registry.json`, valid/invalid fixture corpora, and conformance cases.

Command:

`cd /mnt/data/contract_d_phase_a/reference && python3 -m pytest -q tests/test_rc4.py`

Result: `27 passed in 0.08s`.

## Authority-relevant comparison

A post-reveal comparison harness, separate from and additive to the frozen independent object, exercised public valid/invalid classification, semantic identities, all public conformance cases, the seven required requested-operation/parameter discriminators, exact upstream/policy/target substitution, authority-bearing identity mutation, metadata/default identity invariance, finite-JSON byte ingress, decoded host values including cycles/shared acyclic containers, and representative canonical bytes.

Result: **72 authority-relevant comparisons agreed; 0 authority-relevant comparisons disagreed.**

| Authority area | Frozen independent vs frozen reference | Classification |
|---|---|---|
| Exact RC4 version / structural validation / unknowns | AGREE | authority agreement |
| Valid and invalid public fixture classification | AGREE | authority agreement |
| Effect registry type/version/parameter validation | AGREE | authority agreement |
| Stored safe-default normalization | AGREE | authority agreement |
| External omitted/empty requested params are unconstrained | AGREE | authority agreement |
| Explicit requested parameter constraint matching | AGREE | authority agreement |
| Requested-operation matching before CLEAR/HOLD outcome | AGREE | authority agreement |
| HOLD distinct from failure | AGREE | authority agreement |
| Upstream/policy/target exact applicability binding | AGREE | authority agreement |
| Replay/substitution rejection | AGREE | authority agreement |
| Finite JSON: invalid UTF-8, duplicate keys, non-finite tokens | AGREE | authority agreement |
| Decoded host values: non-JSON types/non-string keys/non-finite numbers | AGREE | authority agreement |
| Decoded host cycles fail closed | AGREE | authority agreement |
| Shared acyclic decoded containers remain valid | AGREE | authority agreement |
| Canonical bytes on tested finite values | AGREE exactly | authority agreement |
| Semantic authority projection and identity | AGREE exactly | authority agreement |
| Metadata/Authorization-only material excluded from Decision identity | AGREE | authority agreement |

No internal architecture, name choice, incidental error string, or return-envelope formatting was counted as an authority disagreement.

## Preserved prereveal-predicted external API edge divergences

Five auxiliary probes intentionally exercised values outside the public authority's declared external expectation shape/domain. They are preserved, not hidden:

1. An external expected-target mapping containing all required target bindings plus an unrelated extra key: independent API returns `cannot_establish`; reference comparator ignores the extra key and, when the listed bindings match, returns `candidate_for_authorization`.
2. Falsy non-mapping `effect_params` values `[]`, `""`, `0`, and `false`: independent API treats each as malformed/nonmatching (`not_applicable`); the reference's typed `dict | None` API is violated by these values, but at runtime its `expected.effect_params or {}` treats them as absent and can return `candidate_for_authorization`.

Classification: **specification underspecification / out-of-declared-API-domain variance**, not an authority-relevant disagreement for the RC4 Decision semantics tested by the packet. This classification is supported by the prereveal `PREDICTIONS.md`, which already recorded external expected-binding container-shape ambiguity and malformed requested-parameter handling before reference reveal. These probes do not change Decision validity, canonical bytes, semantic identity, or any outcome for a conforming external expectation containing the packet-specified binding fields and `effect_params` as `dict | None`.

If a future authority intends arbitrary extra keys or non-mapping effect-parameter values to be part of the conforming caller domain, it should specify that domain explicitly rather than infer it from this experiment.

## Phase A conclusion

Within the authority-relevant RC4 domain defined by the public authority and required prereveal discriminators, the frozen independent implementation reproduces the frozen apparatus reference. No authority-relevant disagreement remains from Phase A.

Phase A is durably captured here before Phase B producer reveal.
