# Contract E Grok post-reveal comparison

Terminal disposition: **FALSIFIED**

This is a post-freeze comparison. The frozen consumer was imported and called directly; no frozen implementation file was modified.

## Execution receipts

- Frozen-suite integrity rerun: `PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_fresh_reproduction.run_tests`; exit 0; 73 passed, 0 failed, 0 errors, 73 total. Its tracked self-test receipt was restored to the frozen blob and was not included in this post-freeze commit.
- Comparison run: `PYTHONDONTWRITEBYTECODE=1 python3 -m research.contract_e_post_reveal_comparison.compare --reference-dir <verified-revealed-artifacts> ...`; exit 0; 234 vector evaluations, 2 false accepts, 15 false rejects, 10 reason disagreements, 4 execution deviations; semantic authority changes false.
- The three earlier exit-1 events were harness-only setup/reporting failures and are preserved in the machine receipt below; none evaluated or altered the frozen consumer.

## Revealed artifacts

- `FROZEN-CASES.json` — verified Git blob `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a` (18556 bytes)
- `AUTHORITY-BASIS-REGISTRY.json` — verified Git blob `76ea333ee0460d9614e9899edb69e6865e48eccb` (6766 bytes)
- `FROZEN-BASIS-ATTACKS.json` — verified Git blob `c726fb0ef914a850620e545131a70d427f4027bd` (4003 bytes)
- `HARDENING-PREREGISTRATION.md` — verified Git blob `1d85e2036d410b3af08d4b2b8926586da8fe6088` (2491 bytes)

## Vector counts

- `rc3a_envelope`: 31 vectors; 7 disagreements; 0 execution errors
- `rc3a_propagation`: 4 vectors; 2 disagreements; 0 execution errors
- `rc3a_delegation`: 4 vectors; 4 disagreements; 4 execution errors
- `rc3a_historical`: 2 vectors; 0 disagreements; 0 execution errors
- `rc3b_attack`: 13 vectors; 1 disagreements; 0 execution errors
- `compatibility_matrix`: 135 vectors; 3 disagreements; 0 execution errors
- `authority_reference_type_mutation`: 18 vectors; 0 disagreements; 0 execution errors
- `semantic_metamorphic`: 27 vectors; 9 disagreements; 0 execution errors

## False accepts / false rejects

- False accepts: 2
- False rejects: 15

## Reason disagreements

- `rc3a_envelope/N03-wrong-qualification` expected `qualification_type_mismatch`; raw actual violations `['missing_required_qualification']`; normalized actual classes `['missing_required_qualification']`
- `rc3a_envelope/N13-supported-does-not-cite` expected `missing_domain_authority_basis`; raw actual violations `['authority_basis_domain_mismatch']`; normalized actual classes `['authority_basis_domain_mismatch']`
- `rc3a_envelope/N14-decision-does-not-execute` expected `missing_domain_authority_basis`; raw actual violations `['authority_basis_domain_mismatch', 'warrant_not_allowed_for_domain', 'warrant_is_not_operational_permission']`; normalized actual classes `['authority_basis_domain_mismatch', 'warrant_is_not_operational_permission', 'warrant_not_allowed_for_domain']`
- `rc3a_envelope/N19-revoked-new-action` expected `authority_basis_not_current`; raw actual violations `[]`; normalized actual classes `[]`
- `rc3a_propagation/PROP-N02-decision-mandate` expected `authority_requires_reestablishment`; raw actual violations `['propagation_forbidden_field']`; normalized actual classes `['forbidden_authority_propagation', 'propagation_forbidden_field']`
- `rc3a_propagation/PROP-N03-task-dispatch` expected `authority_requires_reestablishment`; raw actual violations `['propagation_forbidden_field']`; normalized actual classes `['forbidden_authority_propagation', 'propagation_forbidden_field']`
- `rc3a_delegation/DEL-N01-operation-amplification` expected `delegation_operation_amplification`; raw actual violations `[]`; normalized actual classes `[]`
- `rc3a_delegation/DEL-N02-scope-amplification` expected `delegation_scope_amplification`; raw actual violations `[]`; normalized actual classes `[]`
- `rc3a_delegation/DEL-N03-expiry-amplification` expected `delegation_expiry_amplification`; raw actual violations `[]`; normalized actual classes `[]`
- `rc3b_attack/BASIS-N12-envelope-current-false` expected `authority_basis_not_current`; raw actual violations `[]`; normalized actual classes `[]`

## Shape / execution deviations

- `rc3a_envelope/P04-numeric` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `rc3a_envelope/P05-source-boundary` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `rc3a_envelope/P09-verify` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `rc3a_envelope/N03-wrong-qualification` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `rc3a_delegation/DEL-P01-narrower-child` — revealed delegation scope is a list preserved in optional record.scope; scope coercion was not applied
- `rc3a_delegation/DEL-N01-operation-amplification` — revealed delegation scope is a list preserved in optional record.scope; scope coercion was not applied
- `rc3a_delegation/DEL-N02-scope-amplification` — revealed delegation scope is a list preserved in optional record.scope; scope coercion was not applied
- `rc3a_delegation/DEL-N03-expiry-amplification` — revealed delegation scope is a list preserved in optional record.scope; scope coercion was not applied
- `compatibility_matrix/numeric_ok::grant:numeric-validation` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `compatibility_matrix/source_boundary_ok::policy:source-boundary` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `compatibility_matrix/verify_ok::grant:verify` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/numeric_ok::negative-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/numeric_ok::positive-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/numeric_ok::indeterminate-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/source_boundary_ok::negative-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/source_boundary_ok::positive-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/source_boundary_ok::indeterminate-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/verify_ok::negative-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/verify_ok::positive-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied
- `semantic_metamorphic/verify_ok::indeterminate-result` — revealed envelope.competence is a list of qualification objects; coercion to a singular object was not applied

- `rc3a_delegation/DEL-P01-narrower-child` — `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
- `rc3a_delegation/DEL-N01-operation-amplification` — `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
- `rc3a_delegation/DEL-N02-scope-amplification` — `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`
- `rc3a_delegation/DEL-N03-expiry-amplification` — `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`

## Semantic metamorphic result

- Payload mutations run: 27
- Authority-signature changes: 0

## Preregistered ambiguity correspondence

- `W1` (warrant required vs allowed): 100 vectors; 17 disagreements.
- `B1` (any-of vs all-of basis combination): 234 vectors; 26 disagreements.
- `R1` (in-memory resolver): 234 vectors; 26 disagreements.
- `H1` (explicit exercise_kind): 230 vectors; 22 disagreements.
- `T1` (validity-bound inclusivity): 2 vectors; 0 disagreements.
- `Q1` (qualification scope matching): 99 vectors; 16 disagreements.
- `S1` (stale-target definition): 98 vectors; 17 disagreements.
- `O1` (overall check order): 44 vectors; 8 disagreements.
- `D2` (delegation vs domain any_of via parent chain): 4 vectors; 4 disagreements.
- `G1` (generic authorized reject vs ignore): 1 vectors; 0 disagreements.

## Contamination / deviation status

- Reference reveal was limited to the four SHA-pinned artifacts listed above.
- No reference validator, generated reference RESULTS, workflow artifacts/logs, prior PR reasoning, or post-freeze repair was used by this harness.
- The pre-reveal marker remains exactly `FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL`; it was not rewritten to the requested vector-reveal literal.
