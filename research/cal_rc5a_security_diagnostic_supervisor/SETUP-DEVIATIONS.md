# CAL RC5A Supervisor Setup Deviations

These are apparatus observations only. They are preserved before evaluator seal and before any fresh RC5A verifier exists.

## 1. Durable qualification path correction

The first committed `qualify_rc5a.py` used the local staging sibling name `aperture`. In the repository the public aperture directory is `cal_rc5a_security_diagnostic_aperture`.

This was detected before evaluator seal and before fresh implementation. The durable runner was corrected at commit `66d9c3f93ba9011e56a30795bbff5c46727b57e9`.

No public protocol semantics, hidden expected class, reference behavior, or weak-control behavior changed.

## 2. Local qualification vector formatting mismatch

The local apparatus-development run that produced the current `QUALIFICATION-RESULT.json` used a local JSON serialization of `PUBLIC-POSITIVE-VECTORS.json` that is semantically equivalent to the committed public vector and contains the same context, signed statements, statement digests, signatures, and semantic request, but is not byte-identical as a whole JSON document to Git blob `babbd96c632e23db6a56d8ff1630e50cb5d5875c`.

The evaluator parses the public vector as JSON and supplies the embedded receipt objects to the candidate as freshly serialized raw receipt JSON. Therefore outer vector-file whitespace/formatting is not part of the scientific input consumed by `verify_pair`.

Nevertheless, the existing local qualification is classified only as **supporting apparatus-development evidence**, not final seal evidence. Before evaluator seal, qualification must be rerun from an exact checkout or exact materialization of the frozen GitHub public aperture and supervisor blobs.

## 3. Same-context evaluator construction

The public RC5A contract and the first supervisor evaluator were designed in the same supervisory context. This is not used as independent oracle evidence.

A separate context-free oracle review is mandatory before seal. Its aperture is prepared on:

`research/cal-rc5a-security-diagnostic-oracle-review-20260906`

## Current gate

- public aperture: frozen for review
- local evaluator development: discriminating on 23 cases and six weak controls
- evaluator seal: **NOT AUTHORIZED YET**
- fresh independent verifier: **NOT STARTED**
- production authorization: **false**
