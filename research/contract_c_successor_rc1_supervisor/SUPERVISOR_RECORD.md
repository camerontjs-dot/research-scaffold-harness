# Contract C Successor RC1 — Supervisor Preparation Record

**Classification:** Draft Research Infrastructure / clean-room supervisor record. This file is not part of the fresh implementer aperture and must not be shown to the implementer before freeze. It does not authorize merge, release, version assignment, promotion, production use, or evaluator reveal.

## Objective

Prepare a fresh independent reproduction of a research-only Contract C successor representation that preserves a neutral `non_deciding` retained contribution channel under the existing Contract C ownership boundary, without exposing prior implementations, fixtures, evaluator logic, reference results, or CAL/Decision research to the fresh implementer.

This supervisor record captures preparation state only. It is deliberately on a branch based from harness `main`, not on the fresh execution branch, and is not an ancestor of that execution branch.

## Live harness base at preparation

- repository: `camerontjs-dot/research-scaffold-harness`
- live `main`: `548bfa81f65290eda15af658f647497679b840ef`

## Frozen public aperture

Aperture branch:

`research/contract-c-successor-rc1-fresh-aperture-20260910`

Final frozen aperture head:

`04560a7311a510c8ee4c82ad401b35bd7ca7590c`

The only pre-freeze project files authorized to the implementer are:

1. `research/contract_c_successor_rc1_fresh_aperture/SPEC.md`
   - Git blob: `04d07b92f48a1dcb67cf5ebe58d74e985cdad150`
2. `research/contract_c_successor_rc1_fresh_aperture/schema.json`
   - Git blob: `290259d60722553698e5cdddb8a02fa50ec2f3d0`
3. `research/contract_c_successor_rc1_fresh_aperture/PRE_FREEZE_TASK.md`
   - Git blob: `663b27cfc1df2c1ede1fb76fadf2a901808d2b3d`

The aperture uses the non-canonical research sentinel:

`research-contract-c-successor-rc1`

It exposes semantic/validation obligations but no prior implementation, prior fixture, expected output, prior result, PR lineage, evaluator, or answer key.

## Fresh execution branch

Execution branch:

`research/contract-c-successor-rc1-fresh-independent-execution-20260910`

Verified execution head after evaluator qualification:

`04560a7311a510c8ee4c82ad401b35bd7ca7590c`

Thus the execution branch remains exactly the three-file aperture head. No supervisor/evaluator commit is its ancestor after that point. This contaminated supervisor session must not implement on that branch.

## Aperture preparation deviations

The aperture preparation itself had repository-packaging deviations before any fresh implementer was launched or exposed:

1. An all-three-file Git tree/commit was created as `2933969274ee90f305dad4ccac4c3338aabcef35`, but the aperture branch ref was not moved to it before a subsequent contents-API write.
2. A later contents write produced `a0d62effcd93c05c522df6852080c5cbbbc52cf0` with an unhelpful `noop` commit message and incomplete aperture packaging.
3. An intermediate sibling/ancestor preparation commit `737e37eaf4f171202f63e8c3196eda33f556cc4d` still lacked the complete final three-file aperture.
4. The branch was then completed at `04560a7311a510c8ee4c82ad401b35bd7ca7590c`, whose three authorized file blobs are pinned above.

These are preparation/hygiene deviations, not scientific reproduction events. No context-free implementer had been launched before the final head was frozen, so they do not constitute implementer contamination. They must nevertheless remain part of the audit trail.

## Sealed evaluator

Sealed evaluator branch:

`sealed/contract-c-successor-rc1-fresh-eval-20260910`

Qualified evaluator head:

`6685bd9dc99fca6eff5398c9dc8bb4fd635d0c84`

Pinned sealed assets:

- evaluator blob: `8a15f745d10994235f908a7c2c5828354edfec57`
- known-good qualification adapter blob: `c98f7ef2edb2998782259083d8da9e480e1bf411`
- final mutant-wrapper blob: `bfad010e25c780846a7b418895a1e3c058c88c66`
- qualification oracle head: Apparatus `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`
- oracle released-validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- oracle research-shadow blob: `76df0c956a80ee5160c1da9bb27c5d0ffafeda40`

The evaluator constructs its own fixtures, canonical bytes, result identities, and hostile cases. The fresh candidate therefore cannot pass merely by using its own faulty canonicalizer to construct evaluator inputs.

The hidden matrix contains 62 checks spanning valid polarized/neutral forms, neutral causal versus residual state, independent-sufficient multiplicity, execution/conclusion consistency, contribution classification, causal cardinality, rule/measurement references, exact Contract-B binding, policy/result identities, exact whole-object hashes, canonicalization, array-order identity effects, duplicate-key rejection, non-finite numbers, UTF-8, and unknown fields/vocabulary.

