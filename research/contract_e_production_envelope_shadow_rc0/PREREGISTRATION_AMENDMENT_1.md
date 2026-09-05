# Contract E Production Envelope Shadow RC0 — Preregistration Amendment 1

Status: **FROZEN BEFORE CANDIDATE IMPLEMENTATION**

Production authorization: **false**

Parent preregistration commit: `d879dddb07e0c4f4f1b6588cebddefa662e15829`

## Reason for amendment

During exact Contract D authority inspection after the parent preregistration and before any RC0 candidate implementation was created, the supervisor found that the released Contract D 1.0.0 authority already contains a canonical applicability consumer.

The experiment therefore MUST consume that existing boundary rather than reimplementing the rule that a valid `clear` Decision with an applicable effect becomes only `candidate_for_authorization`.

This amendment narrows the apparatus. It does not change any case expectation, falsifier, Contract E semantic rule, or production claim.

## Additional exact Contract D pins

Repository: `camerontjs-dot/apparatus-contracts`

Release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

- `validators/contract_d_core.py` blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- `validators/contract_d_validate.py` blob: `c03ef6c6f059cd03addf5e69b01025bb9a6af8d2`
- `validators/contract_d_consume.py` blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- Contract D schema blob: `6da9ee61b9e5011ab1ea068dd419c80caf6a2fac`
- effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`

## Required applicability rule

Before the shadow PEP may consider Contract E authorization, it MUST:

1. validate the exact Contract D object using the released Contract D implementation;
2. evaluate it through the exact released `contract_d_consume.consume()` boundary with an `ApplicabilityExpectation` that exactly binds:
   - input authority;
   - policy;
   - target;
   - requested operation `knowledge.add_verified_tag`;
   - requested effect parameter `scope=claim`;
3. require the consumer outcome to be exactly `candidate_for_authorization`.

Any other outcome, including `hold`, `evaluation_failed`, `not_applicable`, or `cannot_establish`, MUST fail closed before Contract E can produce a shadow allow.

The `decision_identity` returned by the released Contract D consumer MUST be preserved in RC0 evidence when available.

## Additional frozen negative cases

Add these cases to the parent frozen matrix:

- `NEG-CONTRACT-D-HOLD`: otherwise valid Contract D with `evaluation.disposition=hold` -> deny before Contract E authorization can yield shadow allow.
- `NEG-CONTRACT-D-NOT-APPLICABLE`: valid Contract D whose exact expected target/input/policy binding differs from the consuming expectation -> deny.
- `NEG-CONTRACT-D-EVALUATION-FAILED`: valid Contract D with `evaluation.state=failed` -> deny.

These are additional negative controls; no parent case is removed or weakened.

## Updated candidate sequence

Parent sequence step 2 is replaced by:

> Validate the exact Contract D bytes, run the exact released Contract D applicability consumer against a frozen expectation, require outcome `candidate_for_authorization`, and verify the research intent's Contract D digest/effect fields are exactly consistent with that consumed Decision.

All later parent steps retain their ordering.

## Stop rule

This amendment is frozen before candidate implementation. No later candidate observation may be used to revise the Contract D applicability rule or these added negative cases inside RC0.
