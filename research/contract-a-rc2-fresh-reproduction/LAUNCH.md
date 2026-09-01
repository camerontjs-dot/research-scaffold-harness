# CONTEXT-FREE REQUIRED — Contract A RC2 Fresh Independent Consumer Reproduction

Use this packet as the complete task input.

This is a scientific clean-room implementation. Your independence is part of the evidence.

Do not retrieve or use prior Contract A conversations, CAL Pipeline context, project memory, personal context, summaries, prior implementations, normal-context research results, field ablations, compatibility conclusions, evaluator results, or other agents' work.

Do not ask for routine clarification. Everything authorized before implementation freeze is already present in the aperture.

The objective is **recoverability**, not making an evaluator pass. A genuine disagreement or ambiguity is valuable evidence.

## 1. Repository and branch

Repository:

`camerontjs-dot/research-scaffold-harness`

Aperture branch:

`research/contract-a-rc2-fresh-reproduction-aperture-20260901`

Before implementation, read:

`research/contract-a-rc2-fresh-reproduction/APERTURE-MANIFEST.md`

Obey that manifest as the complete pre-freeze information boundary.

## 2. Pre-freeze normative authority

The only Contract A semantic authority you may use is:

- `research/contract-a-rc2-fresh-reproduction/public/SPEC.md`
- `research/contract-a-rc2-fresh-reproduction/public/schema.json`

Verify their exact Git blobs before implementation:

- `SPEC.md`: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `schema.json`: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`

If either identity differs, stop with `APERTURE_INTEGRITY_FAILURE`.

Do not inspect any reference validator, evaluator, fixtures, research results, Apparatus Contract A branch, sealed branch, or reveal packet before your implementation freeze.

## 3. Scientific question

Determine whether an independent implementer can recover a mechanically usable Contract A consumer from the frozen specification and schema alone.

Implement what the public authority actually requires. Do not add behavior because it seems useful.

## 4. Required independent implementation

Create a new implementation area under:

`research/contract-a-rc2-fresh-reproduction/independent/`

Use Python 3.11. Prefer the standard library unless a dependency is genuinely required.

Implement a small public consumer API that can, at minimum:

1. parse a Contract A RC2 JSON object;
2. validate the public schema-level shape and closed-field behavior;
3. enforce all integrity and cross-field invariants that the normative specification requires, including hashes, identities, source representation bindings, and declared-decomposition ordering/uniqueness rules;
4. fail closed on invalid required state rather than inventing defaults;
5. return the exact retrieval proposition targets implied by the declared decomposition state;
6. expose a mechanical source-contract proposition projection suitable for downstream consumption without inventing semantic authority;
7. preserve the distinction among `not_decomposed`, `failed`, `unknown`, and `declared`;
8. preserve exact supplied source representations and explicit empty-source state.

Do not implement Evidence Bundler retrieval quality, CAL NLI semantics, Contract B, Contract E, authorization, delegation, execution, trust judgment, support judgment, source reliability judgment, or decomposition correctness certification.

## 5. Independent prereveal tests

Author your own tests from the normative authority. Do not search for reference fixtures or expected outputs.

Your prereveal tests should exercise, at minimum:

- a valid undecomposed object;
- valid `failed` and `unknown` decomposition states;
- a valid declared `all_of` object;
- whole-object integrity verification;
- proposition text-hash verification;
- source content-hash verification;
- unknown/extra-field rejection;
- missing required identity rejection;
- duplicate or invalid child identity/order rejection where required by your reading;
- explicit empty `sources` behavior;
- retrieval-target projection for each decomposition state;
- downstream source-contract proposition projection.

If the public authority is ambiguous, record the ambiguity and your chosen interpretation **before reveal**. Do not silently guess and later erase the uncertainty.

## 6. Freeze protocol

Before reading any post-freeze material:

1. commit the independent implementation and prereveal tests;
2. record the exact commit SHA;
3. record the independent implementation subtree SHA;
4. record the prereveal test subtree SHA or exact file identities;
5. run the prereveal tests and record their result;
6. create an immutable prereveal freeze receipt under the independent area;
7. commit that receipt;
8. report the receipt commit SHA and all frozen identities.

After that receipt is committed, do **not** modify the independent implementation or prereveal tests after seeing reference behavior and then count the modified result as independent agreement.

Any post-reveal repair must be preserved separately and cannot erase the original disagreement.

## 7. Stop boundary

This packet authorizes only the pre-freeze independent implementation phase.

Do **not** search for, open, or infer a post-freeze evaluator/reveal packet on your own.

After the immutable prereveal freeze receipt is committed, stop and return:

- `PRE_REVEAL_FROZEN`;
- aperture branch/head used;
- normative blob identities verified;
- independent implementation commit/tree identities;
- prereveal test result;
- freeze-receipt commit;
- all prereveal ambiguities/uncertainties;
- any deviations or failures.

A separate explicit `POST-FREEZE REVEAL AUTHORIZED` instruction will provide the only authorized reveal location.

## 8. Nonclaims

A successful prereveal implementation does not prove agreement with the reference, authorize Contract A production promotion, assign a canonical version, or establish downstream semantic correctness.

Do not merge or promote anything as production authority in this run.
