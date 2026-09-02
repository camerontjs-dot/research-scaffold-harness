# PRE-FREEZE TASK — Contract E RC2 Fresh Independent Reproduction

## Scientific purpose

Independently recover and implement the behavior described by the frozen Contract E RC2 public specification and machine schema.

This is a **fresh clean-room reproduction**. The goal is recoverability, not agreement with an unseen reference implementation or evaluator. A principled disagreement is scientific evidence and must be preserved.

Do not optimize for an evaluator you have not seen. Do not guess an answer key.

## Exclusive pre-freeze information aperture

Before your implementation and prereveal tests are frozen, you may inspect only these three files on the exact execution branch/head supplied by the operator launch prompt:

1. `research/contract_e_v1_fresh_rc2_aperture/SPEC.md`
2. `research/contract_e_v1_fresh_rc2_aperture/schema.json`
3. `research/contract_e_v1_fresh_rc2_aperture/PRE_FREEZE_TASK.md`

Retrieve them only by exact path. You may verify the exact execution branch/head named by the launch prompt, but do not browse the surrounding tree, commits, diffs, PR, Actions, issues, history, or repository contents.

If an allegedly file-scoped retrieval exposes unrelated repository or project content, stop and record the run `INCONCLUSIVE` for contamination rather than using that information.

## Forbidden pre-freeze inputs

Do not inspect, retrieve, use, infer from, or ask another agent/model about:

- any Contract E RC2 reference implementation;
- candidate tests or adversarial harnesses;
- hidden cases or expected outputs;
- evaluator code, qualification logic, seal receipts, or evaluator results;
- the Contract E RC1 implementation, evaluator, reproduction, mismatch IDs, or reconciliation;
- D→E pressure-test code or results;
- other Contract E research branches, PRs, issues, docs, commits, or repository files;
- Contract A/B/C/D implementations, fixtures, validators, or consumers;
- Claim Audit Lab, Evidence Bundler, Decision Engine, CAL Pipeline, Mainframe, or other project-specific context;
- prior or parallel conversations, summaries, project memory, personal-context retrieval, or other agents' work;
- web search or external project research.

General programming-language and standard-library knowledge is allowed. The implementation should not require network access or third-party project-specific libraries.

Do not inspect the Draft PR for this reproduction before the implementation freeze. Its body is supervisor-facing and may contain post-freeze evaluator provenance that is deliberately outside your aperture.

## Required implementation

Create a fresh implementation at:

`research/contract_e_v1_fresh_rc2/authority_e.py`

It must expose:

```python
def evaluate(authority_state: dict, request: dict) -> dict:
    ...
```

Implement the public SPEC/schema as you understand them. Do not import or invoke a hidden/reference implementation.

You may create helper functions in the same file. Keep the implementation self-contained unless a standard-library module is sufficient.

## Required prereveal tests

Create your own tests at:

`research/contract_e_v1_fresh_rc2/test_authority_e.py`

Your prereveal tests should exercise the semantics you believe the public contract determines, including positive, negative, malformed, identity, currentness/revocation, delegation, preservation, and receipt-identity behavior. Do not attempt to reconstruct hidden cases.

Run the tests before freezing. Preserve failures rather than deleting inconvenient tests merely to obtain a green result.

## Interpretation uncertainties

If the public SPEC/schema leaves any behavior genuinely underdetermined, record the uncertainty in your freeze receipt. Choose the smallest fail-closed implementation you believe is justified, but do not silently pretend the text determined more than it did.

Do not alter the public aperture files.

## Freeze

When implementation and prereveal tests are complete:

1. commit `authority_e.py` and `test_authority_e.py`;
2. record the exact implementation/test commit and Git blob IDs;
3. record SHA-256 hashes of both files;
4. record prereveal test command/result;
5. record any interpretation uncertainties;
6. record contamination status and any apparatus deviation;
7. create `research/contract_e_v1_fresh_rc2/FREEZE_RECEIPT.json` in a subsequent metadata-only commit;
8. verify the receipt commit did not alter the frozen implementation/test blobs;
9. stop.

The freeze receipt must explicitly state:

- `implementation_frozen: true`;
- `post_freeze_repair_permitted: false`;
- exact execution branch;
- exact aperture head supplied by the operator;
- exact implementation commit/blob/SHA-256;
- exact prereveal-test blob/SHA-256;
- prereveal test result;
- uncertainties;
- contamination status;
- deviations.

## Post-freeze rule

Do not inspect any evaluator, reference implementation, hidden cases, expected outputs, or post-freeze reveal material until a separate supervisor explicitly verifies your freeze and provides a post-freeze reveal authorization.

After reveal, your frozen implementation and prereveal tests must remain immutable. A repair after observing reference/evaluator behavior is a different successor reproduction and cannot be counted as this run.

## Terminal boundary for this phase

This task ends at the verified pre-reveal freeze. Do not independently search for an evaluator or continue into comparison.

Return a compact freeze record containing:

- execution branch;
- aperture head used;
- implementation commit and blob;
- test blob;
- prereveal test count/result;
- uncertainties;
- contamination/deviation status;
- freeze receipt commit.

Then stop.