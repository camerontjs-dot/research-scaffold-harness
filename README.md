# Research Scaffold Harness

Research Scaffold Harness runs a bounded research task under a controlled workflow condition, preserves the model's original output, and writes a provenance-sealed `scaffold-run-{run_id}/` artifact. It is the upstream stage of a small apparatus built around one question: do structured workflow scaffolds reduce unsupported claims in AI-assisted research?

I built it the way I built quality records in pharma QA. Every run is reproducible, every artifact is hash-covered, and the line between what the model produced and what anyone later concludes about it stays visible. The harness creates the original record to be measured. It does not decide whether a claim is true.

## Apparatus role

The harness is the experimental treatment stage of a three-component apparatus:

1. Research Scaffold Harness runs the task under one of four workflow conditions and emits a C-A `scaffold-run` artifact.
2. [Evidence Bundler](https://github.com/camerontjs-dot/evidence-bundler) consumes C-A, nominates candidate evidence for each claim, and emits a C-B evidence bundle.
3. [Claim Audit Lab](https://github.com/camerontjs-dot/claim-audit-lab) consumes C-B and produces deterministic claim-support verdicts.

Each component honors a locked handoff contract, so the stages stay independently testable. The harness produces the record; the support verdict is two stages downstream.

## Contract pin

The harness produces C-A artifacts that conform to the [Apparatus Handoff Contracts](https://github.com/camerontjs-dot/apparatus-contracts/blob/main/handoff-contract-v1.0.0.md). The canonical controlled vocabulary lives in the [apparatus-contracts repository](https://github.com/camerontjs-dot/apparatus-contracts/blob/main/schema/vocabulary.yaml); a byte-identical copy is embedded here at `schema/vocabulary.yaml`, with the version pinned in `schema/.contract-version`.

The harness knows the v1.1.0 vocabulary (`baseline`, `format_only`, `provenance_scaffold`, `full_scaffold`). Phase 1 fixture artifacts still emit `"1.0.0"` in their `CONTRACT_VERSION` and `schema_version` fields as a documented compatibility accommodation, and downstream consumers accept both.

## What it does

For a chosen condition, the harness renders a frozen prompt over a bounded source packet, runs it through an adapter, and captures the model's raw output verbatim. A uniform extractor then reads the visible answer body and pulls candidate claims. The harness writes a `scaffold-run-{run_id}/` artifact holding the claims, the raw output, a run disposition, per-extractor sidecars, and a `SHA256SUMS` manifest that covers all of it.

Two adapters ship: a deterministic offline stub for plumbing and tests, and an MLX adapter that runs local open-weight models on Apple Silicon. Prompt templates are frozen and hash-tracked, so the same condition renders identically across runs.

## What it does not do

The harness does not verify claims. The `support_status` and `source_refs` written into `claims.yaml` are extraction defaults, not audit output, and must not be read as verdicts. It does not retrieve or score evidence; that is the Evidence Bundler's job.

It also does not treat chain-of-thought as evidence. Reasoning-mode `<think>` content is stripped before official extraction and kept only in a separate exploratory sidecar, so reasoning models and non-reasoning models are measured on the same surface.

## Install and test

Use Python 3.11 or 3.12.

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/python -m pytest -m "not live"
```

The `live` marker covers tests that load a local MLX model on Apple Silicon. To run them, install the model path with `.venv/bin/python -m pip install -e ".[mlx]"` and drop the marker filter.

## Try it offline

The deterministic stub adapter runs the whole path with no model download.

```bash
.venv/bin/scaffold-harness run-task \
  --task tests/fixtures/source-packet-minimal --condition baseline \
  --adapter stub --extract --write --output-dir build/stub-run
.venv/bin/scaffold-harness verify-run build/stub-run/scaffold-run-*
```

The stub echoes the prompt, so this checks the plumbing, not model behavior. `--extract` runs the offline uniform extractor; `--write` seals a C-A artifact with raw-output and run-disposition sidecars under one SHA manifest; `verify-run` re-checks the artifact against the contract. `pilots/pilot-001-rsh-001/` holds a realistic bounded packet (FDA CGMP guidance excerpts plus a fictional challenge memo) for a fuller run.

## Workflow conditions

| Condition | Experimental role |
|---|---|
| `baseline` | Ordinary LLM-assisted source-packet research, minimal process requirements. |
| `format_only` | Visible structure without provenance discipline, disconfirmation, or audit. |
| `provenance_scaffold` | Provenance discipline only. |
| `full_scaffold` | Provenance, disconfirmation, uncertainty labels, and a final claim audit. |

The frozen prompt template for each condition lives in `src/research_scaffold_harness/prompts/` and is hash-tracked in every artifact.

## Status

Phase 1 (skeleton and C-A writer) and Phase 2 (frozen prompts and source-packet runner) are complete. The Phase 2 matrix ran five local MLX models across the four conditions on the RSH-001 task and produced `verify-intake`-green artifacts for all 20 cells.

Phase 5 (measurement alignment) is active. After a human-adjudicated calibration round, Mistral Nemo is the official live extractor (F1 0.89 against the gold sample); the deterministic stub stays the offline default. Cells where a model emitted no visible answer are held for a human scan rather than scored as zero unsupported claims. None of these runs is a support-rate result yet. That waits on the downstream audit.

## Layout

```
research-scaffold-harness/
├── README.md
├── DECISIONS.md                ← architectural decision record for the harness
├── pyproject.toml
├── schema/
│   ├── vocabulary.yaml         ← byte-identical copy of the canonical v1.1.0 vocabulary
│   └── .contract-version       ← contract version pin
├── src/research_scaffold_harness/
│   ├── cli.py                  ← write-fixture-run, run-task, verify-run
│   ├── prompts/                ← frozen condition prompt templates (hash-tracked)
│   ├── runner/                 ← stub adapter, MLX adapter, source-packet loader
│   ├── extractor/              ← uniform answer-body extraction (stub, Nemo, Small 3)
│   ├── models/                 ← Pydantic models for tasks and C-A artifacts
│   ├── contracts/              ← C-A writer, hashing, YAML I/O
│   └── fixture.py              ← contract-shape fixture writer
├── tests/
│   └── fixtures/source-packet-minimal/
├── pilots/
│   └── pilot-001-rsh-001/      ← bounded FDA CGMP packet plus a fictional challenge memo
└── docs/                       ← phase analyses and pilot handoff notes
```

## Decisions

Architectural decisions specific to the harness live in `DECISIONS.md`, following the same decision, rejected-alternatives, rationale, and consequences format used across the apparatus.
