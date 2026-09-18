# CAL Pipeline Provenance Run Series RC1

Status: **prepared for local execution**. Research qualification only.

This package instruments the already-frozen CAL Pipeline rather than changing its semantic machinery. It is the successor to provenance reconstruction RC0, whose result was `SUPPORTED_RECONSTRUCTION_ARCHITECTURE_WITH_RETENTION_GAP`.

## Purpose

Run a small series through exact pinned components while adding:

- producer-originated apparatus attestations;
- durable byte retention for every reconstruction-required artifact;
- one run manifest per case;
- a candidate manifest digest that can later be frozen by an independent actor/control plane;
- a context-free reconstruction verifier.

The run is successful as a provenance experiment if it preserves the actual pipeline behavior and leaves enough immutable state for later reconstruction. A particular CAL verdict or Decision is **not** required, except that the historical replay must reproduce the historical result if the exact historical bytes are available.

## Frozen machinery

See `RUN-SERIES.json` for exact identities. Important pins:

- Gate V1: `camerontjs-dot/proposition-authoring@341db0b46d5d663a97b4f93e6ac443c467170b8b`
- Contract A 2.0.0 release lock: `529c92b49a34d5c610618551a8737f019f9fa332`
- Evidence Bundler: `camerontjs-dot/evidence-bundler@4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- EB profile: `eb-v1-integration-10x3-rc0`
- Contract B: `1.2.0`, lock `c314e53bd91c0736aa4370a364673b069aceb43e`
- CAL C2 authority checkout: `8204417f478cfbd891499145a7edec5ee33405ad`
- CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- Contract C2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- resolver: `1d33e0612befcf8016816197c90c062373796df9`
- Decision Engine: `b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55`
- Contract D authority: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- provenance candidate schemas: `camerontjs-dot/apparatus-contracts@1a5929295e735e351320cbd8c966dc43afed2859`

If a required checkout is not at the exact pin, create a disposable worktree at that pin. Do not advance to a newer implementation for convenience.

## Cases

### 1. `first-genuine-b-side-replay`

Exact historical control. Start at the original B-side path.

Use the local frozen record corresponding to `FIRST-GENUINE-B-SIDE-001`. The portable receipt identifies the required historical hashes. If the exact local bytes cannot be found, stop this case as `BLOCKED_HISTORICAL_BYTES_UNAVAILABLE`; do not recreate or substitute them.

Expected historical semantics if replay is possible:

- CAL: `not_checkable / MEASUREMENT_MISS / UNRESOLVED`
- C2: `not_checkable / no_deciding_relation`
- D: `hold / contract_c_no_deciding_relation_not_supported`

### 2. `health-canada-ozempic-001`

Full pipeline from Gate V1. Input packet is frozen at:

`cases/health-canada-ozempic-001.json`

This is the exact real-world Gate V1 packet used by proposition-authoring PR #43.

### 3. `rimebridge-simple-support`

Full pipeline. Exact frozen benchmark case:

- `case-dev-claim-001-a0`
- subset `ordinary_window`

Materialize the Gate input from the exact EB checkout using `materialize_benchmark_gate_packet.py`.

### 4. `amberbraid-temporal-supersession`

Full pipeline. Exact frozen benchmark case:

- `case-dev-claim-017-a0`
- subset `full`

This exercises a temporal/version supersession evidence world with multiple decisive evidence items.

### 5. `wick-missing-decisive`

Full pipeline. Exact frozen benchmark case:

- `case-dev-claim-049-a0`
- subset `bounded_missing_decisive`

The source aperture intentionally excludes `src-wickarchive-current`. Preserve the resulting stop/abstention/HOLD path rather than widening retrieval.

## Benchmark gold firewall

Gold files are not causal pipeline inputs.

Do **not** open or pass `gold/dev_relevance.jsonl` to Gate, EB, CAL, or Decision before each case has terminally frozen its outputs and manifest candidate.

After terminal freeze, gold may be copied into an analysis area and recorded only as `diagnostic_input`.

## Output layout

Use this root relative to MainFrame:

`20_live/cal-pipeline/cal-v1-studies/provenance-rc1/`

Each case should have:

```
<case-id>/
  INPUT/
    GATE-PACKET.json                 # full-pipeline cases
    INPUT-IDENTITY.json              # root byte identities / source authority
  GATE/
    CLAIM-GATE.json                  # if stage ran
    EVIDENCE-GATE.json
    STANDARDIZATION-RECEIPT.json
    CONTRACT-A.json                  # if authoring emitted it
  EB/
    native/                          # native output as produced
    native.snapshot.zip              # deterministic byte snapshot
    contract-b/                      # raw Contract B bundle
    contract-b.snapshot.zip          # deterministic byte snapshot
    projection-receipt.json
  CAL/
    native-result.json
    contract-c2.json
    c2-validation-receipt.json
  DECISION/
    contract-d.json
    decision-receipt.json
  PROVENANCE/
    claim-gate.attestation.json
    evidence-gate.attestation.json
    evidence-bundler.attestation.json
    cal.attestation.json
    decision-engine.attestation.json
    RUN-MANIFEST.draft.json
    RUN-MANIFEST.candidate.json
    CANDIDATE-ROOT.txt
    RETENTION-CHECK.json
  OBSERVATIONS.md
