# Contract A RC2 Fresh Independent Consumer Reproduction — Terminal Record

Terminal disposition: **`INDEPENDENTLY_RECOVERED`**

Status: **POST-FREEZE COMPARISON COMPLETE**

This record closes the fresh independent reproduction authorized by `POST-FREEZE REVEAL AUTHORIZED`. It is research evidence only. It does not merge, promote, release, or assign a canonical Contract A version.

## 1. Frozen prereveal evidence

Repository: `camerontjs-dot/research-scaffold-harness`

Aperture branch: `research/contract-a-rc2-fresh-reproduction-aperture-20260901`

Prepared aperture head used: `711347313ee4bd9b425d36e63d339133043d92b5`

Normative blobs verified before implementation:

- `SPEC.md`: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `schema.json`: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`

Frozen independent implementation/test commit: `464ccae7aa89371a5b7df00c73b3e7d4372a8f8c`

Frozen independent subtree: `4b84bd5fc1416308afa57d0b9723b142c5b15430`

Frozen prereveal test subtree: `f307d58214e018b5730e294d8d1eb92a9ec3b247`

Frozen file identities:

- `independent/contract_a_rc2.py`: `84c50051242873c304be18c4d8a2f4173a811988`
- `independent/__init__.py`: `72072ee492f8d5bd23dbeeecf412b36c5bd9030a`
- `independent/AMBIGUITIES.md`: `5ad6182319d67f3c76ac3894e79e4b06c9778e94`
- `independent/tests/test_contract_a_rc2.py`: `ea87fa2e6c949c78320b782296f0d27528b5c025`

Prereveal freeze-receipt commit: `a95dd4d97a97666ad9e3982f9aa9c75557117bc9`

Prereveal tests before reveal: **16 run, 16 passed, 0 failures, 0 errors**.

The exact Python 3.11 runtime was unavailable prereveal. Execution used Python 3.13.5 and all Python files were additionally parsed with Python 3.11 grammar mode. This remains an immutable prereveal runtime deviation.

## 2. Sealed reveal authority verification

Reveal repository: `camerontjs-dot/apparatus-contracts`

Sealed branch: `sealed/contract-a-rc2-fresh-reproduction-eval-20260901`

Verified sealed branch head/commit: `bedd9b129f23a78bab681f3e534d6f9d008bfe30`

Reveal packet:

- path: `research/contract-a-minimality-rc2-20260901/sealed/POST_FREEZE_REVEAL_PACKET.md`
- verified blob: `c616c0ff9cf0a94da5f6ddb45cd595c05d610c78`

Sealed manifest:

- path: `research/contract-a-minimality-rc2-20260901/sealed/SEALED-MANIFEST.json`
- observed blob: `8231660eccb020747ae0c2c5bb55644912b78965`
- bound original freeze receipt: `6cf9019b9672075af674929455bef78c950dddc6`

At original freeze receipt commit `6cf9019b9672075af674929455bef78c950dddc6`, direct Git tree traversal verified:

- candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`
- reference/normal-context tree: `18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`
- evaluator tree: `5d7eb3e3a9a98ba1626118a5e06a018c02fa81ec`

Frozen revealed code identities:

- candidate validator `validate.py`: `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- evaluator `test_candidate.py`: `c5e489033ffc566511e70fa14192a0f88a62ab6a`
- reference `run_conformance.py`: `1765b489590fca10462ad451847e0ddcb249f77f`
- reference `run_conformance_v2.py`: `3fbaa3882921c13286c07c81751dc6527e6be348`
- reference `run_conformance_v3.py`: `27199e94f80b4f8686d4c460fd7b86eccb00e8eb`

Frozen fixture identities:

- `valid-all-of.json`: `c9e2e886d7fa2bcd3d979bfc6cdebd0de2763ce0`
- `valid-failed-decomposition.json`: `b54dfee6b48f2d6a78d48d723409fdbc314202fd`
- `valid-undecomposed.json`: `5bf59a4b310496fda9f8bdc9f1a88aa9345660b5`
- `valid-unknown-decomposition.json`: `873536d219d46aa846466a836e65db312e82e574`
- `invalid-forbidden-semantic-field.json`: `3cc1fb6790e3a58f54641c8ad77dc4737100f0a1`
- `invalid-missing-proposition-id.json`: `68162754ec00dc00c838ad52c7150441aa8e8c08`
- `invalid-source-content-hash.json`: `113c668d517325a05e959f15a64c06f939153f97`

The connector-materialized validator, evaluator, and fixtures were checked with `git hash-object`; every local byte sequence matched the frozen Git blob above before execution.

## 3. Reference evaluator self-test

The exact frozen evaluator `c5e489033ffc566511e70fa14192a0f88a62ab6a` was run against the exact frozen candidate validator and fixtures first, as required.

Result: **PASS**, exit status `0`.

It emitted 18 PASS records covering the seven frozen fixtures and its built-in mutation/metamorphic controls.

Reference-evaluator stdout/stderr capture SHA-256: `416ec3359cc1227e523cb924600f574a7795319fc11b7a78a84432462409f735`.

Classification: `INDEPENDENT_AGREEMENT` for evaluator self-consistency. There is no current frozen evaluator failure.

## 4. Mechanical invocation adapter

The exact frozen evaluator was then run against the immutable prereveal validator through a call-shape-only adapter outside the frozen independent subtree.

Durable adapter path:

`research/contract-a-rc2-fresh-reproduction/post-freeze/reference-evaluator-independent-adapter.py`

Adapter Git blob: `4678f95317f6a55c2b7a1246db03c1e4d7557190`

Adapter commit: `e710f3fb27e072797af19e1aa49475309de7329e`

The adapter only aliases the prereveal exception class and hash function and forwards `validate_candidate(value)` unchanged. It adds no validation, normalization, hashing, defaults, parsing behavior, or semantic behavior.

The exact frozen evaluator emitted the same 18 PASS records against the independent implementation. The captured output bytes were identical to the reference self-test capture and therefore had the same SHA-256: `416ec3359cc1227e523cb924600f574a7795319fc11b7a78a84432462409f735`.

Classification: `INDEPENDENT_AGREEMENT`. No `REPRESENTATION_ADAPTER_DEFECT` was observed.

## 5. Frozen fixture comparisons

| Case | Reference | Independent | Material result | Classification |
|---|---|---|---|---|
| `valid-all-of.json` | accept | accept | Whole hash `sha256:f9d2f7be6eaaa21bcc032d3d91a9f9b42d645b15ed5130fc4b69807ba0ed6142`; declared state; children `a,b` in sequence `1,2`; source bytes/ID/hash preserved | `INDEPENDENT_AGREEMENT` |
| `valid-failed-decomposition.json` | accept | accept | Whole hash `sha256:334d61879ad5a85962666bdda6ae060b946201312ae67c59c04dbdbdd95c7bf8`; exact root retrieval; `failed` preserved | `INDEPENDENT_AGREEMENT` |
| `valid-undecomposed.json` | accept | accept | Whole hash `sha256:b1fe0b846023655d6a2fe07bc09fe54a616865a2f49546d5db878f9e944ce2bc`; exact root retrieval; `not_decomposed` preserved | `INDEPENDENT_AGREEMENT` |
| `valid-unknown-decomposition.json` | accept | accept | Whole hash `sha256:766e55eb3992bc5d07dcae9b6681db7915c7c7b60d86077840af596fdb344592`; exact root retrieval; `unknown` preserved | `INDEPENDENT_AGREEMENT` |
| `invalid-forbidden-semantic-field.json` | reject | reject | Unknown `root_proposition.support_status` rejected | `INDEPENDENT_AGREEMENT` |
| `invalid-missing-proposition-id.json` | reject | reject | Missing required proposition identity rejected | `INDEPENDENT_AGREEMENT` |
| `invalid-source-content-hash.json` | reject | reject | Source content/hash mismatch rejected | `INDEPENDENT_AGREEMENT` |

For every valid fixture, independent `compute_handoff_sha256` equaled the reference computation and the supplied `handoff_sha256`. `supplied_sources()` returned a deep-equal representation of the exact supplied source list.

## 6. Retrieval and source-contract projection comparison

### Retrieval propositions

Reference `semantic_propositions` and the normal-context V3 behavior select the exact root proposition for `not_decomposed`, `failed`, and `unknown`, and exact declared children in list/sequence order for `declared`.

The independent `retrieval_targets()` produced exactly those IDs, texts, text hashes, and order for all four valid fixtures.

Classification: `INDEPENDENT_AGREEMENT`.

### Authoritative root / atom semantics

For declared `all_of`, both sides preserve the authoritative root identity and text, `operator=all_of`, and the exact two child atom IDs/texts/order. For root-only states, both preserve the exact root as the single atom and use `operator=single`.

Classification: `INDEPENDENT_AGREEMENT`.

### Provenance hash binding

Both sides bind downstream source-contract provenance to the exact Contract A `handoff_sha256`. Failed and unknown therefore remain mechanically distinguishable by distinct immutable bindings even though both use the root/single semantic shape.

Classification: `INDEPENDENT_AGREEMENT`.

### Provenance reference-ID representation

The prereveal implementation froze a local projection with one top-level `reference_id`: `handoff_id` for root-only states and `decomposition_id` for declared state. The revealed normal-context CAL adapter instead constructs per-atom reference IDs as `handoff_id#proposition_id`.

Both are paired with the same whole-object hash and point only to existing Contract A identities. The public specification requires provenance reference IDs/hashes to bind the corresponding Contract A declaration but does not prescribe an adapter wire schema or exact reference-ID encoding.

