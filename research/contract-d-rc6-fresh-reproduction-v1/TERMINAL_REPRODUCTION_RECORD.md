# Contract D RC6 Fresh Independent Consumption Reproduction v1 — Terminal Reproduction Record

## Thread state

`TERMINAL`

## Primary research disposition

`SUPPORTED FOR PROMOTION`

This is a research disposition only. It does not itself authorize a production release, production merge, tag, Decision Engine behavior change, operational Authorization, or downstream execution.

## Frozen prereveal evidence

- freeze commit: `f5ce28cef76808e390e016d63dec3d50a28fbda2`
- freeze tree: `805c3b229922a605b16990a699ffa03f3a2e6250`
- durable receipt commit: `e1d436cd9813eefc84aec5129afa0bef4594ed72`
- frozen independent implementation blob: `26058b7901347c6e7e3c207de2195a0ab529aa08`
- frozen independent test blob: `c4f733088fe25f482b07b24fe2685d7a524d1e20`
- prereveal test-log blob: `f4f1864e78166d8c0ec58ed0c2c90b2fa952c9ce`
- prereveal result: **67 passed, 0 failed, 67 total**
- preserved earlier prereveal run: **66 passed, 1 failed, 67 total**, corrected before freeze solely from public authority as recorded by the frozen receipt

The frozen implementation/test blobs were not changed after reveal.

## Revealed RC6 reference identities

Reference commit: `bb656fc50806c344fda1ddeaf08a9878f5cb460e`  
Candidate tree: `5151e2c30235784d4ae594db454ac24c1e3868b4`

- `RC6_CHANGE_NOTE.md`: `2eeb6e719ef4c5efac3adad0c3edc8d43454e364`
- `contract_d_core.py`: `473f3c65ef838f9d4f03ee01b497e7263a6d2da7`
- `contract_d_validate.py`: `8cc6d81515d7c5b0a86df163a38d1c12931f897f`
- `contract_d_consume.py`: `42536aaac5acd953f150a87891a70e9c194b7aaf`
- `requirements.txt`: `9bc3e4b733b2963a79a756a696eeafc92b532634`
- tests tree: `520e13eb378e0a23736fb3c3b102ed8a1e8de377`
- `test_rc6_expectation_hardening.py`: `9d02b269fe83ba79ded16d154f59fed0267e87c5`
- `test_rc6_jcs_vectors.py`: `35a01f918fc4b993e5367d7878e5b11a90bcd428`
- `test_rc6_normalized_effect_shape.py`: `e16d12efcc847bdab9754c7192c3614bda015993`
- `test_rc6_regression.py`: `1f8470b4f6efea5bec3260cd575a626e8242c045`

## Reference verification

Pinned dependency: `rfc8785==0.1.4`.

Because direct package installation was unavailable in the local execution environment, the exact `trailofbits/rfc8785.py@v0.1.4` source was used, resolving to commit `4d9b161f6054301d98d0566e813d020fb019ee10`; material source blobs matched `5a1f9d919643fa3bcaa0999ea66d9c535568c42a` and `3137d3326b98938affadb1be711ee411eb2ab86e`.

Runtime: Python `3.13.5`, pytest `9.0.2`. Reference result: **71 passed, 0 failed, 0 skipped**.

One non-material reference-test input defect was preserved: the duplicate-key regression test embeds duplicate `0.3.0-rc5` values in an RC6 suite. Duplicate-key rejection happens before version interpretation, so the intended test still passes. This is recorded as an `EVALUATOR_OR_HARNESS_DEFECT`, not as Contract D authority evidence.

## Differential method

A post-reveal harness invoked the frozen JavaScript implementation and frozen Python reference independently. Inputs were described once as bounded machine-readable case descriptors. Each driver separately constructed the relevant programmatic-host or JSON-byte-ingress value and returned normalized observations. Exact canonical bytes were compared in hexadecimal where applicable; semantic identities were compared as exact `decision:sha256:` values. The exact 25,138-byte orchestrator is preserved compressed as `POST_REVEAL_DIFFERENTIAL_HARNESS/run_differential.py.gz` because the connector text-transfer surface could not safely carry it uncompressed; its uncompressed SHA-256 is `ead48542941734a21f083ca8af24101b22e76de885dd8342302729cee301aae8`.

