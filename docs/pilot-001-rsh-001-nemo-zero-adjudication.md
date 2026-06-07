# PILOT-001 / RSH-001 — Nemo-Official Zero-Claim Adjudication Packet

Date: 2026-06-02
Status: **OPEN — awaiting human sentence scan.** Confirmatory reporting is HALTED (queue stop-threshold exceeded).
Decision of record: Mistral Nemo = official extractor (F1 0.8916, strong tier; DECISIONS § 2026-06-01).
Source: first real FDA-grounded evidence run — `build/pilot-001-rsh-001` over the `pilots/pilot-001-rsh-001` packet (FDA *Quality Systems Approach to CGMP* bounded excerpt + fictional challenge memo). Distinct from the `build/phase-2-unit4-matrix-v2` calibration corpus. Regenerate this doc with `scripts/calibration/build_pilot_zero_adjudication.py`.

Run provenance: 20 cells (5 models x 4 conditions), one run per cell, temp 0.7, max_tokens 2048, Nemo official, --extractor all --skip-verify-intake. Completed in two segments after an overnight machine-sleep interruption: 16 cells on 2026-06-01 21:57-23:16, then Phi-4-reasoning-plus x4 resumed 2026-06-02 06:34-07:00. Each cell mints a fresh run_id; no cell was run twice (verified: every model x condition appears exactly once).

---

## Why this packet exists

Under Nemo-official, **9 of 20** pilot cells extract zero official claims. The run-disposition gate routes empty-body cells to `missing_final_answer` (excluded from the support-rate denominator, no human-review flag). But the zero-claim integrity rule is explicit: *never treat a zero-claim cell as zero-unsupported without a human sentence scan.* 9 nemo-zero cells exceed the queue stop-threshold of 4, so this packet is produced and confirmatory re-reporting halts until a human scans these cells.

**Two classes (mechanically separated):**

- **Class A — genuine no-answer (7 cells).** The stub footer-reader ALSO found 0 claims. The model exhausted its budget mid-`<think>` and never emitted a visible answer. `missing_final_answer` is appropriate; the human scan should *confirm* no answer is present.
- **Class B — footer-only answer (2 cells).** The stub footer-reader found claims that Nemo's body-reader misses, because the model wrote its answer ONLY in the `Final claims:` footer with no prose body — and the official surface (visible answer body) strips the footer. These cells carry a human-readable answer. Routing them to `missing_final_answer` silently drops real claims; the human must decide whether to (a) re-include via the footer, or (b) accept the body-only protocol and exclude.

## Queue determination

- Nemo-zero cells: **9** of **20** cells that produced a disposition (Class A: 7, Class B: 2).
- Queue stop-threshold: **4**.
- 9 > 4 → **STOP: produce this packet, halt before confirmatory re-reporting.**
- Results stay **Exploratory, not Confirmatory**, until the Evidence-Bundler + Claim-Audit-Lab human-calibrated audit. No support-rate number is promoted from this packet.

## Cell index

| run_id | model | condition | class | stub (footer) | nemo (body) | disposition |
|---|---|---|:--:|--:|--:|---|
| `rsh-cf44b5efe77a` | Phi-4-mini-reasoning-MLX-4bit | format_only | A | 0 | 0 | missing_final_answer |
| `rsh-418e440065fb` | Phi-4-mini-reasoning-MLX-4bit | full_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-d11978a16a46` | Phi-4-mini-reasoning-MLX-4bit | provenance_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-539be3d8d4bc` | Phi-4-reasoning-plus-4bit | baseline | A | 0 | 0 | missing_final_answer |
| `rsh-c2e3367aec08` | Phi-4-reasoning-plus-4bit | format_only | A | 0 | 0 | missing_final_answer |
| `rsh-2bb1e57c241d` | Phi-4-reasoning-plus-4bit | full_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-f3e86c8a807f` | Phi-4-reasoning-plus-4bit | provenance_scaffold | A | 0 | 0 | missing_final_answer |
| `rsh-57a027d76aba` | Qwen3-8B-4bit | full_scaffold | B | 6 | 0 | missing_final_answer |
| `rsh-2dd94a12b220` | Qwen3-8B-4bit | provenance_scaffold | B | 8 | 0 | missing_final_answer |

---

## Class A — genuine no-answer

### `rsh-cf44b5efe77a` — Phi-4-mini-reasoning-MLX-4bit / format_only

- disposition: `missing_final_answer`  ·  raw_output: 11270 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
cs one by one.

**Quality-system scope:**
The first source (pass-qms-framework) mentions that the quality system integrates process consistency, risk assessment, corrective actions, and promotes improvement (sections 211.22(a) and 215.192). So, the first source supports that the quality system must include these elements, but does not detail every aspect, such as the specific procedures for handling nonconformities, which might be covered elsewhere in the guidance.

**Management responsibility:**
The first source implies that management is responsible for ensuring the quality system integrates knowledge-building mechanisms into operational decisions, but does not detail responsibilities like
```

