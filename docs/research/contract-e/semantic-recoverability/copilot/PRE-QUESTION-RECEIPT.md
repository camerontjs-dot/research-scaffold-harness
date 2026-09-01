# Contract E semantic reader 1 — Copilot pre-question freeze

Run ID: `20260831T220634Z-014cd2`

Class: interpretation-only pre-question freeze. This receipt does **not** make a pass/fail claim about Contract E semantic recoverability. Reader-to-reader comparison cannot occur until the cohort exists.

## Reader identity

| Field | Value |
| --- | --- |
| Copilot executable | `copilot` from Homebrew cask `copilot-cli` |
| Copilot version | GitHub Copilot CLI 1.0.82 |
| Operating system | macOS Darwin 25.5.0 arm64 |
| Authentication | existing GitHub Copilot subscription login stored in the macOS credential store after an isolated `copilot login --with-token` using a GitHub CLI OAuth token; the scientific process environment did not receive `GH_TOKEN`, `GITHUB_TOKEN`, or `COPILOT_GITHUB_TOKEN` |
| Requested model flag | `auto` |
| Actual underlying model identity | `mai-code-1.1-flash` (CLI-reported via `session.auto_mode_resolved.chosenModel` and `model.turn_started`) |
| Session identity | `6cf631a8-59ff-45da-9595-306627ff3989` |
| Isolated child directory identifier | `ce-copilot-reader-20260831T220634Z-014cd2/child` |

## Frozen child aperture

Child working directory contained exactly three files:

| File | Identity |
| --- | --- |
| `RESOLVED-CONTRACT.json` | SHA-256 `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9` |
| `INTERPRETATION-RECORD-SCHEMA.json` | Git blob `54268fe089aa88507faa03f63cdbd9b37e27993d` |
| `READER-TASK.md` | Git blob `a04d2d05df31ddb8bfa3731dd7857276f9a34134` |

Source retrieval (operator-side, not present in the child):

- repository: `camerontjs-dot/apparatus-contracts`
- research branch: `research/contract-e-semantic-recoverability-audit-20260831`
- Draft Research PR: `#47` (verified live Draft / unmerged)
- frozen reader-apparatus content commit: `3e522b79208f5b918d51d903b4fcc0623145923d`
- content tree: `455c286c1569f80b0f34fdcb9b444f7dcf7d2ea6`
- metadata-only freeze-receipt successor / PR head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`
- compressed resolved artifact Git blob: `ddf667cf53c8388e6e8bfc6f099ec453a0c2628d`

No `.git`, remotes, hidden question files, launch packets, prior outputs, notes, or operator scripts were present in the child directory.

## Scientific CLI controls

Scientific session (attempt 3; first two attempts produced no semantic output):

```text
copilot
  -C <child>
  -p "$(cat <child>/READER-TASK.md)"
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

Not passed: `--allow-all`, `--allow-all-tools`, `--allow-all-paths`, `--allow-all-urls`, `--enable-memory`, `--continue`, `--resume`, `--connect`, `--autopilot`, agent/plugin/custom-instructions options.

Environment: `env -i` with `HOME`, `USER`, `LOGNAME`, `PATH`, `LANG`, `COPILOT_HOME`, `COPILOT_CACHE_HOME` only. Fresh `COPILOT_HOME` contained only the automatically managed `config.json` login/application-state file. `COPILOT_CACHE_HOME` was an empty directory.

GitHub MCP: builtin `github-mcp-server` reported `status: disabled`. File writes: none (`codeChanges.filesModified` empty; child still exactly three files after the run).

## Frozen interpretation

| Field | Value |
| --- | --- |
| Interpretation SHA-256 | `73ca20406b07df6981079ff98a6501378edfea62aca54b77551747ff5bd879bd` |
| Freeze marker | `FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL` |
| Operator structural validation | valid JSON; all required top-level keys present; metadata contains the exact resolved-contract SHA-256; contamination status present; material rule records contain contract pointer(s); freeze marker exact |
| Reader-reported contamination status | `clean: only RESOLVED-CONTRACT.json and INTERPRETATION-RECORD-SCHEMA.json plus the task prompt were used; no other project material or history was consulted.` |
| Operator contamination status | no semantic question set was retrieved or revealed to the child; `FROZEN-SEMANTIC-QUESTIONS.json` and `QUESTION-PHASE-TASK.md` were absent from the child and absent from the raw transcript; no implementation code was requested or written |

The interpretation was extracted from the final assistant JSONL message without semantic editing, correction, repair, or reformatting.

## Apparatus deviations (setup / invocation, not semantic repair)

1. First Homebrew cask fetch of `copilot-cli` hung on an expired GitHub release-asset URL after auto-update. Killed and retried with `HOMEBREW_NO_AUTO_UPDATE=1`. Installed version: 1.0.82.
2. CLI 1.0.82 rejected `--attachment` of JSON files (`file type not supported (must be an image or native document)`). No semantic output. Clean replacement launched with the three authorized files in the child working directory instead of attachments. Isolation flags were not weakened.
3. CLI 1.0.82 rejected `--model=auto --effort=high` (`Model "auto" does not support reasoning effort configuration (requested: "high")`). No semantic output. Clean replacement omitted `--effort` and kept `--model=auto` so the CLI-chosen model identity could be recorded. Isolation flags were not weakened.
4. Child / Copilot home / cache were kept off the system temporary directory so `--disallow-temp-dir` would not block the authorized child aperture.
5. CLI listed builtin skills `customize-cloud-agent` and `github-pr-media` in `session.skills_loaded`. They were not invoked as tools. The only executed tool was `view`.
6. One `view` call targeting a non-child/invalid path was denied (`Permission denied and could not request permission from user`). Subsequent ranged `view` reads of the three authorized child files succeeded. `RESOLVED-CONTRACT.json` could not be read in one shot (38.0 KB) and was read with `view_range`.
7. Gemini was not substituted.

## Confirmations

- Semantic questions were **not** revealed or retrieved for the child.
- The question phase was **not** run.
- No implementation code was requested or written.
- No Contract E disposition is claimed after reader 1.

