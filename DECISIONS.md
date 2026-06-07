# Research Scaffold Harness — Decisions

Architectural decisions specific to the harness live-asset. Contract-level and portfolio-wide decisions live in the portfolio decision log; the harness defers to those.

Format follows ADR conventions used elsewhere in the portfolio: decision, reasoning, what changes, consequences, rejected alternatives.

---

## 2026-06-01 — Pre-calibration guard lifted; `--official-extractor` selects the written extraction (default Nemo)

**Status:** Accepted 2026-06-01. Consumes the 2026-05-31 round-2 calibration decision (Mistral Nemo = official extractor, F1 0.8916; see § 2026-05-25 calibration ADR Outcome + findings-log § 2026-05-31 round 2). Phase-5 Step 12, Stage 1.

**Decision:** The pre-calibration hard block that refused live-extractor writes (`cli.py`, formerly "live extractor writes are blocked before calibration") is **removed**. A new `--official-extractor {stub,nemo,small3}` option designates which of the run extractions is written to `claims.yaml` and the run disposition; `--extractor=all` still persists all three under `intermediates/`. When `--official-extractor` is omitted it resolves to **nemo** for `--extractor=all` (the calibrated production path) and to the single extractor that ran otherwise — so the offline stub path (`--extractor=stub`, the default) keeps writing the stub official with no flags and no MLX load. Asking for an official extractor that was not in the run set is a fast `exit 2` error (`select_official_extraction`), replacing the old blanket block with a deliberate, explicit selection guard.

**Reasoning:** Before calibration the stub was kept official by fiat so no unvalidated live extractor could silently become the source of record. Calibration round 2 closed that question (Nemo, strong tier), so the guard's job is done; what remains is *selecting* the calibrated extractor rather than *blocking* live ones. Keeping the default resolution stub-for-stub-runs preserves the deterministic, offline-first default the harness relies on for tests and quick checks, while making Nemo the effective default exactly where the full extractor set runs.

**What changes:**
- `runner/writer_bridge.py`: new `resolve_official_extractor()` (default resolution) and `select_official_extraction()` (slug-matched pick over the run set, raises `WriterBridgeError` if absent). The disposition builder is refactored to a pure `build_run_disposition_fields()` core so the Stage-2 re-pointing tool recomputes dispositions through the *same* gate logic; the object-based `_build_run_disposition()` is now a thin wrapper with identical output.
- `cli.py run-task`: `--official-extractor` option + early validation; `extraction = extractions[0]` replaced by `select_official_extraction(...)`; an `official_extractor:` line added to the extraction echo.
- `scripts/run_phase_2_unit4_smoke.py` / `run_phase_2_unit4_matrix.py`: `--official-extractor` passthrough (auto → Nemo when the set is `all`), recorded in the cell result + matrix report header.
- Tests: `test_writer_bridge.py` gains selection/resolution/pure-disposition coverage and a Nemo-official write assertion (`extractor_is_stub: false`, all sidecars present); the obsolete `…rejects_single_live_extractor_before_calibration` test is replaced by a `--help` advertisement test and a mismatched-set guard test.

**Consequences:** Live-extractor writes are now first-class. Re-pointing the existing matrix-v2 cells to Nemo (Stage 2) and the PILOT-001 run (Stage 5) both consume this selection. The offline stub path is behaviourally unchanged. No C-A/C-B schema change; `run-disposition-v1` is unchanged.

**Rejected alternatives:**
1. **Click `default="nemo"` literally on `--official-extractor`.** Rejected: with the default `--extractor=stub`, a bare `run-task --extract --write` would demand a Nemo that never ran, breaking the offline default and forcing an MLX load in tests. The resolve-to-the-set-that-ran default keeps the stub path flag-free while still defaulting to Nemo wherever all three run.
2. **Auto-add the official extractor to the run set.** Rejected: would make the default offline invocation load the Nemo MLX model, defeating the deterministic stub default.

---

## 2026-05-25 — Live extractor models: Mistral Nemo 12B (primary) + Mistral Small 3 (secondary), both from outside the generator family set

