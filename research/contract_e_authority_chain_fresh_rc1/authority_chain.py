from __future__ import annotations

from copy import deepcopy


AUTHORITY_KINDS = {
    "observation",
    "measurement",
    "semantic",
    "comparison",
    "resolution",
    "composition",
    "decision",
    "action",
    "verification",
}

PRODUCER_ALLOWED_KINDS = {
    "action_authorizer": {"action"},
    "authority_resolver": {"resolution"},
    "comparison_engine": {"comparison"},
    "composition_governor": {"composition"},
    "decision_engine": {"decision"},
    "executor_reporter": {"measurement"},
    "language_instrument": {"measurement"},
    "outcome_verifier": {"verification"},
    "semantic_validator": {"semantic"},
    "source_observer": {"observation"},
}

CONFERRING_BASIS_TYPES = {"grant", "policy", "delegation"}
BASIS_REQUIRED_FIELDS = {
    "basis_type",
    "authority_conferring",
    "subject",
    "domain",
    "operation",
    "scope",
    "target_class",
    "current",
    "valid",
}

COMPARISON_RELATIONS = {
    "EXACT_AGREEMENT",
    "SEMANTIC_EQUIVALENCE",
    "COMPATIBLE_PARTIAL_OVERLAP",
    "COMPLEMENTARY_ORTHOGONAL",
    "GRANULARITY_MISMATCH",
    "SLOT_BOUNDARY_DISAGREEMENT",
    "SCOPE_ATTACHMENT_DISAGREEMENT",
    "ROLE_BINDING_DISAGREEMENT",
    "OPERATOR_VALUE_DISAGREEMENT",
    "POLARITY_DISAGREEMENT",
    "JURISDICTION_DISAGREEMENT",
    "PROVENANCE_OR_VISIBILITY_DISAGREEMENT",
    "CONTRADICTION",
    "INCOMMENSURABLE",
}

EMBEDDING_VALUES = {
    "quantifier",
    "modality",
    "probability",
    "permission",
    "conditional",
    "attribution",
    "temporal",
    "quantitative",
    "exception",
    "negation",
}

BLOCKING_KINDS = {"semantic", "composition", "decision", "action", "verification"}

SUCCESS_REASONS = {
    "observation": "observation_lineage_valid",
    "measurement": "measurement_lineage_valid",
    "semantic": "semantic_lineage_valid",
    "comparison": "comparison_lineage_valid",
    "resolution": "resolution_lineage_valid",
    "composition": "composition_lineage_valid",
    "decision": "decision_lineage_valid",
    "action": "action_lineage_valid",
    "verification": "verification_lineage_valid",
}


def _basis_valid_and_matching(node: dict) -> bool:
    basis = node.get("basis")
    if not isinstance(basis, dict):
        return False
    if not BASIS_REQUIRED_FIELDS.issubset(basis.keys()):
        return False
    if basis.get("basis_type") not in CONFERRING_BASIS_TYPES:
        return False
    if basis.get("authority_conferring") is not True:
        return False
    if basis.get("current") is not True or basis.get("valid") is not True:
        return False

    for field in ("subject", "domain", "operation", "scope", "target_class"):
        node_value = node.get(field)
        if node_value is not None and basis.get(field) != node_value:
            return False

    if basis.get("target") is not None and basis.get("target") != node.get("target"):
        return False
    return True


