# Terminal Record — Contract C 2.0 Promotion Consumer B Conformance RC0

Terminal disposition: **`SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE`**

Classification: Draft Research / production-promotion independent-consumer conformance evidence. This record does not authorize Contract C merge/release, canonical C2 discovery, Decision Engine production support, Contract E / Authorization, or execution.

## Exact independent subject

Frozen Consumer B subject:

`ba09743b28e57bc87dd1f315046ef79b93f24021`

Exact unchanged subject blobs:

- `candidate/consumer.py`: `1f0e64d22f11d7dbe620fef209852870e6b5203d`;
- `candidate/test_consumer.py`: `54e03ff388974fb3524b164c17b7af9f7cf9870c`;
- `candidate/FREEZE_RECEIPT.json`: `1f57979b23eb37d8611acfb58b288e4952eaa717`.

Original independent evidence remains intact:

- clean context-free aperture;
- forbidden inputs `[]`;
- prereveal suite 38/38 PASS;
- post-reveal terminal in PR #31: `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE`;
- 27/27 adversarial mutations rejected through `ConsumerError`;
- deliberately weaker consumer accepted 15/27 attacks and was killed by the evaluator.

This production-profile gate did not modify Consumer B or recreate its independence claim.

## Exact production subject

Apparatus Draft promotion PR #98, exact locally-qualified head:

`b42c827acb0a9fe65353354d709add0e27bab307`

- candidate public compatibility version: `2.0.0`;
- integrity-bearing wire profile: `contract-c-successor-candidate-a-rc2-research`;
- local promotion gate run: `34804396671`, green on Python 3.11/3.12/3.13;
- global Contract C discovery intentionally remained released C1 during this gate.

## Frozen gate

Frozen experiment blobs:

- preregistration: `4d43beb805f081098d63f48fb8de7e03a0d47ef9`;
- evaluator: `ed1f47d13180f1f96bca13e731c51ad7576e3244`;
- freeze receipt: `f0e2614cb91898e72d574ef959c8c41fdccd2ee9`.

Executed workflow subject:

`5aec168835c36b1478b0d782b3bbcd7d2f3308b3`

## Decisive execution

- workflow run: `34804822687`;
- job: `103854514028`;
- conclusion: `success`;
- artifact: `10332322281` (`contract-c-2.0-promotion-consumer-b-conformance-rc0-34804822687`);
- artifact ZIP digest: `sha256:70d0c42cecdaa9b4b921310a857cb11e2ecbe84a9b6cf0642bd11f77e9d1951c`;
- frozen Consumer B prereveal suite: **38/38 PASS**;
- frozen subject/aperture identity checks: PASS;
- exact production C2 authority checks: PASS;
- preregistered production-profile evaluator: PASS;
- failures: `[]`.

## Preregistered result

`research_disposition = SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE`

All seven terminal checks were true:

1. `production_identity_exact = true`;
2. `premerge_global_discovery_remains_c1 = true`;
3. `candidate_c2_version_is_external_and_noncanonical = true`;
4. `all_four_validate_under_production_c2 = true`;
5. `all_four_production_bytes_and_authority_exact = true`;
6. `all_four_consumed_by_frozen_consumer_b = true`;
7. `all_four_public_semantics_exact = true`.

## Exact four-handoff observations

### Independent supports

- production canonical bytes equal frozen raw bytes;
- whole-object authority: `sha256:a1d48ca4b2906602475413627cef3d07abb8306540f023b3d7cf09e9eff14f5e`;
- Consumer B terminal: `supported / categorical_support`;
- basis groups: `{{S1},{S2}}`.

### Alternative-joint mixed

- production canonical bytes equal frozen raw bytes;
- whole-object authority: `sha256:9444086e38bc18ae03aba4c31fdf8879fb139d47168124d7fa1079b35e0cecce`;
- Consumer B terminal: `not_checkable / MIXED_RELATIONS`;
- basis groups: `{{R1,S1},{R1,S2}}`.

### No deciding relation

- production canonical bytes equal frozen raw bytes;
- whole-object authority: `sha256:ea40a42c2267ac59f65dca6777f9c6777164fa9af73259f076449171c76c72f3`;
- Consumer B terminal: `not_checkable / no_deciding_relation`;
- basis groups: empty.

### Unsupported semantic family

- production canonical bytes equal frozen raw bytes;
- whole-object authority: `sha256:71434a260eeb1af0fb40937031f76aed39fb9b27a47a7f0f9b19f4a4e4b45aee`;
- Consumer B terminal: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`;
- basis groups: empty.

## Interpretation

Observed:

- `consumer_b_modified = false`;
- `producer_private_state_required = false`;
- `production_profile_consumer_gate_satisfied = true`;
- `postreveal_27_attack_programme_rerun_here = false`;
- `contract_c_2_released = false`;
- `promotion_merge_authorized = false`.

The smallest supported conclusion is:

> The exact already-independent frozen Consumer B consumes the exact Contract C 2.0 production-promotion profile without modification or producer-private state, and the exercised production canonical bytes/authorities are identical to the authoritative frozen RC2 handoffs that originally established independent reconstructability.

This closes the independent-consumer production-profile gate for exact Apparatus promotion head `b42c827...`.

## Remaining promotion gates

Still required before Contract C 2.0 merge authorization:

- RC2-specific C1/C2 compatibility and no-downgrade matrix against the exact promotion head;
- production-profile adversarial/fail-closed matrix with evaluator discrimination, reusing preserved attack classes rather than reopening architecture;
- release-artifact/package reproducibility;
- then, and only then, an atomic canonical discovery switch plus full gate rerun;
- post-merge release lock before immutable `contract-c-v2.0.0` publication.

Decision Engine may independently begin its smallest ingress/conformance port against the frozen exact promotion head, but its success does not replace the remaining Contract C release gates.