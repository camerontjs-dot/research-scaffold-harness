# Contract E Authority/Warrant Specification — Fresh Independent Reproduction Launch Packet

Status: **CONTEXT-FREE REQUIRED / research only**

Purpose: give a competent local coding agent enough information to independently implement and test the frozen Contract E authority/warrant research specification without seeing the reference implementation, hidden cases, prior reasoning, or expected results before implementation freeze.

This packet is an execution instruction, not Contract E authority. A successful run does not authorize Contract E promotion or production behavior.

---

## 1. Operator setup

Run this experiment in a genuinely fresh local execution context. Prefer a model family that did not participate in designing the candidate, such as Claude, Gemini, or Grok. A second independent run with another model family is encouraged and should use a separate workspace and branch.

### Required isolation

The agent-visible environment must contain only:

1. this task packet;
2. the independent repository/base described below;
3. the four authorized normative specification files listed in Section 3;
4. files the fresh agent itself creates during this run.

Before the implementation freeze, the agent must **not** have access to:

- `camerontjs-dot/apparatus-contracts` other than the four copied normative files;
- Contract E PRs, issues, comments, branches, workflow logs, or artifacts;
- prior Contract E validators, reference implementations, registries, frozen hidden cases, expected outcomes, or result files;
- prior CAL, Evidence Bundler, Decision Engine, or Contract E authority-research notes;
- ChatGPT/CAL Pipeline conversation history;
- outputs from another independent reproduction;
- web search, GitHub search, GitHub MCP/connectors, browser tools, or repository-discovery tools.

The model provider may of course require network transport. What must be unavailable is **information-retrieval tooling** that could reveal the reference work.

Use the CLI's strongest practical workspace/file sandbox. Ideally the agent cannot read outside its experiment directory. Do not mount or expose local checkouts of `apparatus-contracts`, CAL, Decision Engine, Verbose Engine, or other CAL Pipeline repositories inside the agent-visible filesystem.

Do not expose `GH_TOKEN`, `GITHUB_TOKEN`, GitHub CLI authentication, GitHub MCP, or repository remotes to the agent before freeze. Provider authentication needed to run the model is allowed.

### Independent repository

Target repository:

`camerontjs-dot/research-scaffold-harness`

Authorized clean base:

`548bfa81f65290eda15af658f647497679b840ef`

Create a fresh local worktree/clone at exactly that base. Use a new branch whose name identifies the model/run, for example:

`research/contract-e-fresh-reproduction-claude-20260830`

or

`research/contract-e-fresh-reproduction-gemini-20260830`

Remove or disable the Git remote before starting the agent. Do not push until the pre-reveal implementation is frozen.

A practical operator sequence is:

```bash
# Adapt paths to your machine.
BASE=548bfa81f65290eda15af658f647497679b840ef
RUN=/tmp/contract-e-fresh-claude

# Create a clean copy/worktree from research-scaffold-harness at BASE.
# Ensure the resulting agent-visible checkout contains no unrelated CAL Pipeline repos.

cd "$RUN"
git checkout --detach "$BASE"
git switch -c research/contract-e-fresh-reproduction-claude-20260830
git remote remove origin 2>/dev/null || true

mkdir -p authority_input
```

The exact clone/worktree command is operator-dependent. The scientific requirements are the exact base, isolation, and absence of reference access.

After copying the four normative files and this task packet into the workspace, commit those inputs **before** launching the agent. Record that input commit SHA.

---

## 2. Exact objective

Independently determine whether the frozen Contract E research specification is sufficiently explicit for a competent implementation to recover its authority/warrant semantics without access to the reference implementation or expected behavior.

Using only the authorized pre-freeze aperture, independently:

1. interpret the specification;
2. identify ambiguities, unknowns, and load-bearing assumptions;
3. derive falsifiers and adversarial tests from the specification itself;
4. implement a native consumer/validator;
5. test the implementation using cases you design yourself;
6. freeze the implementation, tests, interpretation notes, and predicted behavior before any reference reveal.

Do **not** try to make the implementation agree with an imagined reference. There is no reward for passing later hidden cases. Specification ambiguities and disagreements are scientific evidence and must be preserved.

The experiment is testing **independent recoverability**, not coding speed and not whether a plausible authority framework can be invented.

---

## 3. Authorized pre-freeze information aperture

Copy exactly these four files into `authority_input/` using the exact Git blobs below. Do not copy their parent directories or neighboring files.

### A. Authority/warrant candidate specification

Source path:

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-CANDIDATE.json`

Required Git blob:

`9c1090335d87eb5e4885a755542923b453c45317`

### B. Structural shapes

Source path:

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-SHAPES.json`

Required Git blob:

`c3f293430ae6ddb87523d83ea6e5380b8b832136`

