# Context-free Consumer B pre-freeze task

**Mode:** CONTEXT-FREE REQUIRED. This task tests whether a fresh downstream consumer can recover and preserve the bounded Contract C `non_deciding` handoff semantics from the supplied aperture without access to prior implementations, evaluators, results, or project history.

## Starting condition

Work only on the exact execution branch and starting commit supplied by the operator. Before reading content, you may perform only the minimum ref/HEAD lookup needed to confirm that exact starting identity.

Your entire pre-freeze information aperture is the seven files under:

`research/contract_c_minimal_in_band_consumer_b_aperture/`

Read no other repository file. Do not inspect parent commits, repository history, other branches, tags, pull requests, issues, Actions, search results, or remote repositories.

Internet/network access must remain off.

## Objective

Implement the smallest independent Python consumer that can validate the bounded research handoff, recover its exact epistemic attribution state, preserve causal multiplicity and causal/residual participation, and keep `non_deciding` semantically distinct from support, counterevidence, and operational authorization.

Do not optimize for matching an unseen reference implementation. Implement from the supplied specification and handoff only.

## Write surface

You may create only:

- `candidate/consumer.py`
- `candidate/test_consumer.py`
- `candidate/FREEZE_RECEIPT.json`

If contamination occurs, you may instead create only:

- `candidate/CONTAMINATION_RECORD.json`

and must stop.

Use the Python standard library only.

## Required public API

`candidate/consumer.py` must expose:

```python
class ConsumerError(Exception):
    code: str


def consume_contract_c(raw: bytes, contract_b_index: dict, expected_profile: dict) -> dict:
    ...


def evaluate_supported_claim(consumed: dict, proposition_id: str) -> dict:
    ...
```

The exact normalized output contract and validation requirements are in `SPEC.md`.

## Pre-freeze tests

Write your own tests from the supplied specification. At minimum, exercise the valid frozen handoff and discriminating negative/metamorphic cases you believe are required to establish the specified boundary. Do not seek hidden cases or expected outputs.

A legitimate pre-freeze outcome may be a failure. If the public specification is insufficient to implement a required invariant without invention, record that explicitly and use `INCONCLUSIVE_PRE_REVEAL` or `FALSIFIED_PRE_REVEAL` as appropriate rather than guessing.

## Freeze

Once implementation and prereveal tests are complete:

1. commit `candidate/consumer.py` and `candidate/test_consumer.py`;
2. record the resulting exact commit and blob identities;
3. create `candidate/FREEZE_RECEIPT.json` containing at least:
   - aperture starting commit;
   - frozen candidate commit;
   - consumer/test blob IDs and SHA-256 values if available;
   - Python version;
   - model identity if exposed, otherwise `UNKNOWN / PLATFORM-SELECTED`;
   - network state;
   - exact allowed files actually read;
   - `forbidden_inputs_read`;
   - tests executed and results;
   - contamination state;
   - terminal pre-reveal state;
   - explicit statement that no post-freeze evaluator/reference/results were seen;
4. commit the freeze receipt;
5. STOP.

Do not request, inspect, or run any post-freeze evaluator in this task.

## Contamination stop rule

If you see or access any forbidden source before the candidate is frozen, do not continue as an independent reproduction. Preserve a `candidate/CONTAMINATION_RECORD.json` describing exactly what was exposed and stop with terminal state `CONTAMINATED`.

## Allowed terminal states

- `FROZEN_CANDIDATE_READY_FOR_REVEAL`
- `FALSIFIED_PRE_REVEAL`
- `INCONCLUSIVE_PRE_REVEAL`
- `BLOCKED`
- `CONTAMINATED`

Return only a compact handoff: terminal state, exact final commit, consumer/test/freeze-receipt blob IDs, test summary, and contamination status.
