# Phase 2 Unit 4 — Zero-Claim Forensic Analysis

Date: 2026-05-18
Status: Open — findings feed Phase 5 extractor and prompt iteration
Source data: `build/phase-2-unit4-matrix-smoke-report.md` (20 cells, 5 models × 4 conditions)

---

## Summary

The Phase 2 Unit 4 matrix produced 7 zero-claim cells out of 20. This document records what each model actually emitted, classifies the failure modes, and identifies which are recoverable through extractor tolerance vs. prompt/model changes.

**Bottom line:** Three distinct failure modes. One (1 cell) is directly recoverable by an extractor change. Six (6 cells) require prompt-side or model-selection changes — the extractor received outputs that genuinely lacked extractable claims in any format.

---

## Full Compliance Matrix

| Model | baseline | format_only | provenance_scaffold | full_scaffold |
|---|---|---|---|---|
| Phi-4-mini-reasoning (3.8B) | 10 claims | **0 claims** (FM-B) | 20 claims | 23 claims |
| Qwen3-8B | 3 claims | 3 claims | **0 claims** (FM-B) | 5 claims |
| Llama-3.1-8B-Instruct | **0 claims** (FM-A) | 7 claims | 5 claims | **0 claims** (FM-C) |
| Gemma-3-12b-it QAT | 3 claims | 4 claims | 4 claims | 4 claims |
| Phi-4-reasoning-plus (14B) | 3 claims | **0 claims** (FM-B) | **0 claims** (FM-B) | **0 claims** (FM-B) |

**Legend:** FM-A = double-marker, FM-B = think-block budget exhaustion, FM-C = scaffold-stage exhaustion

**Model-level compliance:** Gemma 4/4, Qwen 3/4, Phi-4-mini 3/4, Llama 2/4, Phi-4-RP 1/4.

---

## Failure Mode A: Double Marker (1 cell — recoverable)

**Affected:** Llama-3.1-8B / baseline (`rsh-14cc40061937`)

### What the model emitted

The model wrote a well-structured answer, then emitted `Final claims:` with 3 substantive claims, then emitted a second `Final claims:` with empty bullet stubs:

```
Final claims:
- Management Responsibility is a crucial element of a pharmaceutical quality system.
- Process validation and in-process controls are essential in a production system.
- Laboratory data integrity and complete records are necessary for quality assurance.

Final claims: 
- 
- 
-
```

### Why the extractor returned 0 claims

`_last_final_claims_segment()` in `extractor/adapters.py:83` uses `re.finditer` and takes the **last** match. The second `Final claims:` marker has 3 lines that are just `- ` (bare bullets) — `_normalize_candidate` strips the `- ` prefix, leaving empty strings, which fail the 4-word `_is_substantive` gate. Diagnostic: `"final-claims segment contained no extractable claims"`.

### Why the model repeated the footer

The baseline prompt instructs:

> End your response with the exact line `Final claims:` on its own, followed by one substantive claim from your answer per line, each prefixed with `- `. This footer is required for downstream measurement; do not omit it or rename the header.

At 4-bit quantization, Llama-3.1-8B appears to have treated the footer instruction as both (a) a content directive and (b) a format template to reproduce. The second marker reads like the model "echoing" the format spec itself — empty `- ` stubs matching the instruction's description rather than filling in content. This is a known small-model behavior: the model generates the instructed format as a structural echo after already completing the task.

### How to eliminate the double-marker

Two options (non-exclusive):

1. **Extractor tolerance (cheap):** Change `_last_final_claims_segment` to iterate markers from last to first and return the first one whose claim-extraction is non-empty. Falls back to reporting `"all final-claims segments empty"` only if every marker's segment yields 0 substantive claims. This preserves the "prefer the last marker" heuristic while recovering the double-marker case.

2. **Prompt hardening (prevents recurrence):** Add a single-occurrence constraint to the footer instruction: "Emit this footer exactly once at the very end." This tells the model not to repeat the marker. Whether small models reliably follow "exactly once" instructions at 4-bit quantization is itself a measurement signal worth observing in Phase 5.

### Recoverability verdict

**Directly recoverable.** An extractor change would rescue 3 claims from this run. The prompt hardening is a separate improvement that reduces the chance of recurrence.

---

## Failure Mode B: Think-Block Budget Exhaustion (5 cells — not recoverable by extractor)

**Affected:**

