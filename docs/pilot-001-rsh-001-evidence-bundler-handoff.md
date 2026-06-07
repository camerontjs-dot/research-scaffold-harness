# PILOT-001 / RSH-001 — Evidence Bundler Handoff (C-A → C-B)

Date: 2026-06-02
Status: **Exploratory — NOT Confirmatory.** No support-rate number may be promoted from this run
until the downstream audit is human-calibrated. Confirmatory re-reporting is **additionally HALTED**
by the zero-claim queue rule (9 nemo-zero cells > threshold 4 — see the adjudication packet).

## What this is

The first real FDA-grounded evidence run of the research-scaffold harness over
`pilots/pilot-001-rsh-001` (FDA *Quality Systems Approach to Pharmaceutical CGMP* bounded excerpt +
fictional compliance-review challenge memo). Distinct from the `build/phase-2-unit4-matrix-v2`
calibration corpus. The harness produced **extraction + disposition only**. This note hands the
artifacts to the Evidence Bundler for the anchor-match + bundle-seal, ahead of the Claim Audit Lab's
support-verdict pass.

## Component boundary

- **Harness (C-A) — DONE.** Generate → extract (stub + Nemo + Small 3 sidecars; **Nemo official**,
  F1 0.8916) → run-disposition. Stops here. Produces neither the evidence match nor the support
  verdict. `support_status`/`source_refs` in `claims.yaml` are extraction defaults, **not** audit
  output — do not read them as verdicts.
- **Evidence Bundler (C-B) — NEXT.** Consume the Nemo-official `scaffold-run-*` artifacts; match each
  extracted claim to candidate FDA passage anchors; seal the measurement-ready bundle with provenance
  + integrity hashes. `pilots/pilot-001-rsh-001/source-provenance.yaml` carries the
  `anchor → related_claim` linkage to seed the match.
- **Claim Audit Lab — AFTER.** Audit the sealed bundle; assign support verdicts
  (`supported` / `partially_supported` / `unsupported` / `overstated` / `needs_source` /
  `not_checkable`), false-caution, and coverage against the freeze's **Expected Audit Hooks**,
  **Synthetic Challenge Items**, and **Required-Answer Checklist**.

## Artifacts handed off

Location: `build/pilot-001-rsh-001/` (gitignored; local-only).
Per cell (`scaffold-run-<run_id>/`):
- `claims.yaml` — Nemo official extraction (the claims to audit)
- `raw_output.txt` — the model's full generated text (official answer body + any footer)
- `run_disposition.yaml` — disposition, `extracted_claim_count`, diagnostics, surface flags
- `intermediates/claims_extractor_{stub,nemo,small3}.yaml` — sidecar extractions (stub = footer-reader)
- `scaffold_run.yaml`, `SHA256SUMS`, `CONTRACT_VERSION` — manifest + integrity

Anchor linkage: `pilots/pilot-001-rsh-001/source-provenance.yaml` maps the 9 frozen FDA passage
anchors to the challenge-memo claim ids they bear on:

| anchor | related_claim |
|---|---|
| pass-qms-framework | clm-qms-coverage |
| pass-management-improvement | clm-capa-risk |
| pass-capa-system | clm-capa-risk |
| pass-annual-review | clm-apr-scope |
| pass-process-validation | clm-validation-exemption |
| pass-equipment-qualification, pass-quality-unit-equipment | clm-equipment-requalification |
| pass-supplier-controls | clm-supplier-qualification |
| pass-stability-requirements | clm-stability-extension |

## Cell inventory — 20 cells (5 models × 4 conditions), Nemo official

| Model | Condition | Nemo claims | disposition | run_id |
|---|---|--:|---|---|
| Phi-4-mini-reasoning-MLX-4bit | baseline | 6 | ready_for_audit | `rsh-a7f18c3e5071` |
| Phi-4-mini-reasoning-MLX-4bit | format_only | 0 | missing_final_answer | `rsh-cf44b5efe77a` |
| Phi-4-mini-reasoning-MLX-4bit | provenance_scaffold | 0 | missing_final_answer | `rsh-d11978a16a46` |
| Phi-4-mini-reasoning-MLX-4bit | full_scaffold | 0 | missing_final_answer | `rsh-418e440065fb` |
| Qwen3-8B-4bit | baseline | 5 | ready_for_audit | `rsh-b5d588064593` |
| Qwen3-8B-4bit | format_only | 8 | ready_for_audit | `rsh-9d1b028c3d7e` |
| Qwen3-8B-4bit | provenance_scaffold | 0 | missing_final_answer | `rsh-2dd94a12b220` |
| Qwen3-8B-4bit | full_scaffold | 0 | missing_final_answer | `rsh-57a027d76aba` |
| Meta-Llama-3.1-8B-Instruct-4bit | baseline | 7 | ready_for_audit | `rsh-39aab307211f` |
| Meta-Llama-3.1-8B-Instruct-4bit | format_only | 6 | ready_for_audit | `rsh-52b585a316e7` |
| Meta-Llama-3.1-8B-Instruct-4bit | provenance_scaffold | 13 | ready_for_audit | `rsh-2da38f6221f1` |
| Meta-Llama-3.1-8B-Instruct-4bit | full_scaffold | 6 | ready_for_audit | `rsh-c42867a9489d` |
| gemma-3-12b-it-qat-4bit | baseline | 14 | ready_for_audit | `rsh-ff5b2229f3c0` |
| gemma-3-12b-it-qat-4bit | format_only | 6 | ready_for_audit | `rsh-30715f88f28f` |
| gemma-3-12b-it-qat-4bit | provenance_scaffold | 6 | ready_for_audit | `rsh-473931ee43a3` |
| gemma-3-12b-it-qat-4bit | full_scaffold | 3 | ready_for_audit | `rsh-c1f1829df729` |
| Phi-4-reasoning-plus-4bit | baseline | 0 | missing_final_answer | `rsh-539be3d8d4bc` |
| Phi-4-reasoning-plus-4bit | format_only | 0 | missing_final_answer | `rsh-c2e3367aec08` |
| Phi-4-reasoning-plus-4bit | provenance_scaffold | 0 | missing_final_answer | `rsh-f3e86c8a807f` |
| Phi-4-reasoning-plus-4bit | full_scaffold | 0 | missing_final_answer | `rsh-2bb1e57c241d` |

