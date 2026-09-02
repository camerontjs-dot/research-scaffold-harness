# Contract E Authority-Chain Fresh Independent Reproduction RC1 — Successor Comparison Terminal Record

Thread state: **TERMINAL**

Scientific state: **INDEPENDENT_RECOVERABILITY_FALSIFIED**

Primary research disposition: **FALSIFIED**

## Frozen subject preserved

The comparison used the exact prereveal independent implementation and test bytes from RSH PR #9 without post-reveal repair:

- implementation commit: `e9ef0f06e503f280db748532bc7547f3e1234f32`
- implementation blob: `cbbb5d6478dbcfdc54fb6377d57301570500c2ac`
- implementation SHA-256: `9273fe17f54ac2902390bf3af124e290ffc9896bdba2fe8e2e1c4dc9bac14eaa`
- test blob: `bc1a274785eaa4b9502e7c212eeba3d6582bd923`
- test SHA-256: `2f53ae7fa370e15937a79fd32230015650276acea157502cc1ec2654af1cc88d`

The successor workflow verified Git-blob identity, SHA-256 identity, zero diff from the implementation freeze, and reran the frozen prereveal tests before comparison.

## Sealed evaluator

- final seal commit: `396ffbb07d403032a45545d696046466a9ed2561`
- accepted qualification run: `33467464302`
- accepted qualification artifact: `9785351749`
- qualification digest: `sha256:8b886e4445f47c6a63b1fefbb8e54b29600609b988ea81c3d68b034fc95af6de`
- qualification: 94/94 reference matches; no evaluator qualification failures

## Original apparatus failure preserved

Original post-reveal run `33469485659` remains an **INCONCLUSIVE apparatus deviation**. It failed before GitHub created any job or check run, so no scientific comparison occurred. The failed workflow/run record was not overwritten or retried as if it had succeeded.

The exact lower-level GitHub parser/registration diagnostic is unavailable from the exposed Actions metadata. The failure is therefore classified narrowly as `WORKFLOW_STARTUP_CONTROL_PLANE_DEFECT`, not as an implementation or evaluator defect.

## Successor apparatus

The apparatus-only successor added one independent read-only workflow on a separate successor branch:

- branch: `research/contract-e-authority-chain-fresh-rc1-comparison-successor-20260902`
- workflow-introduction commit: `cbea551cbeca87afd2977ae961cde5cb63df1b11`
- workflow: `.github/workflows/research-contract-e-authority-chain-fresh-rc1-comparison-successor.yml`
- successful run: `33632782962`
- job: `100256090527`
- artifact: `9847493780`
- artifact digest: `sha256:db6361a269989ce1e2f1fd30037f004f6fe6c2b26c42838bace83885a41511fb`

The successor changed no implementation, prereveal test, sealed case, reference implementation, comparison semantics, field names, cardinalities, authority bindings, or expected outcomes. It supplied no semantic adapter. Its only purpose was to make the already-authorized sealed comparison executable after the zero-job control-plane failure.

## Scientific result

Cases: **94**

- exact contract matches: **93/94** (`0.9893617021`)
- allowed-outcome matches: **94/94**
- status matches: **94/94**
- authority-kind matches: **94/94**
- false permits: **0**
- false rejects: **0**
- exceptions: **0**
- preservation failures: **0**
- preservation rate: **1.0**
- metamorphic pairs: **13/13**
- canonical reason matches: **93/94**

Sole disagreement: `OBS-NEG-KIND`.

Both implementations rejected the case with `status=insufficient_authority` and `authority_kind=null`. The sealed reference emitted `producer_authority_ceiling`; the frozen independent implementation emitted `unsupported_authority_kind`.

Because the frozen evaluator defines canonical reason equality as part of exact contract agreement, the exact RC1 recoverability claim is **FALSIFIED**. The result must not be relabeled as a pass merely because the disagreement is non-permitting.

## Interpretation bound

Observed evidence supports a narrower statement: the fresh independent consumer recovered every tested authority allow/reject outcome, status, authority kind, preservation obligation, and metamorphic authority relation, with one diagnostic reason-precedence disagreement and no safety-direction disagreement.

This narrower observation does not amend RC1, does not erase the failed exact-recoverability claim, and does not authorize Contract E production promotion.
