# CAL Pipeline provenance reconstruction RC0

Status: preregistered research qualification. No contract promotion, runtime mutation, release, Authorization, or execution permission.

## Decision

Decide whether the proposed `ApparatusAttestation v1` + `RunManifest v1` provenance layer is structurally capable of supporting later reconstruction, and whether the frozen first-genuine CAL Pipeline run can actually be reconstructed from the durable/public aperture currently available.

## Exact authorities

- Apparatus Contracts provenance candidate commit: `1a5929295e735e351320cbd8c966dc43afed2859`.
- Candidate attestation schema: `research/provenance-chain-v1-candidate/apparatus-attestation.schema.json`.
- Candidate run-manifest schema: `research/provenance-chain-v1-candidate/run-manifest.schema.json`.
- First-genuine portable receipt commit: `camerontjs-dot/claim-audit-lab@93c4f162c0f22a5c2e599fd332160628bc8b2986`.
- First-genuine portable receipt path: `research/first_genuine_b_side_001/PORTABLE_RECEIPT.md`.

The portable receipt is an evidence index, not permission to infer omitted artifacts. Its publication boundary explicitly says raw Contract A/B/C2/D packets, source passage, execution logs, local paths and private runtime state are excluded.

## Claim under test

A provenance layer that separates domain contracts from apparatus attestations and a content-addressed run manifest can represent a complete reconstructable run when required bytes are retained, while failing explicitly rather than inventing state when a historical run exposes commitments but not retrievable artifacts or producer attestations.

## Phase A: schema / evaluator controls

Create one synthetic complete run using the candidate schemas.

Required positive behavior:

1. both candidate schemas validate;
2. every required synthetic artifact can be recovered by its locator;
3. recovered bytes match independently pinned commitments;
4. the complete synthetic chain is classified `reconstructable`.

Required weak controls:

1. mutate one retained artifact without changing its independently pinned commitment -> reject with digest mismatch;
2. remove a required locator while preserving the commitment -> classify incomplete/partial, not reconstructable;
3. change both artifact bytes and the self-declared manifest commitment while leaving an independent expected manifest commitment fixed -> reject;
4. move an input from `observed_context` to `causal_input` -> attestation identity must change;
5. remove a behaviorally relevant configuration identity -> attestation identity must change or validation must fail.

If a weak control passes as reconstructable, terminal disposition is `FALSIFIED_PROVENANCE_SCHEMA_OR_EVALUATOR`.

## Phase B: first-genuine reconstruction attempt

Using only the exact portable receipt and independently pinned public component identities named by it, build the smallest truthful candidate run manifest.

Do not invent locators, raw packets, stage attestations, Contract-A identity, Gate artifacts, source bytes, or private runtime state that the portable receipt does not expose.

Attempt to recover every artifact necessary to walk the observed path backward from Contract D to the original source claim.

At minimum inspect these historical identities when exposed by the receipt:

- source payload;
- Contract B bundle;
- native CAL result;
- Contract C2 object;
- Contract D output;
- freeze manifest;
- execution receipt;
- component implementation / contract authority identities.

A hash without retrievable bytes is recorded as a commitment with `retention.state = locator_absent`, not as retained evidence.

An artifact whose identity is not exposed is recorded as `identity_absent` in the reconstruction report; do not manufacture a placeholder digest.

## Terminal dispositions

### `SUPPORTED_FIRST_GENUINE_RECONSTRUCTABLE`

Only if every material historical artifact required by the observed run can be recovered, its exact bytes independently verified, stage lineage established without invented state, and the resulting manifest validates.

### `SUPPORTED_RECONSTRUCTION_ARCHITECTURE_WITH_RETENTION_GAP`

If Phase A passes all positive and weak controls, while Phase B fails reconstruction specifically because historical artifacts/attestations/locators were not durably exposed in the authorized aperture. This supports the architecture as a discriminator and identifies retention/producer-attestation debt. It does not establish independent reproduction or a production schema.

### `FALSIFIED_PROVENANCE_SCHEMA_OR_EVALUATOR`

If the candidate schemas cannot represent the positive control, the evaluator accepts a preregistered weak control, materially different causal/configuration state can preserve the same attestation identity, or missing required state is silently treated as reconstructable.

### `INCONCLUSIVE_APPARATUS`

If network/GitHub/schema-tooling failure prevents the discriminator from executing.

## Independence limit

RC0 is authored and executed from the normal CAL Pipeline project context. It is not a clean-room independent reproduction. A later context-free consumer must reproduce the candidate semantics from the frozen specification before any promotion claim.

## Stop rule

Stop after the first decisive Phase A + Phase B result. Preserve failures. Do not patch historical first-genuine artifacts, widen a released contract, or fabricate missing provenance after observing the result.
