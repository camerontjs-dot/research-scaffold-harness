# Phase 5 Step 12 — Nemo-Official Zero-Claim Adjudication Packet

Date: 2026-06-01
Status: **OPEN — awaiting human sentence scan.** Confirmatory re-reporting is HALTED.
Decision of record: Mistral Nemo = official extractor (F1 0.8916, strong tier; DECISIONS § 2026-06-01, findings-log § 2026-05-31 round 2).
Source: `build/phase-2-unit4-matrix-v2` re-pointed Nemo-official via `scripts/calibration/promote_official_extractor.py`; regenerate this doc with `scripts/calibration/build_nemo_zero_adjudication.py`.

---

## Why this packet exists

Under Nemo-official, **8 of 20** matrix-v2 cells extract zero official claims. The run-disposition gate routes all of them to `missing_final_answer` (official answer body empty → excluded from the support-rate denominator, no human-review flag). But the zero-claim integrity rule is explicit: *never treat a zero-claim cell as zero-unsupported without a human sentence scan.* 8 nemo-zero cells exceed the queue stop-threshold of 4, so per the queue rule this packet is produced and confirmatory re-reporting halts until a human scans these cells.

**Two classes (mechanically separated):**

- **Class A — genuine no-answer (4 cells).** The stub footer-reader ALSO found 0 claims. The model exhausted its budget mid-`<think>` and never emitted a visible answer. `missing_final_answer` is appropriate; the human scan should *confirm* no answer is present.
- **Class B — footer-only answer (4 cells).** The stub footer-reader found claims that Nemo's body-reader misses, because the model wrote its answer ONLY in the `Final claims:` footer with no prose body — and the official surface (DECISIONS § 2026-05-25, *visible answer body is the official surface*) strips the footer. These cells carry a human-readable answer. Routing them to `missing_final_answer` silently drops real claims; the human must decide whether to (a) re-include via the footer, or (b) accept the body-only protocol and exclude.

## Queue determination

- Mechanical `requires_human_zero_claim_scan` count: **0** (every nemo-zero cell also has an empty official body, so the gate routes to `missing_final_answer`).
- Nemo-zero cells in total (spirit of the rule): **8** (> 4 → STOP).
- Already human-scanned in the calibration gold (`gold_2026-05-31.yaml`): the zero-claim non-answer cell `rsh-318e7831856f` (Phi-4-RP / format_only, Class A).
- **Action: produce this packet, halt before confirmatory re-reporting.** The Stage-3 re-interpretation is marked Methodological + Exploratory, not Confirmatory.

## Cell index

| run_id | model | condition | class | stub (footer) | nemo (body) | disposition |
|---|---|---|:--:|--:|--:|---|
| `rsh-61941c57d529` | Phi-4-mini-reasoning-MLX-4bit | format_only | A | 0 | 0 | missing_final_answer |
| `rsh-318e7831856f` | Phi-4-reasoning-plus-4bit | format_only | A | 0 | 0 | missing_final_answer |
| `rsh-854768db6de1` | Phi-4-reasoning-plus-4bit | full_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-4215dcf2aa5b` | Phi-4-reasoning-plus-4bit | provenance_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-deae87836ffb` | Meta-Llama-3.1-8B-Instruct-4bit | provenance_scaffold | B | 5 | 0 | missing_final_answer |
| `rsh-62e3bb973255` | Phi-4-mini-reasoning-MLX-4bit | full_scaffold | B | 11 | 0 | missing_final_answer |
| `rsh-bd453e79e4c5` | Qwen3-8B-4bit | format_only | B | 3 | 0 | missing_final_answer |
| `rsh-7ba55f9a70e5` | Qwen3-8B-4bit | full_scaffold | B | 3 | 0 | missing_final_answer |

---

## Class A — genuine no-answer

### `rsh-61941c57d529` — Phi-4-mini-reasoning-MLX-4bit / format_only

- disposition: `missing_final_answer`  ·  raw_output: 10451 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
ne substantive claim per line, each prefixed with '- '. So, perhaps each original bullet point (each .1, .2, .3, .4, .5 under sections 1-3) is a separate claim, but given the final answer requires only one per line, perhaps they group related points into a single claim per section.

But given the user example, I'm a bit confused. However, perhaps the user expects three main claims, one per section, each encompassing multiple subpoints.

But let's look back at the original answer required to be written after the claim table. The user provided an example where the answer ended with the final claims listed as, for example:

- Management responsibility...
- Production system...
- Laboratory...
```

### `rsh-318e7831856f` — Phi-4-reasoning-plus-4bit / format_only

- disposition: `missing_final_answer`  ·  raw_output: 11725 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
hrough finished product release." So that's two or three claims.

Thus I can produce around 8 claims. But I need to check if the instructions required to list each "substantive claim" in my answer. I can produce a claim table with each claim text from my answer.

The final answer should be a description of the core elements. Should I mention risk management in a separate point? Well, the introduction is already mentioned as "risk management" which is integrated with CGMP requirements. So I'll include that as a claim.

I need to produce a final answer that is a summary text that includes these claims. And then I need to produce a claim table listing each claim text. Then I need to produce the
```