| Run ID | Model | Condition | Output tokens | Raw chars |
|---|---|---|---|---|
| `rsh-e9827bcbb2f6` | Phi-4-mini-reasoning | format_only | 1,599 | 10,812 |
| `rsh-122f1c1ffec7` | Phi-4-reasoning-plus | format_only | 1,617 | 11,960 |
| `rsh-e07e21b3dc50` | Phi-4-reasoning-plus | provenance_scaffold | 1,581 | 11,145 |
| `rsh-58c5f6d2408a` | Phi-4-reasoning-plus | full_scaffold | 1,602 | 11,547 |
| `rsh-f2957bfdc6d1` | Qwen3-8B | provenance_scaffold | 738 | 5,338 |

All have `finish_reason: stop` (not `length`) and `max_tokens: 2048`.

### What the models emitted

Every output begins with `<think>` and the excerpt shows the model deep in chain-of-thought reasoning — restating the source text, planning the answer, reasoning about claim structure. The extractor searched the full raw output and reported `final-claims marker not found`: the `Final claims:` footer never appeared anywhere.

### Step-by-step reconstruction of what happened

These are single-turn inferences (no tool calls, no multi-step orchestration). The model receives one prompt and produces one continuous output. The reasoning-mode models (Phi-4-mini-reasoning, Phi-4-reasoning-plus, Qwen3-8B with `<think>`) structure their output as:

```
<think>
[chain-of-thought reasoning — restating the task, reading the sources, planning the answer]
</think>

[visible answer with Final claims: footer]
```

For the 5 failed cells, two things may have happened:

**Hypothesis B1 — Never closed the think block.** The model's reasoning loop did not converge. It kept elaborating, restating, and re-planning without ever deciding it was ready to emit `</think>` and produce the answer. It then hit its own stopping criterion (EOS token) while still inside `<think>`. The output is a long monologue with no visible answer at all.

Evidence for B1:
- Token counts are high (1,581–1,617) but below `max_tokens: 2048` — the model stopped voluntarily, not due to truncation.
- The excerpts show circular reasoning patterns: "Let me check the source... the source says... I need to produce a claim table... Let me re-read the source..." — restating the task without progressing.
- The same models under the same conditions sometimes DO succeed (Phi-4-mini baseline: 10 claims, Phi-4-RP baseline: 3 claims) — temperature 0.7 makes the think-block exit stochastic.

**Hypothesis B2 — Closed think, but emitted a non-standard footer.** The model did produce `</think>` and an answer, but used a variant marker (`**Final Claims:**`, `Final Answer:`, `Claims:`) that the regex `r"(?im)^final claims:\s*$"` doesn't match.

Evidence for B2:
- Gemma-3-12b format_only (a SUCCESSFUL run) emitted `**Final Answer:**` in its visible output but still had a separate `Final claims:` marker that the extractor found. So some models do produce both variant markers and the required one.
- However, if this were the case, a more permissive regex would recover the claims. We cannot confirm or deny B2 without the full raw text, which is not persisted to disk.

**Key evidence gap:** The smoke report only preserves the **beginning** of each raw output (the excerpt). The `<think>` block is at the beginning. We cannot see the end of these outputs — which is where the `</think>` tag and `Final claims:` footer would appear (or fail to appear). The `final-claims marker not found` diagnostic confirms the marker was absent from the full text, but we cannot distinguish between B1 (never exited think) and B2 (exited think but used variant marker).

### Stochastic evidence

The same model-condition pair does not deterministically fail:

- **Phi-4-mini baseline:** Failed in both smoke runs (`rsh-7b69f9a1fd78`, `rsh-b8505215c253` — 0 claims each) but succeeded in the matrix run (`rsh-7324949470df` — 10 claims). Same model, same condition, same settings, temperature 0.7. The think-block exit is probabilistic.
- **Phi-4-RP:** Succeeded only on baseline (simplest prompt). Failed on format_only, provenance_scaffold, and full_scaffold. Pattern: more complex prompts → longer think blocks → higher probability of never exiting.

### Why the models stopped (finish_reason: stop)

`finish_reason: stop` means the model generated its EOS (end-of-sequence) token voluntarily. For reasoning models trapped in a think block, this can happen when:

1. The model generates EOS inside `<think>` because it "decides" the reasoning is complete, even though it never generated `</think>` or the answer body.
2. The model generates `</think>` followed immediately by EOS — producing an empty visible answer.
3. The model reaches a point where the next-token probability for EOS exceeds the continuation probability, which is more likely at higher temperatures and after long sequences.

All three are consistent with the observed data: high token count + stop finish reason + no marker found.

### Recoverability verdict

**Not recoverable by extractor alone.** The `Final claims:` marker was never emitted (confirmed by the diagnostic running on the full output). No regex tolerance change will find claims that don't exist.

**Candidate interventions for Phase 5:**

