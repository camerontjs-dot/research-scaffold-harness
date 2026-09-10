# EB Retrieval-Audit Package — Independent Consumer RC3 Specification

## Status and scope

This is a frozen, research-only consumer specification for an Evidence Bundler package composed of three surfaces:

1. a canonical Contract B 1.2 bundle tree under `contract_b/`;
2. an EB retrieval-audit sidecar `EB_RETRIEVAL_AUDIT.json`;
3. an outer package envelope `EB_EVIDENCE_PACKAGE_ENVELOPE.json`.

The consumer under test must be implemented independently from this specification and the supplied frozen packages only.

This specification establishes structural/integrity semantics only. It does not grant semantic judgment, admission authority, authentication, signer identity, trusted time, authorization, or production status.

## Package layout

Each case directory has this shape:

```text
<case_id>/
  EB_EVIDENCE_PACKAGE_ENVELOPE.json
  EB_RETRIEVAL_AUDIT.json
  contract_b/
    CONTRACT_VERSION
    SHA256SUMS
    bundle_manifest.yaml
    extensions/contract-b-factual-context-v1.json
    ... other Contract B files ...
```

## JSON canonicalization

For sidecar integrity operations, canonical JSON bytes are:

- parse JSON to a data structure;
- serialize with keys sorted lexicographically;
- use separators `,` and `:` with no extra spaces;
- UTF-8, `ensure_ascii=false` semantics;
- append one final LF byte (`0x0a`).

The SHA-256 identifier is written as lowercase hex prefixed with `sha256:`.

A conforming consumer MUST reject a sidecar whose canonical JSON SHA-256 does not equal the digest named in the envelope.

## Outer envelope

`EB_EVIDENCE_PACKAGE_ENVELOPE.json` has schema value:

`eb-evidence-package-envelope-v1`

Required fields and semantics:

- `case_id`: package case identifier.
- `integrity_mode`: MUST equal `sha256-content-binding-only`.
- `authentication_provided`: MUST be `false`.
- `contract_b.bundle_id`: exact Contract B bundle identifier.
- `contract_b.contract_b_version`: exact Contract B version.
- `contract_b.bundle_hash`: exact Contract B bundle hash declared by the bundle.
- `retrieval_audit.schema`: MUST equal `eb-retrieval-audit-v1`.
- `retrieval_audit.sha256`: canonical sidecar SHA-256.

The envelope is an integrity/co-binding record only. It MUST NOT be interpreted as proof of producer identity, trusted signing, trusted time, authorization, or semantic correctness.

## Retrieval-audit sidecar

`EB_RETRIEVAL_AUDIT.json` has schema value:

`eb-retrieval-audit-v1`

Required top-level fields:

- `schema`
- `case_id`
- `retrieval_profile_sha256`
- `candidate_history_complete`
- `authority_boundary`
- `contract_b_binding`
- `queries`
- `candidates`
- `candidate_passages`
- `count_checks`

### Authority boundary

A conforming sidecar MUST declare exactly the following authority boundary:

- `retrieval_audit_only = true`
- `admission_authority = false`
- `semantic_judgment_authority = false`

The sidecar records retrieval/selection history only. Admission/review decisions belong to Contract B, not to the sidecar.

### Contract B binding

The sidecar `contract_b_binding` MUST exactly equal the envelope's Contract B tuple:

- bundle ID;
- Contract B version;
- bundle hash.

### Query records

Each query record contains:

- `query_id`
- `proposition_id`
- `proposition_role`
- `query_text`
- `retrieval_lane`
- `candidate_count`
- `retained_count`

`query_id` MUST be unique within a case.

### Candidate records

Each candidate record contains:

- `query_id`
- `proposition_id`
- `proposition_role`
- `retrieval_lane`
- `evidence_id`
- `source_id`
- `rank`
- `score`
- `score_kind`
- `retained`

For every candidate:

- its `query_id`, proposition, role, and lane MUST agree with exactly one query record;
- `rank` MUST be a positive integer;
- ranks MUST be unique within a query;
- its `evidence_id` MUST resolve to exactly one `candidate_passages` record;
- its `source_id` MUST agree with that passage record.

No candidate field may be treated as support/refutation, truth, verdict, admission, or authorization.

### Candidate passage records

Each record contains:

- `evidence_id`
- `source_id`
- `passage_text`
- `passage_sha256`
- `source_content_sha256`

