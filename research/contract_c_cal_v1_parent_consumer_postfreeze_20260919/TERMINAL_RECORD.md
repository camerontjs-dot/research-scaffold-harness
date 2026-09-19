# Contract C CAL V1 parent-binding independent consumer — post-freeze terminal record

## Terminal scientific disposition

**FALSIFIED_INDEPENDENT_CONSUMER_REAL_HANDOFF_REJECTION**

This result is terminal for the exact frozen clean-room consumer. It does **not** authorize repair of that consumer, production promotion, Contract C version assignment, canonical discovery, Decision Engine compatibility, release, Authorization, or execution.

A post-reveal source diagnostic localizes the failure to the **clean-room aperture specification**, which is not faithful to the frozen CAL V1 native result wire for `proposition.text_sha256`.

The appropriate higher-level classification is therefore:

**APERTURE_SPEC_NATIVE_TEXT_HASH_DOMAIN_MISMATCH**

The experiment falsifies this aperture/consumer conformance attempt. It does not falsify the producer-side RC2 + typed parent-recomposition binding result from Apparatus PR #118.

## Exact frozen consumer subject

- aperture commit: `52869e08f98ebaaf4acd31dd5955874f7fdaec81`
- candidate commit: `49251b3f8ea19f600249e8189254d257ccd6aa3e`
- freeze commit: `c91b9bb9a0b03522f1cd94da82544fa02e72f862`
- consumer blob: `3d36881673575adafc42e9a0f9b2b7fae2d5bf9d`
- prereveal-test blob: `1b89b9536106fa66568953d3ff5f8e3e850027b2`
- freeze-receipt blob: `c381f36f9d438468e2f8ec956f77317c3486f623`
- prereveal suite: **10 passed / 0 failed**
- recorded contamination: **NONE**
- network state during fresh implementation: **OFF**
- post-freeze consumer modification: **false**
- adapter used in comparison: **false**

## Exact producer/reveal subject

