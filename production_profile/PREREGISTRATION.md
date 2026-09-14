# Contract C 2.0 Promotion Consumer B Conformance RC0

Classification: Draft Research / production-promotion conformance evidence. Do not merge for production behavior.

## Decision sentence

If exact frozen Consumer B `ba09743b28e57bc87dd1f315046ef79b93f24021`, without modification, continues to pass its 38-case prereveal suite and consumes all four exact authoritative handoffs after those same bytes are independently validated by exact Contract C 2.0 promotion head `b42c827acb0a9fe65353354d709add0e27bab307`, record `SUPPORTED_C2_PROMOTION_INDEPENDENT_CONSUMER_CONFORMANCE`.

If the production adapter changes canonical bytes/identity, rejects a legitimate frozen handoff, accepts only after a consumer change, loses a public terminal/basis distinction, or requires producer-private state, record `FALSIFIED`.

Harness/evaluator failure is `INCONCLUSIVE_EVALUATOR_INVALID`.

## Frozen independent subject

Exact Consumer B subject: `ba09743b28e57bc87dd1f315046ef79b93f24021`.

Required unchanged blobs:

- `candidate/consumer.py`: `1f0e64d22f11d7dbe620fef209852870e6b5203d`;
- `candidate/test_consumer.py`: `54e03ff388974fb3524b164c17b7af9f7cf9870c`;
- `candidate/FREEZE_RECEIPT.json`: `1f57979b23eb37d8611acfb58b288e4952eaa717`;
- `AUTHORITIES.json`: `3f4ec7063679f5fb5e2797eb553ec2886275d225`;
- `CONTRACT_B_INDEXES.json`: `7aad2771f603c724c44e948863f1fd8f0bad14e2`;
- independent-supports handoff: `ddb4f97d1815b56e966f9f7e184b25b049dcb98c`;
- alternative-joint handoff: `fb2eb1872d2a17229caf79fbd6d7a311aae3e2c9`;
- no-deciding handoff: `e82a560d58871653c993640ceae887b98b1dbd20`;
- unsupported-family handoff: `efa7cd5226bb17d749f1b494c897775564c9ac33`.

Original independent evidence:

- prereveal suite 38/38 PASS;
- contamination state `clean`;
- forbidden inputs `[]`;
- post-reveal terminal in PR #31: `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE`;
- 27/27 adversarial mutations rejected;
- weak consumer accepted 15/27 attacks and was killed.

This gate does not recreate independence. It tests whether the already-independent frozen consumer remains a valid consumer of the exact production-promotion profile.

## Exact production subject

Apparatus Draft PR #98, exact locally-qualified head:

`b42c827acb0a9fe65353354d709add0e27bab307`

Local promotion run `34804396671` is green across Python 3.11/3.12/3.13.

Candidate compatibility version: `2.0.0`.

Frozen wire profile: `contract-c-successor-candidate-a-rc2-research`.

Global discovery intentionally remains C1 while pre-merge gates are open.

## Required checks

1. Verify all frozen Consumer B/aperture blobs above exactly.
2. Run frozen `candidate/test_consumer.py` unchanged and require 38/38 PASS.
3. Checkout exact Apparatus promotion head and verify its frozen RC2/production-adapter identities.
4. For each of the four authoritative handoffs:
   - parse the exact frozen raw bytes;
   - validate under production `validators.contract_c_v2`;
   - verify exact Contract-B references from the frozen independent index;
   - verify producer/policy/resolver against independently supplied frozen authority;
   - verify whole-object SHA-256 against independently supplied frozen authority;
   - require production canonical bytes equal the exact frozen handoff bytes;
   - call frozen Consumer B with the same raw bytes/index/authority;
   - preserve the expected terminal/basis semantics.
5. Require production public candidate version `2.0.0` to remain external to the frozen wire profile.
6. Require global Contract C discovery to remain C1 during this pre-merge gate.

## Expected public semantics for the four authoritative handoffs

- `independent_supports`: `supported / categorical_support`, two independent singleton basis groups;
- `alternative_joint_mixed`: `not_checkable / MIXED_RELATIONS`, two two-member alternative joint basis groups;
- `no_deciding`: `not_checkable / no_deciding_relation`, empty basis groups, non-polarized residual evidence;
- `unsupported_family`: `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`, empty basis groups, only non-polarized residual evidence.

## Nonclaims

This gate does not re-run the 27-attack post-reveal programme, assign canonical C2 discovery, establish C2/C1 compatibility by itself, establish Decision Engine support, merge/release Contract C, or authorize execution.

The separate compatibility/adversarial promotion matrix remains required after this gate.