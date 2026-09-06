# CAL RC5A Evaluator Qualification Plan

Status: supervisor-side research apparatus. Not visible to a fresh implementer before freeze.

## Claim

The evaluator must discriminate:
1. normative security-class disagreement;
2. unsafe acceptance;
3. diagnostic collapse;
4. diagnostic instability under transport-only variants;
without requiring exact cross-implementation diagnostic strings.

## Required controls

The evaluator is not qualified merely because one reference implementation passes.

Before seal, it must catch at least these deliberately weak behaviors:

1. `weak_accept_wrong_role`: cryptographically valid wrong-role statements are accepted.
2. `weak_all_refusals_malformed`: every refusal is classified `MALFORMED`.
3. `weak_old_rc5_profile_as_schema`: unsupported receipt type/schema/signature profile are treated as malformed.
4. `weak_signature_format_as_malformed`: truncated Ed25519 signature is treated as malformed rather than `UNAUTHENTICATED`.
5. `weak_generic_diagnostic`: normative classes are correct but every refusal emits the same diagnostic tuple.
6. `weak_transport_sensitive_diagnostic`: semantically identical malformed input changes diagnostic tuple solely because whitespace/order changes.

## Oracle review

Before seal, an independent reviewer must inspect only:
- public `SPEC.md`;
- public `WIRE-SCHEMA.json`;
- public key/trust-policy shapes as needed;
- this hidden case manifest without candidate outputs.

The reviewer must confirm each hidden case's normative class and the declared transport/diagnostic relation.

Any material disagreement blocks seal.

## Seal prerequisites

- reference/conforming implementation passes all normative cases;
- all six weak controls are caught for their intended reason;
- no hidden case depends on an exact diagnostic token;
- public positive control accepts;
- wrong-role signatures are cryptographically valid;
- unknown-signer control signature is independently valid under KU but KU is absent from verifier public keys;
- hidden packet identity frozen;
- candidate/fresh implementation does not exist at evaluator seal.

Terminal qualification states:
- `QUALIFIED_FOR_FRESH_REPRODUCTION`
- `INCONCLUSIVE_ORACLE_DISAGREEMENT`
- `INCONCLUSIVE_CONTROL_ESCAPE`
- `BLOCKED`
