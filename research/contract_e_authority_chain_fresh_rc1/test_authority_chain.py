import copy
import unittest

from authority_chain import evaluate


SOURCE = "source-sha"


def basis(**extra):
    b = {
        "basis_type": "grant",
        "authority_conferring": True,
        "subject": None,
        "domain": None,
        "operation": None,
        "scope": None,
        "target_class": None,
        "current": True,
        "valid": True,
    }
    b.update(extra)
    return b


def obs(rid="o1", **extra):
    r = {
        "id": rid,
        "authority_kind": "observation",
        "producer_type": "source_observer",
        "source_hash": SOURCE,
        "dependencies": [],
    }
    r.update(extra)
    return r


def meas(rid="m1", deps=None, **extra):
    r = {
        "id": rid,
        "authority_kind": "measurement",
        "producer_type": "language_instrument",
        "source_hash": SOURCE,
        "dependencies": ["o1"] if deps is None else deps,
        "basis": basis(),
    }
    r.update(extra)
    return r


def sem(rid="s1", deps=None, proposal_id="p1", **extra):
    r = {
        "id": rid,
        "authority_kind": "semantic",
        "producer_type": "semantic_validator",
        "source_hash": SOURCE,
        "dependencies": ["m1"] if deps is None else deps,
        "proposal_id": proposal_id,
        "basis": basis(semantic_dimensions=["meaning"], allowed_embeddings=[]),
    }
    r.update(extra)
    return r


def comp(rid="c1", deps=None, **extra):
    r = {
        "id": rid,
        "authority_kind": "composition",
        "producer_type": "composition_governor",
        "source_hash": SOURCE,
        "dependencies": ["s1"] if deps is None else deps,
        "component_dimensions": ["meaning"],
        "basis": basis(component_dimensions=["meaning"], composition_rule=True),
    }
    r.update(extra)
    return r


def dec(rid="d1", deps=None, **extra):
    r = {
        "id": rid,
        "authority_kind": "decision",
        "producer_type": "decision_engine",
        "source_hash": SOURCE,
        "dependencies": ["s1"] if deps is None else deps,
        "basis": basis(),
    }
    r.update(extra)
    return r


def action_request(deps=None, **extra):
    r = {
        "authority_kind": "action",
        "producer_type": "action_authorizer",
        "source_hash": SOURCE,
        "dependencies": ["d1"] if deps is None else deps,
        "basis": basis(authority_domain="action"),
    }
    r.update(extra)
    return r


def proposal(pid="p1", dimension="meaning", **extra):
    p = {"id": pid, "dimension": dimension}
    p.update(extra)
    return p


def case(request, receipts=None, proposals=None, conflicts=None, residues=None, comparison_receipts=None, raw_source=None):
    return {
        "id": "case-1",
        "raw_source": {"text": "raw", "nested": [1, {"x": 2}]} if raw_source is None else raw_source,
        "source_hash": SOURCE,
        "proposals": [proposal()] if proposals is None else proposals,
        "receipts": [] if receipts is None else receipts,
        "conflicts": [] if conflicts is None else conflicts,
        "residues": [] if residues is None else residues,
        "comparison_receipts": [] if comparison_receipts is None else comparison_receipts,
        "request": request,
    }


