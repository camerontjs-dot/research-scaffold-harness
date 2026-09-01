# Contract A RC2 independent prereveal freeze receipt

Status: `PRE_REVEAL_FROZEN`

This receipt freezes the independent implementation and prereveal tests produced from the authorized public aperture only. No reference validator, evaluator, reference fixture, sealed/reveal branch, post-freeze packet, prior Contract A implementation, or prior Contract A research result was inspected.

## Aperture

- Repository: `camerontjs-dot/research-scaffold-harness`
- Branch: `research/contract-a-rc2-fresh-reproduction-aperture-20260901`
- Prepared aperture head used before implementation: `711347313ee4bd9b425d36e63d339133043d92b5`
- Implementation/test freeze commit (branch head before this receipt): `464ccae7aa89371a5b7df00c73b3e7d4372a8f8c`

## Normative identities verified before implementation

- `research/contract-a-rc2-fresh-reproduction/public/SPEC.md` Git blob: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `research/contract-a-rc2-fresh-reproduction/public/schema.json` Git blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`

Both matched the required aperture identities exactly.

## Frozen independent identities

Independent subtree at implementation/test freeze commit:

- Git tree: `4b84bd5fc1416308afa57d0b9723b142c5b15430`

Frozen files:

- `independent/contract_a_rc2.py`: blob `84c50051242873c304be18c4d8a2f4173a811988`
- `independent/__init__.py`: blob `72072ee492f8d5bd23dbeeecf412b36c5bd9030a`
- `independent/AMBIGUITIES.md`: blob `5ad6182319d67f3c76ac3894e79e4b06c9778e94`
- `independent/tests/test_contract_a_rc2.py`: blob `ea87fa2e6c949c78320b782296f0d27528b5c025`

Prereveal test subtree:

- Git tree: `f307d58214e018b5730e294d8d1eb92a9ec3b247`
- Test file blob: `ea87fa2e6c949c78320b782296f0d27528b5c025`

## Prereveal test result

Command executed against executable bytes matching the committed implementation and test blobs:

`python -m unittest discover -s /mnt/data/contract_a_independent/tests -v`

Available runtime: Python `3.13.5`.

Result: **PASS**. `16` tests run, `0` failures, `0` errors.

The implementation and tests also parse successfully with Python's `ast.parse(..., feature_version=(3, 11))` grammar mode for all Python files.

### Python 3.11 runtime deviation

The execution environment did not contain a `python3.11` executable. A generic runtime-only attempt to install CPython 3.11 with the available `uv` tool failed because the isolated environment could not resolve/download the Python runtime. Therefore an exact Python 3.11 runtime test was **not executed**. The implementation targets Python 3.11 syntax and standard-library APIs; this runtime availability deviation is preserved rather than hidden.

## Prereveal ambiguities and chosen interpretations

1. **Whole-object non-ASCII serialization:** the public hash instructions do not uniquely settle literal UTF-8 non-ASCII versus `\uXXXX` escaping. The implementation chooses `ensure_ascii=False` and hashes literal Unicode serialized to UTF-8.
2. **Downstream source-contract projection shape:** the public authority specifies semantic constraints but no adapter wire schema. The implementation exposes a local mechanical dictionary shape and does not claim those field names as Contract A authority. Root-only states bind `handoff_id` + `handoff_sha256`; declared state binds `decomposition_id` + the whole-object `handoff_sha256`.
3. **Duplicate JSON member names:** parser behavior is unspecified. The implementation rejects duplicate members instead of allowing Python's default last-value overwrite.
4. **Cross-family identifier equality:** only the uniqueness/prohibition relationships expressly stated by the public authority are enforced. No global identifier namespace is invented.
5. **Duplicate source contents/hashes:** source IDs are required unique, but byte-identical representations under distinct source IDs are permitted because the authority does not prohibit them.

## Deviations and failures

- Aperture integrity: no failure.
- Implementation/test semantic execution under available runtime: no failure; all 16 prereveal tests passed.
- Exact Python 3.11 runtime execution: not available, as recorded above.
- No post-freeze comparison, repair, promotion, merge, or production claim has been performed.

This receipt commits the prereveal boundary. Any later reference comparison or repair must remain separate and must not alter the frozen implementation/test identities above when assessing independent agreement.