def evaluate(case: dict) -> dict:
    receipts = case.get("receipts", [])
    proposals = case.get("proposals", [])

    receipt_index: dict[object, list[dict]] = {}
    if isinstance(receipts, list):
        for receipt in receipts:
            if isinstance(receipt, dict) and "id" in receipt:
                receipt_index.setdefault(receipt.get("id"), []).append(receipt)

    proposal_index: dict[object, list[dict]] = {}
    if isinstance(proposals, list):
        for proposal in proposals:
            if isinstance(proposal, dict) and "id" in proposal:
                proposal_index.setdefault(proposal.get("id"), []).append(proposal)

    memo: dict[int, tuple[bool, str, str | None]] = {}
    active: set[int] = set()

    def validate(node: dict) -> tuple[bool, str, str | None]:
        node_obj = id(node)
        if node_obj in active:
            return False, "authority_lineage_cycle", None
        if node_obj in memo:
            return memo[node_obj]

        kind = node.get("authority_kind")
        if kind not in AUTHORITY_KINDS:
            result = (False, "unsupported_authority_kind", None)
            memo[node_obj] = result
            return result

        producer = node.get("producer_type")
        if kind not in PRODUCER_ALLOWED_KINDS.get(producer, set()):
            result = (False, "producer_authority_ceiling", None)
            memo[node_obj] = result
            return result

        if node.get("source_hash") != case.get("source_hash"):
            result = (False, "source_identity_mismatch", None)
            memo[node_obj] = result
            return result

        dependencies = node.get("dependencies")
        if not isinstance(dependencies, list):
            dependencies = []

        if kind == "observation":
            if dependencies:
                result = (False, "observation_root_has_dependencies", None)
                memo[node_obj] = result
                return result
            if producer != "source_observer":
                result = (False, "observation_root_not_independent", None)
                memo[node_obj] = result
                return result
            result = (True, SUCCESS_REASONS[kind], kind)
            memo[node_obj] = result
            return result

        dep_nodes: list[dict] = []
        for dep_id in dependencies:
            matches = receipt_index.get(dep_id, [])
            if len(matches) != 1:
                result = (False, "authority_lineage_missing_dependency", None)
                memo[node_obj] = result
                return result
            dep_nodes.append(matches[0])

        active.add(node_obj)
        try:
            for dep in dep_nodes:
                ok, reason, _ = validate(dep)
                if not ok:
                    result = (False, reason, None)
                    memo[node_obj] = result
                    return result
        finally:
            active.discard(node_obj)

        dep_kinds = [dep.get("authority_kind") for dep in dep_nodes]

        if kind == "comparison":
            if len(dep_nodes) < 2 or any(dep_kind != "measurement" for dep_kind in dep_kinds):
                result = (False, "comparison_requires_measurements", None)
                memo[node_obj] = result
                return result
            if node.get("relation") not in COMPARISON_RELATIONS:
                result = (False, "comparison_relation_unknown", None)
                memo[node_obj] = result
                return result
            result = (True, SUCCESS_REASONS[kind], kind)
            memo[node_obj] = result
            return result

        if not _basis_valid_and_matching(node):
            result = (False, "authority_conferring_basis_invalid", None)
            memo[node_obj] = result
            return result

        basis = node["basis"]

        if kind == "measurement":
            if not dep_nodes or any(dep_kind != "observation" for dep_kind in dep_kinds):
                result = (False, "measurement_requires_observation", None)
                memo[node_obj] = result
                return result

        elif kind == "semantic":
            if node.get("promotion_source") == "comparison_agreement":
                result = (False, "agreement_has_no_truth_authority", None)
                memo[node_obj] = result
                return result
            if not dep_nodes or any(dep_kind != "measurement" for dep_kind in dep_kinds):
                result = (False, "semantic_requires_measurement", None)
                memo[node_obj] = result
                return result
            proposal_matches = proposal_index.get(node.get("proposal_id"), [])
            if len(proposal_matches) != 1:
                result = (False, "semantic_proposal_missing", None)
                memo[node_obj] = result
                return result
            proposal = proposal_matches[0]
            semantic_dimensions = basis.get("semantic_dimensions")
            if not isinstance(semantic_dimensions, list) or proposal.get("dimension") not in semantic_dimensions:
                result = (False, "semantic_dimension_not_covered", None)
                memo[node_obj] = result
                return result
            embedding = proposal.get("embedding")
            if embedding in EMBEDDING_VALUES:
                if node.get("claim_level") == "narrator_fact" or node.get("preserves_embedding") is not True:
                    result = (False, "embedding_scope_laundering", None)
                    memo[node_obj] = result
                    return result
                allowed_embeddings = basis.get("allowed_embeddings")
                if not isinstance(allowed_embeddings, list) or embedding not in allowed_embeddings:
                    result = (False, "embedding_not_covered_by_basis", None)
                    memo[node_obj] = result
                    return result

        elif kind == "resolution":
            if basis.get("domain") != "resolution" or basis.get("operation") != "resolve":
                result = (False, "resolver_basis_mismatch", None)
                memo[node_obj] = result
                return result
            if not dep_nodes or any(dep_kind not in {"measurement", "semantic", "comparison"} for dep_kind in dep_kinds):
                result = (False, "resolution_dependency_invalid", None)
                memo[node_obj] = result
                return result
            if producer != "authority_resolver":
                result = (False, "resolver_producer_invalid", None)
                memo[node_obj] = result
                return result
            resolves_ids = node.get("resolves_ids")
            if not isinstance(resolves_ids, list) or not resolves_ids:
                result = (False, "resolver_targets_missing", None)
                memo[node_obj] = result
                return result

        elif kind == "composition":
            if set(node.get("component_dimensions", [])) != set(basis.get("component_dimensions", [])):
                result = (False, "composition_dimensions_not_covered", None)
                memo[node_obj] = result
                return result
            if not basis.get("composition_rule"):
                result = (False, "composition_rule_missing", None)
                memo[node_obj] = result
                return result
            if not dep_nodes or any(dep_kind not in {"semantic", "composition"} for dep_kind in dep_kinds):
                result = (False, "composition_requires_semantics", None)
                memo[node_obj] = result
                return result

        elif kind == "decision":
            if not dep_nodes or any(dep_kind not in {"semantic", "composition"} for dep_kind in dep_kinds):
                result = (False, "decision_requires_semantics", None)
                memo[node_obj] = result
                return result

        elif kind == "action":
            if basis.get("authority_domain") not in {"action", "execution"}:
                result = (False, "decision_does_not_confer_execution_authority", None)
                memo[node_obj] = result
                return result
            if not dep_nodes or any(dep_kind != "decision" for dep_kind in dep_kinds):
                result = (False, "action_requires_decision", None)
                memo[node_obj] = result
                return result

        elif kind == "verification":
            if basis.get("authority_domain") != "verification":
                result = (False, "verification_domain_mismatch", None)
                memo[node_obj] = result
                return result
            if not dep_nodes or any(dep_kind != "observation" for dep_kind in dep_kinds):
                result = (False, "verification_requires_observation", None)
                memo[node_obj] = result
                return result
            if any(dep.get("producer_type") == "executor_reporter" for dep in dep_nodes):
                result = (False, "executor_report_not_verification_authority", None)
                memo[node_obj] = result
                return result

        result = (True, SUCCESS_REASONS[kind], kind)
        memo[node_obj] = result
        return result

    request = case.get("request")
    if not isinstance(request, dict):
        request = {}

    discharged_ids: set[object] = set()
    resolver_ids = request.get("resolver_receipt_ids", [])
    if isinstance(resolver_ids, list):
        for resolver_id in resolver_ids:
            matches = receipt_index.get(resolver_id, [])
            if len(matches) != 1:
                continue
            resolver = matches[0]
            ok, _, validated_kind = validate(resolver)
            if ok and validated_kind == "resolution":
                resolves_ids = resolver.get("resolves_ids", [])
                if isinstance(resolves_ids, list):
                    discharged_ids.update(resolves_ids)

    request_kind = request.get("authority_kind")
    reason: str
    allowed = False
    authority_kind: str | None = None

    if request_kind in BLOCKING_KINDS:
        residues = case.get("residues", [])
        if isinstance(residues, list):
            for residue in residues:
                if not isinstance(residue, dict):
                    continue
                if residue.get("relevant", True) is not False and residue.get("status") in {"unresolved", "contested"} and residue.get("id") not in discharged_ids:
                    reason = "relevant_residue_unresolved"
                    break
            else:
                reason = ""
        else:
            reason = ""

        if not reason:
            conflicts = case.get("conflicts", [])
            if isinstance(conflicts, list):
                for conflict in conflicts:
                    if not isinstance(conflict, dict):
                        continue
                    if conflict.get("relevant", True) is not False and conflict.get("status") in {"unresolved", "contested"} and conflict.get("id") not in discharged_ids:
                        reason = "relevant_conflict_unresolved"
                        break
                else:
                    reason = ""
            else:
                reason = ""
    else:
        reason = ""

    if not reason:
        ok, reason, validated_kind = validate(request)
        if ok:
            allowed = True
            authority_kind = validated_kind

    return {
        "allowed": allowed,
        "status": "established" if allowed else "insufficient_authority",
        "reason": reason,
        "authority_kind": authority_kind if allowed else None,
        "raw_source": deepcopy(case.get("raw_source")),
        "proposals": deepcopy(case.get("proposals")),
        "conflicts": deepcopy(case.get("conflicts")),
        "residues": deepcopy(case.get("residues")),
        "comparison_receipts": deepcopy(case.get("comparison_receipts")),
    }
