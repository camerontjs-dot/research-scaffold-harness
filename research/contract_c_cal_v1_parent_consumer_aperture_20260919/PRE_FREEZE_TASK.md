# Context-free Contract C CAL V1 parent-binding consumer task

**Mode:** CONTEXT-FREE REQUIRED.

This task tests whether a fresh downstream consumer can recover and verify the public Contract C parent-recomposition binding using only this frozen aperture.

## Starting condition

Work only from the exact starting commit supplied by the operator. Before reading content, perform only the minimum ref/HEAD lookup needed to verify that starting identity.

Your entire pre-freeze information aperture is the files under:

`research/contract_c_cal_v1_parent_consumer_aperture_20260919/`

Read no other repository file. Do not inspect repository history, parent commits, other branches, tags, pull requests, issues, Actions, search results, sibling repositories, package source, prior Contract C implementations, prior consumers, evaluators, or internet sources. Network access must remain off.

The real frozen CAL V1 producer handoffs and post-freeze evaluator are deliberately withheld until after candidate freeze.

## Objective

Implement the smallest standard-library Python consumer that can:

- validate the nested Candidate A RC2 public-result object from `INNER_RC2_SPEC.md`;
- validate the exact outer parent-recomposition wire from `PARENT_BINDING_SPEC.md`;
- derive each child result identity from exact native CAL-result bytes rather than trusting the outer object;
- derive the declared `all_of` parent conclusion from exact child conclusions;
- derive and verify the exact decomposition receipt identity;
- verify root/child proposition and content bindings;
- verify independently supplied Contract-B and producer/policy authority;
- verify local object identities and independently supplied whole-object authority;
- fail closed on stale, omitted, cross-run, reordered, resealed, or opaque/private-codec child bindings;
- preserve epistemic/result state without inventing Decision, Authorization, action, confidence, score, rank, or winner semantics.

Do not reproduce CAL semantic auditing, retrieval, measurement, relation derivation, or Decision policy.

## Required public API

Create `candidate/consumer.py` exposing:

```python
class ConsumerError(Exception):
    code: str


def consume_parent_bound_contract_c(
    raw: bytes,
    *,
    contract_b_index: dict,
    expected_authority: dict,
    contract_a_decomposition: dict,
    native_child_results: dict[str, bytes],
) -> dict:
    ...
```

The return value must deterministically preserve the validated public RC2 epistemic state plus the verified parent-recomposition state.

## Allowed write surface

You may create only:

- `candidate/consumer.py`
- `candidate/test_consumer.py`
- `candidate/FREEZE_RECEIPT.json`

If contamination occurs, create only:

- `candidate/CONTAMINATION_RECORD.json`

and stop.

Use the Python standard library only.

## Pre-freeze work

1. Read only this aperture.
2. Implement from the supplied specifications and authority constants.
3. Build your own synthetic prereveal tests. No real frozen producer handoff is available before freeze.
4. Your tests must include success cases for supported+supported, contradicted+supported, supported+not_checkable, and contradicted+not_checkable `all_of` parents.
5. Your tests must include mutations for child-result identity, native-result bytes, child omission, sequence/order, root binding, receipt identity, parent conclusion, cross-run replay, coherent reseal, private-codec result IDs, inner RC2 substitution, external whole-object mismatch, and destination-policy injection.
6. Run prereveal tests with network disabled.
7. If the specification is insufficient to implement an invariant without invention, preserve that as an inconclusive or falsified prereveal outcome rather than guessing.

## Freeze procedure

Once implementation and prereveal tests are complete:

1. commit `candidate/consumer.py` and `candidate/test_consumer.py`;
2. record exact candidate commit and blob IDs;
3. create `candidate/FREEZE_RECEIPT.json` recording at least:
   - aperture starting commit;
   - candidate commit;
   - consumer/test blob IDs;
   - Python version;
   - model/agent identity if exposed, otherwise `UNKNOWN / PLATFORM-SELECTED`;
   - network state;
   - exact allowed aperture files read;
   - `forbidden_inputs_read`;
   - prereveal test command and result counts;
   - contamination state;
   - terminal pre-reveal state;
   - statement that no real frozen CAL producer handoff, evaluator, prior implementation, prior consumer, hidden expected output, or post-freeze result was seen;
4. commit the receipt;
5. STOP.

Do not request or inspect the post-freeze evaluator in this task.

## Allowed terminal states

- `FROZEN_CANDIDATE_READY_FOR_REVEAL`
- `FALSIFIED_PRE_REVEAL`
- `INCONCLUSIVE_PRE_REVEAL`
- `BLOCKED`
- `CONTAMINATED`
