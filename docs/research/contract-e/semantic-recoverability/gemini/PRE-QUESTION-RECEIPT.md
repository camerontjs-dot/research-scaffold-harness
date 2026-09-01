# PRE-QUESTION RECEIPT — READER_GEMINI

Status: interpretation frozen before semantic-question reveal.

## Reader identity

- Provider/runtime: Google Gemini CLI (headless)
- Executable: gemini
- CLI version: 0.46.0
- Actual model identity reported by the runtime during phase 1:
  - `gemini-3.1-pro-preview-customtools`: 1 request / 1 error
  - `gemini-3-flash-preview`: 4 requests / 0 errors
- Reader-authored `metadata.model_identity`: `gemini-2.0-flash-exp` (not repaired)
- Session identity: `16fd5a48-84c7-491c-b804-107f9eaa805f`

## Frozen authority

- Repository: `camerontjs-dot/apparatus-contracts`
- Content freeze: `3e522b79208f5b918d51d903b4fcc0623145923d`
- Content tree: `455c286c1569f80b0f34fdcb9b444f7dcf7d2ea6`
- Freeze-receipt / PR #47 head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb` (Draft, unmerged)
- Materialized `RESOLVED-CONTRACT.json` SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- Schema Git blob: `54268fe089aa88507faa03f63cdbd9b37e27993d`
- Reader-task Git blob: `a04d2d05df31ddb8bfa3731dd7857276f9a34134`

## Phase 1

- Start: `2026-09-01T04:03:40.304167Z`
- End: `2026-09-01T04:04:37.130183Z`
- Duration: 56.826 s
- Exit code: 0
- Continuation mechanism used to create the session: `--session-id 16fd5a48-84c7-491c-b804-107f9eaa805f`
- Output format: `-o json`
- Approval mode: `plan`
- `--skip-trust` set
- Model selection: not forced; runtime default / fallback
- Observed tools: `read_file` x2 success, `update_topic` x3 success, `run_shell_command` x1 fail
- Freeze marker: `FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL`
- Interpretation SHA-256: `717746bb32bcf9e2ec625a0160ffd99436dce46d4b30367ad1fcdb36578d8444`
- Raw phase-1 stdout SHA-256: `d1d8954cae834ca7ef39cccd14f6428bb3d7d7509cadc67cdc8939f0c0affe4f`
- Structural validation: pass

## Isolation

- Isolated `GEMINI_CLI_HOME` containing only authentication settings and an API-key env file; no copied history
- Phase-1 accessible files: `RESOLVED-CONTRACT.json`, `INTERPRETATION-RECORD-SCHEMA.json`, `READER-TASK.md`
- Questions held in orchestrator-private until both readers froze
- Gemini `--sandbox` was not applied (no additional macOS sandbox profile configured). Isolation is working-directory + isolated CLI home + plan-mode + no MCP config
- Default Gemini CLI system prompt / tool catalog remains large; this is a runtime default, not Contract E material

## Contamination status

- Reader-reported: `NONE`
- Orchestrator-observed: successful tools were `read_file` and `update_topic`. One `run_shell_command` attempt failed (`Tool "run_shell_command" not found`). No web, GitHub, Copilot, Grok-reader, or CAL retrieval succeeded.

## Deviations (phase 1)

1. No Gemini CLI sandbox flag.
2. Runtime model (`gemini-3-flash-preview` after a failed `gemini-3.1-pro-preview-customtools` call) differs from the reader-authored metadata string `gemini-2.0-flash-exp`. Both recorded; neither repaired.
3. Isolated `.env` contains both `GOOGLE_API_KEY` and `GEMINI_API_KEY`; CLI logged that it used `GOOGLE_API_KEY`.
4. Frozen `INTERPRETATION.json` is pretty-printed JSON extracted from fenced model output; lossless CLI wrapper retained separately.
5. Failed shell-tool attempt is recorded; it did not return command output.
