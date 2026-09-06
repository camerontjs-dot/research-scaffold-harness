# CONTEXT-FREE REQUIRED

You are the fresh independent implementer for CAL RC5A security-class / diagnostic-separation verification.

Repository: `camerontjs-dot/research-scaffold-harness`

Your exclusive pre-freeze information aperture is the exact RC5A public aperture supplied by the supervisor. Do not inspect RC5 implementation branches, RC5 post-reveal material, RC5 evaluator/oracle results, supervisor branches, prior CAL receipt implementations, Claim Audit Lab RC3/RC4 code, RC8J code, web search, prior conversations, memory, or any answer-bearing material.

## Objective

Implement a public-only verifier for the two receipt classes exactly as specified by `SPEC.md`, using `WIRE-SCHEMA.json`, `PUBLIC-KEYS.json`, `TRUST-POLICY.json`, and the public positive vectors.

The verifier must:
- reconstruct RFC 8785 JCS signed bytes independently;
- verify Ed25519 signatures with public keys only;
- enforce exact scoped issuer authority;
- independently derive atom/proposition projections;
- enforce exact pair compatibility;
- emit the normative `protocol_result`;
- preserve an implementation-specific `audit_record`;
- contain no signing operation or private/shared secret;
- not rerun RC8J.

## Required implementation interface

Create:

`experiments/cal-rc5a-independent-verifier/rc5a_verifier.py`

with callable:

`verify_pair(semantic_request, atom_receipt_raw, proposition_receipt_raw, public_keys, trust_policy) -> dict`

`atom_receipt_raw` and `proposition_receipt_raw` are raw UTF-8 JSON strings so duplicate-key behavior remains testable.

Also create self-authored prereveal tests and a contamination declaration.

## Required prereveal tests

At minimum test:
- public positive pair accepts;
- whitespace/member-order transport invariance;
- duplicate-key refusal;
- structurally malformed refusal;
- unsupported profile refusal;
- digest mismatch refusal;
- signature-format refusal;
- invalid signature refusal;
- wrong-role issuer refusal;
- atom binding refusal;
- proposition binding refusal;
- incompatible pair refusal;
- diagnostics present;
- deterministic diagnostics on repeated identical input;
- transport-only representation changes preserve diagnostic tuple for the same defect;
- diagnostic tuple is not globally constant across distinct subcauses inside at least one failure class.

Do not infer hidden diagnostic strings.

## Freeze

Freeze implementation, prereveal tests, dependency record, contamination declaration, and a freeze receipt before any reveal.

Stop at the pre-reveal boundary.

Allowed pre-reveal terminal states:
- `FROZEN_CLEAN_PRE_REVEAL`
- `INCONCLUSIVE_APERTURE_CONTAMINATION`
- `BLOCKED`

No comparison, repair after reveal, promotion, merge, tag, or release is authorized.
