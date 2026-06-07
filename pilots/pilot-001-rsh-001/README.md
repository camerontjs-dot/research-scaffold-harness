# PILOT-001 / RSH-001 — harness source packet (v0.1 materialized)

Date: 2026-06-01 · Phase 5 Step 12, Stage 5 · Status: **MATERIALIZED — both sources present, harness-runnable.**

Materializes the PILOT-001 / RSH-001 source-packet freeze (`pilot-001-rsh-001-source-packet.md`)
into the runnable RSH source-packet schema (`task.yaml` + `sources/<id>/{content.md,metadata.yaml}`,
modeled on `tests/fixtures/source-packet-minimal/`). Loads via `load_source_packet`.

## What is materialized

| Source id | Role | Status |
|---|---|---|
| `src-cgmp-quality-systems` | **Primary FDA evidence** source | ✅ bounded excerpt packet — nine frozen passage anchors quoted from the FDA *Quality Systems Approach to Pharmaceutical CGMP Regulations* guidance; full PDF SHA-pinned, not committed (see `source-provenance.yaml`); `trust_level: primary` |
| `src-fictional-compliance-review-note` | Synthetic **challenge** memo (claims to assess) | ✅ committed text (verbatim from `evidence-bundler/examples/phase-5-draft/fictional-compliance-review-note.md`, fictional banner preserved); `trust_level: background` |
| `src-001` | RSH engineering fixture | ⛔ intentionally excluded (freeze: "Do not use as PILOT-001 scoring evidence unless explicitly relabeled") |

`task.yaml` carries the frozen PILOT-001 task prompt as the research question (`pharma_regulatory`, `expert_checkable: true`, `source_scope: bounded`).

## FDA primary source — bounded excerpt materialization

The primary evidence source is the FDA *Quality Systems Approach to Pharmaceutical CGMP Regulations* guidance (Guidance for Industry, Sept 2006). It is a runtime-download PDF that is **not committed** (`evidence-bundler/examples/phase-5-draft/source-manifest.yaml`: url + pinned `expected_sha256: 69fa9da5…`, retrieval date `2026-05-13`). It is materialized here as a **bounded excerpt packet**, resolving the freeze's three Open Implementation Questions:

1. **FDA text scope → selected excerpts + linked manifest (hybrid).** `sources/src-cgmp-quality-systems/content.md` quotes the nine pre-registered passage anchors (~9.5 KB of text) instead of the full ~80 KB guidance. The complete PDF stays recoverable and integrity-checked via the URL + SHA-256 pinned in `source-provenance.yaml`. This keeps prompt context bounded and the source auditable; `source_scope` stays `bounded`. Whole-PDF-as-text remains a possible *future* variant — and findings-log § 2026-06-01 records why output-token limits do not bind at this source size, so that variant is not forced now.
2. **Fictional note → real source directory** (`src-fictional-compliance-review-note`, in-file fictional banner preserved).
3. **Passage IDs → reuse the Phase-5 anchor IDs exactly** (`pass-qms-framework`, …), preserving source linkage back to the freeze.

**Provenance / integrity.** The PDF on disk was re-verified against the pinned SHA-256 on 2026-06-01. Excerpt text was extracted with pdfminer (the evidence-bundler `PDFExtractor`); the extraction coordinate system was proven by reproducing two published passage hashes exactly. Every excerpt carries an `excerpt_sha256` in `source-provenance.yaml` that round-trips from `content.md` via the recipe recorded there. No model output was generated or altered in this materialization.

## Harness demonstration (what was run)

A **stub-adapter plumbing smoke** over this packet (offline, deterministic) confirms it is harness-runnable end to end:

```
.venv/bin/python -m research_scaffold_harness.cli run-task \
  --task pilots/pilot-001-rsh-001 --condition baseline \
  --adapter stub --extract --write --output-dir build/pilot-001-smoke
# → scaffold-run artifact, run_disposition: ready_for_audit, verify-run PASS
```

The stub echoes the prompt, so this remains a **plumbing check, not a pilot result**. The **Nemo-official** write path it would use is covered by `tests/test_writer_bridge.py::test_bridge_writes_selected_nemo_official_not_stub` (Nemo → `claims.yaml` + `run_disposition` with `extractor_is_stub: false`, all sidecars present) and DECISIONS § 2026-06-01.

## The full pilot run

Per `experiment-design/methods-plan.md` (resolved 2026-05-17): **5 models × 4 conditions = 20 cells**, one run per condition, temperature 0.7, max_tokens 2048. Run extraction + disposition only, with Nemo official:

```
caffeinate -ims .venv/bin/python scripts/run_phase_2_unit4_matrix.py \
  --task-dir pilots/pilot-001-rsh-001 \
  --output-dir build/pilot-001-rsh-001 \
  --extractor all --official-extractor nemo --skip-verify-intake
```

(MLX models load sequentially under the 24 GB ceiling.) Expect the same model-driven compliance + footer-only/body surface effects documented in findings-log § 2026-06-01; re-run the zero-claim adjudication step on the output.

## Component boundary — Evidence Bundler + Claim Audit Lab handoff

The harness stops at **extraction + disposition.** Two components sit downstream, and the split matters. The **Evidence Bundler** consumes the `scaffold-run-*` artifacts (C-A) and builds the measurement-ready bundle (C-B): it matches each extracted claim to candidate FDA passage anchors and seals the bundle with provenance and integrity hashes. The **Claim Audit Lab** then audits that bundle (C-B) and assigns the support verdicts (`supported` / `partially_supported` / `unsupported` / `overstated` / `needs_source` / `not_checkable`), false-caution, and coverage against the freeze's **Expected Audit Hooks**, **Synthetic Challenge Items**, and **Required-Answer Checklist**. The harness produces neither the evidence match nor the verdict. Hand the Nemo-official `scaffold-run-*` artifacts to the Evidence Bundler; `source-provenance.yaml` carries the `related_claim` linkage to seed the match.
