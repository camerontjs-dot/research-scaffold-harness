# PRE-FREEZE TASK — Contract E Dual-Identity Successor Fresh Independent Reproduction

## Scientific purpose

Independently recover and implement the behavior described by the frozen Contract E dual-identity successor public specification and machine schema.

This is a fresh clean-room reproduction. The goal is recoverability, not agreement with any unseen reference implementation or evaluator. A principled disagreement is scientific evidence and must be preserved.

Do not optimize for an evaluator you have not seen. Do not guess an answer key.

## Exclusive pre-freeze aperture

Before the implementation and prereveal tests are frozen, you may inspect only these exact three files at the exact execution branch/head supplied in the launch prompt:

1. `research/contract_e_v1_dual_identity_successor_aperture/SPEC.md`
2. `research/contract_e_v1_dual_identity_successor_aperture/schema.json`
3. `research/contract_e_v1_dual_identity_successor_aperture/PRE_FREEZE_TASK.md`

Retrieve them only by exact path/ref. You may perform a branch/ref lookup solely to verify that the execution branch points to the launch-supplied aperture head. Do not inspect the aperture commit object, tree, diff, PR, Actions, issues, history, repository search, README, or unrelated files.

If a supposedly file-scoped retrieval exposes unrelated repository/project content, stop and record `CONTAMINATED_PRE_FREEZE_APERTURE` and terminal state `INCONCLUSIVE`. Do not use leaked material.

## Forbidden pre-freeze inputs

Do not inspect, retrieve, use, infer from, or ask another model/agent about:

- any Contract E reference implementation;
- candidate tests, adversarial tests, pressure harnesses, or expected outputs;
- hidden cases;
- evaluator code, qualification logic, qualification evidence, evaluator seal receipts, or comparison results;
- any prior Contract E candidate implementation, evaluator, fresh reproduction, result, mismatch, reconciliation, or post-falsification analysis;
- any other Contract E branch, PR, issue, commit, tree, diff, workflow, release, or repository file;
- Contract A/B/C/D implementations, validators, fixtures, consumers, or pipeline behavior;
- Claim Audit Lab, Evidence Bundler, Decision Engine, CAL Pipeline, Mainframe, or other project-specific context;
- prior or parallel conversations, project memory, personal-context retrieval, summaries, or other agents' work;
- web search or external project research.

General programming-language knowledge and public standards knowledge are allowed. RFC 8785 is explicitly part of the supplied specification. You may either implement RFC 8785 behavior independently or use a general-purpose conforming RFC 8785 library. If you use a third-party JCS library, record its exact package/version in the freeze receipt. Do not inspect project reference code to learn canonicalization behavior beyond what the supplied SPEC states.

Do not inspect any Draft PR associated with this reproduction before the implementation freeze. Supervisor-facing PR metadata may contain material deliberately outside the aperture.

## Required implementation

Create a fresh implementation at:

`research/contract_e_v1_dual_identity_successor_fresh/authority_e.py`

It must expose:

```python
def evaluate(authority_state: dict, request: dict) -> dict:
    ...
```

Implement only what the supplied SPEC/schema establish. Do not import or invoke hidden/reference behavior.

You may create helper functions inside `authority_e.py`. Do not add project-specific dependencies.

## Required prereveal tests

Create your own prereveal tests at:

`research/contract_e_v1_dual_identity_successor_fresh/test_authority_e.py`

Exercise the semantics you believe the public contract determines. At minimum cover:

- positive root grant and policy authorization;
- delegation and non-amplification;
- exact subject/domain/operation/scope/target bindings;
- AuthorityState claimed and recomputed identities, including identity mismatch;
- RFC 8785 + one-LF canonical identity behavior;
- malformed/canonicalization-invalid input;
- currentness, inclusive validity boundaries, and revocation;
- relevant versus irrelevant conflicts/residues;
- supporting artifacts remaining non-conferring;
- immutable-reference identity and target resolution;
- preservation behavior on denials where input fields remain recoverable;
- receipt identity excluding diagnostics but including both AuthorityState identity facts.

Do not attempt to reconstruct hidden cases.

Run the tests before freezing. Preserve inconvenient tests/failures rather than deleting them merely to produce a green result.

## Interpretation uncertainty

If the SPEC/schema genuinely do not determine a behavior, record it explicitly in the freeze receipt. Choose the smallest fail-closed behavior justified by the public aperture. Do not silently import semantics from convention or imagined implementation behavior.

Do not modify the three aperture files.

## Immutable pre-reveal freeze

When implementation and prereveal tests are complete:

1. commit `authority_e.py` and `test_authority_e.py` so both exact states coexist at one immutable implementation freeze commit;
2. record that commit, both Git blob IDs, and both SHA-256 hashes;
3. record the prereveal test command, test count/result, and exit code;
4. record the Python/runtime version and any general-purpose RFC 8785 dependency/version used;
5. record interpretation uncertainties;
6. record contamination status and any apparatus deviations;
7. in a subsequent metadata-only commit, create `research/contract_e_v1_dual_identity_successor_fresh/FREEZE_RECEIPT.json`;
8. verify that the receipt commit changed no frozen implementation/test bytes;
9. stop before reveal.

The freeze receipt must contain at minimum:

- `schema`;
- an explicit pre-reveal freeze marker;
- `implementation_frozen: true`;
- `post_freeze_repair_permitted: false`;
- exact execution branch;
- exact clean base supplied by the launch prompt;
- exact aperture head supplied by the launch prompt;
- exact aperture file Git blobs supplied by the launch prompt;
- implementation freeze commit/path/blob/SHA-256;
- test path/blob/SHA-256;
- prereveal command/count/result/exit code;
- runtime and dependency information;
- uncertainties;
- contamination status;
- deviations.

## Post-freeze boundary

Do not inspect any reference implementation, evaluator, hidden cases, expected outputs, qualification evidence, seal material, or comparison packet until a separate supervisor verifies your freeze and explicitly authorizes post-freeze reveal.

After reveal, the frozen implementation and prereveal tests must remain immutable. A repair after observing reference/evaluator behavior is a different successor reproduction and cannot be counted as this run.

## Return

Return only a compact freeze record containing:

- execution branch;
- aperture head;
- implementation freeze commit/blob/SHA-256;
- test blob/SHA-256;
- prereveal test count/result;
- runtime/dependency information;
- uncertainties;
- contamination status;
- deviations;
- freeze-receipt commit.

Then stop.