`evidence_id` MUST be unique within a case.

For each passage, a conforming consumer MUST recompute SHA-256 over the UTF-8 bytes of `passage_text` and require exact equality with `passage_sha256`.

### Count checks

For each proposition/query, the sidecar's observed candidate and retained counts MUST agree across:

- the query record;
- the number of matching candidate records;
- the number of matching candidate records with `retained=true`;
- the corresponding `count_checks` record.

When Contract B's factual-context aperture exposes a known `candidate_count` for that proposition, it MUST equal the sidecar candidate count.

## Contract B cross-checks

### SHA256SUMS

The consumer MUST verify every file listed in `contract_b/SHA256SUMS` by hashing the exact file bytes. Paths are relative to `contract_b/`. A missing file, duplicate listed path, malformed digest, or digest mismatch is a failure.

`SHA256SUMS` itself is not required to list itself.

### Bundle identity

The consumer MUST extract from `contract_b/bundle_manifest.yaml` the scalar values:

- top-level `bundle_id`;
- top-level `schema_version`;
- nested `bundle.bundle_hash`.

The package files use ordinary YAML scalar syntax for these values. A minimal line/indent parser is sufficient; use of a YAML library is also allowed.

The extracted tuple MUST exactly equal both:

- the envelope `contract_b` tuple;
- the sidecar `contract_b_binding` tuple.

`contract_b/CONTRACT_VERSION`, after trimming surrounding ASCII whitespace, MUST equal the same Contract B version.

### Retention versus Contract B history

Parse `contract_b/extensions/contract-b-factual-context-v1.json`.

Define the sidecar retained identity set as all pairs:

`(candidate.proposition_id, candidate.evidence_id)` where `candidate.retained == true`.

Define the Contract B history identity set as all pairs:

`(history.claim_id, history.passage_id)` from the extension `history` array.

These sets MUST be exactly equal.

Admission/review state MUST be read from Contract B only. The sidecar MUST NOT supply or override it.

### Candidate counts versus Contract B aperture

For each Contract B aperture row whose outcome is `known` and whose value includes an integer `candidate_count`, require exact equality with the corresponding sidecar candidate count for that claim/proposition.

## Required consumer output

For each case, the consumer MUST emit a deterministic JSON record containing at least:

- `case_id`
- `package_valid`
- `errors` as a sorted list of machine-readable strings
- `contract_b_sha256s_valid`
- `envelope_sidecar_digest_valid`
- `binding_tuple_valid`
- `authority_boundary_valid`
- `candidate_passage_hashes_valid`
- `candidate_count_consistent`
- `retention_contract_b_consistent`
- `candidate_identities_by_proposition`, ordered by rank
- `retained_identities_by_proposition`, ordered by rank
- Contract B review/admission decisions keyed by `(claim_id, passage_id)`

The whole-run report MUST include:

- schema `eb-retrieval-audit-independent-consumer-rc3-report-v1`;
- exact aperture/package archive SHA-256 supplied by the task;
- case count;
- per-case records;
- a global validity boolean;
- implementation/runtime information sufficient to reproduce the run.

Do not include a semantic truth/support/refutation judgment.

## Required negative controls

The independent implementation MUST construct mutations from the frozen packages at runtime, without altering the frozen originals, and show the consumer detects all of the following:

1. mutate one sidecar byte/value without updating the envelope digest;
2. swap a sidecar between two cases while retaining the original envelope;
3. mutate a Contract B file listed in `SHA256SUMS` without updating its digest line;
4. flip one candidate `retained` flag, then correctly recompute the sidecar digest and envelope sidecar digest, while leaving Contract B unchanged;
5. remove one candidate, then correctly recompute sidecar query/count-check counts and reseal the sidecar/envelope, while leaving Contract B aperture unchanged;
6. alter a sidecar authority field to claim semantic or admission authority and correctly reseal the sidecar/envelope.

The first three test external integrity binding. The latter three test internal cross-surface invariants and authority boundaries even when an attacker can recompute unkeyed hashes.

## Non-claims

Passing this specification does NOT establish:

- retrieval quality;
- corpus completeness;
- semantic support/refutation correctness;
- admission correctness;
- Contract B production readiness;
- cryptographic authentication or signer identity;
- resistance to an attacker able to replace all package surfaces and their distribution channel;
- authorization or execution permission.