### `rsh-854768db6de1` — Phi-4-reasoning-plus-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 11326 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
a separate core element."

Step 5: Label uncertainty and scope limits. I need to label uncertainty if any. The answer is based on the provided source. But the source is the only packet. It says "provided source packet", so this is the only evidence. There's no uncertainty. Perhaps I'll mention that the delineation of risk management as a separate element is not explicitly provided. But it's integrated. So I'll mention that risk management is not separate. So I'll mention that the risk management is integrated into process understanding and is not an independent element.

Step 6: Create final claim audit table: I'll produce a table with columns: Claim, Status (Retained, Downgraded, or Removed
```

### `rsh-4215dcf2aa5b` — Phi-4-reasoning-plus-4bit / provenance_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 11293 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
se the claims from the table, with inferred or uncertain claims visibly qualified. So I must mention "This claim is inferred, based on the integrated approach mentioned in the introduction." etc.

Let me produce the final answer text that says: "The core elements of a pharmaceutical quality system under FDA CGMP guidance include: Management Responsibility, Production System Controls, Laboratory and Documentation Controls, and integrated Risk Management. Claim 1: ...". But I need to write the final answer using only the claims from the table. I must list each claim in a sentence and then at the end produce the footer "Final claims:" on its own line, and then list each substantive claim on its
```

---

## Class B — footer-only answer

### `rsh-deae87836ffb` — Meta-Llama-3.1-8B-Instruct-4bit / provenance_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 2983 chars
- nemo diagnostics: `['official-answer-body-empty']`
- surface diagnostics: `[]`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (5) — candidate answer for human scan:**

- A robust pharmaceutical quality system integrates current good manufacturing practice requirements with a systematic approach to process understanding and risk management.
- Senior management establishes quality policy objectives and allocates adequate resources for manufacturing operations.
- Process validation demonstrates that manufacturing operations produce consistent results within predefined specifications.
- Analytical methods undergo validation to confirm specificity, accuracy, and reproducibility.
- Laboratory data integrity practices require complete, attributable, and contemporaneous records.

### `rsh-62e3bb973255` — Phi-4-mini-reasoning-MLX-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 12278 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (11) — candidate answer for human scan:**

- Senior management establishes quality policy objectives and oversees manufacturing resources and personnel qualifications.
- Process validation and operational controls ensure consistent production quality through in-process checks, equipment qualification, and environmental monitoring.
- Analytical method validation and traceable laboratory practices maintain accuracy and traceability from raw materials to product release.
- Senior management defines quality objectives and oversees manufacturing resources.
- Process validation and operational controls ensure consistent production quality.
- Analytical method validation and traceable laboratory practices ensure product accuracy.}<|end|><|assistant|><think>
- Alright, so I need to figure out the core elements of a pharmaceutical quality system under FDA CGMP guidance based on the provided passage.
- Let me start by breaking down the passage into its main sections and key points.
- The passage is divided into three sections: Management Responsibility, Production System Controls, and Laboratory and Documentation Controls.
- Each section lists specific elements critical to meeting CGMP requirements.
- Starting with Management Responsibility: The first point mentions that senior management establishes quality policy objectives, allocates resources, defines roles, ensures

### `rsh-bd453e79e4c5` — Qwen3-8B-4bit / format_only

- disposition: `missing_final_answer`  ·  raw_output: 2647 chars
- nemo diagnostics: `['think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (3) — candidate answer for human scan:**

- Senior management establishes quality policy objectives, allocates resources, defines roles, ensures personnel qualifications, and oversees quality through periodic management reviews.
- Process validation, in-process controls, environmental monitoring, equipment qualification, and deviation handling procedures ensure consistent manufacturing results within specifications.
- Analytical method validation, data integrity practices, and documentation of batch records, standard operating procedures, and change control ensure traceability and product quality.

### `rsh-7ba55f9a70e5` — Qwen3-8B-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 2449 chars
- nemo diagnostics: `['think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (3) — candidate answer for human scan:**

- A pharmaceutical quality system under FDA CGMP guidance includes management responsibility for establishing quality policy, allocating resources, defining roles, ensuring personnel qualifications, and conducting periodic management reviews (src-001).
- Production system controls require process validation, in-process controls, environmental monitoring, equipment qualification, and deviation management with root cause analysis and corrective actions (src-001).
- Laboratory and documentation controls mandate validated analytical methods, data integrity practices (complete, attributable, contemporaneous records), and traceability through batch records, standard operating procedures, and change control (src-001).

