# Contract C CAL V1 parent-binding independent consumer RC1 — terminal record

## Terminal disposition

**SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1**

This is bounded research evidence for the exact frozen CAL V1 / Contract C RC2 + typed parent-recomposition subject and exact hidden PIPE01–PIPE04 cohort.

It does not by itself authorize production promotion, canonical Contract C discovery, Decision Engine compatibility, release, Authorization, or execution.

## Frozen independent consumer

- corrected aperture: `aab10774970c2f83af6f918396f9fa36d5d519b7`
- candidate commit: `cc30821c15d8dd17301f8d8935feebe86e6ce0f4`
- final pre-reveal freeze: `12e7e640b229619501960b1b89cf4716d8d985b3`
- consumer blob: `662e94c4445d2be9034e786711429394f217c0a6`
- prereveal-test blob: `50f3104650a946b834c3ff6415bafb347863e836`
- freeze-receipt blob: `cb99cd2ee29d38e19c845771654898561b91552f`
- prereveal suite recorded by freeze receipt: **21 passed / 0 failed / 0 errors**
- contamination: **CLEAN**
- network: **OFF**
- forbidden inputs read: none
- real handoffs/evaluator/prior consumer/post-freeze result seen before freeze: false

The consumer was not modified after reveal.

## Exact producer / reveal authority

- Apparatus RC0 decisive head: `7138f6c1599b9b8f8c655f85c9eba0c264fb3b26`
- producer candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- Candidate A RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- frozen CAL V1: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- qualified CAL semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`
- CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- frozen Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- current-CAL resolver: `1d33e0612befcf8016816197c90c062373796df9`

## Preserved post-freeze comparator deviations

### 1. Workflow-trigger generation defect

The first generated RC1 workflow contained an accidental double `rc1-rc1` suffix in the trigger branch/path. No Actions run started and no scientific input was consumed.

Classification: **POSTFREEZE_WORKFLOW_TRIGGER_DEFECT**.

Only the trigger strings were corrected.

### 2. Wrong expected-authority profile input

Run `35461258222` supplied the outer parent-binding profile in `expected_authority.profile`. The RC1 aperture / nested RC2 public specification uses that field for the exact nested RC2 profile.

All cases therefore stopped immediately at `WRONG_EXPECTED_PROFILE`.

Classification: **POSTFREEZE_COMPARATOR_AUTHORITY_INPUT_DEFECT**.

Only comparator-side construction of the independently supplied authority profile was corrected from the outer profile to the exact RC2 profile. No consumer, producer, hidden case, or semantic criterion changed.

### 3. RC0-specific success-projection assertion

Run `35461293095` reached the real handoffs successfully. The frozen RC1 consumer returned normally for all four positive cases, and the revealed mutation campaign produced no false accepts. The comparator then attempted to read a top-level `whole_object_sha256` field that existed in the RC0 consumer projection but is not required by the public RC1 successful-result contract.

All positive records were therefore marked failed only because the comparator itself raised `KeyError:'whole_object_sha256'` after native consumer success.

Classification: **POSTFREEZE_COMPARATOR_PROJECTION_ASSUMPTION_DEFECT**.

Only the comparator assertion was changed to verify returned `result_set_id` identity plus exact parent conclusion. The consumer already independently verifies the supplied whole-object authority before returning.

## Decisive hosted execution

- comparison head: `d0c49a2a87cf2f341e39652f36737d1417a6895d`
- comparator blob: `a96b4eac7a7a42a221ce889414a6748405f5b20e`
- workflow run: `35461341449`
- job: `105945652626`
- workflow conclusion: **success**
- artifact: `10589539839`
- artifact ZIP digest: `sha256:74dc44f76dabe0b5ae69dd6e00eab66d02f7936ed41d61b2f49d67c94bf57f9f`
- frozen prereveal suite rerun: **21/21 PASS**
- frozen CAL decomposition controls: **27/27 PASS**
- adapter used: **false**
- consumer modified post-freeze: **false**

## Positive real-handoff results

All four exact hidden producer handoffs were natively accepted.

| Case | Expected parent | Observed parent | Result |
| --- | --- | --- | --- |
| PIPE01 | `supported` | `supported` | accepted |
| PIPE02 | `contradicted` | `contradicted` | accepted |
| PIPE03 | `not_checkable` | `not_checkable` | accepted |
| PIPE04 | `contradicted` | `contradicted` | accepted |

Positive failures: **0/4**.

Exact whole-object authorities:

- PIPE01: `sha256:a0e2f77b48a9a9fe8347df345e5f112cfe76bde19cc82986c2efaccf90730524`
- PIPE02: `sha256:f2a1c54ea5e7eb9aaeca256d035247b79b563d3a4dbb19fd580362d2065a6e24`
- PIPE03: `sha256:bfad4513810c30ab7e17c2dd6779a04e19733c3e297a58374d646d7a912b7eff`
- PIPE04: `sha256:0e9f6e028685e5ed5e739e71cc78e88058aeb47734db284322240e2de8ca1304`

## Revealed mutation / replay pressure

All **49/49** executed real-handoff mutation checks were rejected.

PIPE01 exercised 13 checks, including the cross-run same-proposition/same-conclusion replay control. PIPE02–PIPE04 exercised 12 each.

Rejected classes included:

- changed native-result hash;
- omitted child;
- semantic sequence change;
- wrong root;
- stale decomposition receipt;
- parent-conclusion mutation;
- opaque/private-codec child-result ID;
- nested RC2 child-content substitution;
- coherent reseal against fixed whole-object authority;
- external whole-object authority mismatch;
- destination-policy injection;
- wrong child-result ID;
- cross-run replay.

False accepts: **0**.

Observed error localization remained specific rather than collapsing to one baseline failure, including `NATIVE_RESULT_HASH_MISMATCH`, `WHOLE_OBJECT_AUTHORITY_MISMATCH`, `INVALID_RECOMPOSITION`, `PROPOSITION_CONTENT_MISMATCH`, `CHILD_COUNT_MISMATCH`, `INVALID_CAL_RESULT_ID`, `PARENT_CONCLUSION_MISMATCH`, `CHILD_DECLARATION_BINDING_MISMATCH`, `DECOMPOSITION_RECEIPT_ID_MISMATCH`, `CAL_RESULT_ID_MISMATCH`, and `ROOT_BINDING_MISMATCH`.

## Supported claim

Within the exact frozen PIPE01–PIPE04 CAL V1 cohort, a fresh context-free downstream consumer independently recovered and verified the public Candidate A RC2 child-result grammar plus the corrected typed parent-recomposition binding.

This supports the bounded claim that the existing RC2 child-result grammar need not widen for this frozen cohort and that the additional typed, externally reference-checked parent recomposition surface is independently consumable.

## Explicit limits

This result does not establish:

- coverage beyond the frozen PIPE01–PIPE04 semantic/decomposition cohort;
- that every future CAL V1 semantic family fits unchanged RC2;
- production Contract C version assignment;
- canonical discovery mutation;
- Decision Engine compatibility with this richer Contract C handoff;
- release authorization;
- Authorization or execution permission.

The earlier RC0 aperture/consumer falsifier remains valid evidence about that incorrect aperture and must not be rewritten away.

## Next justified gate

The independent-consumer gate is now established for the bounded subject.

The smallest next step is to formalize an exact Contract C successor/freeze candidate from the already-qualified producer subject, corrected public aperture, and this independent-consumer evidence, without widening semantics. After that exact Contract C candidate is frozen, Decision Engine must be requalified against that exact handoff before any pipeline-wide promotion or release claim.
