# CAL Pipeline Provenance RC1 — Preparation Receipt

Status: `READY_FOR_LOCAL_EXECUTION`

This receipt covers preparation only. It does not record any pipeline case execution.

## Exact package head tested

`079575a2c01701e5af58c4649a311906eb968595`

## Hosted preflight

- workflow: `Research - CAL Provenance RC1 Package Preflight`
- run: `35289905727`
- job: `105430271492`
- conclusion: `success`

Observed passing steps:

- helper Python compilation;
- frozen `RUN-SERIES.json` and Health Canada packet JSON parsing;
- exact Evidence Bundler checkout at `4e1f6fe00e7c350b28f52bfea14f1f8988847884`;
- materialization of all three frozen benchmark Gate packets;
- source counts: Rimebridge 58, Amberbraid 60, Wick 59;
- exact provenance schema checkout at `1a5929295e735e351320cbd8c966dc43afed2859`;
- candidate attestation sealing + schema validation;
- candidate run-manifest sealing + schema validation;
- deterministic directory snapshot equality.

## Prepared cases

1. `first-genuine-b-side-replay`
2. `health-canada-ozempic-001`
3. `rimebridge-simple-support`
4. `amberbraid-temporal-supersession`
5. `wick-missing-decisive`

## Prepared machinery

- exact component/version registry;
- historical replay identities/stopping rule;
- frozen real-world Health Canada Gate packet;
- exact benchmark packet materializer;
- provenance attestation/manifest sealing helper;
- deterministic directory snapshot helper;
- context-free reconstruction verifier;
- retention/artifact layout and stage obligations;
- bounded local-agent execution brief;
- package CI preflight.

## Execution boundary

The executing agent may produce candidate manifest digests but MUST NOT treat its own digest as an independently trusted root.

Phase 1 terminates at:

`READY_FOR_INDEPENDENT_ROOT_FREEZE`

No merge, promotion, release, production authorization, or automatic action is authorized by this preparation receipt.
