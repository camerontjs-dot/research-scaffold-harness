# PRE-FREEZE TASK — EB Retrieval-Audit Independent Consumer RC3

## Classification

CONTEXT-FREE REQUIRED.

Fresh independent consumer implementation / research evidence.

This is not a production build, not a promotion, not a Contract B amendment, not a retrieval-quality experiment, and not a semantic evaluation.

## Objective

Implement the smallest independent consumer that, using only the frozen specification and frozen package archive authorized below, can:

1. verify the EB evidence-package structural/integrity rules;
2. reconstruct the complete pre-retention candidate trail for every supplied case;
3. reconstruct the retained candidate trail;
4. recover Contract B admission/review decisions without granting those decisions to the sidecar;
5. detect the six required negative controls;
6. emit a deterministic machine-readable report and a freeze receipt.

The scientific question is whether the package format is independently consumable from its frozen specification and package bytes, without access to the producer implementation or expected results.

## Exact execution repository and aperture branch

Repository:

`camerontjs-dot/research-scaffold-harness`

The supervisor will supply an exact aperture branch and exact starting head. Before reading file contents, perform only the minimum ref lookup necessary to confirm the branch points exactly to that head.

## Exclusive pre-freeze allowlist

At the authorized aperture head, read exactly these files and no other repository content:

- `research/eb_retrieval_audit_independent_consumer_rc3_aperture/SPEC.md`
- `research/eb_retrieval_audit_independent_consumer_rc3_aperture/PRE_FREEZE_TASK.md`
- `research/eb_retrieval_audit_independent_consumer_rc3_aperture/APERTURE_MANIFEST.json`
- the exact GitHub Actions artifact `eb-independent-consumer-rc3-frozen-packages-34434614031` from run `34434614031`, artifact ID `10135740397`, in `camerontjs-dot/research-scaffold-harness`.

You may use the GitHub connector only to download that exact artifact. Do not inspect the workflow, run logs, PR narrative, or any other Actions/repository surface. The artifact ZIP is expected to contain only `FROZEN_PACKAGES.tar.gz` and `FROZEN_PACKAGES.sha256`. Verify both the Actions artifact digest and the inner archive SHA-256 from `APERTURE_MANIFEST.json` before extracting. You may then inspect every file contained inside `FROZEN_PACKAGES.tar.gz`; those archive contents are part of the authorized aperture.

## Pre-freeze denylist

Before the implementation freeze, do NOT inspect or search:

- any other file or directory in `research-scaffold-harness`;
- any Evidence Bundler repository content;
- `camerontjs-dot/evidence-bundler`;
- Evidence Bundler PRs, issues, branches, Actions, source, tests, or history;
- the producer implementation that created the supplied packages;
- prior RC1/RC2 experiment code or results;
- expected per-case counts, expected reconstructed identities, or a reference report;
- CAL repositories or CAL semantic engines;
- prior conversations, project memory, summaries, web search, external documentation, or other project repositories.

General-purpose language/runtime documentation already present in the execution environment is allowed. Do not use network access to obtain project-specific information.

## Implementation location

Create a fresh execution branch from the exact aperture head named:

`research/eb-retrieval-audit-independent-consumer-rc3-<date-or-run-suffix>`

Write implementation and prereveal tests only under:

`research/eb_retrieval_audit_independent_consumer_rc3_execution/`

Do not modify the aperture files or frozen downloaded archive.

Prefer Python standard library only. If a dependency is genuinely required and already available, record it in the freeze receipt. Do not install project-specific packages or import Evidence Bundler code.

## Required prereveal tests

At minimum test:

- all frozen cases can be processed;
- deterministic report generation;
- exact sidecar canonicalization and digest verification;
- Contract B `SHA256SUMS` verification;
- Contract B/envelope/sidecar binding tuple agreement;
- complete candidate reconstruction;
- retained-set versus Contract B history agreement;
- Contract B aperture candidate-count agreement;
- passage-text digest verification;
- authority-boundary enforcement;
- all six mutations from SPEC.md fail for the intended reason;
- frozen input files remain byte-identical to the aperture head/archive.

Do not create tests that depend on supervisor-provided expected per-case answers. Derive only structural invariants from SPEC.md.

## Freeze point

When implementation and prereveal tests pass:

1. write `FREEZE_RECEIPT.json` under the execution directory;
2. include exact aperture head, archive SHA-256, implementation file hashes, test file hashes, runtime/dependency information, commands run, test outcome, and a contamination record listing every project file opened pre-freeze;
3. generate `INDEPENDENT_CONSUMER_REPORT.json` from the frozen packages;
4. commit all implementation, tests, report, and freeze receipt;
5. push the execution branch;
6. open a Draft Research PR against the aperture branch;
7. stop.

Do not seek, read, or infer any post-freeze reference result until the supervisor independently verifies the freeze.

## Contamination stop rule

If you access any forbidden project-specific material before freeze, stop immediately. Do not continue and do not present the run as independent. Emit:

`CONTAMINATED_NO_RESULT`

with the exact material accessed.

If a required aperture file is missing, corrupt, or its hash does not match the manifest, stop with:

`BLOCKED_APERTURE_INVALID`

If implementation cannot be completed from the allowed materials without forbidden information, stop with:

`INCONCLUSIVE_SPEC_INSUFFICIENT`

## Allowed pre-freeze terminal states

Exactly one:

- `FROZEN_AWAITING_REVEAL`
- `CONTAMINATED_NO_RESULT`
- `BLOCKED_APERTURE_INVALID`
- `INCONCLUSIVE_SPEC_INSUFFICIENT`

No production/promotion conclusion is authorized in this thread.