## Preserved evaluator-qualification failure

Qualification run `34533603698` at sealed head `3a8e85be74ecc7b7b2bcb6e50513712a13b18cf4` did not establish evaluator qualification.

Observed:

- aperture ancestry and blob pins passed;
- exact Apparatus oracle checkout and identity pins passed;
- evaluator compilation passed;
- the known-good adapter passed all 62 evaluator checks;
- targeted mutation qualification then became apparatus-invalid because the `canonicalize_before_validate` and `repair_unclassified` mutant wrappers could crash on the evaluator's malformed/non-finite JSON case instead of emitting a normal mutant result; the summarizer consequently lacked an expected mutant result file.

This is `INCONCLUSIVE_EVALUATOR_QUALIFICATION_APPARATUS_INVALID`, not Contract C evidence and not evidence against the evaluator semantics. No change to the sealed evaluator or public aperture was justified by that failure.

## Qualification repair

Only qualification-mutant apparatus was repaired:

- previous mutant blob: `a65ed98deb08862cb419d5dc4d651825dc1ac79e`
- repaired mutant blob: `bfad010e25c780846a7b418895a1e3c058c88c66`
- repair commit / final qualified head: `6685bd9dc99fca6eff5398c9dc8bb4fd635d0c84`

The repair catches malformed/non-finite normalization failures in the intentionally bad wrappers and delegates them back to the reference path so each mutant remains a defined bad implementation instead of crashing the qualification harness.

The following remained byte-stable across the repair:

- public aperture `SPEC.md`, `schema.json`, `PRE_FREEZE_TASK.md`;
- evaluator blob `8a15f745d10994235f908a7c2c5828354edfec57`;
- known-good reference adapter blob `c98f7ef2edb2998782259083d8da9e480e1bf411`;
- fresh execution branch/head.

## Successful evaluator qualification

Decisive qualification run:

`34533845520`

Exact tested head:

`6685bd9dc99fca6eff5398c9dc8bb4fd635d0c84`

Observed:

- frozen aperture ancestry/blob checks: PASS;
- sealed-only mutation-surface check: PASS;
- exact qualified Apparatus oracle identities: PASS;
- known-good evaluator cohort: `62/62` PASS;
- targeted mutant cohort: all 7 mutants killed;
- qualification disposition: `SUPPORTED_EVALUATOR_QUALIFIED`.

Targeted mutants killed:

- `accept_all`
- `reject_all`
- `reject_neutral`
- `ignore_contract_b`
- `ignore_whole_hash`
- `canonicalize_before_validate`
- `repair_unclassified`

Evidence artifact:

- artifact ID: `10174584299`
- digest: `sha256:dd4303af6ba0c290021dc3be2b7453f0805764aa3df7946d646eb6c61f5a4d30`
- artifact size: 2304 bytes

## Scientific boundary after qualification

The evaluator is qualified to compare a future frozen implementation against this exact bounded public specification. This does not make the underlying Contract C successor correct or promotion-ready.

The next costly-to-fake evidence is a fresh implementation produced under the three-file aperture, frozen before any evaluator/reference reveal.

This supervisor session is contaminated by prior Contract C implementation/evaluator knowledge and therefore **must not** act as that implementer. Doing so would destroy the clean-room claim.

## Exact launch boundary for a fresh implementer

A context-free implementer should receive only:

- repository: `camerontjs-dot/research-scaffold-harness`
- execution branch: `research/contract-c-successor-rc1-fresh-independent-execution-20260910`
- required starting/aperture head: `04560a7311a510c8ee4c82ad401b35bd7ca7590c`
- the three exact aperture paths listed above
- an instruction to follow `PRE_FREEZE_TASK.md` exactly and stop after producing/verifying its freeze receipt.

It must not be given this supervisor record, sealed evaluator branch/name, qualification run, prior Contract C PRs/results, or any prior implementation context before freeze.

## Reveal rule

Do not reveal or run the sealed evaluator against the future candidate until a supervisor independently verifies:

- execution branch started exactly from `04560a7311a510c8ee4c82ad401b35bd7ca7590c`;
- implementation and prereveal-test blobs are frozen;
- prereveal tests were executed and recorded;
- freeze receipt is metadata-only relative to those two blobs;
- contamination status is clean;
- no post-freeze repair has occurred.

Only then may a separate post-freeze comparison consume the sealed evaluator.

## Not established

- fresh independent reproduction outcome;
- evaluator agreement with an unseen independent implementation;
- canonical Contract C successor version;
- production migration or promotion;
- root / `all_of` CAL composition;
- arbitrary semantic-family sufficiency;
- Contract E or operational authorization.