Classification: `PUBLIC_SPEC_AMBIGUITY`.

No repair was applied.

### Root-only parent-envelope representation

The prereveal local projection exposes the authoritative root directly. The revealed CAL adapter must satisfy CAL's structural requirement that a `single` request parent envelope ID differ from its atom ID, so it constructs `contract-a-single:{handoff_id}:{work_id}` as the CAL parent envelope while retaining the exact Contract A root as the sole authoritative atom.

The public Contract A specification requires the exact root as the `single` atom and says representation adapters may change serialization shape; it does not prescribe this CAL envelope ID.

Classification: `PUBLIC_SPEC_AMBIGUITY`.

No repair was applied. There is no disagreement about the authoritative Contract A root/atom identity.

### Per-atom text-hash field representation

The independent local projection surfaces each Contract A `text_sha256` directly. The revealed CAL `ExplicitClaimAtom` construction shown in the reference adapter supplies atom ID, exact text, and source-contract provenance, while the whole `handoff_sha256` binds the proposition text hash transitively; it does not surface a separate CAL atom `text_sha256` field in that adapter call.

Classification: `OUT_OF_SCOPE_DIFFERENCE` because this is downstream representation shape, not a disagreement over Contract A proposition identity, exact text, or immutable binding.

## 7. Required mutation/metamorphic controls

| Control | Reference | Independent | Classification |
|---|---|---|---|
| proposition text changed while proposition text hash stale, whole object resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| source content changed while content hash stale, whole object resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| root/parent identity substitution with stale handoff binding | reject | reject | `INDEPENDENT_AGREEMENT` |
| root identity substitution with legitimate fresh reseal | accept | accept | `INDEPENDENT_AGREEMENT` |
| child identity substitution with stale handoff binding | reject | reject | `INDEPENDENT_AGREEMENT` |
| child identity substitution with legitimate fresh reseal | accept | accept | `INDEPENDENT_AGREEMENT` |
| source identity substitution with stale handoff binding | reject | reject | `INDEPENDENT_AGREEMENT` |
| source identity substitution with legitimate fresh reseal | accept | accept | `INDEPENDENT_AGREEMENT` |
| work identity substitution with stale handoff binding | reject | reject | `INDEPENDENT_AGREEMENT` |
| work identity substitution with legitimate fresh reseal | accept | accept | `INDEPENDENT_AGREEMENT` |
| unsupported `any_of` composition, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| one-child `all_of`, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| noncontiguous child sequence `[1,3]`, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| omitted `sources` | reject | reject | `INDEPENDENT_AGREEMENT` |
| explicit `sources: []`, resealed | accept | accept | `INDEPENDENT_AGREEMENT` |
| duplicate child proposition ID, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| duplicate child text with matching text hash, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| duplicate source ID, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |
| legitimate bound `handoff_id` change with stale handoff hash | reject | reject | `INDEPENDENT_AGREEMENT` |
| same legitimate bound `handoff_id` change after fresh reseal | accept | accept | `INDEPENDENT_AGREEMENT` |
| missing decomposition state | reject | reject | `INDEPENDENT_AGREEMENT` |
| Boolean child sequence `true`, resealed | reject | reject | `INDEPENDENT_AGREEMENT` |

The comparison runner's raw result capture had SHA-256 `be752cb9cbc451eb3456facaa3b69ded1bd8692e73b13e1070d628adba0e4462`.

## 8. Frozen prereveal ambiguity checks after reveal

### Whole-object non-ASCII serialization

The prereveal implementation chose literal Unicode JSON (`ensure_ascii=False`) encoded as UTF-8. The revealed reference validator makes the same choice. A non-ASCII resealed candidate produced identical reference/independent hashes and was accepted by both.

Classification: `INDEPENDENT_AGREEMENT`.

### Duplicate JSON object members

The prereveal parser deliberately rejects duplicate raw JSON member names. The revealed reference `load_candidate` uses Python's default `json.loads` duplicate-member behavior, so a valid fixture with an identical duplicate `schema` member was accepted by the reference loader but rejected by independent `parse_json`.

The public Contract A authority does not state a duplicate-member parsing policy, and this exact uncertainty was recorded before reveal.

Classification: `PUBLIC_SPEC_AMBIGUITY`.

No repair was applied.

### Cross-family identifier equality

A valid candidate with `source_id == root_proposition.proposition_id` and a fresh valid handoff binding was accepted by both sides. Neither implementation invented a global identifier namespace not stated by the public authority.

Classification: `INDEPENDENT_AGREEMENT`.

### Duplicate source representation bytes under distinct source IDs

Two byte-identical supplied source representations with distinct unique source IDs and a fresh valid handoff binding were accepted by both sides.

Classification: `INDEPENDENT_AGREEMENT`.

