# Contract E Production Envelope — RC0 Reconnaissance

Status: **RESEARCH ONLY / PRE-EXECUTION**

Production authorization: **false**

This record reconciles the live GitHub state available to the supervisor with an operator-provided read-only local MainFrame archaeology report and a narrow external standards check. It does not authorize a MainFrame mutation, production integration, Contract E promotion, merge, tag, or release.

## 1. Live GitHub facts

Observed by the supervisor on 2026-09-04:

- `camerontjs-dot/decision-engine` `main` is `a4425f8eb47449ff6c683222921bbea9483742e2`. Its maintained boundary remains Contract C -> Decision policy -> Contract D, with Authorization/execution outside the Decision Engine.
- `camerontjs-dot/apparatus-contracts` Draft research PR #82 remains open/unmerged at sealed successor head `a678c73a661853a3a704666fc6bbf29fa378948f`.
- Contract E RC3 successor evidence remains 62/62 exact with the target-cardinality defect repaired; production profile remains `NOT_READY`.
- `camerontjs-dot/research-scaffold-harness` Draft research PR #21 remains open/unmerged at final reproduction seal `9feb44d8c8ea96176f797fe0ef692cc8e4d13656`.
- Fresh independent Contract E RC3 recoverability remains supported only for that bounded reproduction.
- `camerontjs-dot/mainframe-live` remote `main` remains `bdd96c010b42e8752f9c451aa552b7e2fd37a2cc`.

Exact Contract E authority pinned for this reconnaissance:

- RC3 public SPEC blob: `8c142c6b86dd2512f1df0c19aa36dbef759d6c18`
- sealed successor reference blob: `00d4d8f078073388d751546c24678825b89a6402`
- sealed successor evaluator blob: `5bba49c6a412c689232ea1315df0153455dd316f`
- fresh independent implementation blob: `9019abd8ade820988de1f899b2ccef9e57e9a908`

Exact Contract D authority pinned:

