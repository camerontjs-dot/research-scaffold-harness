# CAL RC5A Security-Class / Diagnostic-Separation Verification Specification

Status: experimental successor specification. RC5 remains terminal `INCONCLUSIVE_EVALUATOR_INVALID` and is not reinterpreted or repaired by this document.

## 1. Bounded question

Can a fresh independent verifier reconstruct the asymmetric two-receipt public-verification boundary while agreeing on security-relevant protocol meaning and preserving detailed audit diagnostics without requiring byte-for-byte equality of implementation-specific diagnostic tokens?

RC5A does not change the underlying two-receipt trust architecture. It separates:
1. **normative protocol semantics**, which downstream security/epistemic logic may consume; and
2. **audit diagnostics**, which must be preserved but MUST NOT confer authority or alter protocol meaning.

## 2. Frozen identifiers and cryptographic profile

- context_id: `cal.rc5a.asymmetric-two-receipt.strict-comparison.v1`
- claim_namespace: `cal.rc5a.experimental.claims.v1`
- authority_profile_id: `CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38`
- receipt types: `CAL.AtomWarrant/v1`, `CAL.PropositionBinding/v1`
- schema_major: `1`
- signature_profile: `Ed25519`
- signed bytes: RFC 8785 JCS of the exact `statement` object, UTF-8
- digest: lowercase SHA-256 of those JCS bytes
- signature encoding: raw Ed25519 signature, RFC 4648 base64url without padding
- public key encoding: raw Ed25519 public key, RFC 4648 base64url without padding

Semantic JSON remains restricted to I-JSON-compatible values: objects with string keys, arrays, strings without lone surrogates, booleans, null, and integers in `[-9007199254740991, 9007199254740991]`. Floats are forbidden. Duplicate JSON member names at any nesting depth are forbidden.

## 3. Structural wire validity is not profile admission

`WIRE-SCHEMA.json` defines **structure only**: required members, JSON types, object closure, and projection shapes.

It deliberately does NOT encode the supported values of:
- `receipt_type`
- `schema_major`
- `context_id`
- `signature_profile`
- `authority_profile_id`
- `claim_namespace`
- `authority_status`
- `authority_reason`

It also does NOT encode Ed25519 signature byte length or SHA-256 digest width.

Those are checked by later protocol stages. A structurally valid receipt can therefore be refused as `UNSUPPORTED`, `UNAUTHENTICATED`, or another later normative class without being reclassified as malformed.

## 4. Semantic projections

For `CAL.AtomWarrant/v1`, derive `atom_projection` by selecting exactly these top-level fields from `authority_case`, preserving values without normalization:

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

The AtomWarrant statement contains exactly:
- receipt_type
- schema_major
- context_id
- signature_profile
- authority_profile_id
- issuer_key_id
- authority_status
- authority_reason
- claim_id
- atom_id
- atom_projection

For `CAL.PropositionBinding/v1`, derive:

```json
{
  "family": proposition.family,
  "lhs_entity": proposition.lhs_entity,
  "rhs_entity": proposition.rhs_entity,
  "comparison_direction": proposition.comparison_direction
}
```

The PropositionBinding statement contains exactly:
- receipt_type
- schema_major
- context_id
- signature_profile
- claim_namespace
- issuer_key_id
- claim_id
- proposition_projection

Exact representation identity remains intentional. No semantic-equivalence normalization is authorized.

## 5. Key lookup and statement authority

`PUBLIC-KEYS.json` is only key lookup. `TRUST-POLICY.json` is the sole statement-authority policy.

Policy is default-deny.

The atom issuer is authorized only for the exact AtomWarrant receipt type, schema major, context, and authority profile.

The proposition issuer is authorized only for the exact PropositionBinding receipt type, schema major, context, and claim namespace.

A cryptographically valid cross-role signature MUST be refused with normative failure class `UNAUTHORIZED_ISSUER`.

Signature validity never implies unrestricted authority.

## 6. Normative protocol result

The only authority-bearing output is `protocol_result`.

Success:

```json
{
  "protocol_result": {
    "decision": "ACCEPT",
    "failure_class": null,
    "claim_id": "...",
    "atom_id": "..."
  },
  "audit_record": { "...": "..." }
}
```

Failure:

