# Contract A RC2 Fresh-Reproduction Aperture Manifest

Status: **PRE-FREEZE PUBLIC APERTURE**

This manifest defines the complete information aperture for a genuinely fresh independent implementation of Contract A RC2.

## Repository and branch

Repository: `camerontjs-dot/research-scaffold-harness`

Branch: `research/contract-a-rc2-fresh-reproduction-aperture-20260901`

Branch base before aperture files: `548bfa81f65290eda15af658f647497679b840ef`

## Normative resources allowed before implementation freeze

Only these frozen public authority files may be used to derive Contract A behavior:

1. `research/contract-a-rc2-fresh-reproduction/public/SPEC.md`
   - exact Git blob: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
   - byte-identical to the frozen Apparatus candidate specification.
2. `research/contract-a-rc2-fresh-reproduction/public/schema.json`
   - exact Git blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`
   - byte-identical to the frozen Apparatus candidate schema.
3. `research/contract-a-rc2-fresh-reproduction/APERTURE-MANIFEST.md`
4. `research/contract-a-rc2-fresh-reproduction/LAUNCH.md`

The implementation may use Python standard-library documentation or local language/runtime documentation strictly to implement generic JSON/SHA-256 mechanics. It may not seek Contract A semantics from any outside source.

## Explicitly outside the pre-freeze aperture

Do **not** read, retrieve, search, infer from, or import:

- `camerontjs-dot/apparatus-contracts` Contract A RC2 research branch;
- the frozen reference validator implementation;
- the frozen reference/evaluator trees;
- valid or invalid reference fixtures;
- field-family or ablation results;
- compatibility matrices or conclusions;
- Evidence Bundler PR #43/#44/#45 results;
- CAL implementation or prior Contract A mapping code;
- prior Contract A conversations, summaries, memory, personal context, or project history;
- any sealed/reveal branch or post-freeze comparison packet;
- GitHub code search or repository-wide exploration for Contract A answers;
- web search for Contract A answers.

Existing unrelated files elsewhere in this repository are physically present because the aperture branch starts from repository `main`; they are **not authorized information** for this reproduction.

## Independence claim

The scientific question is whether the frozen public Contract A specification is sufficiently precise for an independent implementer to recover its consumer behavior without seeing the reference implementation or evaluator.

A disagreement is evidence. It must not be repaired after reveal and then counted as independent agreement.

## Aperture integrity rule

Before implementation begins, verify that the two normative public files resolve to the exact blob identities above. If either differs, stop and report an aperture-integrity failure.

The pre-freeze implementation and prereveal tests must be committed and immutably identified before any post-freeze reference/evaluator material is read.
