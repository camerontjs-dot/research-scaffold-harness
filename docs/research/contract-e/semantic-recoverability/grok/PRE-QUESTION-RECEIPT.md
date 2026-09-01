# PRE-QUESTION RECEIPT — READER_GROK

Status: interpretation frozen before semantic-question reveal.

## Reader identity

- Provider/runtime: xAI Grok CLI (headless)
- Executable: grok
- CLI version: 1.0.13 (5e9a58528b76) [stable]
- Actual model identity reported during phase 1: `grok-4.6-build` (`modelUsage` key); session summary `current_model_id` = `grok-4.6`
- Session identity: `f6a9e985-4d54-48c5-a0cb-d5b679b256fc`
- Session kind: headless; sandbox profile saved on session: `workspace`
- Agent name recorded by runtime: `grok-build-plan`
- Reasoning effort recorded by runtime: `high`

## Frozen authority

- Repository: `camerontjs-dot/apparatus-contracts`
- Content freeze: `3e522b79208f5b918d51d903b4fcc0623145923d`
- Content tree: `455c286c1569f80b0f34fdcb9b444f7dcf7d2ea6`
- Freeze-receipt / PR #47 head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb` (Draft, unmerged)
- Materialized `RESOLVED-CONTRACT.json` SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- Schema Git blob: `54268fe089aa88507faa03f63cdbd9b37e27993d`
- Reader-task Git blob: `a04d2d05df31ddb8bfa3731dd7857276f9a34134`

## Phase 1

- Start: `2026-09-01T04:03:40.304534Z`
- End: `2026-09-01T04:12:24.538522Z`
- Duration: 524.234 s
- Exit code: 0
- Continuation mechanism used to create the session: `--session-id f6a9e985-4d54-48c5-a0cb-d5b679b256fc` (new session; not `--continue`)
- Output format: `--output-format json`
- Model selection: not forced; runtime default
- Tool allowlist: `read_file,grep,list_dir`
- Web search: disabled
- Subagents: disabled
- Permission mode: `plan`
- Observed tools (session updates, names only): `list_dir` x2, `read_file` x8 during phase 1
- Freeze marker: `FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL`
- Interpretation SHA-256: `5e1d0b7c86297f5b67fa132718304fdc806c9b54682f72f5265f59422b01ea20`
- Raw phase-1 stdout SHA-256: `3a1899d9db8033f74697f72cbbd646f7968c70b31c5b4fc1a4fdc04d994a03ef`
- Structural validation: pass (required top-level keys, metadata keys, freeze marker, contract SHA)

## Isolation

- Experiment root created outside CAL / MainFrame / apparatus-contracts / research-scaffold-harness working trees
- Isolated `GROK_HOME` with copied authentication material only; no user MCP servers, no plugins, memory disabled, Claude/Cursor/Codex compat surfaces disabled except Cursor sessions remaining default-enabled with no sessions loaded
- Phase-1 accessible files: `RESOLVED-CONTRACT.json`, `INTERPRETATION-RECORD-SCHEMA.json`, `READER-TASK.md`
- Questions held in orchestrator-private until both readers froze
- Isolation limitation: requested `--sandbox strict` / `read-only` / custom `reader` profile refused to start (`/var/run/docker.sock` symlink). Fell back to `--sandbox workspace` plus tool allowlist and Read/Grep deny rules for Desktop, Copilot reader state, sibling reader, and orchestrator-private
- Bundled Grok skills were copied into the isolated home by the CLI; they were not in the tool allowlist

## Contamination status

- Reader-reported: `none_observed_within_authorized_aperture`
- Orchestrator-observed: no successful retrieval of apparatus-contracts, research-scaffold-harness, CAL, GitHub, web, Copilot Reader 1, Gemini outputs, or prior sessions. Tool record is directory listing plus file reads inside the reader aperture.

## Deviations (phase 1)

1. `--sandbox strict` could not be applied; `workspace` used instead.
2. Isolated runtime still advertises bundled skills; tools were restricted to read/grep/list.
3. Frozen `INTERPRETATION.json` is pretty-printed JSON extracted from fenced model output; lossless CLI wrapper retained separately by the orchestrator.
4. Reader self-described `model_identity` as "Grok 4.6 released by xAI"; runtime spend key is `grok-4.6-build`. Both recorded; neither repaired.