**11 cells `ready_for_audit`** (≥1 Nemo official claim) → the support-rate audit operates on these.
80 Nemo-official claims total across the 11.

## Zero-claim hold — do NOT score these as zero-unsupported

**9 cells `missing_final_answer`** (zero Nemo official claims) are excluded from the support-rate
denominator by the disposition gate, **but are held** under the zero-claim adjudication packet
[`docs/pilot-001-rsh-001-nemo-zero-adjudication.md`](pilot-001-rsh-001-nemo-zero-adjudication.md).
The integrity rule: *never treat a zero-claim cell as zero-unsupported without a human sentence scan.*

- **7 Class A — genuine no-answer.** Both reasoning models burned the 2048-token budget mid-`<think>`
  and emitted no visible answer body: Phi-4-mini-reasoning ×3 (format_only, provenance_scaffold,
  full_scaffold) + Phi-4-reasoning-plus ×4 (all conditions). Human scan should *confirm* no answer.
- **2 Class B — footer-only answer.** Qwen3-8B provenance_scaffold (footer=8) and full_scaffold
  (footer=6) wrote claims ONLY in the `Final claims:` footer; the official surface strips the footer,
  so Nemo's body-reader reads 0. **These carry a human-readable answer** — the human must decide to
  re-include via the footer or accept the body-only protocol and exclude. Until then they must not be
  silently dropped.

## Run provenance

20 cells, one run per cell, temp 0.7, max_tokens 2048, Nemo official,
`--extractor all --official-extractor nemo --skip-verify-intake`. Pre-flight `load_source_packet`
confirmed 2 sources + `source_scope: bounded`; a one-cell warm-up (Llama-3.1-8B / baseline, 7 claims)
validated the MLX path on the packet before the sweep.

Completed in **two segments** after an overnight machine-sleep/shutdown interruption (the run died
mid–cell 17 at ~23:16 despite `caffeinate -ims`, while the machine was at 10% battery):
- **16 cells** — 2026-06-01 21:57–23:16 (Phi-4-mini-reasoning, Qwen3-8B, Llama-3.1-8B, gemma-3-12b)
- **4 cells** — Phi-4-reasoning-plus ×4, resumed 2026-06-02 06:34–07:00

Each cell mints a fresh `run_id`; **no cell was run twice** — verified every (model, condition) pair
appears exactly once, 0 partial/corrupt dirs. The interruption did not corrupt or duplicate any cell.

## Gates before any support-rate number is promoted (Exploratory → Confirmatory)

1. **Human sentence scan** of the 9 zero-claim cells (the adjudication packet); resolve the 2 Class B
   footer-only Qwen cells explicitly.
2. **Evidence Bundler** anchor-match + bundle-seal over the 11 audit-ready cells.
3. **Claim Audit Lab** support verdicts + Expected-Audit-Hooks / Synthetic-Challenge / Required-Answer
   coverage, **human-calibrated**.

Only after all three may a support-rate move from Exploratory to Confirmatory.

## Update — 2026-06-03 (match RUN; zero-set may shrink via a scaffold fix)

- **Gate 2 (Evidence Bundler match) is RUN — Exploratory.** All 11 ready cells bundled: **80 claims → candidate FDA passages, 0 no-candidate**; sealed bundles in `build/pilot-001-rsh-001-bundles/<run_id>/` (per-claim match files + `bundle_manifest.yaml` + `SHA256SUMS`), retrieval reports alongside. `scaffold_support_status` stays `uncertain` — candidate matches, **not verdicts**. Gates 1 (human zero-cell scan) and 3 (Claim Audit Lab, human-calibrated) remain open; results stay Exploratory.
- **The 9-cell zero set is partly recoverable and may shrink before the audit.** Root cause: the reasoning models never close `</think>`, so the official surface is empty (findings-log § 2026-06-03). A prompt nudge already rescued 4/7 zeros at the same token budget; nudge v2 + budget-forcing target the rest. **Implication for the denominator:** some current `missing_final_answer` cells may become `ready_for_audit` once the scaffold is fixed — re-run the match over any recovered cells before finalizing the support-rate denominator. The 2 Class B Qwen cells (+ 1 new Class B, Phi-4-reasoning-plus full_scaffold) hinge on the surface-policy decision (count the footer?), still open.
