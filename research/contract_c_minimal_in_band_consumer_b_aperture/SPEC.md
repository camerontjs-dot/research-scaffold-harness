# Contract C minimal in-band Consumer B reproduction specification

## Classification and question

This is a bounded clean-room consumer reproduction. It is not a Contract C release, version assignment, promotion, production Decision change, Authorization, or execution task.

Question:

> Can an implementation written only from this frozen aperture consume the exact `research-non-deciding-rc0` handoff, preserve neutral causal attribution and multiplicity without inventing scalar/winner semantics, and fail closed on the specified identity/reference boundary?

## Normative lineage supplied by this aperture

The research handoff is frozen from Apparatus receipt commit `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff` and inherits released Contract C 1.0 semantics except for the two-leaf research delta in `schema-delta.json`.

Released Contract C 1.0 authority identities:

- release commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- normative spec blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- normative schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`

Only the bounded rules needed by this reproduction are restated below. Do not infer additional implementation details from these identities and do not inspect the upstream repository pre-freeze.

## Research delta

Relative to released Contract C 1.0:

1. `contract_c_version` is exactly `research-non-deciding-rc0`.
2. contribution `channel` permits `support`, `counterevidence`, and `non_deciding`.

`non_deciding` means evidence participated in the CAL-attributable terminal epistemic basis without being classified as support or counterevidence. It is not permission, authorization, confidence, probability, a scalar winner, support, or refutation.

## Exact externally selected profile

The consumer must receive authority from the caller. It must not let the object select its own validation profile.

`expected_profile` is required and must be an object containing non-empty:

- `contract_c_version`
- `whole_object_sha256`
- `result_set_id`

For the supplied fixture the externally authorized values are:

- version: `research-non-deciding-rc0`
- whole-object SHA-256: `sha256:325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3`
- result-set ID: `result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0`

Missing or malformed external authority context must fail closed before the object can self-authorize.

## Canonical bytes and result identity

Canonical Contract C JSON uses:

1. UTF-8 JSON;
2. object keys sorted lexicographically;
3. compact separators with no presentation whitespace;
4. Unicode preserved rather than ASCII-escaped;
5. non-finite numbers rejected;
6. exactly one trailing newline.

Duplicate object keys are invalid. Array order is part of canonical byte identity.

`result_set_id` is:

`result-set:` + lowercase SHA-256 of the canonical object after removing only the top-level `result_set_id` field.

The consumer must independently recompute and verify this identity.

Whole-object SHA-256 is separate from internal identity. Compare the exact received bytes to the externally selected `expected_profile.whole_object_sha256`. A coherent object with recomputed internal identities is still a different object and must fail when the authorized whole-object digest is not changed by the external authority.

## Producer policy binding

`producer.policy.canonical` is opaque producer-owned JSON. `producer.policy.sha256` is lowercase SHA-256 of the same canonical JSON rule applied to the `canonical` payload. The consumer must verify this binding.

## Contract B binding

The top-level `input.contract_b` binding must exactly match the supplied `contract_b_index` values:

- `contract_version`
- `bundle_id`
- `bundle_hash`

Each proposition must bind its `proposition_id` to exactly one `contract_b_index.propositions` entry and its `text_sha256` must match that entry.

Each retained evidence reference must exactly match one supplied Contract B passage by:

- `source_id`
- `passage_id`
- `passage_sha256`

No source/evidence payload is invented or duplicated by the consumer.

## Contribution and terminal-basis integrity

Each contribution has:

- a `contribution_id` matching `^contribution:[0-9a-f]{64}$`;
- a channel in `{support, counterevidence, non_deciding}`;
- an exact evidence reference.

The public aperture does not supply a content-derivation formula for `contribution_id`. Do not invent one. Treat contribution IDs as stable typed identities and validate their format, uniqueness, and all internal references to them.

Every retained contribution must be classified exactly once as either:

- causal, through a `basis_members` entry with `namespace="contribution"`; or
- residual, through `residual_contribution_ids`.

A contribution cannot be both. A contribution cannot be left unclassified. Every causal or residual contribution reference must resolve to a retained contribution. Duplicate causal or residual IDs are invalid.

For this bounded profile:

- `single_necessary` requires exactly one causal contribution when causal contribution membership is the basis being represented;
- `independent_sufficient_alternatives` requires at least two causal contributions;
- `jointly_sufficient` requires at least two causal contributions;
- `redundant_non_deciding` has no causal contribution members.

Do not collapse `independent_sufficient_alternatives` and `jointly_sufficient`; causal form is retained semantic state.

## Execution versus conclusion

Result-set execution state is separate from proposition verdict.

A completed proposition may have `completion=assessed` or `completion=not_checkable`. A completed `not_checkable` proposition is not an execution failure.

Preserve:

- proposition execution object;
- `reported_verdict`;
- `terminal_branch`;
- `causal_form`;
- causal contributions;
- residual contributions.

If a proposition has no conclusion because its execution state legitimately does not carry one, normalize the corresponding conclusion fields to `null`/empty collections rather than inventing a verdict.

## Required normalized consumer output

`consume_contract_c(raw, contract_b_index, expected_profile)` must return a deterministic dictionary with this logical shape:

```json
{
  "contract_c_version": "...",
  "result_set_id": "...",
  "whole_object_sha256": "sha256:...",
  "contract_b": {
    "contract_version": "...",
    "bundle_id": "...",
    "bundle_hash": "..."
  },
  "propositions": [
    {
      "proposition": {
        "proposition_id": "...",
        "text_sha256": "..."
      },
      "execution": {},
      "reported_verdict": "... or null",
      "terminal_branch": "... or null",
      "causal_form": "... or null",
      "causal_contributions": [
        {
          "contribution_id": "...",
          "channel": "...",
          "evidence_ref": {
            "source_id": "...",
            "passage_id": "...",
            "passage_sha256": "sha256:..."
          }
        }
      ],
      "residual_contributions": []
    }
  ]
}
```

Do not add sidecar-specific member/state/receipt identities. Do not add score, confidence, probability, rank, winner, action, authorization, or execution-effect fields.

Order the normalized proposition/contribution collections deterministically without changing their semantic distinctions.

## Supported-claim policy probe

`evaluate_supported_claim(consumed, proposition_id)` is a deliberately narrow downstream-policy probe, not Contract C semantics.

Required behavior:

- if the target proposition is absent: return a failed result or raise an explicit consumer error;
- only a proposition with `execution.state=completed`, `execution.completion=assessed`, and `reported_verdict=supported` may return disposition `clear`;
- every other valid proposition state returns disposition `hold`;
- the existence of causal or residual `non_deciding` evidence must never itself cause `clear`.

A recommended deterministic return shape is:

```json
{"state":"completed","disposition":"hold","reason":"..."}
```

or the analogous explicit failed/clear shape.

## Required discriminating pre-freeze coverage

Your own tests must include at least:

- the exact frozen handoff is consumed successfully;
- its two causal `non_deciding` evidence references remain distinct and its causal form remains `independent_sufficient_alternatives`;
- wrong external digest rejects;
- missing/malformed expected profile rejects;
- wrong version rejects;
- wrong Contract B binding rejects;
- wrong proposition binding rejects;
- wrong evidence reference rejects;
- missing causal contribution rejects;
- causal/residual overlap rejects;
- unclassified retained contribution rejects;
- stale `result_set_id` rejects;
- the baseline policy probe HOLDS and never CLEARs merely because `non_deciding` is causal;
- a coherent same-members `jointly_sufficient` object, if re-bound with a recomputed result-set ID and separately supplied new whole-object digest, remains observably distinct from `independent_sufficient_alternatives`;
- a coherent causal/residual-role variant, if re-bound consistently, remains observably distinct.

These are public prereveal obligations, not the post-freeze evaluator corpus.

## Error behavior

Expose a `ConsumerError` carrying a stable short `code`. Exact prose is not normative. Fail closed rather than silently repairing malformed input.

## Non-claims

This experiment does not establish:

- production Contract C successor versioning;
- universal Contract C interoperability;
- CAL semantic correctness;
- destination policy correctness beyond the narrow probe;
- operational authorization;
- Contract E;
- cryptographic actor/origin authentication;
- merge, release, tag, or promotion readiness.
