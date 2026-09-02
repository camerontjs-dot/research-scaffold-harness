# PRE-FREEZE TASK — Contract E RC3 Fresh Independent Reproduction

## Scientific purpose

Independently recover and implement the behavior described by the frozen Contract E RC3 public specification and machine schema.

This is a **fresh clean-room reproduction**. The objective is recoverability and independent agreement, not evaluator passing. A principled disagreement is scientific evidence and must be preserved.

Do not optimize for an evaluator you have not seen. Do not infer or construct an answer key.

## Exclusive pre-freeze information aperture

Before your implementation and prereveal tests are frozen, you may inspect only these three repository files at the exact execution branch/head supplied by the operator launch prompt:

1. `research/contract_e_v1_fresh_rc3_aperture/SPEC.md`
2. `research/contract_e_v1_fresh_rc3_aperture/schema.json`
3. `research/contract_e_v1_fresh_rc3_aperture/PRE_FREEZE_TASK.md`

Retrieve them only by exact path and exact ref. You may perform the minimum branch/ref lookup necessary to confirm that the named execution branch points to the supplied aperture head.

Do not inspect the aperture commit diff, surrounding tree, branch history, pull request body, Actions history, issues, README, repository search results, or unrelated files before the implementation freeze.

If an allegedly file-scoped retrieval exposes unrelated project/repository content, stop and record `CONTAMINATED_PRE_FREEZE_APERTURE`; do not use the leaked information.

## Forbidden pre-freeze inputs

Do not inspect, retrieve, use, infer from, or ask another agent/model about:

- any Contract E RC3 reference implementation;
- candidate tests, adversarial suites, pressure harnesses, integration profiles, or frozen candidate receipts;
- hidden cases, expected outputs, evaluator code, qualification code, evaluator qualification results, or seal receipts;
- Contract E RC1/RC2 implementations, reproductions, mismatches, falsifiers, diagnostics, reconciliation, or historical research;
- other Contract E branches, PRs, issues, workflows, commits, docs, or repository files;
- Contract A/B/C/D implementations, fixtures, validators, consumers, or release internals;
- Claim Audit Lab, Evidence Bundler, Decision Engine, CAL Pipeline, Mainframe, or other project-specific context;
- previous or parallel conversations, project summaries, memory/personal-context retrieval, or other agents' work;
- web search or external project research.

General programming-language/standard-library knowledge is allowed.

### Public RFC 8785 allowance

RFC 8785 JCS is an explicit normative dependency of the public RC3 specification, not hidden project behavior.

You may use a public RFC 8785 implementation as a dependency. For Python, `rfc8785==0.1.4` is explicitly allowed if available. You may also independently implement the required RFC 8785 behavior from your existing knowledge.

Do not browse RFC 8785 implementation source, issue history, project tests, or external examples during this run. If you use the public library, treat it as a standards primitive, not as a source of Contract E semantics.

No other non-standard/project-specific dependency is authorized pre-freeze unless it is already part of the ordinary runtime and does not convey Contract E behavior.

## Required implementation

Create a fresh implementation at:

`research/contract_e_v1_fresh_rc3/authority_e.py`

It must expose:

```python
def evaluate(authority_state: dict, request: dict) -> dict:
    ...
```

Implement the public SPEC/schema exactly as you understand them.

Do not import, invoke, copy, adapt, or reconstruct a hidden/reference Contract E implementation.

Keep project-specific behavior in `authority_e.py`. Standard-library helpers and the explicitly allowed RFC 8785 dependency are permitted.

## Required prereveal tests

Create your own tests at:

`research/contract_e_v1_fresh_rc3/test_authority_e.py`

The prereveal tests should be derived from your interpretation of the public aperture, not from guessed hidden cases.

At minimum, test the semantics you believe the public contract determines across:

- positive exact authorization;
- subject/domain/operation/scope/target binding;
- valid and invalid delegation;
- claimed versus recomputed AuthorityState identities;
- request/state identity binding;
- RFC 8785 + LF deterministic identities/hashes, including numeric/Unicode edge behavior you believe is required;
- exact fractional timestamp ordering beyond host microsecond precision;
- inclusive `valid_from` / `valid_until` and revocation boundary behavior;
- reference integrity and request-local uniqueness;
- supporting-artifact non-conferral and local reference resolution;
- conflict/residue fail-closed behavior, including resolution requests;
- malformed/unknown fields;
- safe preservation;
- receipt semantic identity;
- diagnostic non-authority.

Preserve test failures and interpretation disagreements rather than deleting inconvenient cases merely to obtain a green result.

## Execution infrastructure

Run your prereveal tests before freezing.

You may use local Python execution or a minimal hosted execution mechanism if required by your available tools. Execution infrastructure does not widen the information aperture.

If a hosted workflow is required, it may:

- check out only the execution branch;
- install exactly `rfc8785==0.1.4` if your implementation depends on it;
- run your own prereveal tests;
- emit hashes/receipts for your own files.

It must not retrieve other branches, candidate/reference code, evaluator material, other contract repositories, or project research.

Record any execution-infrastructure file or deviation in your freeze receipt. Infrastructure is not part of the scientific implementation identity unless you explicitly say otherwise.

## Interpretation uncertainties

If the public SPEC/schema genuinely underdetermines behavior, record the uncertainty before reveal.

Choose the smallest fail-closed behavior you believe is justified where an implementation choice is unavoidable, but do not claim the text determined what it did not determine.

In particular, do not resolve uncertainty by searching for historical Contract E behavior or by guessing what a hidden evaluator probably expects.

## Freeze

When implementation and prereveal tests are complete:

1. commit `authority_e.py` and `test_authority_e.py`;
2. record the exact commit at which both frozen files coexist;
3. record the exact Git blob ID and SHA-256 of `authority_e.py`;
4. record the exact Git blob ID and SHA-256 of `test_authority_e.py`;
5. record the exact prereveal test command/mechanism, count, result, and exit status;
6. record all interpretation uncertainties;
7. record contamination status;
8. record any apparatus deviations;
9. create `research/contract_e_v1_fresh_rc3/FREEZE_RECEIPT.json` in a subsequent metadata-only commit;
10. verify that the receipt commit did not change either frozen implementation/test blob;
11. stop.

The freeze receipt must explicitly contain or state:

- `implementation_frozen: true`;
- `post_freeze_repair_permitted: false`;
- exact execution branch;
- exact aperture head supplied by the operator;
- exact implementation freeze commit;
- implementation blob and SHA-256;
- prereveal-test blob and SHA-256;
- prereveal test result/count/exit status;
- whether `rfc8785==0.1.4` or an independent JCS implementation was used;
- interpretation uncertainties;
- contamination status;
- apparatus deviations.

## Post-freeze rule

Do not inspect any evaluator, hidden case, expected result, project reference implementation, qualification artifact, or post-freeze reveal material until a separate supervisor verifies your freeze and explicitly authorizes reveal.

After reveal, the frozen implementation and prereveal tests are immutable. A repair after observing reference/evaluator behavior is a different successor reproduction and cannot count as this run.

No adapter, compatibility shim, field translation, fallback default, diagnostic normalization, or coercion may be inserted between the frozen implementation and a later sealed evaluator unless a post-freeze packet explicitly authorizes it. A disagreement is evidence.

## Terminal boundary for this phase

This task ends at the verified pre-reveal freeze.

Do not independently search for an evaluator or reference implementation. Do not continue into comparison.

Return only a compact freeze record containing:

- execution branch;
- aperture head used;
- implementation freeze commit/blob/SHA-256;
- test blob/SHA-256;
- prereveal test count/result/exit status;
- JCS dependency choice;
- interpretation uncertainties;
- contamination/deviation status;
- freeze receipt commit.

Then stop.
