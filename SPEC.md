# CAL RC5 Independent Asymmetric Two-Receipt Verification Specification

Status: frozen experimental specification for a clean-room verifier. This is not a production cryptography or release decision.

## 1. Bounded question

Implement a verifier that uses public verification material only to validate two signed statement classes, enforce explicit issuer-to-statement scope, re-derive exact semantic projections from supplied semantic input, and accept only a compatible atom/proposition pair. The verifier MUST NOT rerun RC8J and MUST NOT require any signing private key or shared secret.

## 2. Frozen identifiers

- context_id: `cal.rc5.asymmetric-two-receipt.strict-comparison.v1`
- claim_namespace: `cal.rc5.experimental.claims.v1`
- authority_profile_id: `CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38`
- receipt types: `CAL.AtomWarrant/v1` and `CAL.PropositionBinding/v1`
- schema_major: `1`
- signature_profile: `Ed25519`

The authority profile identifier names the exact frozen RC8J experimental profile. It is a provenance and scope identifier only. The verifier is not given RC8J and does not evaluate RC8J.

## 3. Raw JSON and deterministic bytes

Receipt transport is UTF-8 JSON. Before ordinary object construction, the parser MUST reject any duplicate member name at any nesting depth with `DUPLICATE_JSON_KEY`. Unknown fields in receipt envelopes and signed statements MUST be rejected.

Signed bytes are exactly RFC 8785 JSON Canonicalization Scheme (JCS) bytes for the receipt's `statement` object, encoded as UTF-8. The signature covers the statement object only. `statement_digest_sha256` is the lowercase SHA-256 hex digest of those canonical statement bytes. It is an ordinary integrity check and is not authority. Recomputing it after a mutation does not create signing authority.

RC5 restricts semantic JSON to I-JSON-compatible values: objects with string keys, arrays, strings without lone surrogate code points, booleans, null, and integers in `[-9007199254740991, 9007199254740991]`. Floating-point values are forbidden. Security-critical member names are fixed ASCII. Implementations may use an RFC 8785 library or a correct implementation for this restricted profile.

Ed25519 signatures are 64 raw bytes encoded with RFC 4648 base64url without padding. Public keys are 32 raw bytes encoded the same way.

## 4. Semantic request

The verifier consumes one semantic request containing:

```json
{
  "context_id": "cal.rc5.asymmetric-two-receipt.strict-comparison.v1",
  "authority_case": { "...": "..." },
  "proposition": {
    "claim_id": "...",
    "family": "...",
    "lhs_entity": "...",
    "rhs_entity": "...",
    "comparison_direction": "..."
  }
}
```

The proposition object has exactly those five fields. The authority case may contain diagnostic top-level fields beyond the authority projection. Those diagnostic fields are deliberately not bound by this receipt profile.

## 5. Atom projection and `CAL.AtomWarrant/v1`

Derive `atom_projection` by selecting exactly these top-level authority-case fields, preserving their JSON values without normalization:

[
  "execution_state",
  "evidence_admitted",
  "authority_subject_id",
  "raw_source_id",
  "authority_subject_source_id",
  "raw_bundle_id",
  "authority_subject_bundle_id",
  "raw_passage_id",
  "authority_subject_passage_id",
  "admitted_passage_span",
  "raw_claim_id",
  "authority_subject_claim_id",
  "target_atom_id",
  "authority_subject_atom_id",
  "proposal",
  "assertion",
  "operator",
  "field_warrants",
  "required_fields",
  "composition",
  "aperture"
]

The signed AtomWarrant statement contains exactly:

- receipt_type `CAL.AtomWarrant/v1`;
- schema_major `1`;
- the frozen context_id;
- signature_profile `Ed25519`;
- the exact authority_profile_id above;
- issuer_key_id;
- authority_status `WARRANTED`;
- authority_reason `ALL_REQUIRED_WARRANT_ESTABLISHED`;
- claim_id equal to `atom_projection.raw_claim_id`;
- atom_id equal to `atom_projection.target_atom_id`;
- the complete atom_projection.

For verification against semantic input, the verifier MUST independently re-select the projection from `authority_case` and require exact JSON structural equality with the signed projection. It MUST additionally require signed claim_id to equal `authority_case.raw_claim_id` and signed atom_id to equal `authority_case.target_atom_id`. The receipt does not authorize any mutation, omitted bound field, or semantic normalization.

## 6. Proposition projection and `CAL.PropositionBinding/v1`

Derive `proposition_projection` from exactly:

