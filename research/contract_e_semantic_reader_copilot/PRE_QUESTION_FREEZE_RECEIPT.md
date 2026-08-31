# Contract E Semantic Recoverability Audit — Copilot Reader 1 Pre-Question Freeze Receipt

Status: **FROZEN BEFORE SEMANTIC QUESTION REVEAL**

This is an interpretation-only evidence record. It is not an implementation reproduction and does not authorize Contract E promotion.

## Reader subject

- execution surface: GitHub Copilot CLI through GitHub Actions
- Copilot CLI: `1.0.82`
- workflow repository: `camerontjs-dot/verbose-engine`
- accepted workflow branch: `research/contract-e-copilot-reader1-actions-20260831`
- accepted workflow commit: `f92a92885a60eeb3712a7bc1251dd28713839ac5`
- accepted run: `33451709033`
- accepted job: `99682859819`
- immutable Actions artifact: `9780058654`
- artifact ZIP SHA-256: `2ce68a3fb1f214db233a673e0d32dc8a26ad39bc785a1bfdc291df6d73e7459f`
- Copilot requested model: `auto`
- Copilot telemetry response model: `mai-code-1.1-flash`

The reader's own raw metadata reported a generic model identity. That raw output is preserved unchanged. The concrete response-model identity above comes from Copilot CLI telemetry and is recorded separately rather than rewriting the reader output.

## Frozen semantic aperture

The child working directory contained exactly three files:

1. `RESOLVED-CONTRACT.json`
   - SHA-256 `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
2. `INTERPRETATION-RECORD-SCHEMA.json`
   - Git blob `54268fe089aa88507faa03f63cdbd9b37e27993d`
3. `READER-TASK.md`
   - Git blob `a04d2d05df31ddb8bfa3731dd7857276f9a34134`

The resolved contract was materialized from the frozen Apparatus Contracts semantic-recoverability content commit `3e522b79208f5b918d51d903b4fcc0623145923d` and hash-verified before reader invocation.

No semantic question set, expected answer key, prior Contract E reproduction, evaluator, comparison result, CAL Pipeline context, custom Copilot instruction, GitHub MCP, remote-control input, or implementation task was exposed to the reader.

The semantic question set was **not revealed** before this freeze.

## Isolation / tool boundary

The accepted run used:

- fresh GitHub-hosted Ubuntu runner;
- fresh `COPILOT_HOME` and `COPILOT_CACHE_HOME` under runner temp;
- `GITHUB_TOKEN` with `contents: read`, `metadata: read`, `copilot-requests: write`;
- no repository checkout;
- child cwd containing only the three verified aperture files;
- custom instructions disabled;
- built-in MCPs disabled;
- remote control/export disabled;
- temp-directory access disallowed by Copilot configuration;
- Copilot tool surface restricted to `view`;
- no shell or write tool exposed to the reader;
- one programmatic prompt invocation;
- Copilot soft AI-credit cap `30` (CLI-enforced minimum).

Copilot emitted a warning that its optional local sandbox was unsupported on the hosted runner. This does not broaden the reader tool surface: only the `view` tool was exposed, and no shell/write tool was available. The warning is preserved as an apparatus deviation.

## Frozen interpretation

The exact stdout interpretation was captured without semantic repair.

- raw interpretation SHA-256: `e05fa02df142aa464b6145d978f2f87e0a32481d583992070aecbd9aa8fc6d04`
- repository preservation: `INTERPRETATION.raw.json.gz.b64`
- reconstruction: base64-decode, gzip-decompress; the resulting bytes must hash to the SHA-256 above
- JSON parse: PASS
- resolved-contract identity inside reader output: PASS
- exact freeze marker: PASS

Required marker observed exactly:

`FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL`

The reader explicitly recorded both frozen open questions as underdetermined:

1. envelope-level warrant cardinality;
2. registry-resolution obligation for non-authority-conferring supporting-artifact references.

It reported no claimed contradictions in the resolved contract.

No interpretation claim is scored against a privileged answer key at this stage.

## Usage evidence

Copilot telemetry for the accepted run reported:

- `github.copilot.turn_count=[10]`
- repeated `gen_ai.response.model=mai-code-1.1-flash`
- `github.copilot.cost` samples ending in aggregate value `10.0`

The CLI credit cap is a soft ceiling and not a statement that 30 credits were consumed. This receipt does not infer account-level billing beyond the telemetry actually emitted by this run.

## Preserved discarded apparatus attempts

These are not scientific reader results.

### Attempt 1

- workflow commit `5411bd6abc0486a4cdd67f546a4aadf0586246f8`
- run `33451477788`
- job `99682119691`
- failure: CLI rejected `--max-ai-credits=15`; version 1.0.82 requires at least 30
- no interpretation output
- no Copilot OTEL file
- classified: apparatus setup failure before model inference

### Attempt 2

- workflow commit `9a674aa05e45d501e85b2b70d4d17d006a7a90e6`
- run `33451540008`
- job `99682316277`
- failure: `.json` is not a supported `--attachment` type
- no interpretation output
- no Copilot OTEL file
- classified: apparatus setup failure before model inference

### Attempt 3

- workflow commit `c9b1285e8a713ff3ffe660962600c6792a0792a6`
- run `33451643564`
- job `99682651938`
- failure: forced model identifier `claude-sonnet-4.6` was unavailable to this Actions-backed Copilot session
- no interpretation output
- no Copilot OTEL file
- classified: apparatus setup failure before model inference

The accepted fourth attempt changed only apparatus invocation choices needed to reach the same frozen reader task: removed the forced unavailable model and allowed Copilot `auto` selection. It did not change the resolved contract, output schema, reader task, or semantic question apparatus.

## Contamination status

**CLEAN PRE-QUESTION APERTURE**

No evidence of semantic-question reveal or prior Contract E research contamination was observed in the accepted reader run.

## Next authority

The interpretation is frozen. A later phase may reveal the already-frozen semantic question set to this reader, without modifying this interpretation record. Do not use this single reader to change the contract or make a Contract E disposition. The primary experiment requires additional independent readers and reader-to-reader comparison.