```

Historical replay may omit Gate artifacts/stages and must record those stages as `not_present`.

If actual component output filenames differ, retain them exactly and reflect the real paths in the manifest. Do not rename native artifacts merely to match this example.

## Required provenance by stage

### ClaimGate

Attestation must bind:

- exact Gate input packet as `causal_input`;
- exact Gate V1 Git commit;
- exact Contract A authority as `authority_input` when applicable;
- ClaimGate output;
- exact Contract A bytes when emitted;
- completed/abstained/failed state.

### EvidenceGate

Attestation must bind:

- exact Gate input packet / supplied evidence bytes as `causal_input`;
- exact Gate V1 Git commit;
- exact EvidenceGate output;
- execution state.

EvidenceGate descriptive fields remain non-authoritative for EB retrieval unless a separately qualified consumer exists. This series does not create one.

### Evidence Bundler

Attestation must bind:

- exact Contract A bytes as `causal_input`;
- compatibility carrier as `compatibility_input` if used;
- exact EB commit and 10/3 profile/config identity;
- Contract B 1.2 authority;
- exact native package snapshot;
- exact Contract B snapshot;
- Contract B bundle ID/hash;
- projection receipt;
- execution state.

Do not classify Gate descriptive metadata as a causal EB input unless the actual frozen EB path consumes it.

### CAL

Attestation must bind:

- exact verified Contract B artifact as `causal_input`;
- exact CAL implementation identity;
- exact C2/producer-policy/resolver authorities as `authority_input`;
- exact native CAL result;
- exact C2 object;
- C2 validation receipt if generated;
- CAL terminal semantic/execution state without reinterpretation.

### Decision Engine

Attestation must bind:

- exact C2 object as `causal_input`;
- verified Contract B artifact/commitment as required for participant authority;
- C2/producer resolver and Decision policy/implementation authorities;
- exact resolved target identity;
- exact Contract D bytes;
- Decision receipt;
- CLEAR/HOLD/FAILED state;
- no Authorization claim.

## Artifact retention rule

A hash without bytes is insufficient.

Every artifact listed in `reconstruction.required_artifact_ids` must have:

1. an exact identity;
2. a `sha256-bytes` commitment;
3. retained bytes;
4. at least one locator;
5. `retention.state = retained_verified`.

For directory outputs, preserve the native directory and create a deterministic ZIP snapshot with:

```bash
python pack_tree.py <directory> <snapshot.zip>
```

Use the snapshot as the byte-reconstruction artifact. Preserve Contract B's own bundle hash separately as a `contract-b-bundle-hash` commitment.

## Attestation and manifest sealing

Use `provenance_support.py`. Its canonicalization matches the successful RC0 discriminator.

Example:

```bash
python provenance_support.py seal-attestation \
  --apparatus-contracts-root /path/to/apparatus-contracts-pinned \
  ATTESTATION.draft.json \
  evidence-bundler.attestation.json
```

After all artifacts and attestations are retained, build `RUN-MANIFEST.draft.json`, then:

```bash
python provenance_support.py seal-manifest \
  --apparatus-contracts-root /path/to/apparatus-contracts-pinned \
  RUN-MANIFEST.draft.json \
  RUN-MANIFEST.candidate.json
```

Copy only the resulting candidate digest into `CANDIDATE-ROOT.txt`.

**Do not treat that value as trusted merely because the executing agent created it.**

The local execution phase terminates at:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

An independent actor/control-plane will later pin the expected manifest digest.

## Manifest contents

For a full-pipeline run, `reconstruction.required_artifact_ids` should include at minimum:

- root Gate input packet;
- ClaimGate output;
- EvidenceGate output;
- Contract A when emitted;
- EB native snapshot;
- Contract B snapshot;
- CAL native result;
- C2 object;
- Contract D;
- every stage attestation.

Include compatibility carriers, validation receipts, and target artifacts when they materially participated and cannot be deterministically recovered from another retained artifact.

The manifest must also list the exact immutable Git/release authorities used by the run.

## Phase 1 pass/fail rules

Phase 1 is setup/execution evidence, not final provenance qualification.

A case may end:

- `READY_FOR_INDEPENDENT_ROOT_FREEZE`: run completed or legitimately stopped, all material outputs/negative states preserved, required bytes retained, manifest candidate sealed;
- `BLOCKED_HISTORICAL_BYTES_UNAVAILABLE`: only permitted for the historical replay when exact old bytes cannot be recovered;
- `FAILED_PROVENANCE_CAPTURE`: material stage ran but required input/output/attestation bytes were lost, omitted, or cannot be identified;
- `FAILED_PIPELINE`: pipeline apparatus failed for a reason not represented as a legitimate semantic/authoring stop.

Do not convert an abstention, `not_checkable`, or Decision HOLD into `FAILED_PIPELINE`.

## Independent reconstruction phase

After manifest roots are independently frozen, hand a context-free consumer only:

- this provenance specification/package;
- exact provenance schema authority commit;
- independently pinned expected manifest digest;
- the run manifest and its locators.

Then run:

```bash
python verify_provenance_package.py \
  RUN-MANIFEST.candidate.json \
  --expected-manifest-sha sha256:<PINNED_ROOT> \
  --apparatus-contracts-root /path/to/apparatus-contracts-pinned \
  --out RECONSTRUCTION-RESULT.json
```

Final success requires `status = reconstructable`.

## Nonclaims

These runs do not establish:

- CAL semantic accuracy;
- universal EB retrieval recall;
- corpus completeness beyond each declared aperture;
- Contract C2 production promotion;
- production Decision correctness;
- Authorization or automatic action;
- release/merge/promotion permission.

The point is to test whether the exact pipeline action can be reconstructed later without producer-private state.