```json
{
  "protocol_result": {
    "decision": "REFUSE",
    "failure_class": "<CLASS>"
  },
  "audit_record": { "...": "..." }
}
```

Allowed normative failure classes are exactly:

- `MALFORMED`
- `UNSUPPORTED`
- `UNAUTHENTICATED`
- `UNAUTHORIZED_ISSUER`
- `BINDING_MISMATCH`
- `INCOMPATIBLE_PAIR`

Downstream CAL logic MUST NOT acquire additional authority from `audit_record`.

## 7. Normative stage groups and precedence

Apply these normative groups in order. If multiple defects coexist, the earliest group determines `failure_class`.

1. **Transport / structural validity -> `MALFORMED`**
   - invalid UTF-8/JSON
   - duplicate JSON member
   - missing/extra members
   - wrong JSON types or structural shapes
   - invalid semantic-request structure
   - forbidden I-JSON value class

2. **Profile admission -> `UNSUPPORTED`**
   - unsupported receipt type
   - unsupported schema major
   - wrong/unsupported context identifier
   - unsupported signature profile
   - wrong AtomWarrant authority_profile_id
   - wrong PropositionBinding claim_namespace
   - unsupported authority_status or authority_reason

3. **Authenticated-byte reconstruction -> `UNAUTHENTICATED`**
   - signed statement cannot be canonicalized under the restricted JCS profile
   - digest encoding/width is invalid
   - digest does not match canonical signed bytes
   - signer key is not available in `PUBLIC-KEYS.json`
   - signature encoding/alphabet/padding/decoded size is invalid
   - Ed25519 verification fails

4. **Issuer scope -> `UNAUTHORIZED_ISSUER`**
   - signature is cryptographically valid with a known key, but the exact trust-policy scope does not authorize that statement

5. **Exact semantic binding -> `BINDING_MISMATCH`**
   - AtomWarrant projection/claim/atom identity differs from the independently derived authority-case projection
   - PropositionBinding projection/claim identity differs from the independently derived proposition projection

6. **Pair compatibility -> `INCOMPATIBLE_PAIR`**
   - individually valid and bound receipts disagree on required context or claim compatibility

Only after all groups succeed may the pair be `ACCEPT`.

## 8. Audit diagnostic preservation

Every result MUST contain `audit_record` with at least:

```json
{
  "verifier_id": "<nonempty stable identifier>",
  "diagnostic_stage": "<nonempty implementation-defined token>",
  "diagnostic_code": "<nonempty implementation-defined token>"
}
```

Additional audit detail is allowed and encouraged.

`diagnostic_stage` and `diagnostic_code` are **not normative across independent implementations**. Exact token equality is not a conformance requirement.

Within one frozen implementation, however:

1. the diagnostic tuple `(diagnostic_stage, diagnostic_code)` MUST be deterministic for the same input;
2. transport-only changes that preserve the parsed object and underlying defect MUST preserve that tuple;
3. designated different subcauses inside the same normative failure class MUST remain diagnostically distinguishable, meaning their tuples cannot all collapse to one generic value;
4. diagnostic contents MUST NOT change `protocol_result`.

The evaluator therefore tests diagnostic **stability and discrimination properties**, not a hidden universal diagnostic vocabulary.

## 9. Pair compatibility

After both receipts are individually valid and bound:
- request context_id must equal the frozen context
- both statement contexts must equal request context
- AtomWarrant claim_id must equal PropositionBinding claim_id
- both must equal semantic `proposition.claim_id` and `authority_case.raw_claim_id`

No different claim may be accepted because a digest, key, or other field matches.

## 10. Unsupported multiplicity and lifecycle

RC5A adds no uniqueness, freshness, revocation, sequence, transparency, registry, latest-state, or equivocation semantics.

Two individually valid incompatible same-claim proposition bindings remain two valid historical signed statements. The verifier MUST NOT invent which one is current, canonical, or authoritative over the other.

## 11. Non-claims

Success does not establish:
- production cryptographic architecture or vendor/library selection
- production PKI, key custody, rotation, revocation, or compromise recovery
- freshness/latest-state semantics
- transparency or equivocation resolution
- semantic truth or RC8J correctness
- semantic-equivalence normalization
- Contract C projection
- Decision Engine policy
- production integration, merge, tag, release, or promotion