- Apparatus RC0 decisive head: `7138f6c1599b9b8f8c655f85c9eba0c264fb3b26`
- producer candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- Candidate A RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- frozen CAL V1: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- qualified CAL semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`
- CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- frozen Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- current-CAL resolver: `1d33e0612befcf8016816197c90c062373796df9`

## Preserved first post-freeze harness deviation

Run `35453984794`, job `105925925345`, reached all identity gates, reran the frozen prereveal suite 10/10 PASS, and ran the frozen CAL decomposition controls 27/27 PASS.

The comparison harness then attempted to serialize the deliberately malformed omitted-child specimen through the producer's validating canonical serializer. The producer correctly rejected the malformed specimen before it reached the frozen consumer.

No `COMPARISON_RESULTS.json` was produced.

Classification:

**POSTFREEZE_COMPARATOR_HARNESS_DEFECT**

Only the comparator's invalid-specimen serialization was changed. The frozen consumer, prereveal tests, freeze receipt, producer subject, authority set, positive cohort, and comparison criteria remained unchanged.

## Decisive post-freeze execution

- comparator-fix head: `b9b30d973a511a305ca4cf4a40196786b8b8f7b8`
- comparator blob: `6f808ecbb529de2e58ac7a882ed95a67acd4c411`
- workflow run: `35454041480`
- job: `105926077124`
- artifact: `10587234482`
- artifact ZIP digest: `sha256:5c8b3c4fd66e19ac22aba6fc57cac395dd5db58def48deee39fd2a577d3b7c20`
- frozen prereveal consumer suite: **10/10 PASS**
- frozen CAL decomposition controls: **27/27 PASS**

The comparison intentionally exits nonzero on a scientific falsifier, so the workflow is red.

## Exact positive result

Every exact real PIPE01–PIPE04 handoff was rejected by the frozen consumer at the same boundary:

`NATIVE_TEXT_HASH`

| Case | Expected parent | Consumer |
| --- | --- | --- |
| PIPE01 | `supported` | rejected: `NATIVE_TEXT_HASH` |
| PIPE02 | `contradicted` | rejected: `NATIVE_TEXT_HASH` |
| PIPE03 | `not_checkable` | rejected: `NATIVE_TEXT_HASH` |
| PIPE04 | `contradicted` | rejected: `NATIVE_TEXT_HASH` |

Exact producer whole-object authorities:

- PIPE01: `sha256:a0e2f77b48a9a9fe8347df345e5f112cfe76bde19cc82986c2efaccf90730524`
- PIPE02: `sha256:f2a1c54ea5e7eb9aaeca256d035247b79b563d3a4dbb19fd580362d2065a6e24`
- PIPE03: `sha256:bfad4513810c30ab7e17c2dd6779a04e19733c3e297a58374d646d7a912b7eff`
- PIPE04: `sha256:0e9f6e028685e5ed5e739e71cc78e88058aeb47734db284322240e2de8ca1304`

Positive failures: **4/4**.

False accepts recorded by the comparison: **0**.

The negative mutation results do not rescue the consumer. Many malformed cases terminate at the same baseline `NATIVE_TEXT_HASH` incompatibility, so they cannot be counted as independent evidence for downstream binding checks.

## Post-reveal diagnostic

The clean-room aperture says, in section 5 requirement 7:

> the native child result's `proposition.text_sha256` equals the declared child's exact tagged text SHA-256

It also specifies the child identity material as:

`"text_sha256": "sha256:<64 lowercase hex>"`

The frozen consumer implements that supplied rule: it requires native `proposition.text_sha256` to match `^sha256:[0-9a-f]{64}$`.

Frozen CAL V1 says something different.

At exact CAL freeze `e24e405f...`:

1. `TypedProposition.create(..., text_sha256=...)` requires `text_sha256` to match **64 lowercase hex characters**, without a `sha256:` prefix.
2. `result_record()` emits `context.proposition.text_sha256` directly as native `result.json -> proposition.text_sha256`.

Therefore the legitimate frozen CAL V1 native result carries the proposition text digest in the untagged 64-hex domain, while Contract A / the outer recomposition binding carries the tagged form.

The aperture collapsed those two hash representation domains into one tagged representation. The fresh consumer followed that aperture and consequently rejected every legitimate real native result before reaching the intended parent-binding comparison.

## Epistemic interpretation

Observed:

- exact frozen consumer independence controls held;
- exact frozen producer/CAL/EB authorities held;
- all four legitimate real handoffs were false-rejected;
- the common rejection was `NATIVE_TEXT_HASH`;
- the frozen aperture explicitly required tagged native text hashes;
- frozen CAL V1 explicitly emits the native proposition text hash untagged.

Supported inference:

- this clean-room aperture was not a faithful public specification of the frozen CAL V1 native wire;
- the frozen consumer's common failure is explained by that aperture mismatch without invoking a defect in the producer-side parent binding;
- the independent-consumer gate is **not established**.

Not established:

- that a correctly specified fresh independent consumer would pass;
- that RC2 + typed parent binding is production-ready;
- Contract C production versioning;
- Decision Engine support for this Contract C shape.

## Required next gate

Do not repair or reuse the frozen consumer.

Create a **new clean-room aperture revision** that explicitly distinguishes:

1. native CAL `result.json -> proposition.text_sha256`: untagged 64 lowercase hex;
2. Contract-A / parent-binding `text_sha256`: tagged `sha256:<64 lowercase hex>`;
3. the exact normalization rule connecting them where comparison is required.

Freeze that corrected specification before any new consumer sees the real handoffs.

Then run a **fresh independent consumer from scratch** against the corrected aperture, freeze it before reveal, and repeat the same exact real PIPE01–PIPE04 comparison and mutation/replay campaign.

Until that successor passes, Contract C promotion remains blocked.
