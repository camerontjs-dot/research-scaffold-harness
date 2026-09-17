# CAL Pipeline Provenance Chain

**Status:** cross-repo architecture pointer / qualification-role record. Research Scaffold Harness is not a production runtime stage in the CAL Pipeline. No contract schema, component semantics, Decision policy, Authorization, release, or production behavior is changed by this document.

## Canonical blueprint

The canonical proposed architecture is maintained in `camerontjs-dot/apparatus-contracts` Draft PR #101:

- `docs/architecture/CAL-PIPELINE-PROVENANCE-CHAIN-BLUEPRINT.md`
- canonical proposal head at this pointer's creation: `d16e5e14cab55ed23bdeee4cdeecf48724c542db`

## Qualification role

The strongest successor test for this architecture should be a fresh/isolated reconstruction consumer that receives only:

- one frozen run manifest;
- the retained artifacts reachable through that manifest;
- independently pinned contract/validator/policy/resolver/trust-root authorities;
- the attestation specification;
- no producer-private runtime state and no narrative handoff that supplies missing semantics.

The consumer should reconstruct the run backward and forward, verify every content identity and authority binding, and determine whether the final Contract D can be reproduced or at minimum independently verified from the frozen chain.

## Minimum discriminators

A future independent provenance qualification should include:

1. positive reconstruction of the frozen first-genuine pipeline run;
2. wrong raw B bytes under the correct trusted B commitment;
3. fully resealed alternate B world under the original commitment;
4. caller-moved expected commitment weak control;
5. C participant substitution;
6. CAL implementation/policy/resolver substitution;
7. behaviorally relevant configuration substitution;
8. artifact-locator substitution that returns wrong bytes;
9. missing reconstruction-required artifact;
10. legitimate ClaimGate abstention with no downstream run;
11. semantic CAL `not_checkable` distinguished from apparatus failure;
12. replay/reproduction identity checks;
13. observed-context/compatibility-input mutation controls proving those roles cannot silently acquire causal authority.

## Falsification posture

If an independent consumer cannot determine exactly what each stage received, which machinery/authority governed it, what it produced, and why downstream artifacts belong to the same run without producer-private state, the provenance architecture is insufficient and should not be promoted.

## Nonclaims

This pointer does not preregister or execute that experiment, qualify an attestation schema, promote a run-manifest format, or make Research Scaffold Harness part of the production pipeline.
