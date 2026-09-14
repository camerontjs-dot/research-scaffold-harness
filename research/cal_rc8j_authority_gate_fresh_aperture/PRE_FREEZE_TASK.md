# CONTEXT-FREE REQUIRED: CAL Authority Gate v1 Fresh Independent Reproduction

You are executing a scientific clean-room implementation of a frozen authority-gate specification.

Your independence is part of the evidence. The goal is recoverability from the normative specification alone, not imitation of a hidden reference implementation.

## 1. Exclusive pre-freeze aperture

Before your implementation, self-authored tests, and freeze receipt are frozen, you may inspect only these two files at the exact repository/ref supplied by the operator:

1. `research/cal_rc8j_authority_gate_fresh_aperture/SPEC.md`
2. `research/cal_rc8j_authority_gate_fresh_aperture/PRE_FREEZE_TASK.md`

The expected Git blob for `SPEC.md` is:

`0f0981744646ab22a62d46a4e6535be0e7cdf773`

This is byte-identical to the frozen normative source specification in `camerontjs-dot/claim-audit-lab` at freeze commit:

`0a3d863580050751d8f87c5a73cfca82d4376901`

Do not browse the repository, inspect the branch tree, inspect a pull request, search GitHub, or open nearby files before freeze. Retrieve only the two exact authorized paths.

If the supplied `SPEC.md` bytes do not match the expected Git blob, stop and report a blocker. Do not substitute a newer or nearby file.

## 2. Explicitly prohibited pre-freeze information

Do not use or retrieve:

- prior conversations, summaries, user memory, project memory, or CAL Pipeline context;
- any Claim Audit Lab RC8/RC8A-RC8J result, preregistration, architecture note, deviation record, test, fixture, evaluator, or implementation;
- any `authority_contract_rc8*.py` file;
- any comparison/reference implementation;
- any hidden or held-out cases;
- any post-freeze reveal packet;
- Git history beyond the exact identities stated in the two authorized files;
- Contract B or Contract C source files outside what `SPEC.md` itself states;
- another implementer's work;
- web search or external guidance used to infer project-specific behavior.

If unauthorized project-specific information becomes visible and could materially influence the implementation, record contamination and stop rather than silently continuing as independent.

## 3. Implementation task

Implement the behavior described by `SPEC.md` from the specification alone.

Use Python 3.11.

Expose exactly this callable interface:

```python
def assess_authority(case: dict) -> dict:
    ...
```

The returned dictionary must contain the two normative keys:

- `authority_status`
- `reason`

Recommended implementation path:

`research/cal_rc8j_authority_gate_fresh_reproduction/authority_gate_independent.py`

Do not import or reuse Claim Audit Lab authority-gate implementation code.

## 4. Self-authored prereveal tests

Write your own tests directly from `SPEC.md` before any evaluator/reference reveal.

At minimum, exercise:

- execution versus evidence precedence;
- source binding absence and mismatch;
- Contract B bundle/passage binding absence and mismatch;
- admitted-passage span validity and exact-boundary containment;
- proposal and required-field support containment;
- claim binding absence and mismatch;
- atom binding absence and mismatch;
- assessment/proposal/assertion/operator same-subject binding;
- assertion states;
- operator domain, applicability, and governed-span rules;
- unsupported extra modifiers;
- required-field jurisdiction, receipt presence, subject binding, support span, typed status, value equality, and supplied-order precedence;
- composition required/not-required behavior;
- aperture required/not-required behavior;
- successful `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED` behavior;
- invariance to diagnostic-only fields such as reader count, instrument count, and scalar confidence.

Do not search for or infer hidden evaluator cases while writing the tests.

Recommended test path:

`research/cal_rc8j_authority_gate_fresh_reproduction/test_authority_gate_independent.py`

## 5. Freeze requirements

After the implementation and self-authored tests pass to your satisfaction, freeze them before any post-freeze reveal.

Create:

`research/cal_rc8j_authority_gate_fresh_reproduction/INDEPENDENT_PRE_REVEAL_FREEZE.json`

The receipt must record at least:

- exact implementation path;
- implementation Git blob, if committed;
- implementation SHA-256;
- exact test path(s);
- test Git blob(s), if committed;
- test SHA-256 values;
- exact prereveal test command;
- prereveal exit code and result;
- Python/runtime identity;
- exact `SPEC.md` Git blob verified;
- repository and execution branch identity;
- exact freeze commit;
- freeze timestamp;
- unresolved interpretations or uncertainties;
- contamination status and any contamination note.

Commit the implementation, tests, and freeze receipt to a fresh execution branch created from the exact aperture head supplied by the operator.

Recommended execution branch name:

`research/cal-rc8j-authority-gate-fresh-independent-reproduction-20260904`

Do not place any reference implementation, evaluator, hidden cases, or post-freeze comparison material on that branch before the freeze.

## 6. Required stopping point

Once the implementation, prereveal tests, and freeze receipt are committed and immutable, stop.

Return only the pre-reveal freeze report needed for supervisor verification:

- execution branch;
- freeze commit;
- implementation path/blob/SHA-256;
- test path(s)/blob(s)/SHA-256;
- test command and result;
- verified specification blob;
- contamination status;
- unresolved interpretations, if any.

Do not reveal, compare, repair, promote, merge, release, or inspect any evaluator/reference material.

The supervisor will separately verify the freeze and, only then, may authorize a post-freeze reveal.

## 7. Scientific posture

A genuine disagreement is useful evidence. Do not optimize for an unseen evaluator.

If the specification is underdetermined at any point, implement the interpretation you can justify from the authorized text and record the uncertainty in the freeze receipt. Do not import unstated project behavior.

A successful fresh reproduction would establish only bounded independent recoverability of this frozen authority transition. It would not by itself authorize production CAL changes, Contract B/C changes, a release, Contract C projection, semantic text extraction, or Decision Engine policy.
