# Contract D RC3 fresh independent consumption reproduction — results

## Repository / isolation identities

- Repository: `camerontjs-dot/research-scaffold-harness`
- Branch: `research/contract-d-rc3-fresh-reproduction`
- Starting base commit: `548bfa81f65290eda15af658f647497679b840ef`
- Starting base tree: `191976638bbf8b7153e3f2c94945a2f15cd640ad`
- Frozen independent implementation final SHA: `7e64784761dc52f881d5c8ab522e8dea9348b841`
- Frozen independent implementation tree: `d4202a8c1df675d0d85c1c4ee650d6ba9f593336`
- Pre-reveal freeze receipt commit: `221141d3f147cd8ffd44e9006b6268d38f879835`
- Pre-reveal freeze receipt tree: `d509e8a04f4e3835b753254bf3bdca3e0fea675f`
- Freeze timestamp: `2026-08-30T17:31:49Z`
- Freeze receipt timestamp: `2026-08-30T17:32:58Z`
- Post-reveal comparison completed locally by `2026-08-30T17:37:25Z`.

The implementation, tests, self-generated fixtures/cases, and predictions were not modified after `7e64784761dc52f881d5c8ab522e8dea9348b841`. This results record is an append-only post-freeze receipt layer.

## Pre-freeze sources actually opened

At `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`:

1. `research/contract-d-independent-authority-rc3/candidate/SPEC.md` — blob `a91a9f171a3b5f3241b5970d7c0415e00f0477d7`
2. `research/contract-d-independent-authority-rc3/candidate/schema.json` — blob `41481aa7941a789534c974ed7b368fddead6ce5a`
3. `research/contract-d-independent-authority-rc3/candidate/effect-registry.json` — blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc3/candidate/fixtures/valid.json` — blob `f823936c9945ea551943c40bee1e956faf1d834d`
5. `research/contract-d-independent-authority-rc3/candidate/fixtures/invalid.json` — blob `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6`
6. `research/contract-d-independent-authority-rc3/candidate/conformance-cases.json` — blob `229f2898f756f9ca078086cfc99d2a6a2edd2a73`

No other `apparatus-contracts` path was opened before freeze.

Administrative reads before freeze were limited to the exact target branch-name existence check and supplied base-commit metadata. The base metadata call exposed only an unrelated MLX test diff; this non-answer-bearing deviation is preserved in `FREEZE_RECEIPT.md`.

The listed durable governance filenames had no repository/ref locator in the packet. One exact lookup for `CONTEXT-FREE-EXECUTION-PROTOCOL(1).md` at the supplied harness base returned 404. No repository-wide search was used to compensate; no governance content was imported.

## Frozen implementation / test / fixture identities

- Implementation `contract_d_rc3.py` — blob `7132e96c635c841daff375faafb05b5fe3bbedca`
- Tests `test_contract_d_rc3.py` — blob `8d60de4c69e8b3a94eb3c817e2660d2f8affa07d`
- Self-generated fixtures — blob `e6bf0591a7aa9625d383265b8f69a4314a3961f0`
- Metamorphic/weak-control cases — blob `c377a37dfdb0e5e86d915d2d7e6773a3ebb87265`
- Combined fixture/case tree — `f93644b5f634e7fccc934039a056a8ab4bfa4318`
- Pre-reveal predictions — blob `ad34757614b13be895533cb870b7fcaeb2ed7575`
- Pre-reveal receipt — blob `1663b2deac0770fca6e6c778a6de9f0308761329`

## Test receipts

### Pre-freeze local

Command: `cd /tmp/contract-d-rc3-fresh && python -m unittest -v`

Result: `Ran 66 tests in 0.022s` / `OK`.

The exact local files were independently Git-hashed after reveal and still matched the frozen blobs for implementation, tests, fixtures/cases, and predictions.

### Hosted

A post-freeze check for workflow runs attached to freeze commit `7e64784761dc52f881d5c8ab522e8dea9348b841` returned no workflow runs. No hosted CI receipt therefore exists for this isolated research branch; the local receipt is the executable test receipt.

## Contamination statement

No packet-denied material was exposed before the implementation freeze. The first apparatus reference implementation reveal occurred only after both freeze commit `7e64784761dc52f881d5c8ab522e8dea9348b841` and pre-reveal receipt commit `221141d3f147cd8ffd44e9006b6268d38f879835` existed. Independence is not contaminated.

No optional historical RC2 or prior independent reproduction material was opened after comparison.

## Post-freeze sources opened

At `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`:

1. `research/contract-d-independent-authority-rc3/candidate/contract_d_core.py` — blob `de46bb146b77fb34e721d16a51423ef83d23e675`
2. `research/contract-d-independent-authority-rc3/candidate/contract_d_validate.py` — blob `d9d621df1e817adbb5468be25ef65272c457e8cc`
3. `research/contract-d-independent-authority-rc3/candidate/contract_d_consume.py` — blob `37b03c8bf3be0ee183ab0369c01ec377a5265e69`
4. `research/contract-d-independent-authority-rc3/candidate/tests/test_rc3.py` — blob `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39`

At `camerontjs-dot/decision-engine@63b0245b03ea63d0248a5aced83fba6697697598`:

5. `research/contract-d-rc3-producer-conformance/emit.mjs` — blob `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`

The producer source copied for local execution Git-hashed exactly to `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`.

## Native Decision Engine -> RC3 -> frozen independent consumer

The exact frozen `emit.mjs` was executed under Node `v22.16.0`. Its emitted Decision objects were parsed and supplied directly, unchanged, to the frozen independent consumer. No translation adapter was inserted. Applicability expectations were configured from the object's declared upstream/policy/target boundary plus the requested operation/parameters, but the Decision object itself was not transformed.

| Producer object | Frozen independent outcome | Frozen semantic identity |
| --- | --- | --- |
| `source-audit-clear` | `candidate_for_authorization` | `decision:sha256:85bd84dc0fbe36d47cbe6325dfa65fc36ccbbd69aff510055b5891136ecbf4ac` |
| `citation-use-clear` | `candidate_for_authorization` | `decision:sha256:f26789dc854d8583f923c4d600e493f910d60c721e861487307d6c64373b6679` |
| `task-dispatch-clear` | `candidate_for_authorization` | `decision:sha256:9f389768439368165671360d08d16bc9f72f5768a5c468344ba27e9432b40eaf` |
| `completed-hold` | `hold` | `decision:sha256:82460425b646110c11bc659a76230f5e4a88620e634f478fc8fc879e4ba93905` |
| `evaluation-failed` | `evaluation_failed` | `decision:sha256:6ed6155819124bc5fc205f84b21bc283a21eee1d937cf36aa1fc2d4aaef49cd9` |

The revealed reference logic yields the same outcomes and semantic identities for those five native exact cases.

**Native cross-repository consumption result: PASS for the required five frozen producer classes, with no bespoke translation adapter.**

## Reference comparison method

The revealed reference source was inspected directly. A separate post-reveal comparison oracle encoded the revealed validation, normalization, identity, and applicability control flow without changing the frozen independent implementation. Systematic JSON-representable mutation matrices then compared reference behavior against the frozen implementation.

Matrix summary:

- Validation cases compared: 13; raw disagreements: 1.
- Jointly valid semantic-identity cases compared: 12; disagreements: 0.
- Applicability cases compared: 51; raw disagreements: 11.
- The 12 raw disagreements reduce to three authority-relevant behavior classes below.

The three classes are also directly evident from the revealed source control flow, so the disposition does not depend only on the post-reveal comparison oracle implementation.

## Complete disagreement table

| # | Behavior | Frozen reference | Frozen independent | Classification | Authority relevance |
| --- | --- | --- | --- | --- | --- |
| 1 | Explicit `effect.params: null` on otherwise valid `knowledge.add_verified_tag@1` | Rejects because supplied `params` must be an object; consumption is `cannot_establish` | Treats `null` as if params were omitted, materializes default `scope=claim`, and can return `candidate_for_authorization` | **Independent implementation defect**. Frozen schema declares `effect.params` type `object`; `null` is not omission. | Accepted/rejected object class; fail-closed machinery; safe-default boundary. |
| 2 | Valid clear `knowledge.add_verified_tag@1` Decision with normalized `scope=object`, while external requested effect parameters are absent/`None`/`{}` | Absence means no requested parameter constraint; exact operation can remain `candidate_for_authorization` | Applies the Decision-side safe default `scope=claim` to the request side, causing `not_applicable` against Decision `scope=object` | **Independent implementation defect**. The frozen spec says compare any externally requested machine-semantic parameters; it does not turn an absent external constraint into a stored Decision default request. | Requested-parameter applicability and effect-parameter meaning. Three raw matrix disagreements. |
| 3 | Valid completed HOLD Decision with requested operation or requested parameters that do not match the Decision effect | Returns `hold` before checking requested operation or requested effect parameters | Checks requested operation/parameters first and returns `not_applicable` on mismatch | **Reference implementation defect relative to frozen SPEC.** The frozen requested-operation section says operation/parameter mismatch is `not_applicable` and provides no HOLD exception. | Requested-operation applicability for completed HOLD. Eight raw matrix disagreements. |

No semantic-identity disagreement was found for jointly valid JSON Decisions, including safe-default normalization and native producer objects.

## Falsifiers

### Triggered

- **Accepted/rejected object-class disagreement:** triggered by explicit `effect.params:null`.
- **Requested machine-semantic parameter applicability disagreement:** triggered when Decision `scope=object` is paired with no external parameter constraint.
- **Requested-operation applicability disagreement:** triggered for completed HOLD under mismatched operation/params because the reference bypasses those checks.
- **All-authority-relevant-agreement success criterion:** triggered by the above disagreements.

### Not triggered

- Pre-freeze contamination: not triggered.
- Exact RC3 version / future version fail-closed behavior: no observed disagreement.
- Completed CLEAR / completed HOLD / evaluation failure distinction on native exact objects: no observed disagreement.
- Target kind/id/content binding: no observed disagreement.
- Upstream kind/id/immutable binding: no observed disagreement.
- Policy id/version binding: no observed disagreement.
- Known effect type/version validation and registered Decision-side safe-default semantic identity: no observed disagreement apart from explicit `params:null` acceptance.
- Unknown effect type/version/parameter fail-closed behavior: no observed disagreement.
- Metadata reason/explanation/diagnostic non-authority: no observed disagreement.
- Authorization-only actor/profile/approval/delegation/context invariance: no observed disagreement.
- Canonical key ordering, compact UTF-8 serialization, trailing newline, duplicate-key rejection, and semantic projection hashing for valid JSON Decisions: no observed disagreement.
- Native Decision Engine -> RC3 -> independent-consumer direct consumption for the five required producer classes: not triggered; it passed.

## Terminal disposition

- **Primary research disposition: `FALSIFIED`**
- **Secondary execution/finding label: `REFERENCE_IMPLEMENTATION_DEFECT`**

Rationale: the frozen reproduction cannot satisfy the success criterion because it has two authority-relevant disagreements of its own, even though native producer consumption passes. Separately, the revealed reference consumer has an authority-relevant HOLD applicability ordering defect relative to the frozen specification. That reference defect does not erase or repair the independent reproduction's own disagreements.

`SUPPORTED FOR PROMOTION` is therefore not justified by this run.

## Explicitly not established

This run does not establish or authorize:

- Contract D promotion, release, or merge;
- production Decision Engine changes;
- production Authorization changes;
- downstream execution or operational permission;
- that every possible Decision Engine output is natively consumable, beyond the five frozen producer objects exercised here;
- that the frozen reference implementation is defect-free;
- that the frozen independent implementation may be repaired post-reveal and still counted as independent;
- historical RC2 diagnosis or comparison with prior reproduction work.

## Smallest justified next step

Do not repair this frozen reproduction in place. Preserve it as the falsifying artifact.

The smallest justified successor is a separately authorized, separately versioned fresh reproduction after the authority owner resolves the revealed HOLD applicability defect in the reference surface. A successor independent implementation should be built fresh from the authorized apparatus inputs and must, before its own reveal, independently reject explicit `effect.params:null` and avoid inventing external requested-parameter constraints from Decision-side safe defaults. Then rerun the same direct Decision Engine producer consumption and mutation matrix.

This recommendation is a research next step only; it is not promotion or release authorization.
