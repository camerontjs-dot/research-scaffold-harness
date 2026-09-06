# RC5 POST-FREEZE REVEAL TASK

POST-FREEZE REVEAL AUTHORIZED.

The independent implementation and prereveal tests are already frozen. Do not edit, repair, regenerate, reinterpret, or replace them from this point onward.

## Frozen independent subject

Repository: `camerontjs-dot/research-scaffold-harness`

Pre-reveal freeze commit:
`e2e79fc6c50b2acb00463d36065aa7d7e0727fa8`

Implementation source commit:
`6ea6793b43a210656ac0b4e92dae40aa23322137`

Frozen implementation blob:
`83bf96ebdeacd3abf276e665374dea172594ce7c`

Frozen prereveal test blob:
`a25ff8b40d1181cf2fb872dd463df6fb51cf0d2c`

Frozen dependency blob:
`ef66329f0538d1bc63c4ae733a1502b4a93d200b`

Frozen contamination declaration blob:
`a72811e29328fefcea70950b4374b0af91dbe26d`

Freeze receipt blob:
`f44595998d5f6b8333f55eec5372171d0a3b78ee`

Prereveal result: 22/22 tests passed. Contamination state: `CLEAN_PRE_FREEZE`.

Before comparison, verify that these exact frozen blobs remain unchanged. If any frozen implementation/test/dependency/contamination byte changed after the pre-reveal freeze, stop with `INCONCLUSIVE_APERTURE_CONTAMINATION`.

## Newly authorized reveal aperture

You may now read exactly the files under:

`experiments/cal-rc5-independent-verifier/POST_FREEZE_REVEAL/`

on this post-reveal branch.

Do not use this authorization to inspect unrelated repository history, prior CAL implementations, RC3/RC4 code, other independent implementations, PR narratives, issues, or other project material.

The reveal directory contains:

- `SEALED-EVALUATOR-MANIFEST.json`
- `EVALUATOR-PREFLIGHT.json`
- `SEALED-PACKET/packet.gzip.part-000`
- `SEALED-PACKET/packet.gzip.part-001`
- `SEALED-PACKET/packet.gzip.part-002`

These bytes are copied by Git object identity from the supervisor-sealed evaluator and were frozen before the independent candidate existed.

## Sealed packet reconstruction

1. Verify every chunk size, SHA-256, and Git blob identity against `SEALED-EVALUATOR-MANIFEST.json`.
2. Concatenate the three chunk files in numeric order with no separator.
3. Verify the concatenated gzip byte length and SHA-256 from the manifest.
4. Gzip-decompress once.
5. Verify the uncompressed byte length and SHA-256 from the manifest.
6. Decode the result as UTF-8 JSON and reject duplicate JSON keys while parsing.

If any identity/hash/length/parse check fails, stop `INCONCLUSIVE_EVALUATOR_INVALID`. Do not improvise a repaired evaluator packet.

## Comparison

The uncompressed sealed JSON packet is the post-freeze evaluator authority. Treat it as evaluator data, not as permission to change the candidate.

Create only post-freeze comparison machinery and result records. Do not edit the frozen verifier or its prereveal tests.

Execute every sealed evaluator case against the frozen verifier using the case's supplied operation selector and supplied raw semantic/receipt/key/policy inputs exactly as encoded. Do not introduce aliases, normalization, repair, field renames, producer assumptions, or semantic transformations not required by the frozen public SPEC.

Compare the candidate result to the sealed expected result exactly, including typed refusal code where the packet specifies one. Preserve every disagreement and exception.

Run and report the evaluator controls separately:

1. **Positive control:** the known-good receipt pair must be accepted by the frozen candidate.
2. **Weak scoped-authority control:** each cryptographically valid wrong-role receipt must be accepted by the sealed weak unscoped rule and rejected by the candidate because the signer lacks authority for that receipt type/scope. If the weak control rejects for an incidental reason, or the signature is not actually valid, the scoped-authority discrimination is invalid and the experiment is `INCONCLUSIVE_EVALUATOR_INVALID`.
3. **Mutation sensitivity:** every security-relevant bound-field mutation represented by the sealed packet must change acceptance as required by the frozen specification.
4. **Representation invariance:** only transformations explicitly non-semantic in the frozen profile may preserve acceptance.
5. **Independent oracle review:** confirm the sealed expected results are derivable from `SPEC.md`, `RECEIPT-SCHEMA.json`, `TRUST-POLICY.json`, and `PUBLIC-KEYS.json`, rather than candidate behavior. Record any oracle disagreement as evaluator evidence and stop `INCONCLUSIVE_EVALUATOR_INVALID` if material.
6. **Unsupported/evidence-preservation case:** preserve the case containing two individually valid incompatible same-`claim_id` proposition bindings. Do not claim equivocation detection, uniqueness enforcement, or conflict resolution unless the frozen public specification explicitly establishes such a rule.

Re-run the exact frozen 22 prereveal tests after reveal only as an identity/regression check. A test failure after reveal does not authorize candidate repair.

## Primary falsifiers and scientific disposition

Use only these terminal dispositions:

- `SUPPORTED_WITH_BOUNDS`
- `FALSIFIED_INDEPENDENT_PORTABILITY`
- `FALSIFIED_SCOPED_ISSUER_AUTHORITY`
- `FALSIFIED_EXACT_BINDING`
- `INCONCLUSIVE_EVALUATOR_INVALID`
- `INCONCLUSIVE_APERTURE_CONTAMINATION`
- `BLOCKED`

Classify a decisive failure by the narrowest applicable preregistered falsifier:

- need for private/shared signing material, producer implementation, undocumented producer state, inability to reconstruct public signed bytes, or public-material minting capability -> `FALSIFIED_INDEPENDENT_PORTABILITY`;
- acceptance of a valid signature from a key unauthorized for that exact receipt type/scope, including cross-role substitution -> `FALSIFIED_SCOPED_ISSUER_AUTHORITY`;
- acceptance of stale exact semantic mutation or exact proposition/atom binding substitution -> `FALSIFIED_EXACT_BINDING`;
- evaluator/control/oracle defect that prevents valid discrimination -> `INCONCLUSIVE_EVALUATOR_INVALID`.

Do not repair the frozen candidate after a decisive falsifier.

`SUPPORTED_WITH_BOUNDS` requires the evaluator controls to be valid, all security-relevant hidden cases to agree with the frozen oracle, no candidate exception or unsafe acceptance, preserved exact-binding behavior, and no post-freeze modification of the frozen candidate/tests.

## Required durable outputs

Freeze post-reveal comparison-only artifacts to GitHub without modifying the frozen subject. At minimum preserve:

- comparison harness/source, if one is needed;
- exact packet identity/hash verification record;
- per-case observed versus expected result record;
- evaluator-control results;
- frozen-candidate identity recheck;
- prereveal-test rerun result;
- deviations/exceptions;
- `POST_FREEZE_RESULT.json` with one allowed scientific disposition;
- a terminal receipt containing the exact final comparison commit and all relevant blob/hash identities.

The strongest positive inference remains bounded to the RC5 experimental profile. Do not infer production cryptographic architecture, signer governance, PKI, lifecycle/revocation, anti-replay beyond tested context, equivocation detection, semantic truth, Contract C projection, Decision Engine policy, production integration, release, merge, or promotion authorization.

No production mutation, merge, promotion, tag, or release is authorized.
