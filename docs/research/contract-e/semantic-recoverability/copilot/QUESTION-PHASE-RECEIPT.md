# Contract E semantic reader 1 — Copilot question-phase freeze

Run ID: `20260831T220634Z-014cd2`

Class: exact-session continuation of Reader 1. This receipt does **not** score Contract E semantic recoverability, create an expected-answer key, or launch Reader 2.

## Continuation identity

| Field | Value |
| --- | --- |
| Copilot executable | `copilot` from Homebrew cask `copilot-cli` |
| Copilot version | GitHub Copilot CLI 1.0.82 |
| Resume mechanism | `--resume=6cf631a8-59ff-45da-9595-306627ff3989` |
| Exact resumed session ID | `6cf631a8-59ff-45da-9595-306627ff3989` |
| Session-directory count after resume | 1 (`6cf631a8-59ff-45da-9595-306627ff3989` only) |
| Requested model flag | `auto` |
| Actual model during question turn | `mai-code-1.1-flash` (CLI-reported via `session.auto_mode_resolved.chosenModel` and `model.turn_started`) |
| Isolated child directory identifier | `ce-copilot-reader-20260831T220634Z-014cd2/child` |
| Pre-resume proof | retained assistant interpretation SHA-256 matched `73ca20406b07df6981079ff98a6501378edfea62aca54b77551747ff5bd879bd`; freeze marker present; no question files in session events |

CLI result event: `sessionId=6cf631a8-59ff-45da-9595-306627ff3989`, `exitCode=0`. Premium request count on the continued session: 2.

## Immutable hashes

| Artifact | Identity |
| --- | --- |
| Resolved-contract SHA-256 | `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9` |
| Frozen interpretation SHA-256 (reverified unchanged) | `73ca20406b07df6981079ff98a6501378edfea62aca54b77551747ff5bd879bd` |
| Interpretation freeze marker | `FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL` |
| Semantic-question Git blob | `867dfe4d1be40344bc07b651c060c78b5e9307d7` |
| Question-task Git blob | `52dd27a23bde3cd0b465cd8cdc93347fd1bdba5d` |
| Question count | 51 |
| Raw answer-response SHA-256 | `53f1cdd678f82f107a65256a1f47b4bed952f53f4c1904f6890ac720da6100c1` |
| Answer freeze marker | `FRESH_CONTRACT_E_SEMANTIC_ANSWERS_FROZEN_WITHOUT_REFERENCE_KEY` |

Live GitHub before continuation:

- research-scaffold-harness Draft PR #8 head `a3c2ea532e5d4ba42bec404760509058198bec62` (Draft/unmerged)
- apparatus-contracts Draft PR #47 content freeze `3e522b79208f5b918d51d903b4fcc0623145923d` / tree `455c286c1569f80b0f34fdcb9b444f7dcf7d2ea6` / metadata head `b7fa5e3885bb75a21573f32268bf7c66d7428fdb` (Draft/unmerged)

The frozen interpretation file was independently re-hashed from that PR #8 head after the question turn and remains byte-identical. It was not overwritten.

## Answer freeze

| Field | Value |
| --- | --- |
| Total answers | 51 |
| Unique question IDs | 51 (exact frozen ID set, no extras/duplicates) |
| PERMIT | 5 |
| REJECT | 45 |
| UNDERDETERMINED | 1 |
| Structural validation | valid JSON; exactly one `PERMIT`/`REJECT`/`UNDERDETERMINED` per frozen ID; supporting contract refs present; brief reasons present; exact freeze marker present as `metadata` string value |
| Semantic repair | none |

## Isolation / tool-use

Question-turn controls:

```text
copilot
  -C <child>
  --resume=6cf631a8-59ff-45da-9595-306627ff3989
  -p "<QUESTION-PHASE-TASK.md + FROZEN-SEMANTIC-QUESTIONS.json>"
  --model=auto
  --output-format=json
  --no-custom-instructions
  --disable-builtin-mcps
  --no-remote
  --no-remote-export
  --no-ask-user
  --no-experimental
  --no-bash-env
  --disallow-temp-dir
  --deny-tool='shell,write,url,memory'
```

Not passed: `--allow-all`, `--allow-all-tools`, `--allow-all-paths`, `--allow-all-urls`, `--enable-memory`, `--continue`, `--autopilot`, `--session-id`.

- GitHub MCP: builtin `github-mcp-server` `status: disabled`
- Tools executed this turn: none
- File writes: none (`codeChanges.filesModified` empty)
- Child files after turn: original three interpretation-phase files plus the two authorized question-phase files only
- `env -i` with `HOME`/`USER`/`LOGNAME`/`PATH`/`LANG`/`COPILOT_HOME`/`COPILOT_CACHE_HOME` only, using original Reader 1 `copilot-home-attempt3`

## Contamination status

Operator: question reveal used only the already-frozen session context, the same resolved contract, the frozen interpretation, `FROZEN-SEMANTIC-QUESTIONS.json`, and `QUESTION-PHASE-TASK.md`. No reference validator, expected-answer file, prior reader response, implementation fixture, or evaluator output was retrieved. Gemini/Grok/Claude/ChatGPT were not substituted.

## Deviations

1. JSON `--attachment` remained unused (CLI 1.0.82 rejects JSON attachments). Questions were presented in the prompt and as a child file.
2. `--effort=high` remained omitted because `--model=auto` rejects it.
3. CLI emitted `prompt_cache_break` during the resumed turn. Isolation flags were unchanged.
4. Freeze marker is the exact required string stored in `metadata` (string), not a `freeze_marker` key. Not repaired.
5. Question-turn tool use was empty because the 51 questions were included in the prompt; `view` was not required.

## Mechanical interpretation-versus-answer comparison

No external answer key was used.

Conservative pointer overlap: the frozen interpretation lists five underdeterminations. Three determinate question answers cite at least one of those same underdetermination contract pointers:

- `Q-GLOBAL-02` = `REJECT` overlapping `/effective_contract/authority_basis/non_implications`
- `Q-GLOBAL-04` = `REJECT` overlapping `/effective_contract/authority_basis/non_implications`
- `Q-BASIS-08` = `PERMIT` overlapping `/effective_contract/authority_basis/non_implications` and `/effective_contract/authority_basis/registry_resolution_of_nonconferring_supporting_artifacts`

A coarser scan that treats any shared JSON pointer plus `REQUIRED`/`REJECT` (or similar) as opposition is **not** treated as a scored conflict: parent pointers are reused across unrelated claims. Those pairs were recorded operator-side only and are not a recoverability disposition.

Conflicts were preserved, not repaired.

## Confirmations

- Exact frozen Copilot session was resumed; no fresh session fallback
- Frozen interpretation remains byte-identical
- Apparatus Contracts PR #47 was not modified
- No Reader 2 / RC3E / contract amendment
