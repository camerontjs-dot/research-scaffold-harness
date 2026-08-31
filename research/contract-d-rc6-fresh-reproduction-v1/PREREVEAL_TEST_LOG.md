# Contract D RC6 Fresh Reproduction v1 — Prereveal Test Log

Runtime: Node.js `v22.16.0`
Command: `node test_contract_d_rc6_consumer.mjs`

## Run 1 — preserved intermediate failure

Result: `66 passed, 1 failed, 67 total`

Failed test: `JCS exponent serialization positive exponent`
Observed controlled error: `non_interoperable_integer`

Public-authority diagnosis: RC5 distinguishes programmatically supplied host integer values from JSON-byte ingress. Exponent-form JSON such as `1e30` is a finite binary64/JCS number token, not an integer-form byte token subject to the special ambiguous integer-spelling rule. The parser was adjusted to preserve byte-ingress provenance for finite numbers that become integer-valued binary64 numbers outside the host safe-integer range. The test was correspondingly changed to exercise exponent serialization through JSON-byte ingress. No hidden/reference material was consulted.

## Run 2 — freeze-candidate prereveal result

Result: `67 passed, 0 failed, 67 total`

This is the exact prereveal suite result used for the implementation/test freeze.