1. **Increase `max_tokens`** — from 2048 to 4096. Won't help if the model stops voluntarily (which it did), but provides headroom if B1 is sometimes caused by the model sensing it's near the token limit.
2. **Think-block stripping** — preprocess the raw output to remove `<think>...</think>` before extraction. Doesn't help if the model never produced the answer body.
3. **Think-block extraction** — extract claims from the think block itself as a secondary signal. Epistemically weaker (these are draft thoughts, not final claims) but could serve as a coverage backup.
4. **Prompt reinforcement** — add a second instruction inside the prompt: "Your `<think>` reasoning block should be concise. The visible answer and `Final claims:` footer are the required output." May help models prioritize exiting the think block.
5. **Temperature reduction** — lower temperature (0.3–0.5) for reasoning models reduces the stochastic variance in think-block length, making exit more deterministic. Trade-off: reduces output diversity.
6. **Model selection** — Phi-4-reasoning-plus (1/4 compliance) may not be viable for the study at current settings. Gemma-3-12b (4/4) and Qwen3-8B (3/4) are stronger candidates.

### Critical gap: raw output persistence

This analysis is limited because the full raw output is not saved to disk. The writer records `raw_output_char_len` but not the text itself. For the 5 FM-B cells, we cannot confirm whether the model ever produced `</think>` or what the tail of the output looked like.

**Recommendation:** Add optional raw-output persistence to the writer. A `raw_output.txt` file alongside `scaffold_run.yaml` would make future forensic analysis conclusive. This is cheap (the text is already in memory at write time) and does not affect the C-A contract.

---

## Failure Mode C: Scaffold-Stage Exhaustion (1 cell — not recoverable by extractor)

**Affected:** Llama-3.1-8B / full_scaffold (`rsh-afe4ff0ca356`)

### What the model emitted

The model followed the 7-stage full_scaffold prompt faithfully through stages 1–5, producing structured output with markdown headers:

```
**Answer Plan:**
[2 sentences]

**Evidence Note Table:**
[3-row markdown table]

**Claim Table:**
[3-row markdown table]

**Disconfirmation Pass:**
[2 sentences]

**Uncertainty and Scope Limits:**
[excerpt cuts off here]
```

Total: 421 tokens, `finish_reason: stop`, `raw_output_char_len: 3,026`.

### Why it stopped

Llama-3.1-8B-Instruct is consistently brief across all conditions:

| Condition | Llama tokens | Gemma tokens | Phi-4-mini tokens |
|---|---|---|---|
| baseline | 148 | 130 | 1,505 |
| format_only | 259 | 369 | 1,599 |
| provenance_scaffold | 487 | 504 | 1,568 |
| full_scaffold | **421** | 725 | 1,610 |

Llama is the shortest model across every condition. For the full scaffold, it produced structured intermediate tables but treated them as the deliverable — not as scaffolding leading to a final answer. After completing the Disconfirmation Pass and starting Uncertainty, the model appears to have decided the task was complete.

Importantly, Llama does NOT use `<think>` tags. Its brevity is not caused by reasoning overhead — it's a model tendency toward concise, structured output. At 4-bit quantization, Llama-3.1-8B-Instruct generates the requested scaffold sections but interprets the 7-stage workflow as "do these stages and stop" rather than "do these stages culminating in a final answer with footer."

### Step-by-step reconstruction

1. Model receives full_scaffold prompt with 7 stages + footer instruction.
2. Model begins stage 1 (Answer Plan) — 2 sentences.
3. Model produces stage 2 (Evidence Note Table) — 3-row table.
4. Model produces stage 3 (Claim Table) — 3-row table with support status.
5. Model produces stage 4 (Disconfirmation Pass) — 2 sentences.
6. Model begins stage 5 (Uncertainty and Scope Limits) — starts writing.
7. Model generates EOS. `finish_reason: stop`.
8. Stages 6 (final claim audit table) and 7 (final answer with `Final claims:` footer) never reached.

The model stopped because it exhausted its "sense of task completion" after producing structured content for 5 stages. At 421 tokens, it had 1,627 tokens of budget remaining — this is not a truncation issue. The model decided it was done.

### Why this didn't happen on provenance_scaffold

Llama succeeded on provenance_scaffold (487 tokens, 5 claims). That prompt has only 3 stages (claim table → final answer → footer), not 7. Fewer intermediate stages means the model reaches the footer instruction before its completion heuristic fires.

### Recoverability verdict

**Not recoverable by extractor.** The `Final claims:` marker was never emitted. The model stopped before reaching stages 6-7.

**Candidate interventions:**