**Status:** Accepted 2026-05-28. Cameron approved this ADR before Phase 5 implementation. **Official extractor determined 2026-05-31: Mistral Nemo** (calibration F1 0.8916 vs Small 3.1's 0.6748) — see § 2026-05-25 calibration ADR Outcome + findings-log § 2026-05-31 round 2.

**Correction (2026-05-30):** The secondary extractor was originally pinned as `mlx-community/Mistral-Small-3-Instruct-2503-4bit`, which does not exist on HuggingFace — it 404'd on first download during the calibration smoke test. Corrected to `mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit`, the 2503 (March 2025) release the date tag intended: a 24B Mistral build outside the generator family, consistent with the ~13-15 GB memory budget stated below. The colloquial "Mistral Small 3 / Small 3" wording and the `mlx-mistral-small3` extractor id are retained as the family label. See findings-log § 2026-05-30.

**Decision:** The v0.1 live LLM extractors are `mlx-community/Mistral-Nemo-Instruct-2407-4bit` (primary, ~12B) and `mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit` (secondary, ~22-24B), with HuggingFace revision SHAs pinned in `scaffold_run.yaml` at first use. Both models run uniformly across all five generator outputs and all four workflow conditions; they load **sequentially** (not concurrently — 24 GB memory ceiling allows one extractor loaded alongside any single generator). Both run alongside the existing `StubUniformExtractor`. All three extractor outputs are persisted with `extractor_identity` metadata. The **official** extractor for pilot interpretation is determined after calibration (§ 2026-05-25 calibration ADR) — whichever live extractor achieves better metrics vs the hand-adjudicated gold. The other live extractor and the stub remain as comparison/validation signals.

**Reasoning:**

The Phase 2 Unit 4 matrix produced 7 zero-claim cells out of 20, with the stub extractor unable to recover claims from cells where the model did not emit the `Final claims:` footer. Live LLM extractors reading the visible answer body — not just the footer — give independent readings. Selection criteria, in order:

1. **Different family from all generators.** Generator families currently in play: Microsoft (Phi-4-mini, Phi-4-RP), Alibaba (Qwen3), Meta (Llama-3.1), Google (Gemma-3). Using a generator-family model as extractor would create a generator-extractor identity confound: the extractor's structural assumptions match the generator's output patterns, and same-family cells extract more cleanly through no fault of the scaffold. Mistral is outside the generator set, eliminating this confound for both Nemo and Small 3.

2. **Dual-extractor design rather than single-extractor.** Running both Nemo 12B and Small 3 22B from the start provides:
   - **Cross-extractor agreement signal.** Cohen's κ between Nemo and Small 3 (same family, different capability) is itself a methodological finding: does extraction stability hold at this capability gap?
   - **Empirical model selection.** Rather than predicting which extractor will pass calibration and switching after failure, both are calibrated at the same time and the better-performing one becomes official. Cuts iteration cost from "fail-rerun-everything" to "compare-and-select."
   - **Hedge against single-model brittleness.** If Nemo misses claims that Small 3 catches (or vice versa), the disagreement pattern is informative for understanding extractor failure modes. Useful input for the v0.2 mechanism test design.
   - **Marginal compute cost.** Both models fit in 24 GB (loaded sequentially, ~8-10 GB and ~13-15 GB at 4-bit respectively). Total extraction time per cell increases ~2x; full matrix re-run with dual extraction adds ~15-20 minutes vs single-extractor flow.

3. **Both models fit the 24 GB unified-memory budget.** Mistral Nemo 12B at 4-bit is ~7.4 GB on disk, ~8-10 GB in memory with KV cache headroom. Mistral Small 3 at 4-bit is ~12 GB on disk, ~13-15 GB in memory. Loaded sequentially, not concurrently. Total harness disk footprint ~48 GB (5 generators + 2 extractors).

4. **Strong instruction-following for structured extraction.** Both Mistral Nemo Instruct (2407) and Mistral Small 3 Instruct (2503) are benchmarked competitively on instruction-following and structured generation. Apache 2.0 license, well-documented chat templates.

5. **MLX-supported.** Both `mlx-community/Mistral-Nemo-Instruct-2407-4bit` and `mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit` are stable community builds.

6. **Within-family capability progression.** Same lab, same architectural lineage, different parameter count. Provides a clean within-family capability scaling comparison for the methodological discussion: does extraction quality scale with capability at this tier, or is 12B sufficient?

**What changes:**

- New file: `src/research_scaffold_harness/extractor/live.py` implementing `MlxLiveExtractor` base class with adapter pattern for model selection.
- New file: `src/research_scaffold_harness/extractor/nemo.py` — `MlxNemoExtractor` adapter for `mlx-community/Mistral-Nemo-Instruct-2407-4bit`.
- New file: `src/research_scaffold_harness/extractor/small3.py` — `MlxSmallExtractor` adapter for `mlx-community/Mistral-Small-3.1-24B-Instruct-2503-4bit`.
- `pyproject.toml` adds both Mistral models to install instructions; downloaded on first use via `mlx_lm.load()`.
- `scaffold_run.yaml` records both extractors' model HF repo paths, quantizations, `mlx-lm` version, and HF commit SHAs. The `extractor_identity` field gates downstream consumption per extractor output.
- All three extractors run over the same `raw_output.txt`. Outputs persisted as `claims.yaml` (the post-calibration official choice copied here for C-A compliance) plus per-extractor copies under `intermediates/`: `intermediates/claims_extractor_nemo.yaml`, `intermediates/claims_extractor_small3.yaml`, `intermediates/claims_extractor_stub.yaml`. Schema unchanged; per-extractor copies are added artifacts that preserve provenance.
- `runner/writer_bridge.py` updated to invoke all three extractors sequentially and persist outputs.
- Tests: `tests/test_extractor_nemo.py`, `tests/test_extractor_small3.py`, and a cross-extractor regression test.

**Consequences:**

- Total harness compute increases ~2x at extraction time vs Nemo-only. Per cell: ~10-30 seconds combined extraction across both live extractors. Full 5 × 4 matrix re-run: ~15-20 minutes for both live extractors (vs ~5-10 for one).
- Extractor identity becomes a load-bearing field in C-A artifacts. Consumers gate on extractor identity to select the official output post-calibration.
- The 2026-05-17 ADR's commitment to local-only, reproducible inference is preserved. Both HF commit SHA pins prevent silent weight changes.
- Total disk footprint grows from ~29 GB to ~48 GB (5 generators + 2 extractors). Comfortable on modern Mac storage.
- If both extractors miss the calibration hard floor (see § 2026-05-25 calibration), the dual-model failure is itself a stronger methodological signal than single-model failure — it suggests the extraction task is unsolved at the 12-24B local-model tier, not just unsolved by one model.

**Rejected alternatives:**

1. **Use Gemma-3-12b QAT (in-generator-family) as extractor.** Rejected because of generator-extractor identity confound. Gemma-generated cells would extract cleanly because the extractor matches the generator's structural assumptions; Phi/Llama cells would extract less cleanly. Cross-cell support-rate comparisons would be contaminated. Same rejection applies to using any current generator as extractor.

2. **Use Mistral Nemo only (drop Small 3).** Rejected (initially considered; reverted 2026-05-25). Nemo-only forces a sequential "calibrate Nemo → if fail, swap to Small 3 and re-run everything" workflow. Including both from the start lets calibration speak to both extractors at once and accelerates the decision on which is official. Compute cost of dual extraction is small (~15-20 minutes per matrix run).

3. **Use Mistral Small 3 only (drop Nemo).** Rejected because Small 3 alone forfeits the within-family capability comparison and provides less cross-extractor agreement data. Running both costs little.

4. **Use a cloud API extractor (Claude, GPT-4, Gemini).** Rejected because it breaks the local-reproducibility commitment recorded in the 2026-05-17 model-selection ADR. API model behavior shifts without notice; the harness's portfolio claim includes reproducibility. A cloud-API "reference rater" could be added in v0.2 alongside (not replacing) the local extractors for one-time calibration anchoring.

5. **Use OLMo 2 13B (fully open weights and training data).** Tempting for full-stack reproducibility, but instruction-following for structured extraction is less battle-tested than Mistral. Reconsider if a fully-open extractor becomes a portfolio requirement.

6. **Use a small extractor (Ministral 8B, etc.).** Rejected on capability grounds. Extraction over long structured outputs requires robust long-context handling. 8B at 4-bit is borderline for this; both 12B and 22B are safer.

**Pre-merge testing commitments:**

- Verify both Mistral Nemo and Mistral Small 3 load via `mlx_lm.load()` on target M3 hardware.
- Smoke test: extract from one raw output per generator (5 cells total) with each extractor — 10 smoke extractions in total. Confirm output structure matches schema, no crashes, claim counts in a sane range.
- Record and pin HuggingFace commit SHAs in this ADR and in the first `scaffold_run.yaml` produced by each extractor. **Pinned 2026-05-30 (first load):** Nemo `647ca0751669b21a364c86ccc5df54c4d7e4e91c`; Small 3.1 `46135ef3c556bfed61013d8789bd26af02e416c4`. Gap noted: live-extractor revisions are not yet surfaced in the C-A `scaffold_run.yaml`/sidecars (only the official stub + generator revision is), so the pin is currently recovered from the HF snapshot dir rather than the artifact — close this so the SHA is artifact-recoverable.

**Pointers:**

- Stub extractor: `src/research_scaffold_harness/extractor/adapters.py` (`StubUniformExtractor`).
- Phase 5 next-slice plan: `phase-5-next-slice-prompt.md` (updated 2026-05-25).
- Findings entry: the research findings log § 2026-05-25.
- Sibling decisions: generator model selection at this file § 2026-05-17; uniform extraction boundary at this file § 2026-05-17; extraction protocol at this file § 2026-05-25; calibration plan at this file § 2026-05-25.

---

## 2026-05-25 — Extraction protocol: visible answer body is the official surface; think blocks extracted into an isolated exploratory directory

**Status:** Accepted 2026-05-28. Cameron approved this ADR before Phase 5 implementation.

**Decision:** Both live LLM extractors (Nemo and Small 3, per § 2026-05-25 model selection) read the visible answer body only as the official extraction surface for ALL conditions. Before official extraction, the raw output is stripped of:

1. `<think>...</think>` content (and equivalent reasoning-mode delimiters used by Phi-4-mini-reasoning, Phi-4-reasoning-plus, and Qwen3-8B with thinking mode).
2. Scaffold-native intermediate tables (Answer Plan, Evidence Note Table, Claim Table, Disconfirmation Pass, Uncertainty and Scope Limits, etc.).
3. The `Final claims:` footer itself (preserved as a compliance signal in extractor diagnostics, not extracted from).

A second extraction pass runs over the stripped `<think>` content (when present) and writes to **`exploratory/think_block_claims.yaml`** — a new top-level directory inside each `scaffold-run-{run_id}/`, deliberately separated from `intermediates/` to make the exploratory-not-official status visually and structurally obvious. This output is **never promoted to the official claim registry under any condition**. It is preserved exclusively for exploratory analysis and reasoning-trace insight.

**Isolation rationale (why `exploratory/` and not `intermediates/`):**

The `intermediates/` directory holds scaffold-native artifacts that are model self-report — claim tables, evidence tables, disconfirmation outputs. These are NOT promoted to official claims (per the 2026-05-17 uniform-extraction ADR), but they ARE inside the C-A consumption boundary; downstream tools like Evidence Bundler's `verify-intake` may inspect them as part of validation flows.

Think-block claims are categorically different: they are CoT-derived content that the proposal explicitly rejects as evidence (Turpin 2023, Chen 2025). Placing them in `exploratory/` — a new top-level directory NOT defined by C-A — provides three layers of isolation:

1. **Visual.** Separate directory tree makes the not-official status obvious in any run-directory listing. A reviewer or future maintainer cannot easily mistake `exploratory/think_block_claims.yaml` for production data.
2. **Schema.** `exploratory/` is outside the C-A schema. Evidence Bundler `verify-intake` does not consume it. Promotion through the standard pipeline is structurally impossible.
3. **Metadata.** Every claim entry in `exploratory/think_block_claims.yaml` carries `extraction_source: think_block` AND `exploratory: true` as defense in depth against accidental promotion via custom tooling.

**Reasoning:**

The proposal commits to measuring external artifacts, not chain-of-thought, per Turpin (2023) and Chen (2025). Including `<think>` content in official extraction would treat CoT as evidence — the exact failure mode the measurement boundary is designed to avoid. Three further considerations:

1. **Generator asymmetry.** Reasoning models (Phi-4-mini, Phi-4-RP, Qwen3) produce extensive `<think>` blocks; non-reasoning models (Llama-3.1, Gemma-3 except CoT-prompted) produce none. Extracting from think blocks would yield dramatically more claims from reasoning models than from non-reasoning models, purely as a measurement artifact. The support-rate denominator would be inconsistent across models.
2. **Drafts are not commitments.** Models often reason about a claim in a think block, then decide not to state it in the answer body. Extracting from drafts treats not-final content as final and inflates the unsupported-claim count for reasoning models in ways unrelated to scaffold behavior.
3. **Scaffold self-report contamination.** Scaffold conditions produce intermediate tables (Claim Table, Disconfirmation Pass, etc.) above the visible final answer. Extracting from these would re-introduce the confound that the 2026-05-17 uniform-extraction ADR was designed to remove — scaffold conditions' self-reported claims would re-enter the official registry, breaking the four-condition comparability.

The think-block exploratory pass preserves insight that would otherwise be lost. For FM-B cells (think-block exhaustion), the think block contains substantive content; treating it as exploratory-but-not-confirmatory lets future analysis ask "what was the model reasoning about?" without contaminating support-rate measurement.

**What changes:**

- Both `MlxNemoExtractor` and `MlxSmallExtractor` (per § 2026-05-25 model selection) strip `<think>...</think>` (regex), scaffold intermediate sections (header-matched), and the footer line before running official extraction.
- New method `extract_think_block()` on each extractor runs over the stripped `<think>` content. Output goes to `exploratory/think_block_claims.yaml` inside the run directory.
- New top-level directory `exploratory/` inside each `scaffold-run-{run_id}/`. Created only when at least one extractor produces think-block output. Outside C-A schema scope; covered by `SHA256SUMS` as harness sidecar metadata, not as a C-A schema field.
- Diagnostics: each extractor records what surfaces were stripped (lengths, presence/absence), boundary positions, so downstream consumers can audit the protocol.
- `claims.yaml`'s official entries are implicitly `extraction_source: answer_body`; the field can be elided since it's the default.
- `exploratory/think_block_claims.yaml` schema mirrors the official claims registry but every entry carries `extraction_source: think_block` AND `exploratory: true`. File present only when think-block content yielded at least one claim.

**Consequences:**

- Generator asymmetry no longer biases official claim counts. The support-rate denominator is computed identically across reasoning and non-reasoning models.
- FM-B cells (5/20 from the Unit 4 matrix) may now have content in `exploratory/think_block_claims.yaml` even when the answer body produces no official claims. Researchers can investigate: did the model reason about claims it then failed to commit to?
- The disconfirmation-tension test (Pre-registered prediction P1 in `methods-plan.md`) remains clean: full_scaffold's official claims still come from the visible answer body, not from its Disconfirmation Pass table.
- Scaffold-native tables remain `intermediates/claim_table_draft.yaml` per the 2026-05-17 uniform-extraction ADR. The think-block exploratory output is in a new sibling directory (`exploratory/`) and does not interact with `intermediates/`.
- Evidence Bundler `verify-intake` does not consume `exploratory/`. The exploratory directory is harness-only metadata; it can be deleted between runs without affecting the C-A consumption chain.

**Rejected alternatives:**

1. **Include `<think>` content in main extraction.** Rejected because it violates the external-artifacts measurement boundary (Turpin 2023, Chen 2025) and introduces generator asymmetry that inflates reasoning-model claim counts.
2. **Discard `<think>` content entirely.** Rejected because user-facing analysis of FM-B cells requires the think-block content as input. The compromise — exploratory pass with hard separation from official — preserves the analytical capability without contaminating measurement.
3. **Extract from `<think>` only when answer body is empty (fallback).** Rejected because it re-creates the measurement boundary problem in a more subtle way: when the answer body is empty, the official surface silently switches, and some cells' "official" claims are now from CoT while others are not. Inconsistent across the matrix.
4. **Place think-block output in `intermediates/think_block_claims.yaml`.** Rejected (initially considered as the default; reverted 2026-05-25 after explicit isolation review). `intermediates/` is the home for scaffold self-report that is non-promoted but still C-A-adjacent; think-block content is categorically different (CoT-derived, explicitly excluded by proposal stance) and deserves stronger structural isolation. `exploratory/` is a separate directory outside C-A schema scope.
5. **Extract from scaffold intermediate tables instead of stripping them.** Rejected because the 2026-05-17 uniform-extraction ADR explicitly excludes scaffold self-report from official claims. Scaffold conditions' Claim Tables remain `intermediates/claim_table_draft.yaml`; they are preserved as model self-report, not promoted.

**Pointers:**

- Uniform-extraction boundary: this file § 2026-05-17 ("Official claims come from uniform final-answer extraction").
- Phase 2 Unit 4 forensic: `docs/phase-2-unit4-zero-claim-analysis.md` (FM-B think-block exhaustion description).
- Measurement-boundary source notes: `2023-turpin-cot-unfaithful-explanations.md`; `2025-chen-reasoning-models-cot-faithfulness.md`.
- Sibling ADRs in this batch: § 2026-05-25 extractor model selection (dual-extractor); § 2026-05-25 calibration plan.
- Findings entry referencing this decision: the research findings log § 2026-05-25.

---

## 2026-05-25 — Live extractor calibration: LLM-proposed + human-adjudicated gold sample, graduated thresholds with transparent reporting

**Status:** Accepted 2026-05-28. Cameron approved this ADR before Phase 5 implementation. Thresholds, proposer choice, and adjudication workflow remain revisitable if calibration consistently misses targets or if the adjudication step proves too time-intensive.

**Outcome (2026-05-31) — RESOLVED:** Calibration ran against a frozen, human-adjudicated 60-claim gold (`tests/calibration/gold_2026-05-31.yaml`, 8 cells stratified across all 5 models × 4 conditions). With the deterministic containment token-overlap matcher (θ=0.6), **Mistral Nemo is the official extractor: F1 0.8916 (strong tier), precision 0.90, recall 0.88.** Small 3.1 (F1 0.6748, minimum acceptable) clears the hard floor and is retained as documented comparison data; the stub (F1 0.3593) fails the floor and is baseline-sanity only. Cross-extractor κ(Nemo, Small 3.1) = 0.4245. Both live extractors cleared the floor, so selection followed the higher-F1 rule below. Full metrics, matcher design, limitations, and the round-1→round-2 controlled comparison are in the research findings log § 2026-05-31 round 2. Round 1's exact-string matcher could not discriminate (all extractors < 0.60); the gold was held constant and only the matcher was upgraded.

**Decision:** Before either live extractor (Nemo or Small 3, per § 2026-05-25 model selection) is used as the **official** source in pilot interpretation, calibrate both against a gold sample of 25-30 atomic claims stratified across all 5 generator models and all 4 workflow conditions. The stub extractor is also evaluated against the same gold as a baseline sanity check.

**Gold sample generation:** LLM-proposed, human-adjudicated. Each cell's atomic claim candidates are first proposed by a fresh-context LLM session (Claude, Codex, or comparable; MUST be a different model family from both Mistral and any generator in the set). The human coder (Cameron) then accepts, rejects, or edits each proposed claim against the visible answer body. The audit trail records the proposer's identity, the prompt template hash, the proposer's output, every adjudication decision and reason, and the final claim list.

**Threshold structure:** Graduated thresholds with transparent reporting. The hard floor blocks pilot interpretation; everything above is reported with the implied pilot-interpretation strength.

| Threshold tier | F1 vs gold | κ vs other extractor | Pilot interpretation |
|---|---|---|---|
| **Hard floor (blocks pilot)** | < 0.60 | < 0.40 | Extractor unusable. Switch model, iterate prompt, or document v0.1 limitation. If neither live extractor clears, the official source falls back to stub or live extraction is removed from v0.1. |
| **Minimum acceptable** | 0.60 – 0.75 | 0.40 – 0.60 | Pilot interpretable; report only effects exceeding 2× the achieved noise floor (i.e., support-rate differences must clear `2 × (1 − F1)` to be reportable). |
| **Adequate** | 0.75 – 0.85 | 0.60 – 0.75 | Pilot interpretable; standard effect-size reporting. |
| **Strong** | 0.85 – 0.95 | 0.75 – 0.85 | High-confidence interpretation; report tight effect-size bounds. |
| **Excellent** | ≥ 0.95 | ≥ 0.85 | Best-in-class; the calibration result is itself a methodological contribution worth reporting alongside the pilot. |

Report achieved metrics in `findings-log.md`. The **official** extractor for pilot interpretation is the one (Nemo or Small 3) with the higher F1 vs gold, provided it clears the hard floor. If both clear, the better-performing one is official; the other becomes documented comparison data.

**Reasoning:**

AttributionBench, CAQA, and CiteEval all show that automated attribution/extraction quality is non-trivial. "The LLM extractor said so" is not evidence unless the extractor itself has been evaluated against ground truth. The minimum defensible calibration is human-adjudicated gold with reported metrics; EvalSense-style perturbation testing is the stronger calibration, deferred to v0.2.

**Why LLM-proposed + human-adjudicated:**

Pure human hand-coding (~4-8 hours of blank-page reading per gold sample) is methodologically strongest but bottlenecks on Cameron's time and induces drift across long sessions. Pure LLM coding is circular — it would measure whether two LLMs agree, not whether either matches reality (AttributionBench specifically warns against this design). LLM-assisted human adjudication splits the difference defensibly:

1. The LLM proposer accelerates initial atomic-claim identification. Cameron reviews proposed claims rather than reading raw outputs from scratch.
2. The human adjudicates every claim. Final gold reflects human judgment, not LLM judgment.
3. The audit trail (proposer output → adjudication decisions → final gold) makes the procedure inspectable to reviewers.
4. The proposer's model family is locked to be different from any live extractor or generator. This prevents same-family bias from contaminating the gold.

This approach is methodologically defensible **if and only if**:

- The human adjudicates EVERY proposed claim (no batch-accept; no skipping cells).
- The audit trail is preserved in the gold YAML.
- The proposer is held constant across the gold sample (same model, same prompt template, fresh context per cell — "incognito mode" or equivalent).
- The proposer is in a different model family from any extractor under evaluation. With Mistral as the extractor family, Claude or Codex are appropriate proposers; using any Mistral model as proposer would be circular.

**Why graduated thresholds:**

A single binary pass/fail threshold creates incentive to either fish for a passing extractor or game the threshold. Graduated thresholds with transparent reporting:

- Make actual achieved metrics visible to reviewers.
- Tie pilot interpretation strength to actual measurement quality (the 2× noise-floor rule disciplines effect-size reporting).
- Encourage iteration toward higher tiers without locking the project to an arbitrary acceptance bar.
- Preserve a hard floor for cases where extraction is too unreliable to support any conclusion.

The 2× noise floor rule follows standard measurement methodology: differences smaller than 2× measurement error are not interpretable. If achieved F1 = 0.70 (30% error), only support-rate differences > 60% would be reportable — which would imply the condition gaps need to be very large to clear the threshold. This honesty up front prevents reviewers from later asking "how do you know this 8-point gap isn't extractor noise?"

**What changes:**

- New file: `tests/calibration/gold_2026-XX-XX.yaml` stores the gold sample. Schema:
  ```yaml
  gold_version: "2026-XX-XX-v1"
  proposer_identity: "claude-XYZ"          # or "codex-XYZ"
  proposer_prompt_hash: "..."
  coder_identity: "Cameron"
  coding_date: "2026-XX-XX"
  cells:
    - cell_id: "rsh-7324949470df"
      model: "Phi-4-mini-reasoning"
      condition: "baseline"
      visible_answer_body_sha256: "..."
      proposed_claims: [...]
      adjudicated_claims: [...]
      adjudication_decisions:
        - claim_index: 0
          proposal: "..."
          decision: "accept"
          reason: ""
        - claim_index: 1
          proposal: "..."
          decision: "edit"
          final: "..."
          reason: "Removed overgeneralization beyond source."
        - claim_index: 2
          proposal: "..."
          decision: "reject"
          reason: "Not a substantive claim per codebook."
  ```
- New file: `tests/calibration/proposer_prompt.md` — fixed prompt template for the LLM proposer, hashed and referenced from the gold YAML.
- New script: `scripts/calibration/extractor_eval.py` computes precision/recall/F1 vs gold for each of {Nemo, Small 3, stub}, plus Cohen's κ between Nemo/Small3, Nemo/stub, Small3/stub. Outputs a calibration report.
- Calibration results published as a dedicated `findings-log.md` entry: each extractor's identity, achieved metrics, threshold tier, official-extractor selection, iteration history if any.
- If calibration falls below hard floor: iterate (extractor prompt; model swap inside the Mistral family; back to design) → document each iteration in `findings-log.md` → recalibrate. The gold sample is held constant across iterations to prevent fishing.

**Test process:**

1. **Smoke test both extractors.** Load Mistral Nemo and Mistral Small 3 sequentially via `mlx_lm.load()`. Run extraction on one raw output from each generator (5 outputs × 2 extractors = 10 extractions). Confirm output structure matches schema, no crashes, claim counts in a sane range.

2. **Select cells for the gold sample.** Pick 25-30 cells from the existing Unit 4 matrix (no re-running needed). Stratify: 1-2 cells per model-condition combination (5 × 4 = 20 combinations; some get one cell, some two to reach 25-30 total). Include both successful cells (Gemma 4/4) and zero-claim cells (Phi-4-RP, Llama scaffold exhaustion). Record selected cell IDs in `tests/calibration/cells_in_scope.yaml`.

3. **Generate the gold sample (LLM-proposed + human-adjudicated).** For each cell, in sequence:
   a. Cameron starts a fresh LLM session (Claude or Codex; new conversation, no memory across cells — "incognito mode" or equivalent).
   b. The proposer is given: the visible answer body for the cell (think blocks and scaffold tables stripped — same surface the live extractors see); the audit codebook excerpt from `metrics-and-rubric.md` defining atomic substantive claims; the fixed prompt template from `tests/calibration/proposer_prompt.md`.
   c. The proposer outputs proposed atomic claims as YAML.
   d. Cameron reviews each proposed claim against the visible answer body. For each: accept (record reason if non-obvious), reject (record reason), or edit (record original + final + reason). All decisions recorded in the gold YAML for this cell.
   e. Cameron does NOT view live extractor outputs during this step.
   f. The proposer's identity, prompt hash, and adjudication decisions are persisted in the gold YAML.

4. **Run both live extractors** on the same 25-30 cells. Persist outputs to per-extractor intermediates per § 2026-05-25 model selection ADR.

5. **Run the stub extractor** on the same cells. Persist output. Serves as baseline reference.

6. **Compute metrics.** `scripts/calibration/extractor_eval.py` computes:
   - **Nemo vs gold:** precision, recall, F1.
   - **Small 3 vs gold:** precision, recall, F1.
   - **Stub vs gold:** precision, recall, F1 (sanity check; baseline for live extractors to beat).
   - **Nemo vs Small 3:** Cohen's κ per claim.
   - **Nemo vs stub:** Cohen's κ per claim.
   - **Small 3 vs stub:** Cohen's κ per claim.
   
   For κ: for each gold claim, label "extractor X caught it" (yes/no); compute κ over these per-claim binary assignments across both extractors. Restrict to cells where at least one extractor produced ≥1 claim.

7. **Decision gate.**
   - **Both live extractors clear hard floor:** select the higher-F1 one as the official source for pilot interpretation. Record selection and threshold tier in `findings-log.md`. Other extractor's outputs preserved as comparison data.
   - **Only one live extractor clears hard floor:** the cleared one becomes official. The other is reported in `findings-log.md` with its actual metrics as a methodological observation (within-family capability gap matters / doesn't matter at this tier).
   - **Neither live extractor clears hard floor:** live extractors are removed from v0.1 official source. The stub remains as the official source; pilot proceeds with stub-only, and the live-extractor failure is documented as a v0.1 methodological limitation in the proposal's discussion. Note: this is itself a finding — it means the visible-answer extraction problem is unsolved at the local 12-24B model tier.

8. **Matrix re-run.** Once the calibration decision is made, re-run the 5 × 4 Unit 4 matrix with all three extractors. All three outputs persisted per the model-selection ADR. New `findings-log.md` entry summarizes: official extractor for pilot, achieved metrics, post-fix breakdown vs the original Unit 4 numbers, what each extractor's failure modes look like, and whether "compliance is model-driven" still holds after the measurement fixes.

**Consequences:**

- Calibration is a precondition for pilot interpretation, not a checkbox. The harness's portfolio claim depends on the audit chain being defensible; calibration is the first link.
- Expect ~2-3 hours of LLM-assisted human adjudication for the gold sample (vs ~4-8 for pure hand-coding) — proposer accelerates initial claim identification; adjudication is ~30 sec per proposed claim once the rhythm is established.
- Single-coder adjudication is weaker than double-coding. Documented as a v0.1 limitation; double-coding deferred to v0.2 unless a second reviewer becomes available. Inter-coder κ ≥ 0.7 target if a second reviewer joins.
- Pilot interpretation strength is now explicitly tied to achieved calibration metrics via the 2× noise-floor rule, not an arbitrary threshold. Effect-size claims in the eventual writeup will be defensible against the "but is that real or extractor noise?" reviewer question.
- If both live extractors fail the hard floor across iteration and model swap, the live-extraction question is unsolved at v0.1 model tier. This is a meaningful methodological finding that should appear in the proposal's discussion — not a bug to hide.

**Open questions:**

- Should the gold sample expand to include cells from PILOT-001 packet runs once they exist? Likely yes for v0.1 final calibration; initial calibration uses Unit 4 matrix cells.
- What is the exact form of `tests/calibration/proposer_prompt.md`? Drafted alongside the smoke test (step 1); iterated only against the smoke cells, never against the gold sample (to avoid fishing).
- If Nemo and Small 3 cross-extractor κ is low (< 0.5) but both clear F1 hard floor against gold, what does that imply? Likely the two extractors catch different real claims; worth investigating in `findings-log.md` before declaring an official source.
- How to handle ambiguous "is this a substantive claim?" cases during adjudication? Use the audit codebook's atomic-claim heuristic; flag ambiguous cases in `adjudication_decisions[i].reason` for later adjudication review.

**Rejected alternatives:**

1. **Skip calibration; trust the live extractor on output structure alone.** Rejected because AttributionBench/CAQA/CiteEval all show structure does not imply quality. The proposal commits to defensible measurement; uncalibrated extractor results are indefensible under review.

2. **Full EvalSense-style perturbation testing now.** Deferred to v0.2. Perturbation testing requires generating perturbed inputs (claim-relevant phrase swaps) and verifying the extractor's output changes appropriately; that's its own methodological mini-project. LLM-assisted human adjudication is the minimum viable for v0.1.

3. **Pure LLM-generated gold (no human adjudication).** Rejected because circular. Two LLMs agreeing tells us nothing about whether either matches reality. AttributionBench specifically warns against this design.

4. **Pure human-coded gold (no LLM proposer).** Methodologically strongest but bottlenecks on Cameron's time (~4-8 hours). The LLM-assisted approach preserves human-judgment-as-final-gold while accelerating initial claim identification. Switch to pure hand-coding if adjudication ever becomes a rubber stamp.

5. **Single fixed threshold (F1 ≥ 0.75 binary pass/fail).** Rejected (initially considered; reverted 2026-05-25) in favor of graduated thresholds. Binary thresholds create incentive to fish for a passing extractor; graduated thresholds report what is actually achieved and tie pilot interpretation strength to measurement quality.

6. **Use the audit codebook (`metrics-and-rubric.md`) outputs as gold.** Rejected because circular. The audit codebook is what the audit produces given the extractor's claims; using it as gold for the extractor would mean evaluating the extractor against its own downstream output. Independent ground truth requires independent hand-adjudication.

**Pointers:**

- AttributionBench: `2024-li-attributionbench.md`.
- CAQA: `2025-hu-caqa.md`.
- CiteEval: `2025-xu-citeeval.md`.
- EvalSense (deferred follow-up): `2026-dejl-evalsense.md`.
- Audit codebook: `metrics-and-rubric.md`.
- Stub extractor: `src/research_scaffold_harness/extractor/adapters.py` (`StubUniformExtractor`).
- Sibling ADRs in this batch: § 2026-05-25 extractor model selection (dual-extractor); § 2026-05-25 extraction protocol.

---

## 2026-05-18 — Uniform extractor marker is `Final claims:`, written into every prompt template

**Decision:** The uniform claim extractor's marker is the exact string `Final claims:` on its own line. All four condition prompt templates (`baseline`, `format_only`, `provenance_scaffold`, `full_scaffold`) end with a uniform closing instruction requiring the model to emit this footer. The `ExtractorResponse.final_answer_text` and `UniformExtractionResult.final_answer_text` fields are renamed to `final_claims_text`. The stub adapter's deterministic output emits the same marker.

**Reasoning:** The first Phase 2 Unit 4 live smoke run on `lmstudio-community/Phi-4-mini-reasoning-MLX-4bit` (2026-05-18) surfaced that the previous marker `Final answer:` was not requested by any prompt template. Live thinking-mode models did not emit it, so the extractor returned 0 claims with `diagnostics: ['final-answer segment not found']`. The artifact still passed `verify-intake` (the schema allows an empty claim list) but the engineering gate was hollow.

`Final claims:` is the right marker for three reasons:

1. **Less ambiguous to the model.** "Final answer" overlaps with the natural conclusion of chain-of-thought reasoning blocks and invites long prose. "Final claims" signals to the model that what follows is a list, not a flowing answer.
2. **Aligned with what the extractor does.** The extractor pulls discrete claim candidates, not an "answer." Marker name matches purpose.
3. **Uniform across conditions.** All four prompts now require the same footer, which keeps the measurement boundary identical across scaffold treatments — the ADR boundary recorded in § 2026-05-17 below.

**What changes:**

- `prompts/baseline.md`, `prompts/format_only.md`, `prompts/provenance_scaffold.md`, `prompts/full_scaffold.md` — append a uniform closing instruction:
  ```
  End your response with the exact line `Final claims:` on its own, followed by
  one substantive claim from your answer per line, each prefixed with `- `. This
  footer is required for downstream measurement; do not omit it or rename the
  header.
  ```
- `extractor/adapters.py` — regex `^final answer:\s*$` → `^final claims:\s*$`; helper `_last_final_answer_segment` → `_last_final_claims_segment`; diagnostics renamed to `final-claims marker not found` and `final-claims segment contained no extractable claims`.
- `extractor/adapters.py` and `extractor/core.py` — field rename `final_answer_text` → `final_claims_text` on `ExtractorResponse` and `UniformExtractionResult`.
- `runner/adapters.py` `_stub_output` — emits `Final claims:` + bullet list for all four conditions; scaffold preamble structures (claim table, evidence note, audit table) are preserved above the marker.
- All four prompt template body hashes change. Old hashes are no longer valid; consumers reading older artifacts should treat the hash difference as expected for any artifact produced after 2026-05-18.
- Tests updated to use the new marker, field name, and diagnostic strings.

**Consequences:**

- Prompt template hashes are now different from the Unit 1 freeze values. The 2026-05-17 freeze is superseded by a 2026-05-18 freeze. Any future change to a prompt template body requires a fresh ADR entry and a new hash record at closeout.
- Live MLX runs against any of the five ADR-listed models can now produce non-empty `final_claims_text` segments, gated on the model following the prompt instruction. Models that ignore the footer instruction will still produce empty claim registries; the diagnostic `final-claims marker not found` records that case visibly.
- No C-A schema fields, vocabulary values, or writer contract-version constants change. The boundary recorded in § 2026-05-17 below is preserved unchanged.

**Rejected alternatives:**

1. **Keep `Final answer:` and accept 0-claim baseline results as the engineering-grade Unit 4 outcome.** Rejected because the user explicitly asked for non-confirmatory Unit 4 work and a 20-cell matrix of empty claim registries does not exercise the extractor in any meaningful way.
2. **Patch the extractor to fall back to "treat whole output as the final segment" when no marker is found.** Rejected because it breaks the measurement boundary — scaffold-conditions' raw output includes claim tables, evidence tables, and audit tables that would then leak into the official claim registry.
3. **Patch only `baseline` and `format_only`; leave `provenance_scaffold` and `full_scaffold` alone.** Rejected because the four conditions need to share the same extraction protocol; inconsistent prompts would invite reader confusion about why some scaffolds have the footer and others don't.

**Status update (2026-05-18 Unit 4 closeout):** Post-marker-change matrix run passed all four Unit 4 engineering gates — 20/20 cells produced `verify-intake`-green artifacts on RSH-001 across the five MLX models × four conditions. Marker-compliance breakdown: 13/20 cells produced ≥1 claim; 7/20 hit `final-claims marker not found` (model did not emit the footer, or emitted a near-miss variant like `**Final Answer:**`). No cell hit `finish_reason: length`. Compliance is model-driven (`gemma-3-12b-it-qat-4bit` 4/4, `Phi-4-reasoning-plus-4bit` 1/4) and is recorded as honest measurement signal for Phase 5 input, not patched away. Full closeout notes including compliance table and near-miss observations: `phase-2-plan.md` § "Unit 4 completion notes (2026-05-18)."

**Status update (2026-05-18 zero-claim forensic analysis):** Deep analysis of the 7 zero-claim cells identifies three distinct failure modes: (A) double-marker — Llama emitted `Final claims:` twice, second one empty, extractor took the last match and lost 3 real claims; (B) think-block budget exhaustion — 5 cells where reasoning models spent entire output in `<think>` and never emitted the footer; (C) scaffold-stage exhaustion — Llama full_scaffold completed stages 1–5 of 7 then stopped before reaching the footer. Only FM-A (1 cell) is directly recoverable by an extractor tolerance change. Full analysis with per-cell step-by-step reconstruction: `docs/phase-2-unit4-zero-claim-analysis.md`.

**Pointers:**

- Live smoke artifact that surfaced this: `build/phase-2-unit4-smoke/scaffold-run-rsh-7b69f9a1fd78/scaffold_run.yaml` — `extractor_diagnostics: ['final-answer segment not found']`.
- Phase 2 Unit 4 plan: `phase-2-plan.md` § "Phase 2 Unit 4 — Live MLX Integration and End-to-End RSH-001 Validation."
- Matrix artifacts: `build/phase-2-unit4-matrix/scaffold-run-{run_id}/` × 20. Matrix summary: `build/phase-2-unit4-matrix-report.md`. Per-cell smoke excerpts: `build/phase-2-unit4-matrix-smoke-report.md` (append-only — preserves the prior failed-run rows too).
- Adjacent settings-plumbing fix landed in the same patch: `ModelResponse` now carries `temperature` and `max_tokens`; the writer bridge records the real values in `scaffold_run.yaml` instead of the previous hardcoded `0.0` / `1`.
- Adjacent PATH fix landed in the same patch: `find_evidence_bundler_binary()` resolves the CLI relative to `sys.executable` first so `subprocess.run(...)` works without `source .venv/bin/activate`.

---

## 2026-05-17 — Official claims come from uniform final-answer extraction

**Decision:** Official C-A `claims.yaml` entries for all workflow conditions come from a uniform post-run extractor over the model's final-answer segment. Scaffold-native claim tables, evidence tables, and audit tables are preserved as model self-report/intermediate artifacts in later writer wiring, but they are not trusted as the official claim registry.

**Reasoning:** The experiment needs differences between conditions to reflect scaffold behavior, not different extraction methods. If scaffold conditions could promote their own self-reported claim tables into official claims while baseline output was parsed separately, the treatment would change both the writing process and the measurement process. Keeping a single extractor over final answers removes that confound and supports the three-rater design: extractor rating, model self-report, and human audit remain separate signals.

**What changes:**

- Phase 2 Unit 3 adds an `extractor/` package with an explicit adapter interface and deterministic offline `StubUniformExtractor`.
- The extractor walks the last `Final answer:` segment only, ignoring runner headers and scaffold preambles.
- The library API returns `UniformExtractionResult` with extractor identity, stub status, diagnostics, final-answer text, and the typed `ClaimsRegistry`; it does not expose a bare registry as the primary result.
- `StubUniformExtractor` identifies itself as `stub-offline-deterministic` so future artifact wiring can reject or gate stub-derived extraction cheaply.

**Consequences:**

- Stub extraction is plumbing, not evidence assessment. It uses neutral `uncertain` / `0.5` defaults and empty source refs until a live extractor and passage-alignment path are deliberately added.
- Phase 3 can preserve scaffold-native tables as intermediates without re-litigating whether they are official labels.
- No C-A/C-B schema fields, vocabulary values, or writer contract-version constants change in this unit.

**Rejected alternative:** Use scaffold self-reported claim tables as the official registry for scaffold conditions. Rejected because it would make scaffold conditions both the intervention and part of the measurement instrument, while baseline would still need a separate extractor.

---

## 2026-05-17 — Phase 1 emits `"1.0.0"` in artifact CONTRACT_VERSION / schema_version

**Decision:** The harness's embedded contract pin (`schema/.contract-version`) reads `1.1.0`, because the harness knows the v1.1.0 vocabulary (including `format_only`). However, the C-A artifacts produced by the Phase 1 writer (`scaffold-run-{run_id}/CONTRACT_VERSION` and `schema_version` fields inside `claims.yaml`, `passages.yaml`, and `metadata.yaml`) carry the literal string `"1.0.0"` as a fixture-stability and compatibility accommodation.

**Status update (2026-05-17):** Evidence Bundler and Claim Audit Lab now accept both `"1.0.0"` and `"1.1.0"` artifacts. The Phase 1 writer still emits `"1.0.0"` for existing fixture stability; changing emitted artifact version strings to `"1.1.0"` should be a deliberate follow-up, not hidden inside Phase 2 Unit 1.

**Reasoning:** At the time this Phase 1 writer accommodation was introduced, Evidence Bundler still rejected artifacts whose `CONTRACT_VERSION` was not `"1.0.0"`. The v1.0.0 → v1.1.0 bump only added a vocabulary value (`format_only`); no schema field changed. Writing `"1.0.0"` in Phase 1 fixture files kept `verify-intake` passing during the producer build. Evidence Bundler and Claim Audit Lab now accept both `"1.0.0"` and `"1.1.0"`, but the writer's emitted version should still change only in a dedicated pin-bump unit.

**What changes:**

- `schema/.contract-version` (this asset) is `1.1.0` — reflects what the harness knows.
- Writer (Unit 6) emits `"1.0.0"` in `scaffold-run/CONTRACT_VERSION` and in `schema_version` fields of YAML artifacts.
- Pydantic `ContractVersion` type alias accepts both `"1.0.0"` and `"1.1.0"` for read flexibility.
- This accommodation is recorded here, in `harness-plan.md`, and in `phase-1-plan.md`.

**Consequences:**

- Evidence Bundler `verify-intake` passes on harness output.
- The `format_only` value is still emitted in `scaffold_run.yaml`'s `workflow_condition`; downstream consumer-side passthrough is now in place.
- The accommodation can lift in a future writer pin-bump unit. At that point the writer's emitted `CONTRACT_VERSION` and `schema_version` strings change to `"1.1.0"` and this ADR moves to a closed/superseded state.

**Rejected alternative:** Update Evidence Bundler's `CONTRACT_VERSION` constant and `ContractVersion` literal to `"1.1.0"` inside Phase 1. Rejected because it adds a cross-component Bundler change inside what is intended to be a contained "create the harness skeleton" phase. Better as a separate, deliberate Bundler maintenance unit.

**Pointer:** Portfolio decision adding `format_only` is at the portfolio decision log § 2026-05-15.

---

## 2026-05-17 — Model selection and inference runtime for v0.1 pilot

**Decision:** The v0.1 harness runs five local open-weight models via **MLX** (`mlx-lm` Python package) on Apple Silicon. All five models are used across all four workflow conditions to enable within-model comparison of scaffold effects. The same model set also serves the uniform LLM extractor (model TBD from this list; separate decision when extractor is built).

### Selected models

| Model | Author | Params | MLX HuggingFace Repo | Quant | ~Disk | ~RAM |
|---|---|---|---|---|---|---|
| Phi-4-mini-reasoning | Microsoft | 3.8B | `lmstudio-community/Phi-4-mini-reasoning-MLX-4bit` | 4-bit | ~2.5 GB | ~3.5-4 GB |
| Qwen3-8B | Alibaba / Qwen | 8B | `mlx-community/Qwen3-8B-4bit` | 4-bit | ~5.5 GB | ~6-7 GB |
| Llama 3.1 8B Instruct | Meta | 8B | `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit` | 4-bit | ~4.9 GB | ~6-7 GB |
| Gemma 3 12B IT QAT | Google DeepMind | 12B | `mlx-community/gemma-3-12b-it-qat-4bit` | QAT 4-bit | ~6.7 GB | ~8-9 GB |
| Phi-4-reasoning-plus | Microsoft | 14B | `mlx-community/Phi-4-reasoning-plus-4bit` | 4-bit | ~9 GB | ~10-12 GB |

Total disk for all five: ~29 GB. Each model loads individually; the largest (14B at ~12 GB runtime) fits comfortably in 24 GB unified memory with headroom for macOS and KV cache.

### Inference runtime

MLX via `mlx-lm` (Apple's ML framework, native to Apple Silicon unified memory). Not Ollama.

### Model settings (locked for v0.1 pilot)

These settings are frozen before experimental runs. Changes after seeing pilot results are labeled exploratory.

- **Temperature:** TBD — will be set uniformly across all models and conditions. Likely 0.7 for generation, 0.0 for extraction. Exact value locked at prompt-template freeze (Phase 2).
- **Max tokens:** TBD — set per task to prevent truncation without encouraging padding. Locked at task-set freeze.
- **Tools allowed:** None. Source-packet bounded; no live web search, no tool use.
- **Source access:** Bounded source packet only. Source text provided in prompt context.
- **Number of runs:** 1-3 per model per condition per task (stretch goal: 3). Locked at pilot freeze.
- **Prompt templates:** Frozen and hash-tracked. See `condition-prompts.md`.
- **Chat template:** Each model's native chat template via `tokenizer.apply_chat_template()`.

**Reasoning:**

*Why these five models:*

1. **Five organizations** (Microsoft, Alibaba, Meta, Google, optionally Mistral) — demonstrates scaffold effects are not model-specific. Reviewers expect architectural diversity.
2. **Three size tiers** (3.8B / 8B / 12-14B) — tests whether scaffold benefit scales with model capability. A small model that can't follow complex instructions may not benefit from the full scaffold; a large model may already self-correct without it. Both outcomes are informative.
3. **Thinking-mode models** (Phi-4-mini-reasoning, Qwen3-8B, Phi-4-reasoning-plus) have native `<think>` chain-of-thought. This creates a natural sub-question: does a model with built-in CoT reasoning still benefit from an external process scaffold? Qwen3's toggleable thinking mode (`/think` vs `/nothink`) is especially useful — same model, with and without internal reasoning traces.
4. **QAT vs post-hoc quantization** (Gemma 3 QAT is quantization-aware trained; the others use post-hoc 4-bit). Worth noting as a potential methodological factor, even if not a primary variable.
5. **All models released 2024-2025**, well-benchmarked, and available as pre-converted MLX 4-bit weights on HuggingFace.

*Why MLX over Ollama:*

1. **Hardware constraint.** Ollama's MLX backend (v0.19+) requires 32 GB+ unified memory. The target hardware is a 24 GB M3 MacBook Air. Without the MLX backend, Ollama falls back to llama.cpp — slower and higher memory overhead.
2. **Performance.** MLX on Apple Silicon delivers 15-30% faster token generation and up to 5x faster prompt prefill than llama.cpp, with ~10% lower memory usage (no CPU-GPU copy; direct unified memory access via Metal compute shaders).
3. **Programmatic control.** `mlx-lm` exposes a direct Python API (`load`, `generate`, `stream_generate`) with no HTTP layer. For a scripted research harness running batch experiments, this eliminates unnecessary overhead. An OpenAI-compatible server (`mlx_lm.server`) is available when needed.
4. **Model swapping.** `load()` with a different HuggingFace repo path. Models cache on disk after first download; reloading into GPU memory takes seconds.

*Why five models, not one:*

The canonical proposal's methods-plan lists "same model across all conditions, or multiple models?" as an open question. For the pilot, running all five models across all conditions is feasible (5 models x 4 conditions x 3 tasks x 1-3 runs = 60-180 runs). Using multiple models strengthens external validity and avoids the reviewer objection that scaffold effects are idiosyncratic to one model's training.

**What changes:**

- The harness `runner/` module targets `mlx-lm` as the inference backend, not an OpenAI-compatible HTTP API.
- Phase 2 prompt templates must be tested against all five models' chat templates.
- `scaffold_run.yaml` records: model HuggingFace repo path, quantization, mlx-lm version, prompt hash, config hash, hardware identifier.
- The `runner/` abstraction loads models via `mlx_lm.load()` and generates via `mlx_lm.generate()`.
- Closes open item #8 in `canonical-scaffold-evaluation-proposal.md` (model and settings).
- Partially closes the methods-plan open question "same model across all conditions, or multiple models?" — answer: multiple models, all conditions.

**Consequences:**

- The harness is Mac-only for v0.1. This is acceptable — the pilot runs on one researcher's machine. If the study scales to collaborators, a llama.cpp or vLLM backend adapter can be added without changing the C-A output contract.
- Approximate generation speed on M3 Air: 35-45 tok/s (3.8B), 25-40 tok/s (8B), 15-25 tok/s (12-14B). Adequate for pilot-scale runs but not fast. A full 180-run stretch goal may take several hours of compute time.
- Temperature and max-tokens settings remain open until prompt-template freeze (Phase 2). This ADR records the model list and runtime; the full settings lock is a Phase 2 gate.
- If a model's MLX weights are updated or re-quantized on HuggingFace between now and pilot runs, the harness must pin the exact revision hash in `scaffold_run.yaml` to ensure reproducibility. The runner should record the HuggingFace commit SHA.

**Pre-merge testing commitments:**

- Before Phase 2 prompt-template freeze: verify each model loads, generates, and respects its chat template via `mlx-lm` on the target hardware.
- Before pilot runs: verify that `scaffold_run.yaml` correctly records model repo, quantization, mlx-lm version, and HuggingFace commit SHA for each model.
- Smoke test: one baseline run per model on RSH-001, confirming the C-A writer produces valid artifacts that pass Evidence Bundler `verify-intake`.

**Rejected alternatives:**

1. **Ollama as runtime.** Rejected because Ollama's MLX backend requires 32 GB+ RAM, exceeding the target hardware. Falling back to llama.cpp sacrifices 15-30% generation speed and ~10% memory efficiency. Ollama's convenience (one-command pull, built-in API) is outweighed by the performance and compatibility constraints.
2. **Single model design (one model, all conditions).** Rejected for the pilot because it weakens external validity. Reviewers will ask whether scaffold effects generalize across architectures. Running five models is feasible at pilot scale and directly answers this. A single-model sensitivity analysis can still be reported per-model.
3. **Larger models (30B+, 70B+).** Rejected because they exceed the 24 GB memory ceiling even at aggressive quantization. The 14B ceiling is a hardware constraint, not a design preference. If results warrant, a follow-up study on larger hardware can test whether scaffold effects persist at higher capability.
4. **Cloud API models (GPT-4, Claude, Gemini).** Rejected for v0.1 because: (a) cost scales with run count, (b) API models change without notice, breaking reproducibility, (c) the portfolio claim includes local reproducibility and inspectability. Cloud models are a natural extension for a follow-up comparison.
5. **LM Studio as runtime.** Rejected because scripting and reproducibility are harder than with `mlx-lm`'s direct Python API. LM Studio's GUI is useful for manual exploration but adds unnecessary indirection for a batch research harness.
6. **Mistral Nemo 12B as a sixth model.** Deferred, not rejected. Adds European-lab architectural diversity but is from July 2024 (oldest in the set). Can be added if reviewer feedback specifically requests Mistral representation.

**Pointers:**
- Open item #8 in `canonical-scaffold-evaluation-proposal.md` line ~525.
- Methods-plan open question at `methods-plan.md` § "Design Choices To Resolve."
- Harness runner architecture at `harness-plan.md` § "Architecture Sketch."
- Contract version accommodation at this file § 2026-05-17 (above).