### `rsh-418e440065fb` — Phi-4-mini-reasoning-MLX-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 10337 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
s exemptions, volume thresholds, three-year requalification) are removed from scope.  
- All supported claims carry direct source attribution or inferred compliance alignment.  

---  
*End of assessment.*<|end|><|assistant|><think>

Okay, I need to write a QA-facing assessment based on the provided source packets about pharmaceutical quality systems under FDA CGMP. The user wants a clear evaluation of what's supported and what's not, focusing on quality-scope, management responsibility, CAPA, ANPV, purchasing controls, and noting out-of-scope claims.

First, let me parse the two sources. The first one (src-cgmp-quality-systems) is an actual regulatory source, while the second (src-fictional
```

### `rsh-d11978a16a46` — Phi-4-mini-reasoning-MLX-4bit / provenance_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 10293 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
planning, training, etc. (sourced).
- Claims remaining: escalation (note in passage 2).

Third passage (pass-quality-unit-equipment):

- Process equipment emphasis (sourced).
- Claims remaining: storage/release (note in passage 3).

Fourth passage (pass-capa-system):

- CAPA elements like root cause analysis, etc. (sourced).
- No claims remaining noted here.

Fifth passage (pass-annual-review):

- Evaluation activities (sourced).
- No claims remaining noted here.

Sixth passage (pass-process-validation):

- Process validation ongoing (sourced).
- No claims remaining noted here.

Seventh passage (pass-equipment-qualification):

- Higher standards for calibration (sourced).
- Claims remaining:
```

### `rsh-539be3d8d4bc` — Phi-4-reasoning-plus-4bit / baseline

- disposition: `missing_final_answer`  ·  raw_output: 11424 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
ocused on investigating, understanding, and correcting discrepancies while preventing recurrence. It details that the system should include remedial corrections, root cause analysis, corrective action, and preventive action. The guidance supports a structured CAPA approach.

(4) Annual Product Review: The excerpt "pass-annual-review" suggests that annual product reviews are part of the quality system, however, it doesn't explicitly state that annual product review is mandated by the guidance, but it is recommended as a mechanism to evaluate product performance and quality through trend analyses and process capability assessments. It says "bolster data already collected for the annual review"
```

### `rsh-c2e3367aec08` — Phi-4-reasoning-plus-4bit / format_only

- disposition: `missing_final_answer`  ·  raw_output: 10862 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
der." So I'll produce a footer that says exactly "Final claims:" then new line, then each claim with "- " prefix.

The instructions require that the answer includes a claim table and then the final answer, then the footer with "Final claims:" and then one claim per line with "- " prefix.

I must produce my answer. Let's produce final answer below.

I produce final answer in plain text (no markdown formatting by default?) But instructions said: "By default, do not reply with markdown formatting unless requested" so I'll produce plain text. But instructions say "final answer should be produced with no markdown formatting" by default.

I'll produce a final answer as text with a claim table then
```

### `rsh-2bb1e57c241d` — Phi-4-reasoning-plus-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 10804 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
an annual review activity.

6. "pass-process-validation — Process Validation (PDF chars 52009–52909)". This excerpt says: "Although initial commercial batches can provide evidence to support the validity and consistency of the process,15 the entire product life cycle should be addressed by the establishment of continual improvement mechanisms in the quality system.16 Thus, in accordance with the quality systems approach, process validation is not a one-time event, but an activity that continues throughout a product’s life. As experience is gained in commercial production, opportunities for process improvements may become evident. (CGMP regulations § 211.180 require the review and evaluation
```

### `rsh-f3e86c8a807f` — Phi-4-reasoning-plus-4bit / provenance_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 11157 chars
- nemo diagnostics: `['unclosed-think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['unclosed-think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Raw output tail (last 700 chars) — confirm no answer was produced:**

```
y produces more than fifty commercial batches of a given product per calendar year." But the FDA guidance excerpt doesn't mention any such threshold for annual product reviews. So that claim might be unsupported by the FDA guidance.

The instructions say: "and any claims the packet does not establish." So we need to list claims that are not supported by the FDA guidance excerpts. The fictional compliance review note is clearly fictional. So we need to examine each fictional compliance review finding (the numbered items in the fictional note) and then compare them with what is established in the FDA guidance excerpts (src-cgmp-quality-systems). Let's list the eight findings from the fictional
```

---

## Class B — footer-only answer

### `rsh-57a027d76aba` — Qwen3-8B-4bit / full_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 6567 chars
- nemo diagnostics: `['think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (6) — candidate answer for human scan:**

- The FDA CGMP quality systems require a comprehensive model integrating facilities, equipment, outsourcing, and process validation, with a focus on consistent product safety and effectiveness.
- Management responsibility includes senior involvement in quality improvement evaluation and ensuring contract firms align with regulatory standards.
- Corrective and preventive action (CAPA) systems must include root cause analysis, risk assessment, and documented preventive measures to address discrepancies.
- Annual product reviews must incorporate statistical process control, trend analysis, and process capability assessments to monitor quality and drive improvements.
- Supplier controls require audit-based risk assessments, verification of supplier quality systems, and analysis of material acceptance/rejection trends.
- Change control systems must document impact assessments and align with quality unit approvals for equipment, facilities, and outsourced operations.

### `rsh-2dd94a12b220` — Qwen3-8B-4bit / provenance_scaffold

- disposition: `missing_final_answer`  ·  raw_output: 4661 chars
- nemo diagnostics: `['think-block-stripped', 'official-answer-body-empty']`
- surface diagnostics: `['think-block-stripped']`
- official answer body (what Nemo reads): **empty**

**Footer claims the stub recovered (8) — candidate answer for human scan:**

- The FDA CGMP quality systems scope includes a comprehensive model for pharmaceuticals, including biological products, with a focus on consistent production of safe and effective products (sourced: src-cgmp-quality-systems:pass-qms-framework).
- Management responsibility includes senior management involvement in quality system evaluation and ensuring alignment with CGMP regulations (sourced: src-cgmp-quality-systems:pass-management-improvement, pass-quality-unit-equipment).
- Corrective and preventive action (CAPA) systems are explicitly required under FDA CGMP, involving root cause analysis, preventive actions, and documentation (sourced: src-cgmp-quality-systems:pass-capa-system).
- Annual product reviews are part of the quality system, utilizing statistical process control and trend analysis to monitor quality and support continual improvement (sourced: src-cgmp-quality-systems:pass-annual-review).
- Supplier controls require audits based on risk assessment and verification of supplier quality systems (sourced: src-cgmp-quality-systems:pass-supplier-controls).
- The packet does not support claims about process validation exemptions for legacy processes or annual review thresholds tied to batch counts (unsupported: src-fictional-compliance-review-note).
- Equipment qualification is required under CGMP, but the packet does not establish specific intervals for requalification (uncertain: src-cgmp-quality-systems:pass-equipment-qualification).
- The packet does not support claims about extending shelf life based on accelerated stability data alone (unsupported: src-fictional-compliance-review-note).

