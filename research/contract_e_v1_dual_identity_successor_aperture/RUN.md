# CLEAN-ROOM RUN METADATA

This file contains operational metadata only. It does not add or modify Contract E semantics.

- repository: `camerontjs-dot/research-scaffold-harness`
- execution branch: `research/contract-e-v1-dual-identity-copilot-reproduction-20260902`
- clean-room base branch: `research/contract-e-v1-dual-identity-cleanroom-base-20260902`
- clean-room base head: `52ade243f0ee8e84466fe9af81c17982b836260c`
- frozen source candidate commit: intentionally not supplied pre-freeze; use only the byte-identical aperture files below

Allowed aperture identities:

- `research/contract_e_v1_dual_identity_successor_aperture/SPEC.md`
  - Git blob: `90bfa10fda928796f9b14c6a430ee12e412d9e3e`
- `research/contract_e_v1_dual_identity_successor_aperture/schema.json`
  - Git blob: `ababc25a6dc9fc938251df57bea3ddcc3dd78850`
- `research/contract_e_v1_dual_identity_successor_aperture/PRE_FREEZE_TASK.md`
  - Git blob: `20f07ee2a7b89297cf11bb94178ae7efc87a52a5`

The exact execution starting head is the launch-supplied current head of the execution branch containing this RUN.md. Verify that head only with a branch/ref lookup. Do not inspect its commit object, parents, history, tree API, diff, PR body/history, or unrelated repository content.

Execute `PRE_FREEZE_TASK.md` exactly. Freeze the independent implementation and prereveal tests before any evaluator/reference reveal. Stop after the freeze receipt.
