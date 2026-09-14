# Context-free Contract C Candidate A RC2 Consumer B task

**Mode:** CONTEXT-FREE REQUIRED.

This task tests whether a fresh downstream consumer can implement and recover the public semantics of the supplied Contract C research handoffs using only this frozen aperture.

## Starting condition

Work only from the exact starting commit supplied by the operator. Before reading content, perform only the minimum ref/HEAD lookup needed to verify that starting identity.

Your entire pre-freeze information aperture is the files under:

`research/contract_c_candidate_a_rc2_consumer_b_aperture/`

Read no other repository file. Do not inspect repository history, parent commits, other branches, tags, pull requests, issues, Actions, search results, sibling repositories, package source, or internet sources. Network access must remain off.

Do not infer hidden expected behavior from filenames, history, or project conventions. Implement from `SPEC.md`, the supplied handoffs, exact Contract-B indexes, and `AUTHORITIES.json` only.

## Objective

Implement the smallest independent standard-library Python consumer that can:

- validate the exact research profile and immutable authority bindings;
- verify canonical bytes, local result identity, and independently supplied whole-object identity;
- verify exact Contract-B, proposition, evidence-reference, producer and policy-resolution bindings;
- preserve participant relation and causal/residual role;
- preserve every minimal sufficient basis group without selecting an artificial winner;
- distinguish independent alternatives from joint necessity;
- preserve exact terminal reasons, including case-sensitive `MIXED_RELATIONS`, `no_deciding_relation`, and `UNSUPPORTED_SEMANTIC_FAMILY`;
- keep epistemic/result state separate from destination policy, Authorization, requested effects, and execution permission.

Do not reproduce CAL, re-audit evidence, infer missing causal structure, or add downstream action semantics.

## Allowed write surface

You may create only:

- `candidate/consumer.py`
- `candidate/test_consumer.py`
- `candidate/FREEZE_RECEIPT.json`

If contamination occurs, create only:

- `candidate/CONTAMINATION_RECORD.json`

and stop.

Use the Python standard library only.

## Required public API

`candidate/consumer.py` must expose:

```python
class ConsumerError(Exception):
    code: str


def consume_contract_c(raw: bytes, contract_b_index: dict, expected_authority: dict) -> dict:
    ...
```

`ConsumerError.code` must be a stable machine-readable string chosen by the implementation. The exact code vocabulary is not supplied and is not scored except where different failure classes would otherwise be laundered into successful consumption.

The normalized successful return value must preserve the public semantic content described by `SPEC.md`. It must not contain destination-policy, Authorization, action, permission-to-clear, confidence, score, rank, winner, or requested-effect fields invented by the consumer.

## Pre-freeze work

1. Read the aperture files only.
2. Implement the consumer from the public specification.
3. Write your own prereveal tests, including all supplied valid handoffs and discriminating malformed/metamorphic cases you believe the specification requires.
4. Run the prereveal tests locally with network disabled.
5. If the specification is insufficient to implement a required invariant without invention, preserve that result rather than guessing.

A valid pre-reveal outcome may be failure or inconclusive.

## Freeze procedure

Once implementation and prereveal tests are complete:

1. commit `candidate/consumer.py` and `candidate/test_consumer.py`;
2. record the exact frozen candidate commit and consumer/test Git blob IDs;
3. create `candidate/FREEZE_RECEIPT.json` recording at least:
   - aperture starting commit;
   - frozen candidate commit;
   - consumer and test blob IDs;
   - Python version;
   - model identity if exposed, otherwise `UNKNOWN / PLATFORM-SELECTED`;
   - network state;
   - exact allowed aperture files read;
   - `forbidden_inputs_read`;
   - prereveal tests executed and result counts;
   - contamination state;
   - terminal pre-reveal state;
   - explicit statement that no post-freeze evaluator, reference consumer, prior implementation, prior results, or hidden expected outputs were seen;
4. commit the freeze receipt;
5. STOP.

Do not request, inspect, create, or run a post-freeze evaluator in this task.

## Contamination stop rule

If any forbidden source is exposed before candidate freeze, do not continue as an independent reproduction. Record exactly what was exposed in `candidate/CONTAMINATION_RECORD.json` and stop.

## Allowed terminal states

- `FROZEN_CANDIDATE_READY_FOR_REVEAL`
- `FALSIFIED_PRE_REVEAL`
- `INCONCLUSIVE_PRE_REVEAL`
- `BLOCKED`
- `CONTAMINATED`

Return only a compact handoff containing terminal state, exact final commit, consumer/test/freeze-receipt blob IDs, prereveal test summary, and contamination status.