### C. Participant boundary specification

Source path:

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-PARTICIPANT-BOUNDARY.json`

Required Git blob:

`8b1d292a240300388949d502e7b656e7a23a0b8e`

### D. Authority-basis binding specification

Source path:

`docs/research/contract-e/rc3b-authority-basis-binding/BASIS-BINDING-SPEC.json`

Required Git blob:

`63c952c9c28f1be2173e69c79976c7dfe5880c10`

These four files are the **complete authorized Contract E semantic aperture before freeze**.

The operator may obtain them from an existing trusted local checkout or other controlled mechanism, but the fresh agent must see only the copied files. Verify the blobs before launch, for example from the source checkout with `git hash-object <file>`.

Do not expose the source repository or source commit history to the agent.

---

## 4. Forbidden pre-freeze material

The following are specifically withheld until after the fresh implementation is frozen:

- `AUTHORITY-BASIS-REGISTRY.json`;
- `FROZEN-BASIS-ATTACKS.json`;
- RC3A/RC3B frozen case corpora;
- RC3A or RC3B validators;
- hardening/matrix validators;
- `RESULTS.json`, `RESULTS.md`, or hardening results;
- reference workflow files, logs, artifacts, run IDs, and summaries;
- PR #23, #25, #26, or #27 narrative/discussion;
- the deep-research authority synthesis;
- CAL semantic-authority experiment implementation/results;
- Decision Engine authority implementation/results;
- prior independent-consumer behavior;
- any expected accept/reject answer set;
- any implementation produced by another model.

Do not search for these names or equivalents.

If any forbidden material is accidentally observed, stop and record the contamination. Do not continue claiming a context-free reproduction.

---

## 5. Fresh-agent task

The following section is the instruction to give the local coding agent. The operator should not add architectural hints or expected answers.

### BEGIN AGENT TASK

**CONTEXT-FREE REQUIRED**

You are performing a fresh independent implementation of a frozen research specification.

Your only authority for Contract E behavior is:

- `TASK.md` or this launch packet;
- `authority_input/SPEC-CANDIDATE.json`;
- `authority_input/SPEC-SHAPES.json`;
- `authority_input/SPEC-PARTICIPANT-BOUNDARY.json`;
- `authority_input/BASIS-BINDING-SPEC.json`.

Do not search the web, GitHub, other repositories, prior conversations, package registries for project-specific information, or the local filesystem outside this experiment workspace. Do not inspect Git remotes or try to locate the reference project. Do not ask the operator for expected behavior.

### Scientific objective

Determine whether these frozen files are sufficient to independently recover a coherent, mechanically executable authority/warrant contract.

Implement what the specification actually supports. Do not fill underspecified behavior with assumptions merely to obtain a total implementation.

Where behavior is ambiguous:

- record the ambiguity explicitly;
- identify the competing interpretations;
- choose a deterministic local behavior only when implementation requires one;
- mark that choice as an implementation assumption rather than specification authority;
- design a test that would distinguish the interpretations after reference reveal.

Preserve unknowns. Do not turn missing authority into semantic falsity. Do not silently widen authority through convenience mappings.

### Required Phase 1: independent interpretation and preregistration

Before implementing the consumer, create `research/contract_e_fresh_reproduction/PREREGISTRATION.md` containing:

1. your own concise description of the contract's purpose;
2. the entities/relations you believe are normative;
3. the distinction, if any, among competence, warrant, authority basis, participant responsibility, jurisdiction, propagation, delegation, currentness, and historical validity;
4. what information you believe may propagate versus must be re-established;
5. all ambiguities or missing definitions you can identify;
6. your proposed validator outcomes/reason taxonomy, derived only from the spec;
7. at least 15 adversarial or metamorphic tests you will implement;
8. explicit falsifiers for your own interpretation;
9. a list of fields or payload content that you believe must not affect common authority validation;
10. predictions for how your implementation should behave under cross-domain, cross-operation, cross-target, stale/revoked, delegation, warrant, and semantic-payload mutations.

Commit this preregistration **before** implementation work. Record the commit SHA in the file or in a separate receipt.

Do not amend or rewrite the preregistration after implementation begins. If you discover a problem later, add a dated/deviation note rather than erasing the original prediction.

### Required Phase 2: implementation

Create a native implementation under:

`research/contract_e_fresh_reproduction/`

You may choose the implementation language that best fits the repository and available runtime. Prefer existing or standard-library dependencies. Do not download project-specific code or dependencies that expose reference behavior.

At minimum provide:

- a parser/loader for the four specification surfaces;
- a validator or evaluator implementing your independently derived semantics;
- explicit structured outcomes/reasons;
- deterministic handling of unknown or malformed cases;
- tests covering the preregistered falsifiers;
- machine-readable output for test cases where practical.

The implementation must not contain hidden lookups for expected fixture IDs or hard-coded answers to cases you have not yet seen.

### Required self-tests

Your pre-reveal tests must include, at minimum, independently designed probes for:

- subject/principal substitution;
- authority-domain substitution;
- typed-operation substitution;
- scope substitution;
- target-class substitution;
- exact-target substitution where the spec permits exact binding;
- current vs stale/revoked authority;
- validity interval / historical validity;
- authority reference type mismatch;
- unresolvable authority basis;
- competence present but mandate absent;
- mandate present but required competence absent;
- valid warrant with wrong/missing mandate;
- valid mandate with wrong/missing warrant where warrant is required;
- semantic/result payload mutation that should or should not affect authority evaluation according to your interpretation;
- delegation amplification;
- authority propagation versus re-establishment;
- participant responsibility/effect-domain substitution;
- malformed/unknown authority domains or operations.

You may and should add stronger tests if the specification suggests them.

### Independence discipline

You are not trying to pass an external test suite. You are trying to expose whether the specification is sufficient.

Do not repair an ambiguity by inventing semantics and then describing those invented semantics as contractual.

Do not infer a universal authority evaluator unless the supplied specification establishes one.

Do not infer production architecture, a centralized authority registry, cryptographic trust roots, or CAL/Decision/Executor production behavior unless explicitly established by the supplied files.

### Required Phase 3: pre-reveal freeze

When your implementation and self-tests are complete:

1. run the complete local test suite;
2. preserve failures and disagreements;
3. create `research/contract_e_fresh_reproduction/FREEZE-RECEIPT.md` containing:
   - model/provider and model version if known;
   - execution date/time;
   - exact starting/input commit SHA;
   - preregistration commit SHA;
   - final implementation freeze commit SHA;
   - final tree SHA;
   - hashes of the four input specification files;
   - implementation/test file hashes or a deterministic manifest;
   - exact test command(s);
   - test counts and results;
   - unresolved ambiguities;
   - deviations or contamination, if any;
   - the literal marker `FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_REVEAL` if and only if no forbidden material was observed.
4. commit the receipt, implementation, tests, and all pre-reveal notes;
5. do not amend that freeze commit after reference reveal;
6. STOP.

At STOP, report only:

- preregistration SHA;
- freeze SHA;
- tree SHA;
- test summary;
- unresolved ambiguities;
- whether the run remained uncontaminated;
- any operator action needed to preserve/push the frozen branch.

Do not seek or inspect reference behavior after the freeze. The operator will perform a separate authorized reveal/comparison phase.

### Non-authorization

This is research only. Do not modify or promote Contract E, CAL, Evidence Bundler, Decision Engine, production authorization machinery, production execution machinery, or other repositories.

### END AGENT TASK

---

## 6. Operator freeze handling

When the agent stops:

1. verify that the freeze commit exists and the working tree is clean;
2. record `git status`, `git rev-parse HEAD`, and `git rev-parse HEAD^{tree}`;
3. verify the four normative input hashes;
4. re-enable/add the intended Git remote only **after** the freeze;
5. push the frozen branch without amendment;
6. do not merge it;
7. do not show the agent hidden/reference material yet;
8. bring the branch name, preregistration SHA, freeze SHA, tree SHA, and freeze receipt back to the CAL Pipeline governance/reveal side for the authorized post-freeze comparison.

If running a second model, start it from the same authorized base/input aperture in a completely separate workspace. It must not see the first model's branch, tests, notes, commits, or outputs before its own freeze.

---

## 7. What makes the run invalid as an independence claim

Classify the run as contaminated or invalid for fresh-reproduction evidence if, before freeze, the agent:

- sees any reference validator or hidden test vector;
- sees PR/result narratives that reveal expected behavior;
- searches GitHub/web for Contract E or the authority research;
- reads another model's implementation;
- imports prior CAL Pipeline conversation/reasoning;
- receives coaching from the operator about expected outcomes;
- modifies the four normative input files;
- starts from a different repository base without recording the deviation;
- repairs the frozen implementation after reference reveal and counts the repair as independent agreement.

A contaminated run may still be useful engineering work, but it is not evidence of independent recoverability.

---

## 8. Experiment claim boundary

A successful fresh reproduction would support only this bounded claim:

> A competent independent implementation process could recover materially agreeing Contract E authority/warrant behavior from the frozen specification aperture without reference implementation access.

It would **not** establish:

- Contract E 1.0.0;
- a universal theory of authority;
- one universal authority evaluator;
- production readiness;
- correctness of CAL epistemic semantics;
- correctness of Decision Engine policy;
- cryptographic trust or identity infrastructure;
- safe autonomous execution in untested domains.

Disagreement is evidence. Preserve it exactly.
