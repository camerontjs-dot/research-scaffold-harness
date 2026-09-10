# PRE-FREEZE TASK — Contract C Successor RC1 Fresh Independent Reproduction

## Scientific purpose

Independently implement and test the behavior described by the frozen Contract C successor RC1 public specification and machine schema.

This is a **fresh clean-room reproduction**. The objective is recoverability and independent agreement, not evaluator passing. A principled disagreement, ambiguity, or failure is scientific evidence and must be preserved.

Do not optimize for an evaluator you have not seen. Do not infer or construct an answer key.

## Exclusive pre-freeze information aperture

Before the implementation and your prereveal tests are frozen, you may inspect only these three files at the exact execution branch/head supplied by the operator launch prompt:

1. `research/contract_c_successor_rc1_fresh_aperture/SPEC.md`
2. `research/contract_c_successor_rc1_fresh_aperture/schema.json`
3. `research/contract_c_successor_rc1_fresh_aperture/PRE_FREEZE_TASK.md`

Retrieve them only by exact path and exact ref. You may perform only the minimum branch/ref lookup necessary to confirm that the named execution branch points to the supplied aperture head.

Do not inspect the aperture commit diff, branch history, surrounding repository tree, pull requests, issues, Actions history, README, DECISIONS, repository search results, other branches, tags, or unrelated files before freeze.

If an allegedly file-scoped retrieval exposes unrelated project/repository content, stop and record `CONTAMINATED_PRE_FREEZE_APERTURE`; do not use the leaked information.

## Forbidden pre-freeze inputs

Do not inspect, retrieve, use, infer from, or ask another agent/model about:

- any prior or reference Contract C implementation, validator, producer, exporter, fixture, candidate, shadow, sidecar, adapter, migration experiment, or version-compatibility experiment;
- Contract C 1.0 source/schema/validator/release internals outside the three aperture files;
- hidden cases, expected outputs, evaluator code, qualification code, evaluator qualification results, frozen reference receipts, or answer keys;
- Claim Audit Lab implementation/research, Decision Engine implementation/research, Evidence Bundler, Contract A/B/D/E implementation/research, CAL Pipeline project state, MainFrame, or related repositories;
- prior or parallel conversations, summaries, memory/personal-context retrieval, or another agent's work;
- web search or external project research.

General Python and standard-library knowledge is allowed.

No project-specific dependency is authorized pre-freeze. Implement the required behavior from the public aperture using the Python standard library unless a dependency is already part of the ordinary language/runtime and conveys no project semantics. If you believe the supplied JSON Schema requires a third-party validator, do not fetch one merely to match hidden behavior; you may implement the structural checks directly.

## Required implementation

Create a fresh implementation at:

`research/contract_c_successor_rc1_fresh/contract_c_successor.py`

It must expose at least:

```python
def canonical_bytes(value: dict) -> bytes:
    ...

def result_set_identity(value: dict) -> str:
    ...

def validate_contract_c_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict | None = None,
) -> list[str]:
    ...
```

An empty list means valid. Invalid input must yield at least one error string. Exact error wording is not part of the contract.

Do not import, invoke, copy, adapt, or reconstruct any hidden/reference Contract C implementation.

Do not add a pre-validation adapter, coercion, downgrade path, channel relabeling, field deletion, or compatibility shim.

## Required prereveal tests

Create your own tests at:

`research/contract_c_successor_rc1_fresh/test_contract_c_successor.py`

The tests must be derived only from your interpretation of `SPEC.md` and `schema.json`.

At minimum, test the semantics you believe the public contract determines across:

- valid canonical object construction and validation;
- exact research version sentinel and exact-version rejection;
- `support`, `counterevidence`, and `non_deciding` contributions;
- causal versus residual neutral contributions;
- independent-sufficient neutral multiplicity with at least two causal members;
- mixed contribution channels without inventing channel polarity rules beyond validation;
- proposition/result execution-state consistency;
- completed result-set non-empty requirement;
- unique proposition/contribution/basis/rule/residual identities as specified;
- contribution classification completeness and causal/residual disjointness;
- causal-form cardinality;
- measurement basis reference integrity;
- rule-role reference integrity;
- exact Contract-B top-level, proposition, and evidence-reference binding when an index is supplied;
- policy canonical-payload hash binding;
- deterministic result-set identity;
- exact external whole-object SHA binding;
- canonical key ordering, compact separators, Unicode behavior, exact trailing LF, array-order byte identity, duplicate-key rejection, and non-finite-number rejection;
- unknown field/vocabulary rejection;
- no-downgrade behavior: successor bytes are not accepted as another Contract C version merely because fields can be mechanically changed.

Where the public specification leaves behavior genuinely underdetermined, record the uncertainty. Prefer the smallest fail-closed interpretation you believe is justified, but do not claim the text determined what it did not determine.

Preserve prereveal test failures and inconvenient interpretation results rather than deleting them solely to obtain green tests.

## Execution infrastructure

Run your prereveal tests before freeze.

You may use local Python or a minimal hosted workflow if required by your available tools. Execution infrastructure does not widen the information aperture.

If a hosted workflow is required, it may:

- check out only the execution branch;
- use the ordinary Python standard library;
- run only your prereveal tests;
- emit hashes/receipts for your own implementation/test files.

It must not retrieve other branches, repositories, tags, prior Contract C material, evaluator material, reference code, or project research.

Record any execution-infrastructure files or deviations in the freeze receipt. Infrastructure is not part of the scientific implementation identity unless explicitly stated.

## Freeze

When implementation and prereveal tests are complete:

1. commit `contract_c_successor.py` and `test_contract_c_successor.py`;
2. record the exact implementation-freeze commit at which both frozen files coexist;
3. record the Git blob ID and SHA-256 of each frozen file;
4. record the exact prereveal test command/mechanism, test count, result, and exit status;
5. record all interpretation uncertainties;
6. record contamination status;
7. record apparatus deviations;
8. create `research/contract_c_successor_rc1_fresh/FREEZE_RECEIPT.json` in a subsequent metadata-only commit;
9. verify that the receipt commit does not change either frozen implementation/test blob;
10. stop.

The freeze receipt must explicitly contain or state:

- `implementation_frozen: true`;
- `post_freeze_repair_permitted: false`;
- exact execution branch;
- exact aperture head supplied by the operator;
- exact implementation-freeze commit;
- implementation blob and SHA-256;
- prereveal-test blob and SHA-256;
- prereveal test command/mechanism, count, result, and exit status;
- interpretation uncertainties;
- contamination status;
- apparatus deviations.

## Post-freeze rule

Do not inspect any evaluator, hidden case, expected result, prior implementation, project reference code, qualification artifact, or post-freeze reveal material until a separate supervisor verifies your freeze and explicitly authorizes reveal.

After reveal, the frozen implementation and prereveal tests are immutable. A repair after observing evaluator/reference behavior is a different successor reproduction and cannot count as this run.

No adapter, compatibility shim, field translation, fallback default, diagnostic normalization, or coercion may be inserted between the frozen implementation and a later evaluator unless a post-freeze packet explicitly authorizes it. A disagreement is evidence.

## Terminal boundary for this phase

This task ends at the verified pre-reveal freeze.

Do not independently search for an evaluator or reference implementation. Do not continue into comparison.

Return only a compact freeze record containing:

- execution branch;
- aperture head used;
- implementation freeze commit/blob/SHA-256;
- test blob/SHA-256;
- prereveal test count/result/exit status;
- interpretation uncertainties;
- contamination/deviation status;
- freeze receipt commit.

Then stop.
