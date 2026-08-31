# PREREGISTRATION: Contract E RC3D Fresh Reproduction

## 1. Purpose and Bounded Claim
This reproduction independently implements the Contract E RC3D research authority/warrant consumer natively, based strictly on the six provided public specification blobs. The bounded claim is that a fresh Gemini-family implementation process independently recovered materially agreeing Contract E RC3D authority/warrant and public consumer-interface behavior without pre-freeze access to hidden evaluators or prior reproductions. It does not establish production trust roots, a universal authority theory, safe autonomous production execution, etc.

## 2. Model
*   **Authority**: Domain-specific permission to act, conferred by current basis records (`grant`, `policy`, `delegation`). Evaluated strictly before operational payloads.
*   **Competence**: Evaluated via Qualification (e.g., `numeric_relation_validator`). Does not imply jurisdiction.
*   **Warrant**: Epistemic validation, bound to target artifacts. Does not imply operational permission.
*   **Jurisdiction**: Geographic/logical boundary (`scope`). Evaluated against current basis and subject. Does not imply competence.
*   **Participant Responsibility**: Declared participants (e.g., `claim-audit-lab`) must be explicitly declared and accept the requested authority domain/operation. Responsibility is strictly enforced and cannot be bypassed by positive payload.
*   **Propagation**: Default is `none`. `identity_provenance_only` forwards provenance metadata; `explicit` requires specifying fields and implies loss of authority unless explicitly reauthorized.
*   **Delegation**: Parent-child relationship where child must be a strict non-amplifying subset (domain, operations, scope) of parent, and cannot extend expiry.
*   **Currentness**: Evaluated conjunction of reference currentness, record currentness, non-revocation, and validity interval constraints. Fail-closed freshness veto applies.
*   **Historical Validity**: Preserves the fact that authority was valid at evaluation time, ignoring subsequent revocation, but prohibits new exercises based purely on historical validation.

## 3. How RC3C and RC3D Supersede
*   **RC3C** supersedes RC3A/RC3B by enforcing strict canonical wire structures (no silent singular/plural coercion), defining the exact conjunction for currentness evaluation, strict delegation subset/expiry wire shape, and dictating a unified whole-envelope normative reason precedence (restricting reason strings unless explicitly relisted).
*   **RC3D** supersedes inherited evaluation surface by strictly defining a unified `EvaluationRequest` with specific `kind` forms (`envelope`, `propagation`, `delegation`, `historical`). It introduces native `RegistryDocument` consumption, strictly prohibiting external pre-extraction of basis records. It also standardizes the terminology for propagation requests and historical evaluation modes, and introduces new malformed kinds/modes as top-level rejection reasons.

## 4. Exact Interpretation of `EvaluationRequest`
*   `envelope`: Wraps a canonical RC3C envelope evaluation against a natively provided `RegistryDocument`.
*   `propagation`: Validates explicitly specified or implicit propagation modes (none, identity_provenance_only, explicit) and field subsets. Rejects aliases like `requested_fields`.
*   `delegation`: Evaluates `DelegationChild` strictly against its `ParentAuthorityRecord` without amplification.
*   `historical`: Evaluates historical records for `historical_inspection` (succeeds if valid at time) or `new_exercise` (rejects unless currently reauthorized).

## 5. Exact Interpretation of `RegistryDocument`
A full native wrapper representing the authority registry. The consumer must consume `RegistryDocument` exactly (matching `schema` and `records` object, checking `record_id_consistency`). It forbids pre-extraction of records by a hidden adapter prior to consumer invocation.

## 6. Propagation Field/Mode Behavior
*   `none`: `allowed_fields` is empty.
*   `identity_provenance_only`: Permits only `source_id`, `artifact_id`, `content_hash`, `producer_id`, `policy_id`, `policy_version`.
*   `explicit`: Permits explicit fields. Authority fields are forbidden unless `separately_reauthorized` is true.

## 7. `ParentAuthorityRecord` versus `DelegationChild`
The `DelegationChild` must correctly reference `ParentAuthorityRecord` via `parent_authority_id`. The child's operations and scope must be subsets of the parent's. If the parent has a `valid_until` expiry, the child must have one $\le$ the parent's. Domain must strictly match.

## 8. Historical Mode Behavior
*   `historical_inspection`: Affirms authority validity if it was valid at the original time. Later revocation/expiry does not mutate this historical status.
*   `new_exercise`: Explicitly demands a current authority check. Relying purely on a historical token yields `authority_basis_not_current`.

## 9. Reason Taxonomy/Precedence
1. RC3D structural: `unknown_evaluation_kind`, `unknown_evaluation_mode`, `malformed_registry_document`, `malformed_propagation_request`, delegation failures (`delegation_parent_mismatch`, etc.).
2. RC3C structural/malformed envelope failures (`malformed_authority_basis_shape`, etc.).
3. RC3B unresolvable basis or basis mismatch failures (`unresolvable_authority_basis`, `authority_basis_type_mismatch`, `authority_basis_not_current`, etc.).
4. Competence/Qualification mismatches (`missing_required_qualification`, `qualification_not_current`, etc.).
5. Warrant mismatches.
6. Propagation mismatches.
Single primary reason is strictly normative in the precedence defined by RC3C, RC3D, and RC3B.

## 10. Malformed/Unknown Behavior
Rejection is required (e.g., `unknown_evaluation_kind`, `malformed_registry_document`). Silent defaults are forbidden.

## 11. Adversarial/Metamorphic Tests (at least 20)
1. Subject substitution attack (different subject).
2. Domain substitution attack.
3. Operation substitution attack.
4. Scope substitution attack.
5. Target-class substitution attack.
6. Unresolved basis ID.
7. Authority-reference type mismatch.
8. Reference current `false`.
9. Resolved record current `false`.
10. Exercise post-revocation (`revoked_at` reached).
11. Validity interval boundary check (at exactly `valid_until`).
12. Competence present but authority basis missing.
13. Authority basis present but required competence absent.
14. Warrant absent where domain requires it.
15. Warrant hash mismatch.
16. Unknown evaluation `kind`.
17. Malformed registry wrapper (missing `schema`).
18. Explicit propagation without `fields`.
19. Delegation operation amplification.
20. Delegation expiry amplification.
21. New exercise relying solely on historical inspection token.
22. Metamorphic payload substitution (varying `result` payload opacity without changing signature).

## 12. Explicit Falsifiers
*   Accepting an evaluation with an unknown `kind` or `mode`.
*   Authorizing an action because the `result` is positive/success/high-confidence.
*   Authorizing a new exercise based on a historically valid record that is currently revoked.
*   Failing to reject a delegation child that broadens the parent's scope.
*   Accepting canonical wire containing singular instead of plural (violating silent plural coercion ban).

## 13. Fields That Must Not Affect Common Authority
*   Payload domain-local `result` (positive, negative, indeterminate, success).
*   Supporting artifact identifiers that do not confer authority.

## 14. Unresolved Ambiguities and Post-Reveal Discriminators
*   Ambiguity: How strict is `record_id_consistency` if the map key is missing from the record entirely? Predicted discriminator: Will reject natively rather than defaulting.
*   Ambiguity: Are `separately_reauthorized` propagation checks evaluated at consumer-level or deferred? Predicted discriminator: Validated at the structural/schema level.
*   Ambiguity: What happens if `envelope` has a `kind` field embedded inside it that conflicts with the top-level `kind="envelope"`? Predicted discriminator: We prioritize the `EvaluationRequest.kind` strictly and ignore payload inner `kind` if any.
