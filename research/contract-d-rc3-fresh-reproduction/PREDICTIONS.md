# Contract D RC3 independent pre-reveal predictions

This file is frozen before any reference implementation or Decision Engine producer reveal.

## Expected reference agreement

From the frozen specification alone, the independent implementation predicts:

1. Exact `0.3.0-rc3` objects with only registered effect type/version/parameters validate; unknown/future machinery fails closed.
2. Completed `clear`, completed `hold`, and evaluation `failed` remain three distinct outcomes.
3. Applicability binds upstream `(kind,id,immutable_id)`, policy `(id,version)`, target `(kind,id,content_sha256)`, requested operation, and normalized machine-semantic effect parameters.
4. `metadata.reason_codes`, `metadata.explanation`, and `metadata.diagnostics` do not alter semantic identity or applicability.
5. Omitted `knowledge.add_verified_tag@1` params, `{}`, omitted `scope`, and explicit `scope: claim` normalize identically.
6. Semantic identity hashes the canonical normalized authority projection and excludes Authorization-only context.
7. The frozen Decision Engine RC3 producer is expected to emit objects that can be passed directly to this consumer with no translation adapter.

## Native producer outcome predictions

For producer objects representing the three clear effect classes, completed HOLD, and evaluation failure, predicted native outcomes are respectively:

- `knowledge.add_verified_tag@1` clear -> `candidate_for_authorization`
- `knowledge.cite_as_evidence@1` clear -> `candidate_for_authorization`
- `task.dispatch@1` clear -> `candidate_for_authorization`
- completed hold -> `hold`
- failed evaluation -> `evaluation_failed`

Any authority-relevant disagreement after reveal is to be preserved, classified, and counted against independent conformance rather than repaired in this frozen reproduction.