class AuthorityChainTests(unittest.TestCase):
    def assertDenied(self, c, reason):
        out = evaluate(c)
        self.assertFalse(out["allowed"])
        self.assertEqual(out["status"], "insufficient_authority")
        self.assertEqual(out["reason"], reason)
        self.assertIsNone(out["authority_kind"])
        return out

    def assertAllowed(self, c, kind, reason):
        out = evaluate(c)
        self.assertTrue(out["allowed"])
        self.assertEqual(out["status"], "established")
        self.assertEqual(out["reason"], reason)
        self.assertEqual(out["authority_kind"], kind)
        return out

    def test_valid_recursive_lineage(self):
        c = case(action_request(), [obs(), meas(), sem(), dec()])
        self.assertAllowed(c, "action", "action_lineage_valid")

    def test_missing_dependency(self):
        c = case(meas(deps=["missing"]), [obs()])
        self.assertDenied(c, "authority_lineage_missing_dependency")

    def test_cycle(self):
        s1 = sem(deps=["m1"])
        m1 = meas(deps=["s1"])
        c = case(dec(deps=["s1"]), [s1, m1])
        self.assertDenied(c, "authority_lineage_cycle")

    def test_producer_authority_ceiling(self):
        bad = meas(producer_type="semantic_validator")
        c = case(bad, [obs()])
        self.assertDenied(c, "producer_authority_ceiling")

    def test_source_identity_mismatch(self):
        c = case(meas(source_hash="other"), [obs()])
        self.assertDenied(c, "source_identity_mismatch")

    def test_authority_conferring_basis_matching(self):
        req = meas(subject="alice", domain="d", operation="read", scope="s", target_class="t")
        req["basis"] = basis(subject="alice", domain="d", operation="read", scope="s", target_class="t")
        c = case(req, [obs()])
        self.assertAllowed(c, "measurement", "measurement_lineage_valid")
        req2 = copy.deepcopy(req)
        req2["basis"]["scope"] = "other"
        self.assertDenied(case(req2, [obs()]), "authority_conferring_basis_invalid")

    def test_nonconferring_basis(self):
        req = meas()
        req["basis"] = basis(basis_type="supporting_artifact", authority_conferring=False)
        self.assertDenied(case(req, [obs()]), "authority_conferring_basis_invalid")

    def test_stale_or_invalid_basis(self):
        req = meas()
        req["basis"] = basis(current=False)
        self.assertDenied(case(req, [obs()]), "authority_conferring_basis_invalid")
        req2 = meas()
        req2["basis"] = basis(valid=False)
        self.assertDenied(case(req2, [obs()]), "authority_conferring_basis_invalid")

    def test_comparison_narrowness(self):
        receipts = [obs("o1"), obs("o2"), meas("m1", ["o1"]), meas("m2", ["o2"])]
        req = {
            "authority_kind": "comparison",
            "producer_type": "comparison_engine",
            "source_hash": SOURCE,
            "dependencies": ["m1", "m2"],
            "relation": "EXACT_AGREEMENT",
        }
        self.assertAllowed(case(req, receipts), "comparison", "comparison_lineage_valid")
        bad = copy.deepcopy(req)
        bad["dependencies"] = ["m1"]
        self.assertDenied(case(bad, receipts), "comparison_requires_measurements")
        bad2 = copy.deepcopy(req)
        bad2["relation"] = "WINNER"
        self.assertDenied(case(bad2, receipts), "comparison_relation_unknown")

    def test_agreement_not_semantic_truth(self):
        req = sem(promotion_source="comparison_agreement")
        self.assertDenied(case(req, [obs(), meas()]), "agreement_has_no_truth_authority")

    def test_semantic_dimension_coverage(self):
        req = sem()
        req["basis"] = basis(semantic_dimensions=["other"], allowed_embeddings=[])
        self.assertDenied(case(req, [obs(), meas()]), "semantic_dimension_not_covered")

    def test_embedding_scope_preservation(self):
        p = proposal(embedding="modality", payload={"must": True})
        req = sem(claim_level="embedded", preserves_embedding=True)
        req["basis"] = basis(semantic_dimensions=["meaning"], allowed_embeddings=["modality"])
        self.assertAllowed(case(req, [obs(), meas()], proposals=[p]), "semantic", "semantic_lineage_valid")
        launder = copy.deepcopy(req)
        launder["claim_level"] = "narrator_fact"
        self.assertDenied(case(launder, [obs(), meas()], proposals=[p]), "embedding_scope_laundering")
        uncovered = copy.deepcopy(req)
        uncovered["basis"]["allowed_embeddings"] = []
        self.assertDenied(case(uncovered, [obs(), meas()], proposals=[p]), "embedding_not_covered_by_basis")

    def test_authorized_resolution_discharges_relevant_residue(self):
        resolver = {
            "id": "r1",
            "authority_kind": "resolution",
            "producer_type": "authority_resolver",
            "source_hash": SOURCE,
            "dependencies": ["m1"],
            "domain": "resolution",
            "operation": "resolve",
            "basis": basis(domain="resolution", operation="resolve"),
            "resolves_ids": ["res-1"],
        }
        req = sem(resolver_receipt_ids=["r1"])
        c = case(req, [obs(), meas(), resolver], residues=[{"id": "res-1", "status": "unresolved"}])
        self.assertAllowed(c, "semantic", "semantic_lineage_valid")

    def test_bare_resolution_ids_have_no_effect(self):
        req = sem(resolved_residue_ids=["res-1"])
        c = case(req, [obs(), meas()], residues=[{"id": "res-1", "status": "unresolved"}])
        self.assertDenied(c, "relevant_residue_unresolved")

    def test_invalid_resolver_authority_does_not_discharge(self):
        resolver = {
            "id": "r1",
            "authority_kind": "resolution",
            "producer_type": "decision_engine",
            "source_hash": SOURCE,
            "dependencies": ["m1"],
            "domain": "resolution",
            "operation": "resolve",
            "basis": basis(domain="resolution", operation="resolve"),
            "resolves_ids": ["res-1"],
        }
        req = sem(resolver_receipt_ids=["r1"])
        c = case(req, [obs(), meas(), resolver], residues=[{"id": "res-1", "status": "unresolved"}])
        self.assertDenied(c, "relevant_residue_unresolved")

    def test_blocking_relevant_residue_precedes_conflict_and_node(self):
        req = sem(source_hash="bad")
        c = case(req, [obs(), meas()], residues=[{"id": "r", "status": "contested"}], conflicts=[{"id": "c", "status": "unresolved"}])
        self.assertDenied(c, "relevant_residue_unresolved")

    def test_blocking_relevant_conflict(self):
        c = case(sem(), [obs(), meas()], conflicts=[{"id": "c", "status": "unresolved", "relevant": True}])
        self.assertDenied(c, "relevant_conflict_unresolved")

    def test_irrelevant_residue_and_conflict_preserved_but_nonblocking(self):
        residues = [{"id": "r", "status": "unresolved", "relevant": False, "payload": [1]}]
        conflicts = [{"id": "c", "status": "contested", "relevant": False, "payload": {"x": 1}}]
        c = case(sem(), [obs(), meas()], residues=residues, conflicts=conflicts)
        out = self.assertAllowed(c, "semantic", "semantic_lineage_valid")
        self.assertEqual(out["residues"], residues)
        self.assertEqual(out["conflicts"], conflicts)

    def test_composition(self):
        receipts = [obs(), meas(), sem()]
        self.assertAllowed(case(comp(), receipts), "composition", "composition_lineage_valid")
        bad = comp(component_dimensions=["meaning", "scope"])
        self.assertDenied(case(bad, receipts), "composition_dimensions_not_covered")
        bad2 = comp()
        bad2["basis"]["composition_rule"] = False
        self.assertDenied(case(bad2, receipts), "composition_rule_missing")

    def test_decision_dependencies(self):
        self.assertAllowed(case(dec(), [obs(), meas(), sem()]), "decision", "decision_lineage_valid")
        self.assertDenied(case(dec(deps=["m1"]), [obs(), meas()]), "decision_requires_semantics")

    def test_decision_action_authority_separation(self):
        receipts = [obs(), meas(), sem(), dec()]
        bad = action_request()
        bad["basis"] = basis(authority_domain="decision")
        self.assertDenied(case(bad, receipts), "decision_does_not_confer_execution_authority")
        self.assertDenied(case(action_request(deps=["s1"]), receipts), "action_requires_decision")

    def test_execution_verification_separation(self):
        executor_measurement = meas("em1", producer_type="executor_reporter")
        req = {
            "authority_kind": "verification",
            "producer_type": "outcome_verifier",
            "source_hash": SOURCE,
            "dependencies": ["em1"],
            "basis": basis(authority_domain="verification"),
        }
        self.assertDenied(case(req, [obs(), executor_measurement]), "verification_requires_observation")
        good = copy.deepcopy(req)
        good["dependencies"] = ["o1"]
        self.assertAllowed(case(good, [obs()]), "verification", "verification_lineage_valid")

    def test_exact_raw_source_preservation(self):
        raw = {"b": [1, {"z": None}], "a": "x"}
        c = case(obs(), [], raw_source=raw)
        out = self.assertAllowed(c, "observation", "observation_lineage_valid")
        self.assertEqual(out["raw_source"], raw)
        out["raw_source"]["b"][1]["z"] = "changed"
        self.assertIsNone(c["raw_source"]["b"][1]["z"])

    def test_exact_proposal_preservation(self):
        proposals = [proposal(payload={"raw": [1, 2]}), proposal("p2", "scope", embedding="negation")]
        out = evaluate(case(obs(), [], proposals=proposals))
        self.assertEqual(out["proposals"], proposals)
        self.assertIsNot(out["proposals"], proposals)

    def test_exact_conflict_residue_preservation(self):
        conflicts = [{"id": "c", "status": "resolved", "details": {"v": 1}}]
        residues = [{"id": "r", "status": "resolved", "details": [1, 2]}]
        out = evaluate(case(obs(), [], conflicts=conflicts, residues=residues))
        self.assertEqual(out["conflicts"], conflicts)
        self.assertEqual(out["residues"], residues)
        self.assertIsNot(out["conflicts"], conflicts)
        self.assertIsNot(out["residues"], residues)

    def test_exact_comparison_receipt_preservation(self):
        cr = [{"id": "cr1", "relation": "EXACT_AGREEMENT", "opaque": {"x": [1]}}]
        out = evaluate(case(obs(), [], comparison_receipts=cr))
        self.assertEqual(out["comparison_receipts"], cr)
        self.assertIsNot(out["comparison_receipts"], cr)

    def test_status_established_does_not_substitute_for_recursive_verification(self):
        bad_measurement = meas(status="established", source_hash="wrong")
        req = sem(status="established")
        self.assertDenied(case(req, [obs(), bad_measurement]), "source_identity_mismatch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
