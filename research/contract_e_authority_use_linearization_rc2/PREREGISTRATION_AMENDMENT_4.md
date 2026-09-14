# RC2 Preregistration Amendment 4 — Anti-Rollback as Store Invariant

Status: **FROZEN BEFORE EVALUATOR CONSTRUCTION OR CANDIDATE EXECUTION**

## Defect found

The candidate authority installer already rejects non-monotonic generation updates and wrong-parent successors. That is insufficient if a less-privileged bug or alternate maintenance path can directly move the `authority_current` pointer back to an older installed generation while newer history remains present.

A current-pointer rollback would make the old AuthorityState look internally valid again even though the store had previously accepted a later generation.

No evaluator has been created and no candidate execution/result has been observed.

## Frozen correction

Before using current standing authority, the RC2 PEP MUST verify, within its write-serialized transaction, that:

`authority_current.generation == MAX(authority_history.generation)`

for the current authority epoch.

If the current pointer is below the highest installed generation, the authority store is invalid and execution MUST fail closed.

The same check must also preserve the existing immediate-parent lineage validation for generation > 0.

## Strengthened rollback control

`NEG-AUTHORITY-ROLLBACK-A1-TO-A0` now has two sub-observations:

1. the supported installer API rejects a requested A1→A0 rollback;
2. a direct test-harness corruption that rewrites `authority_current` to A0 while A1 remains in history is detected by the PEP and cannot restore execution permission.

`W-NO-AUTHORITY-ANTI-ROLLBACK` deliberately omits the highest-generation invariant and demonstrates that the same direct pointer rollback can restore A0 permission.

This amendment strengthens the preregistered anti-rollback property and does not remove any earlier case or falsifier.