- Contract D 1.0.0 release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`
- registered effect: `knowledge.add_verified_tag@1`, with only `scope = claim | object` as a parameter.

## 2. Contract E boundary that directly constrains the production envelope

The frozen RC3 SPEC states that:

- a content hash is integrity binding, not origin authentication;
- an AuthorizationReceipt is non-conferring evidence of an evaluation;
- a prior receipt is historical evidence, not standing permission;
- a consumer requiring current authority must re-evaluate current AuthorityState at point of use;
- Authorization does not establish execution occurrence;
- execution occurrence does not establish verification;
- signatures, PKI, real-world root authentication, reusable permits/leases, distributed locking, exactly-once execution, execution proof, and verification proof are outside RC3.

Therefore a production-envelope experiment must not turn an authorized receipt into a bearer execution token or silently collapse Authorization, execution, and verification.

## 3. Operator-provided local archaeology

The following is **operator-provided local observation**, not GitHub-verified state.

The local agent reported:

- MainFrame root `/Users/admin/Desktop/MainFrame`, branch `main`, local `HEAD=502f19f855fc3d9abb256801c0683870fc9093ae`;
- local tracking state two commits ahead and one behind remote, with a dirty working tree and dirty nested repositories;
- the local commit `502f19f...` is not resolvable through the supervisor's GitHub connection, so its bytes are not treated as GitHub authority;
- no local implementation/handler of `knowledge.add_verified_tag@1` was found;
- classification: `SEMANTICALLY SIMILAR MUTATION EXISTS` / `ONLY PARTIAL CONSUMER IDENTIFIED`;
- no component consumes a CAL/Contract E authorization result and applies that effect;
- the strongest reusable file-mutation primitive is `scripts/fetch_source_text.py::apply_result_atomically`, using target confinement, `O_NOFOLLOW`, `flock`, stat/version checks, same-directory temporary file, `fsync`, `os.replace`, and retry-on-concurrent-change behavior;
- the strongest database promotion pattern is the MindGraph project-index promotion path with staged hashes, backup, atomic promotion, and post-verification;
- `bin/provenance-attest` provides useful hash-chained material/product evidence but is unsigned and does not authenticate actor identity;
- `bin/knowledge-write-guard` is fail-open, Claude-tool scoped, and bypassable by Bash/Codex/other local clients;
- `bin/knowledge-reconcile` is a post-state provenance backstop, not exact-operation verification;
- no globally enforced fail-closed knowledge-mutation authorization surface exists;
- no end-to-end independent verifier establishes that a CAL-authorized tag/status mutation occurred exactly once;
- current root/nested dirty state and historical Epistemic Research System auto-promotion create local-state ambiguity.

The local agent recommended a first experiment on a disposable Markdown file outside `10_knowledge`, beginning with **shadow validation only**, not a live knowledge write.

## 4. Narrow standards cross-check

This supervisor performed a separate narrow standards check. It is not a substitute for the user's completed Deep Research report.

### NIST SP 800-207, Zero Trust Architecture

Relevant pattern:

- authentication and authorization are distinct functions before resource access;
- a Policy Enforcement Point enforces the access decision at the protected-resource boundary;
- access is resource-specific and least-privilege rather than implied by local/network location;
- policy can be reevaluated as state changes.

Relevance here: Contract E evaluation belongs close to the resource mutation boundary, not merely upstream in Decision Engine.

### RFC 9449, OAuth 2.0 Demonstrating Proof of Possession (DPoP)

Relevant pattern:

- bearer possession alone is insufficient for replay-resistant authorization;
- authorization material can be sender-/request-bound;
- proofs bind to request properties and must be freshness constrained to reduce replay.

Relevance here: an AuthorizationReceipt must not become a reusable bearer execution permit. Exact intent binding and explicit replay controls are separate production-envelope concerns.

### SPIFFE

Relevant pattern:

- workload identity is a separate cryptographically verifiable layer rooted in an explicit trust domain;
- bootstrap identity may rely on out-of-band operating-system/orchestrator facts.

Relevance here: real caller/workload authentication and trusted AuthorityState origin are separate from Contract E's semantic predicate and should not be invented inside RC0.

### in-toto

Relevant pattern:

- authorized functionaries, exact materials/products, signed step evidence, and independent verification are separable concerns.

Relevance here: MainFrame's existing unsigned provenance ledger may be reusable as evidence plumbing, but it cannot by itself establish authenticated execution authority.

## 5. Synthesis

### OBSERVED

There is no real Contract E production consumer yet.

There are, however, reusable local techniques for:

- atomic file replacement and stale-version detection;
- transactional database promotion and post-verification;
- append-only/hash-chained provenance evidence;
- post-state reconciliation.

### INFERENCE

The smallest useful next experiment is not a live `knowledge.add_verified_tag@1` implementation.

The Contract D effect registry does not define a concrete file/frontmatter representation for a "verified tag". Implementing that representation now would introduce execution semantics not established by Contract D or Contract E.

The smaller discriminating question is whether a point-of-use shadow enforcement component can safely bind:

1. an exact valid Contract D Decision/effect;
2. an exact immutable execution intent;
3. an exact disposable target pre-state;
4. current AuthorityState and AuthorizationRequest;
5. replay state;
6. the current point-of-use file state;

and fail closed under stale authority, stale target, replay, substitution, malformed input, path escape, concurrency, or Contract E implementation disagreement.

### UNKNOWN / NOT CLAIMED

This reconnaissance does not establish:

- the production trust root or authenticated AuthorityState origin;
- the production workload/principal identity mechanism;
- the production owner of the PEP/executor;
- the concrete persisted representation of `knowledge.add_verified_tag@1`;
- exactly-once execution;
- a production execution receipt schema;
- independent verification of an actual mutation;
- that the user's completed September 4 Deep Research response has been reconciled here.

The supervisor can locate the separate Deep Research thread prompt in cross-project context, but the completed assistant research response is not exposed through the retrievable cross-conversation surface available in this thread. No older research report is being substituted for it.

## 6. Next bounded action

Proceed only with the shadow point-of-use RC0 preregistered beside this file.

RC0 performs no live `10_knowledge` write and does not decide the final production architecture. Its purpose is to falsify unsafe envelope orderings and determine whether the exact point-of-use binding can be made mechanically sound before choosing trust-root, ownership, or concrete execution semantics.
