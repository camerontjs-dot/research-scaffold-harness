# CONTEXT-FREE REQUIRED — Contract E v1 Fresh Independent Reproduction RC1

You are executing a scientific clean-room reproduction of the frozen Contract E Authority Evaluation Candidate RC1.

Your independence is part of the evidence.

## 1. Scientific question

Determine whether the frozen public Contract E candidate semantics can be independently recovered and implemented from the allowed normative aperture alone.

You are testing **recoverability**, not trying to make a hidden evaluator pass.

A genuine disagreement is valuable evidence.

## 2. Exclusive pre-freeze information aperture

Before implementation freeze you may read **only** these three files on this exact RSH aperture branch/head:

1. `research/contract_e_v1_fresh_rc1_aperture/SPEC.md`
2. `research/contract_e_v1_fresh_rc1_aperture/schema.json`
3. `research/contract_e_v1_fresh_rc1_aperture/PRE_FREEZE_TASK.md`

The launch prompt supplies the exact branch and aperture-head identity.

Retrieve each allowed file only with exact file/path-scoped retrieval.

You may inspect the execution branch/ref identity through a branch/ref lookup. Do **not** inspect the branch commit object, pull request, tree, diff, patch, history, Actions, repository search results, README, or any unrelated file before freeze.

If a supposedly file-scoped retrieval unexpectedly exposes unrelated repository content, record contamination and stop `INCONCLUSIVE` rather than consume it.

## 3. Explicitly forbidden before freeze

Do not use or retrieve:

- `reference.py` from the Contract E candidate;
- `test_candidate.py` from the Contract E candidate;
- any Contract E hidden/sealed cases;
- any Contract E evaluator or qualification code;
- evaluator qualification receipts or seal receipts;
- expected outputs;
- RC0, RC0B, or earlier Contract E implementations/results;
- the earlier authority-chain RC1 fresh implementation, tests, evaluator, or result;
- Contract E semantic-recoverability reader outputs;
- qualification-binding or aggregation implementation behavior;
- Apparatus Contract E PR narratives or issues;
- other repositories or branches;
- project attachments or CAL Pipeline project context;
- prior chats, memory, personal context, summaries, or another agent's work;
- web search;
- general GitHub/repository exploration;
- a guessed or inferred answer key.

Do not ask another model/agent to inspect forbidden material on your behalf.

## 4. Implementation requirement

From only the allowed aperture, independently implement the candidate in Python using the standard library.

Required implementation path:

`research/contract_e_v1_fresh_rc1/authority_e.py`

Required public interface:

`evaluate(authority_state: dict, request: dict) -> dict`

You may create your own prereveal tests at:

`research/contract_e_v1_fresh_rc1/test_authority_e.py`

Your implementation must not call, import, copy, shell out to, or otherwise depend on any reference implementation, hidden evaluator, forbidden branch, or network service.

Implement what the public specification/schema require. Do not optimize for hypothetical hidden cases.

Where the public aperture is ambiguous, choose the interpretation you independently judge best supported and preserve the ambiguity in the freeze receipt. Do not manufacture certainty.

## 5. Required prereveal testing posture

Before freeze, create tests that you believe discriminate the public semantics. At minimum cover the important normative families you infer from the supplied aperture, including positive and fail-closed behavior.

Do not seek hidden examples or expected outputs.

Failures in your own prereveal tests are normal implementation work before freeze.

## 6. Freeze procedure

When you believe the implementation is complete:

1. run your prereveal tests;
2. ensure implementation and tests both exist at their required paths;
3. commit both files to the execution branch;
4. record the exact implementation commit;
5. record each frozen file's Git blob and SHA-256;
6. record the prereveal test command and result;
7. record explicit uncertainties, deviations, and contamination status;
8. write `research/contract_e_v1_fresh_rc1/FREEZE_RECEIPT.json` using the schema described below;
9. commit the freeze receipt as metadata only;
10. stop before reading any post-freeze reveal material.

After freeze, **do not modify `authority_e.py` or `test_authority_e.py`**. If later comparison shows disagreement, preserve it. A repaired implementation would be a successor experiment, not the same independent reproduction.

## 7. Freeze receipt required fields

`FREEZE_RECEIPT.json` must contain at least:

- `schema`: `contract-e-v1-fresh-rc1-freeze-receipt-v1`
- `marker`: `CONTRACT_E_V1_FRESH_RC1_FROZEN_BEFORE_REVEAL`
- `clean_base`: exact launch-supplied clean base
- `aperture_head`: exact launch-supplied aperture head
- `aperture_spec_blob`
- `aperture_spec_sha256`
- `aperture_schema_blob`
- `aperture_schema_sha256`
- `aperture_task_blob`
- `aperture_task_sha256`
- `implementation_commit`
- `implementation_path`
- `implementation_blob`
- `implementation_sha256`
- `test_path`
- `test_blob`
- `test_sha256`
- `prereveal_test_command`
- `prereveal_test_result`
- `contamination_status`
- `uncertainties` as an array
- `deviations` as an array

`contamination_status` must be one of:

- `CLEAN_PRE_FREEZE_APERTURE`
- `CONTAMINATED_PRE_FREEZE_APERTURE`

If contaminated, stop and report `INCONCLUSIVE`; do not continue to reveal.

## 8. Pre-freeze terminal return

Return only a compact freeze record containing:

- branch;
- implementation commit/blob/SHA-256;
- test blob/SHA-256;
- prereveal test result;
- contamination status;
- uncertainties/deviations;
- freeze-receipt commit.

Then stop.

Do not ask for the evaluator. Do not read anything outside the aperture. A separate normal-context supervisor will verify the freeze and, only if clean, provide the immutable post-freeze reveal authority.

## 9. Nonclaims

A successful prereveal implementation does not establish Contract E correctness, production promotion, root-authority legitimacy, execution permission, execution occurrence, or verification. It establishes only that you independently produced an implementation you believe follows the supplied public candidate.