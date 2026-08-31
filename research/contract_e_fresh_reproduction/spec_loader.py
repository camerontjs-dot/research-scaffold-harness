"""Parser/loader for the four authorized Contract E specification surfaces."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SpecLoadError(Exception):
    """Raised when the authorized specification files cannot be loaded or are malformed as specs."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecLoadError(f"failed to read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecLoadError(f"{path} is not a JSON object")
    return data


def default_authority_input_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        candidate = parent / "authority_input"
        if (candidate / "SPEC-CANDIDATE.json").is_file():
            return candidate
    raise SpecLoadError("authority_input/ with SPEC-CANDIDATE.json not found from package location")


@dataclass(frozen=True)
class Spec:
    candidate: dict[str, Any]
    shapes: dict[str, Any]
    participant_boundary: dict[str, Any]
    basis_binding: dict[str, Any]
    source_dir: Path

    @property
    def domains(self) -> dict[str, Any]:
        return self.candidate["authority_domains"]

    @property
    def participants(self) -> dict[str, Any]:
        return self.candidate["participant_declarations"]

    @property
    def warrant_types(self) -> dict[str, Any]:
        return self.candidate["warrant_types"]

    @property
    def domain_basis_requirements(self) -> dict[str, Any]:
        return self.shapes["domain_basis_requirements"]

    @property
    def conferring_types(self) -> tuple[str, ...]:
        types = self.basis_binding["authority_reference"]["authority_conferring_types"]
        return tuple(types)

    @property
    def basis_types(self) -> tuple[str, ...]:
        return tuple(self.shapes["authority_basis_types"])

    @property
    def identity_provenance_fields(self) -> tuple[str, ...]:
        return tuple(self.candidate["propagation"]["identity_provenance_fields"])

    @property
    def never_implicit_fields(self) -> tuple[str, ...]:
        return tuple(self.candidate["propagation"]["never_implicit"])

    @property
    def propagation_modes(self) -> tuple[str, ...]:
        return tuple(self.candidate["common_envelope"]["propagation_modes"])

    @property
    def envelope_required(self) -> tuple[str, ...]:
        required = list(self.candidate["common_envelope"]["required"])
        extra = self.participant_boundary.get("common_envelope_additional_required") or []
        for item in extra:
            if item not in required:
                required.append(item)
        return tuple(required)

    def domain_any_of(self, domain: str) -> tuple[str, ...]:
        req = self.domain_basis_requirements.get(domain) or {}
        return tuple(req.get("any_of") or [])

    def required_qualification_type(self, domain: str) -> str | None:
        req = self.domain_basis_requirements.get(domain) or {}
        if "qualification" in req:
            return req["qualification"]
        domain_spec = self.domains.get(domain) or {}
        accepted = domain_spec.get("accepted_qualification_types") or []
        if len(accepted) == 1:
            return accepted[0]
        return None

    def required_warrant_type(self, domain: str) -> str | None:
        req = self.domain_basis_requirements.get(domain) or {}
        if "warrant" in req:
            return req["warrant"]
        domain_spec = self.domains.get(domain) or {}
        accepted = domain_spec.get("accepted_warrant_types") or []
        if len(accepted) == 1:
            return accepted[0]
        return None

    def competence_required(self, domain: str) -> bool:
        domain_spec = self.domains.get(domain) or {}
        if domain_spec.get("competence_required") is True:
            return True
        return "qualification" in (self.domain_basis_requirements.get(domain) or {})

    def warrant_required(self, domain: str) -> bool:
        # Assumption W1: a warrant named in domain_basis_requirements is required.
        return "warrant" in (self.domain_basis_requirements.get(domain) or {})

    def warrant_allowed(self, domain: str) -> bool:
        domain_spec = self.domains.get(domain) or {}
        return domain_spec.get("warrant_allowed") is True

    def accepted_qualification_types(self, domain: str) -> tuple[str, ...]:
        domain_spec = self.domains.get(domain) or {}
        accepted = list(domain_spec.get("accepted_qualification_types") or [])
        named = self.required_qualification_type(domain)
        if named and named not in accepted:
            accepted.append(named)
        return tuple(accepted)

    def accepted_warrant_types(self, domain: str) -> tuple[str, ...]:
        domain_spec = self.domains.get(domain) or {}
        accepted = list(domain_spec.get("accepted_warrant_types") or [])
        named = self.required_warrant_type(domain)
        if named and named not in accepted:
            accepted.append(named)
        return tuple(accepted)


_EXPECTED_SCHEMAS = {
    "SPEC-CANDIDATE.json": "contract-e-authority-warrant-research-spec",
    "SPEC-SHAPES.json": "contract-e-authority-warrant-research-spec-shapes",
    "SPEC-PARTICIPANT-BOUNDARY.json": "contract-e-participant-boundary-research-spec",
    "BASIS-BINDING-SPEC.json": "contract-e-authority-basis-binding-research-spec",
}


def load_specs(authority_input_dir: Path | None = None) -> Spec:
    source = Path(authority_input_dir) if authority_input_dir else default_authority_input_dir()
    if not source.is_dir():
        raise SpecLoadError(f"authority input dir does not exist: {source}")

    paths = {
        "candidate": source / "SPEC-CANDIDATE.json",
        "shapes": source / "SPEC-SHAPES.json",
        "participant_boundary": source / "SPEC-PARTICIPANT-BOUNDARY.json",
        "basis_binding": source / "BASIS-BINDING-SPEC.json",
    }
    for path in paths.values():
        if not path.is_file():
            raise SpecLoadError(f"missing specification file: {path}")

    loaded = {key: _read_json(path) for key, path in paths.items()}
    schema_files = {
        "SPEC-CANDIDATE.json": loaded["candidate"],
        "SPEC-SHAPES.json": loaded["shapes"],
        "SPEC-PARTICIPANT-BOUNDARY.json": loaded["participant_boundary"],
        "BASIS-BINDING-SPEC.json": loaded["basis_binding"],
    }
    for filename, expected in _EXPECTED_SCHEMAS.items():
        actual = schema_files[filename].get("schema")
        if actual != expected:
            raise SpecLoadError(
                f"{filename} schema {actual!r} does not match expected {expected!r}"
            )

    spec = Spec(
        candidate=loaded["candidate"],
        shapes=loaded["shapes"],
        participant_boundary=loaded["participant_boundary"],
        basis_binding=loaded["basis_binding"],
        source_dir=source,
    )
    _assert_minimum_structure(spec)
    return spec


def _assert_minimum_structure(spec: Spec) -> None:
    missing = []
    if "authority_domains" not in spec.candidate:
        missing.append("candidate.authority_domains")
    if "common_envelope" not in spec.candidate:
        missing.append("candidate.common_envelope")
    if "matching_rules" not in spec.basis_binding:
        missing.append("basis_binding.matching_rules")
    if "reason_precedence" not in spec.basis_binding.get("ordering", {}):
        missing.append("basis_binding.ordering.reason_precedence")
    if missing:
        raise SpecLoadError("specification missing required structure: " + ", ".join(missing))
