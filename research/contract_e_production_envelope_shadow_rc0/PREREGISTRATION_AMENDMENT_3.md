# Contract E Production Envelope Shadow RC0 — Preregistration Amendment 3

Status: **FROZEN BEFORE CANDIDATE IMPLEMENTATION**

Production authorization: **false**

Predecessor preregistration chain:

- parent: `d879dddb07e0c4f4f1b6588cebddefa662e15829`
- amendment 1: `038702cb5aacfbb42e6fee0848d98eb8d7cb6d1a`
- amendment 2: `436edca34a88d7ad85057c6c800ebc3f339a518c`

## Disposable-root fail-closed marker

The RC0 candidate MUST refuse to operate unless the resolved test root contains a regular file named exactly:

`.contract-e-shadow-rc0-disposable`

with exact UTF-8 contents:

`CONTRACT_E_SHADOW_RC0_DISPOSABLE\n`

The marker is test-apparatus state only. It confers no Contract E authority and does not authenticate a caller.

The candidate MUST resolve and verify the marker before opening the target.

The evaluator creates this marker only inside its temporary fixture roots.

## Added negative control

Add:

- `NEG-NONDISPOSABLE-ROOT`: otherwise valid inputs but the fixture-root marker is absent or malformed -> deny before target or authorization processing can produce a shadow allow.

## Purpose

This is a safety boundary against accidental live invocation. It does not claim that a marker file is a production trust mechanism or sandbox.
