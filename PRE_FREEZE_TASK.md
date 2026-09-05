# PRE-FREEZE TASK: RC5 Fresh Independent Two-Receipt Verifier

**CONTEXT-FREE REQUIRED**

Implement the verifier described only by the frozen RC5 public aperture supplied at launch. Do not seek project history or prior CAL implementations.

## Authorized inputs

Read only the exact files enumerated by `APERTURE-MANIFEST.json` at the exact frozen commit supplied by the supervisor launch prompt. The aperture is intended to contain `SPEC.md`, `RECEIPT-SCHEMA.json`, `TRUST-POLICY.json`, `PUBLIC-KEYS.json`, public positive vectors, `GENERATION-RECORD.json`, this task file, and the aperture manifest.

You may use installed general-purpose language and cryptography libraries. If a general-purpose dependency is added, freeze its exact version in your dependency manifest. Network access should remain off. If the execution surface requires a setup phase to install a general-purpose Ed25519 or RFC 8785 dependency, record the package/version and do not retrieve project-specific material.

## Forbidden before freeze

Do not access CAL RC3 or RC4 implementation, tests, runners, PR bodies, producer signing code, RC8J implementation, hidden evaluator or hidden mutation corpus, private signing keys, weak verifier implementation/results, expected hidden-case results, prior conversation/research narrative, the supervisor prompt that created this aperture, deep-research reports, or other independent verifier implementations. Do not browse other branches, repository history, issues, PRs, or unrelated files for orientation.

If any forbidden material is exposed before freeze, stop and record contamination. Do not relabel that implementation independent.

## Deliverable

Create a fresh independent verifier from the specification. It must:

- parse receipt transport and reject duplicate JSON keys;
- derive both semantic projections from request input;
- reconstruct RFC 8785 JCS signed bytes;
- verify Ed25519 signatures using public keys only;
- apply the explicit trust policy;
- enforce exact atom/proposition binding and pair compatibility;
- return typed ACCEPT or fail-closed refusal;
- contain no signing private key, shared HMAC secret, RC8J execution, CAL RC3/RC4 imports, or undocumented producer state.

Expose a deterministic command or testable entry point that accepts: semantic request JSON, atom receipt JSON, proposition receipt JSON, `PUBLIC-KEYS.json`, and `TRUST-POLICY.json`, and emits one result object matching `SPEC.md`. Do not implement receipt issuance.

## Self-authored prereveal tests

Before any post-freeze reveal, write tests from the public specification and positive vectors. Include at least: known-good atom, known-good proposition, known-good pair, stale semantic mutation refusal, malformed signature refusal, unknown signer refusal, duplicate-key refusal, wrong-context refusal, and exact-representation refusal for a swapped/inverse proposition unless separately signed.

## Freeze point

Before seeing any hidden evaluator material, freeze in GitHub:

1. implementation;
2. self-authored tests;
3. dependency manifest with exact versions;
4. exact source commit;
5. the exact aperture manifest actually read;
6. contamination declaration;
7. `PRE_FREEZE_RECEIPT.json`.

The freeze receipt must state that no prohibited implementation/evaluator material was accessed, list every material pre-freeze source opened, identify the model/runtime if exposed by the platform, and state that no private/shared signing material is present. Stop after durable write-back and prereveal test results. Do not reveal, compare, repair after reveal, promote, merge, or release.

Allowed pre-reveal terminal states: `READY_FOR_POST_FREEZE_REVEAL`, `INCONCLUSIVE_APERTURE_CONTAMINATION`, or `BLOCKED`.