Coverage includes the required version/structure, completed/failed state rules, finite JSON and controlled failure boundaries, byte ingress, cycles/shared structures, depth 128, unsafe and canonical large integers, exponent and negative-zero behavior, RFC 8785 number edges, UTF-16 property ordering, all three registered effects, RC6 total normalized effect shape, external requested-parameter semantics, exact applicability bindings, CLEAR/HOLD/failed outcomes, malformed expectations, replay/substitution cases, and the Decision/Authorization firewall.

## Differential result

Total comparisons: **166**

Machine-readable result manifest content SHA-256: `e25776f270557beefe9b87a9e1e512ce7a8abaf561474210ffe09be35488225d`. Its nine manifest-hashed JSON chunks are preserved in deterministic `DIFFERENTIAL_RESULTS.tar.gz` (SHA-256 `032adea622510a506dde2d55229299c1ee4df568721f5ca104b21d9f32ce8368`).

Classification counts:

- `AUTHORITY_RELEVANT_AGREEMENT`: 159
- `AUTHORITY_RELEVANT_DISAGREEMENT`: 0
- `PUBLIC_AUTHORITY_AMBIGUITY`: 0
- `INDEPENDENT_IMPLEMENTATION_DEFECT`: 0
- `REFERENCE_IMPLEMENTATION_DEFECT`: 0
- `NON_AUTHORITY_DIFFERENCE`: 7
- `EVALUATOR_OR_HARNESS_DEFECT`: 0
- `ENVIRONMENT_OR_DEPENDENCY_FAILURE`: 0
- `INCONCLUSIVE`: 0

Authority-relevant disagreements: **none**.

Public-authority ambiguities: **none**.

Non-authority differences:

- `u2.host.cross_language_float_2p53`
- `u2.host.cross_language_float_1e30`
- `u1.cycle`
- `u1.duplicate`
- `u1.target_hash`
- `u1.missing_effect`
- `u1.invalid_effect_param`

The five `u1.*` differences are internal error-code naming only. The two `u2.host.cross_language_float_*` probes compare a JavaScript programmatic `Number` that is integer-valued outside the safe range with a Python programmatic `float` carrying the same binary64 value. The JavaScript frozen implementation rejects those values under its single-number-type host mapping; the Python reference accepts them as `float`. The public rule constrains programmatically supplied **host integer values** to the safe range and separately permits finite binary64/JCS values. Python `int` probes at the same unsafe magnitudes are rejected by the reference exactly as the JavaScript integer-valued Number probes are rejected by the independent implementation. Therefore the cross-language float probes are a host-type-surface difference, not a Decision-authority disagreement.

## U1 / U2 / U3 scoring

### U1 — internal validator error labels

**Resolved: NON_AUTHORITY_DIFFERENCE only.**

Observed label differences include:

- cycle: independent `cyclic_json`; reference `non_json_value`;
- duplicate key: independent `duplicate_key`; reference `duplicate_json_key`;
- malformed target hash: independent `invalid_target_hash`; reference `invalid_target_content_sha256`;
- missing completed effect: independent `missing_effect`; reference `missing_field`;
- invalid declared effect parameter value: independent `invalid_effect_parameter`; reference `invalid_effect_parameter_value`.

In every probe, acceptance/rejection and authority-bearing outcomes agree. Public RC6/RC5 authority does not specify these internal labels. Normatively named controlled cases, including `json_depth_exceeded`, `non_interoperable_integer`, and external `invalid_expectation`, agree where required.

### U2 — JavaScript host-number versus JSON-byte-ingress mapping

**Resolved: independent interpretation is consistent with the public RC6/RC5 authority; two cross-language host-type probes are NON_AUTHORITY_DIFFERENCE.**

Observed:

- safe programmatic host integer accepted;
- programmatic host integers outside the safe range rejected by both implementations when exercised through each runtime's integer surface;
- exact out-of-safe-range integer-form byte tokens accepted;
- canonical shortest-roundtrip integer-form byte tokens above the safe host range accepted and stable;
- precision-losing noncanonical integer spellings rejected, including neighbors around `2**53`, `1e20`, and the RC6/RFC-8785 `2**68` region;
- exponent-form byte tokens that decode to integer-valued binary64 values are accepted and canonicalized;
- registry defaults are not injected into external requested parameters.

