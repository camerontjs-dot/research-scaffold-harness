# Contract E Production Envelope Shadow RC0 — Preregistration Amendment 2

Status: **FROZEN BEFORE CANDIDATE IMPLEMENTATION**

Production authorization: **false**

Parent preregistration commit: `d879dddb07e0c4f4f1b6588cebddefa662e15829`

Amendment 1 commit: `038702cb5aacfbb42e6fee0848d98eb8d7cb6d1a`

## Defect found before implementation

The initial `ShadowExecutionIntent` bound:

- exact Contract D bytes;
- effect ID/version/parameters;
- a disposable target path;
- target pre-state bytes.

It did **not** separately bind the Contract D target `kind` and `id` to that path.

Therefore two distinct Contract D target identities with identical content bytes could be mapped to the same execution path without violating the original intent profile. That leaves an avoidable target-substitution aperture.

No candidate implementation existed when this defect was found.

## Frozen intent-profile correction

Add exactly these required fields to `ShadowExecutionIntent`:

- `contract_d_target_kind` — exact Contract D `target.kind`;
- `contract_d_target_id` — exact Contract D `target.id`.

The candidate MUST additionally establish before Contract E evaluation that:

1. `intent.contract_d_target_kind == decision.target.kind`;
2. `intent.contract_d_target_id == decision.target.id`;
3. `intent.target_pre_state_sha256 == decision.target.content_sha256`;
4. the exact released Contract D applicability consumer expectation binds that same target kind, ID, and content SHA-256.

A mismatch in any of these is fail-closed.

The newly added fields participate in `intent_id` recomputation exactly like every other intent field.

## Added negative control

Add:

- `NEG-TARGET-ID-SUBSTITUTION`: preserve the same target bytes/pre-state and effect but change Contract D target ID relative to the execution intent -> deny.

No previous negative case is removed or weakened.

## Interpretation

This amendment does not claim that a MainFrame knowledge-object ID is already standardized or that the eventual production executor should use a filesystem path as its public target identity.

It establishes only that RC0 will not credit a shadow envelope that allows the exact Contract D target identity to float independently of the disposable point-of-use target.