## 9. Revealed predecessor reference/evaluator deviations

The frozen normal-context V3 runner explicitly preserves two predecessor failures:

1. `run_conformance.py` recorded `HARNESS_FAILURE` because a literal source substring assertion did not account for Markdown line wrapping. Classification for this preserved predecessor harness defect: `EVALUATOR_DEFECT`.
2. `run_conformance_v2.py` recorded `EVALUATOR_ASSUMPTION_FALSIFIED` because the auxiliary whole-document BM25 probe produced zero positive-score hits even though exact query execution remained observable. V3 removed positive hits as a gate and retained the zero-hit result as evidence. Classification for the predecessor gating assumption: `EVALUATOR_DEFECT`.

These are historical frozen normal-context evaluator/harness defects. They are not failures of the current frozen `test_candidate.py`, which passed, and they are not independent implementation disagreements.

No `REFERENCE_IMPLEMENTATION_ERROR` was found in the frozen candidate validator for the comparison surface exercised here.

## 10. Runtime and execution deviations

- Existing prereveal deviation: exact Python 3.11 runtime unavailable; Python 3.13.5 execution plus Python 3.11 grammar parse was used. Classification: `OUT_OF_SCOPE_DIFFERENCE`.
- Post-reveal direct shell `git fetch` could not resolve `github.com`. Exact frozen material was instead obtained through the authorized GitHub connector and byte-verified with `git hash-object`. Classification: `OUT_OF_SCOPE_DIFFERENCE`.
- The first piped shell invocation of the independent evaluator lane printed Python `EXIT_STATUS=0` but the surrounding shell/tool wrapper reported status 1 with `TERM environment variable not set`. A clean rerun without the pipeline confirmed the evaluator's Python exit status was `0` and reproduced the same 18 PASS lines. Classification: `OUT_OF_SCOPE_DIFFERENCE`.

None of these deviations changes a Contract A comparison outcome.

## 11. Prereveal tests after reveal

Before rerunning, the local implementation/test bytes were rechecked:

- implementation Git blob: `84c50051242873c304be18c4d8a2f4173a811988`
- test Git blob: `ea87fa2e6c949c78320b782296f0d27528b5c025`
- init Git blob: `72072ee492f8d5bd23dbeeecf412b36c5bd9030a`

The original prereveal tests were rerun unchanged after reveal.

Result: **16 run, 16 passed, 0 failures, 0 errors**.

Post-reveal unchanged-test output capture SHA-256: `d0f0731391ad6766c2915722d7f2117b8f5ba4f775f86c438befb6eddce328dc`.

Classification: `INDEPENDENT_AGREEMENT`.

## 12. Classification summary

Observed classes in this reproduction:

- `INDEPENDENT_AGREEMENT`: all seven frozen fixtures; all required validation, integrity, identity, resealing, source, decomposition, and ordering controls; canonicalization; retrieval proposition semantics; state preservation; authoritative root/atom semantics; whole-handoff provenance hashes; unchanged prereveal tests.
- `PUBLIC_SPEC_AMBIGUITY`: duplicate raw JSON member handling; exact downstream provenance reference-ID representation; CAL root-only parent-envelope representation.
- `EVALUATOR_DEFECT`: two already-frozen predecessor normal-context harness/gating defects explicitly preserved by V3; not the current frozen evaluator.
- `OUT_OF_SCOPE_DIFFERENCE`: downstream per-atom text-hash field shape and runtime/transport/shell-environment deviations.

Not observed:

- `INDEPENDENT_IMPLEMENTATION_ERROR`
- `REFERENCE_IMPLEMENTATION_ERROR`
- current frozen `EVALUATOR_DEFECT`
- `REPRESENTATION_ADAPTER_DEFECT`
- `UNRESOLVED_DISAGREEMENT`

## 13. Repair/successor boundary

No post-reveal repair was made. No successor implementation was created. The prereveal implementation and tests remain immutable evidence at their original commit/tree/blob identities.

The observed public-spec ambiguities are preserved rather than retrofitted toward the reference representation.

## 14. Terminal disposition

**`INDEPENDENTLY_RECOVERED`**

Basis: the independent implementation recovered the frozen public candidate's validation, integrity, decomposition-state behavior, exact retrieval proposition targets, source preservation, and proposition lineage across every revealed fixture and required mutation/metamorphic control. The exact frozen evaluator passes both the reference candidate and the frozen independent implementation through mechanical invocation glue with byte-identical evaluator output.

The remaining differences are prereveal-recorded or downstream representation ambiguities not affecting the bounded Contract A semantic authority surface. They are preserved above and are not silently repaired.

This disposition is research evidence only. It does not authorize Contract A production promotion, merge, canonical release/version assignment, Evidence Bundler redesign, CAL semantic-policy change, or Contract E authority semantics.