The Python reference additionally accepts programmatic Python `float(2**53)` and `float(1e30)`, while the JavaScript implementation rejects the corresponding integer-valued JavaScript `Number` values. This does not create a same-host-type contradiction: Python `float` is not a host integer type, while JavaScript has one binary64 `Number` type. The authority-level byte-ingress behavior agrees.

### U3 — JCS numeric coverage

**Resolved: bounded differential agreement.**

A deterministic 24-case RFC-8785-relevant finite binary64 edge set was exercised through JSON-byte ingress, including ±0, minimum subnormals, maximum finite values, ±2**53, the `2**68` canonical sample, 1e23 boundary neighbors, 1e21/fixed-format boundaries, 1e-6 boundaries, repeating-decimal precision edges, and representative negative/large precision cases. Exact canonical bytes agreed for all 24 cases. No unbounded fuzzing was performed or required by an observed discrepancy.

## Observed facts

1. Freeze identity verification succeeded before reference reveal.
2. Frozen independent tests were 67/67 prereveal and reran 67/67 post-reveal without modification.
3. Frozen reference tests were 71/71 in the recorded isolated local environment using exact pinned-version source.
4. 166 post-reveal comparisons produced 159 `AUTHORITY_RELEVANT_AGREEMENT`, 7 `NON_AUTHORITY_DIFFERENCE`, and zero entries in every authority-disagreement, ambiguity, implementation-defect, environment/dependency-failure, or inconclusive classification.
5. The RC6 clarification is independently recovered: `knowledge.cite_as_evidence@1` and `task.dispatch@1` always normalize to exactly `type`, `version`, `params`, with `params: {}`; omission and explicit `{}` have identical semantic identity.
6. `knowledge.add_verified_tag@1` preserves the safe default `scope: "claim"`; omitted params, `{}`, omitted scope, and explicit claim are semantically identical; explicit `scope: "object"` is distinct.
7. External requested params remain unconstrained when absent or `{}`; defaults are not injected into the external request.
8. Exact upstream/policy/target/requested-operation/requested-parameter binding, HOLD replay controls, metadata identity invariance, and the Authorization firewall agree.

## Bounded inference

Within the exact RC6 public authority, frozen fixtures/conformance cases, frozen independent implementation, frozen reference implementation/tests, and the bounded post-reveal probes executed here, the public Contract D RC6 consumption authority is independently recoverable by this fresh reproduction. The remaining observed implementation differences do not alter acceptance, applicability, normalized Decision semantics, canonical bytes at the authority boundary, semantic identity, or consumer outcome.

## Residual uncertainty

- No unbounded fuzzing or exhaustive IEEE-754 state-space search was performed.
- Host-language API surfaces can differ because Python distinguishes `int` and `float` while JavaScript uses `Number`; the tested authority-bearing byte-ingress and host-integer rules were consistent, but this record does not claim arbitrary language bindings are automatically equivalent.
- Process-level resource exhaustion outside the explicit depth/value controls was not tested.
- The reference dependency was executed from exact release-tag source rather than an installed wheel because package installation was unavailable; source identity/version was verified and the full reference suite passed.

None of these residuals creates a live public-authority ambiguity in the tested RC6 claim.

## What is not established

This result does not establish Contract D `1.0.0` production readiness by itself; actor identity; approval; delegation; autonomy semantics; trust/profile semantics; operational Authorization; execution permission; execution occurrence; execution receipts; correctness of upstream epistemic judgments; arbitrary future Contract D versions; arbitrary producers or consumers; arbitrary transports; or unlimited resource behavior.

## Research disposition

`SUPPORTED FOR PROMOTION`

Meaning: the bounded research claim of independent recoverability of the frozen public Contract D RC6 authority is supported by this reproduction. This disposition is research evidence only.

## Exact next action

Do not perform production promotion in this thread. Hand this immutable terminal record and its machine-readable differential evidence to the separate Contract D promotion/governance decision process. Any production merge, release, tag, Decision Engine mutation, or operational Authorization requires separate authority.