```json
{
  "family": proposition.family,
  "lhs_entity": proposition.lhs_entity,
  "rhs_entity": proposition.rhs_entity,
  "comparison_direction": proposition.comparison_direction
}
```

The signed PropositionBinding statement contains exactly receipt_type, schema_major, context_id, signature_profile, claim_namespace, issuer_key_id, claim_id, and proposition_projection. Signed claim_id MUST equal semantic input `proposition.claim_id`, and the signed projection MUST be exactly structurally equal to the independently derived projection.

Exact object identity is intentional. `A greater_than B` and `B less_than A` are distinct proposition representations even if another layer could treat them as semantically related. This receipt layer MUST NOT normalize one into the other.

## 7. Public keys and scoped authority

`PUBLIC-KEYS.json` is a key lookup table, not an authority policy. `TRUST-POLICY.json` is the sole frozen statement-authority policy. Signature validity MUST NOT imply unrestricted issuer authority.

The policy is default-deny. An issuer is authorized only when an authorization entry matches its key_id, receipt_type, schema_major, context_id, and the class-specific scope field. For AtomWarrant this includes the exact authority_profile_id. For PropositionBinding this includes the exact claim_namespace.

A cryptographically valid PropositionBinding signed by the AtomWarrant-only key MUST be refused with `UNAUTHORIZED_ISSUER_SCOPE`. A cryptographically valid AtomWarrant signed by the PropositionBinding-only key MUST receive the same refusal.

## 8. Pair compatibility

After both receipts are individually valid and bound to the supplied semantic input, pair acceptance additionally requires:

1. request context_id equals the frozen context_id;
2. both signed context_id values equal request context_id;
3. AtomWarrant claim_id equals PropositionBinding claim_id;
4. both equal semantic input proposition.claim_id and authority_case.raw_claim_id.

No receipt may be accepted under a different claim merely because another field or digest matches.

## 9. Required verification order and typed result

The verifier MUST fail closed. For each receipt, apply these stages in order:

1. raw UTF-8 JSON parse with duplicate-key rejection;
2. strict receipt-class schema and frozen constant validation;
3. JCS reconstruction of the signed statement;
4. `statement_digest_sha256` equality check;
5. public-key lookup by issuer_key_id;
6. Ed25519 signature verification over the reconstructed JCS bytes;
7. explicit trust-policy authorization for exact statement type and scope;
8. exact semantic binding checks;
9. pair compatibility checks after both receipts pass individually.

The machine-readable result MUST be one JSON object. Success:

```json
{"decision":"ACCEPT","code":"ACCEPT","claim_id":"...","atom_id":"..."}
```

Failure:

```json
{"decision":"REFUSE","code":"<CODE>"}
```

Required refusal codes are: `INVALID_JSON`, `DUPLICATE_JSON_KEY`, `INVALID_RECEIPT_SCHEMA`, `INVALID_INPUT`, `UNSUPPORTED_PROFILE`, `STATEMENT_DIGEST_MISMATCH`, `UNKNOWN_SIGNER`, `SIGNATURE_INVALID`, `SIGNATURE_INVALID_FORMAT`, `UNAUTHORIZED_ISSUER_SCOPE`, `ATOM_BINDING_MISMATCH`, `PROPOSITION_BINDING_MISMATCH`, `PAIR_CONTEXT_MISMATCH`, and `PAIR_CLAIM_MISMATCH`.

If several defects coexist, return the code for the earliest stage above.

## 10. Unsupported multiplicity case

This profile contains no uniqueness, registry, conflict-resolution, freshness, transparency, revocation, or equivocation rule for PropositionBinding statements. Two independently valid, exact, same-claim_id proposition bindings with incompatible proposition projections are evidence that two valid statements exist. The verifier MUST NOT invent a rule that labels one authoritative, normalizes them together, or claims equivocation is solved. Each may verify individually when matched to its own semantic input.

## 11. Security boundary and non-claims

The verifier receives only public verification material. It MUST NOT expose or require a signing operation for KA or KP, import any CAL producer/RC3/RC4 verifier implementation, rerun RC8J, depend on undocumented producer state, or use shared HMAC material.

Success in RC5 establishes only bounded public-key verification, explicit issuer scope, exact receipt binding, pair compatibility, and independent reconstructability for this frozen profile. It does not establish production cryptography, PKI, key lifecycle, revocation, compromise recovery, anti-replay beyond this context, equivocation detection, semantic truth, RC8J epistemic correctness, semantic normalization, Contract C projection, Decision Engine policy, production integration, release, or promotion.
