# CAL Pipeline provenance reconstruction RC0 — terminal record

## Disposition

`SUPPORTED_RECONSTRUCTION_ARCHITECTURE_WITH_RETENTION_GAP`

This is a bounded research result. It does not promote `ApparatusAttestation v1`, `RunManifest v1`, Contract A/B/C/D, any producer, any Decision policy, Authorization, or execution behavior.

## Exact execution

- research repository: `camerontjs-dot/research-scaffold-harness`
- executed head: `28a37e32de4d168851c642a49a607d19232379ff`
- workflow run: `35275945303`
- job: `105386488884`
- conclusion: `success`
- artifact: `10519953839`
- artifact ZIP digest: `sha256:6cef2540e020fedf12d507755ff2f04bdc12f47573de94d90ffc55788c5a8cf5`
- candidate provenance schema authority: `camerontjs-dot/apparatus-contracts@1a5929295e735e351320cbd8c966dc43afed2859`
- first-genuine portable receipt: `camerontjs-dot/claim-audit-lab@93c4f162c0f22a5c2e599fd332160628bc8b2986`

## Phase A — schema/evaluator discriminator

All preregistered controls passed.

1. A fully retained synthetic chain validated under the candidate attestation/manifest schemas and reconstructed as `reconstructable`.
2. Mutating retained Contract-B bytes while holding the independently pinned commitment fixed produced `digest_mismatch`.
3. Removing the required Contract-B locator while keeping its commitment produced `partial`, not reconstructable.
4. Moving both artifact bytes and the manifest's self-declared commitment while holding an independently expected manifest root fixed was rejected with a manifest `digest_mismatch` / `root_verified=false`.
5. The deliberately weak control that allowed the caller to move the expected manifest root with the mutated world accepted the mutated world. This demonstrates that a self-hashed manifest is not its own trust root.
6. Reclassifying an EB input from `observed_context` to `causal_input` changed the attestation identity.
7. Removing the behaviorally relevant configuration identity changed the attestation identity.

The synthetic trusted manifest root was:

`sha256:67bed81c5855126d8ad94ba7c57da9af48c99ef62906890bf417b45afb390ca2`

## Phase B — first-genuine reconstruction attempt

The portable receipt was recovered from its exact Git commit and parsed successfully.

All seven public component/authority Git identities named by the receipt resolved at their exact commits:

- Evidence Bundler `4e1f6fe00e7c350b28f52bfea14f1f8988847884`;
- CAL C2 authority `8204417f478cfbd891499145a7edec5ee33405ad`;
- CAL semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
- Contract C2 authority `b42c827acb0a9fe65353354d709add0e27bab307`;
- CAL policy resolver `1d33e0612befcf8016816197c90c062373796df9`;
- Contract D authority `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`;
- Decision Engine `b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55`.

The portable receipt SHA-256 observed by the hosted evaluator was:

`sha256:06402b6ac77055e74f1e4d8d96c1adec56de09ef3cbe3dc0dd8091f8c4cd50ee`

The exact historical identities recovered from it were:

- source payload: `sha256:512e7415ac1c54195d14d93b93cbd191d5713689681773f6f60b3633c33c84fa`;
- Contract B bundle: `fc459009-fc50-5cc7-a874-0371ce7a3853`;
- Contract B bundle hash: `sha256:8c25ad48cb0a87081088706eed98e53bcb426b6f7f1b944ba776db722a134c80`;
- CAL native result: `sha256:d5c771fad5583952e2941c3ffe45a437cb3e2ec281fae73dd3eba44fdede9b5f`;
- Contract C2 object: `sha256:6696bf1fcf92f277767a26d4a8656a03257fdb77074d8a637265bd8ccc7eeda6`;
- Contract D output: `sha256:af5c3c8ee201b29333a9bfa8e63f0d45eafea22b4e62756240e4ff84a05b1817`;
- freeze manifest: `sha256:6e71a620b64a11cfb24af879881c149c3769fffeb1af14169306cee3f3d32d94`;
- execution receipt: `sha256:4c511d0a80f90d81fb57c58059c9138d1b97f43646f5740606ff2ba6fabfcd3f`.

### Observed reconstruction status

`partial`

Only the portable receipt itself was recoverable and byte-verifiable through the authorized public aperture.

The exact gaps were:

- `source_payload`: `locator_absent`;
- `contract_a`: `identity_absent`;
- `eb_native_package`: `identity_absent`;
- `contract_b`: `locator_absent`;
- `cal_result`: `locator_absent`;
- `contract_c2`: `locator_absent`;
- `contract_d`: `locator_absent`;
- `freeze_manifest`: `locator_absent`;
- `execution_receipt`: `locator_absent`;
- `evidence-bundler:attestation`: `attestation_absent`;
- `cal:attestation`: `attestation_absent`;
- `decision:attestation`: `attestation_absent`.

ClaimGate/EvidenceGate were not retroactively added to the historical run because the portable receipt does not state that they participated.

## Observed evidence

The candidate provenance records can represent a complete chain and distinguish it from a commitment-only chain. Missing locators remain missing rather than becoming assumed retention. Mutated bytes are detected when the expected commitment is independently pinned. Causal-role and configuration changes alter attestation identity.

The historical first-genuine portable receipt retains useful commitments and component identities, but it is not a complete reconstruction package.

## Inference

The provenance-chain architecture remains promising. The strongest immediate implementation requirement is not more semantic state in Contract C or more verification logic in Decision Engine. It is producer-originated attestations plus durable run-manifest entries at the moment each artifact is produced.

The Decision Engine trust problem and the pipeline reconstruction problem share the same missing substrate: independently anchored commitments to retained upstream artifacts.

## Falsified alternatives

1. **Portable receipt alone is enough to reconstruct the first-genuine run:** falsified for the authorized public aperture.
2. **A self-hashed run manifest can serve as its own trust root:** falsified by the moving-root weak control. An expected manifest commitment / trusted producer identity must be selected independently.
3. **A hash is equivalent to retention:** falsified. Multiple historical hashes were available while the corresponding bytes had no retrievable locator in the authorized aperture.

## Unknowns / bounds

- Locator absence in this public/authorized aperture does not prove the historical local artifacts were destroyed. The portable receipt explicitly says a frozen local record remains the evidence source.
- RC0 is not a clean-room independent reproduction.
- RC0 does not establish semantic correctness of EB, CAL, C2, Decision Engine, or D.
- RC0 does not establish signatures, key rotation, revocation, mutable API authority, or a production provenance store.
- The candidate schema has not been promoted or versioned as a released contract.

## Next discriminating test

Instrument one real pipeline execution from the claim/evidence boundary forward so every participating apparatus emits a candidate attestation and the run controller emits a complete manifest with durable locators. Freeze the run. Then hand only the frozen provenance specification, independent trust root, and manifest to a context-free consumer and require full backward reconstruction without producer-private state.

If that consumer cannot recover the exact artifacts, verify every commitment, distinguish input roles, and reproduce the recorded terminal states, the architecture is not ready for promotion.
