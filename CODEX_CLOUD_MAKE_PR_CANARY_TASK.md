# Codex Cloud host-bridge write-back canary

This is a harmless infrastructure test.

1. Create `CODEX_CLOUD_MAKE_PR_CANARY_RESULT.txt` containing exactly:

   `CODEX_CLOUD_MAKE_PR_CANARY_OK\n`

2. Verify the bytes exactly.
3. Commit only that result file.
4. Do **not** use direct `git push`.
5. Use the provided Codex host-side PR / GitHub bridge (`make_pr` machinery) to publish the executor-produced commit back to the existing PR branch if that bridge is available.
6. Report the exact local commit SHA, whether the host bridge succeeded, and any bridge error verbatim enough to classify the apparatus.
7. Make no other repository changes.