1. **Prompt restructuring for brief models** — move the `Final claims:` footer instruction to a more prominent position (e.g., repeat it after stage 7, or emphasize "stages 1-6 are working notes; stage 7 is the required deliverable").
2. **Stage-count sensitivity** — track whether compliance drops as stage count increases. If so, consider collapsing stages for models that tend toward brevity.
3. **Per-model max_tokens tuning** — not applicable here (budget wasn't the bottleneck).
4. **Model selection** — Llama's 2/4 compliance is driven by its brevity tendency. It may perform better with shorter scaffold prompts (baseline, format_only, provenance) and worse with the full scaffold. This is itself a research signal worth reporting.

---

## Cross-Cutting Observations

### 1. Compliance is model-driven, not condition-driven

| Model | Compliance | Primary failure mode |
|---|---|---|
| Gemma-3-12b QAT | 4/4 (100%) | — |
| Qwen3-8B | 3/4 (75%) | Think-block (provenance only) |
| Phi-4-mini-reasoning | 3/4 (75%) | Think-block (format_only only, stochastic) |
| Llama-3.1-8B | 2/4 (50%) | Double-marker + scaffold exhaustion |
| Phi-4-reasoning-plus | 1/4 (25%) | Think-block (3 of 4 conditions) |

The same condition (e.g., full_scaffold) produces claims on some models and zero claims on others. The primary determinant is the model's tendency toward either (a) extended reasoning or (b) premature completion.

### 2. Think-mode models have a compliance ceiling at current settings

Models with native `<think>` reasoning (Phi-4-mini, Phi-4-RP, Qwen3-8B) succeed when their think block is short enough to leave room for the answer. At temperature 0.7 and max_tokens 2048, this is stochastic. Phi-4-RP's 1/4 compliance rate suggests its think blocks are systematically too long for the current token budget.

### 3. Gemma's 100% compliance is notable

Gemma-3-12b-it QAT is the only model with perfect compliance. It does not use `<think>` tags, produces moderate-length outputs (130–725 tokens), and consistently emits the `Final claims:` footer. As a QAT (quantization-aware trained) model, it may handle instruction-following more robustly at 4-bit than post-hoc quantized models.

### 4. Raw output persistence is a blocking gap

Five of seven zero-claim cells cannot be fully diagnosed because the full raw output is not on disk. We have the beginning (excerpt) and the extractor's verdict (marker not found), but not the actual tail of the output. Adding raw output persistence is the single highest-leverage infrastructure change for future analysis.

---

## Recommendations for Phase 5

| Priority | Action | Addresses | Effort |
|---|---|---|---|
| P0 | Add raw-output persistence (`raw_output.txt` in run dir) | All future forensic analysis | Small — text is already in memory at write time |
| P1 | Extractor: prefer last marker WITH content (double-marker fix) | FM-A (1 cell) | Small — `_last_final_claims_segment` change |
| P2 | Add run-disposition scaffolding before support analysis | All missing/zero-claim cases | Small/medium — preserves methodology gate |
| P3 | Live extractor should extract from visible final answer, not rely on the footer | Footer brittleness across models | Medium — extractor design + ADR |
| P4 | Prompt: add "emit footer exactly once" instruction | FM-A prevention | Small — one line in all 4 templates |
| P5 | Evaluate think-block stripping before extraction | FM-B investigation | Medium — regex strip `<think>...</think>`, then extract |
| P6 | Increase `max_tokens` to 4096 for reasoning models | FM-B headroom | Small — config change |
| P7 | Prompt: reinforce footer as required deliverable, not optional suffix | FM-B + FM-C | Medium — restructure footer instruction placement |
| P8 | Per-model compliance reporting in matrix runner | All | Small — add compliance summary to matrix report |
| P9 | Consider dropping Phi-4-reasoning-plus or adding per-model settings | FM-B (Phi-4-RP 1/4) | Decision, not code |

Methodology alignment note: support-rate analysis should only use runs that pass the proposal's run-disposition gate. A zero-claim extractor output is not a clean zero-unsupported-claim result until a human scan confirms the visible final answer truly has no substantive claims. The footer can remain useful as a compliance signal, but the official comparison unit remains the substantive claim extracted from the final answer through the same post-run path for every condition.

---

## Pointers

- Extractor code: `src/research_scaffold_harness/extractor/adapters.py` — `_last_final_claims_segment()` line 82
- Prompt templates: `src/research_scaffold_harness/prompts/{baseline,format_only,provenance_scaffold,full_scaffold}.md`
- Matrix report: `build/phase-2-unit4-matrix-report.md`
- Per-cell excerpts: `build/phase-2-unit4-matrix-smoke-report.md`
- Marker-change ADR: `DECISIONS.md` § 2026-05-18
- Model selection ADR: `DECISIONS.md` § 2026-05-17
