#!/usr/bin/env python3
"""Fresh clean-room verifier for the frozen CAL RC5 two-receipt profile."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

CONTEXT_ID = "cal.rc5.asymmetric-two-receipt.strict-comparison.v1"
CLAIM_NAMESPACE = "cal.rc5.experimental.claims.v1"
AUTHORITY_PROFILE_ID = (
    "CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:"
    "blob:f55156e43e0c1b4a7868bc8339585b8892edda38"
)
ATOM_RECEIPT_TYPE = "CAL.AtomWarrant/v1"
PROP_RECEIPT_TYPE = "CAL.PropositionBinding/v1"
SCHEMA_MAJOR = 1
SIGNATURE_PROFILE = "Ed25519"
MAX_SAFE_INTEGER = 9007199254740991

ATOM_PROJECTION_FIELDS = (
    "execution_state",
    "evidence_admitted",
    "authority_subject_id",
    "raw_source_id",
    "authority_subject_source_id",
    "raw_bundle_id",
    "authority_subject_bundle_id",
    "raw_passage_id",
    "authority_subject_passage_id",
    "admitted_passage_span",
    "raw_claim_id",
    "authority_subject_claim_id",
    "target_atom_id",
    "authority_subject_atom_id",
    "proposal",
    "assertion",
    "operator",
    "field_warrants",
    "required_fields",
    "composition",
    "aperture",
)

PROPOSITION_FIELDS = (
    "claim_id",
    "family",
    "lhs_entity",
    "rhs_entity",
    "comparison_direction",
)

PROP_PROJECTION_FIELDS = (
    "family",
    "lhs_entity",
    "rhs_entity",
    "comparison_direction",
)

ATOM_STATEMENT_FIELDS = {
    "receipt_type",
    "schema_major",
    "context_id",
    "signature_profile",
    "authority_profile_id",
    "issuer_key_id",
    "authority_status",
    "authority_reason",
    "claim_id",
    "atom_id",
    "atom_projection",
}

PROP_STATEMENT_FIELDS = {
    "receipt_type",
    "schema_major",
    "context_id",
    "signature_profile",
    "claim_namespace",
    "issuer_key_id",
    "claim_id",
    "proposition_projection",
}

ENVELOPE_FIELDS = {"statement", "statement_digest_sha256", "signature_base64url"}
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
B64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class DuplicateKeyError(ValueError):
    pass


class JSONSyntaxError(ValueError):
    pass


class InvalidInputError(ValueError):
    pass


class SchemaError(ValueError):
    pass


class UnsupportedProfileError(ValueError):
    pass


def _refuse(code: str) -> dict[str, str]:
    return {"decision": "REFUSE", "code": code}


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKeyError(key)
        out[key] = value
    return out


def _parse_json(raw: bytes | str) -> Any:
    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise JSONSyntaxError("invalid UTF-8") from exc
    elif isinstance(raw, str):
        text = raw
    else:
        raise JSONSyntaxError("JSON transport must be bytes or str")
    try:
        return json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(JSONSyntaxError(token)),
        )
    except DuplicateKeyError:
        raise
    except (json.JSONDecodeError, JSONSyntaxError, UnicodeError, ValueError) as exc:
        if isinstance(exc, DuplicateKeyError):
            raise
        raise JSONSyntaxError("invalid JSON") from exc


def _validate_ijson(value: Any) -> None:
    if value is None or isinstance(value, bool) or isinstance(value, str):
        if isinstance(value, str):
            for ch in value:
                cp = ord(ch)
                if 0xD800 <= cp <= 0xDFFF:
                    raise ValueError("lone surrogate")
        return
    if type(value) is int:
        if not -MAX_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
            raise ValueError("integer outside I-JSON safe range")
        return
    if isinstance(value, float):
        raise ValueError("floating-point values forbidden")
    if isinstance(value, list):
        for item in value:
            _validate_ijson(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non-string object key")
            _validate_ijson(key)
            _validate_ijson(item)
        return
    raise ValueError("unsupported JSON value")


def _utf16_sort_key(text: str) -> bytes:
    return text.encode("utf-16-be", "strict")


def _jcs_string(text: str) -> str:
    parts: list[str] = ['"']
    escapes = {
        0x08: "\\b",
        0x09: "\\t",
        0x0A: "\\n",
        0x0C: "\\f",
        0x0D: "\\r",
    }
    for ch in text:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise ValueError("lone surrogate")
        if ch == '"':
            parts.append('\\"')
        elif ch == "\\":
            parts.append("\\\\")
        elif cp in escapes:
            parts.append(escapes[cp])
        elif 0 <= cp <= 0x1F:
            parts.append(f"\\u{cp:04x}")
        else:
            parts.append(ch)
    parts.append('"')
    return "".join(parts)


def jcs_canonicalize(value: Any) -> bytes:
    """RFC 8785 JCS for the RC5 restricted profile (no floating point)."""
    _validate_ijson(value)

    def encode(item: Any) -> str:
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if isinstance(item, str):
            return _jcs_string(item)
        if isinstance(item, list):
            return "[" + ",".join(encode(v) for v in item) + "]"
        if isinstance(item, dict):
            pieces = []
            for key in sorted(item.keys(), key=_utf16_sort_key):
                pieces.append(_jcs_string(key) + ":" + encode(item[key]))
            return "{" + ",".join(pieces) + "}"
        raise ValueError("unsupported value")

    return encode(value).encode("utf-8")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value) >= 1


def _validate_atom_projection(proj: Any) -> None:
    if not isinstance(proj, dict) or set(proj) != set(ATOM_PROJECTION_FIELDS):
        raise SchemaError("atom projection fields")
    string_fields = (
        "execution_state",
        "authority_subject_id",
        "raw_source_id",
        "authority_subject_source_id",
        "raw_bundle_id",
        "authority_subject_bundle_id",
        "raw_passage_id",
        "authority_subject_passage_id",
    )
    for field in string_fields:
        if not isinstance(proj[field], str):
            raise SchemaError(field)
    for field in ("raw_claim_id", "authority_subject_claim_id", "target_atom_id", "authority_subject_atom_id"):
        if not _is_nonempty_string(proj[field]):
            raise SchemaError(field)
    if not isinstance(proj["evidence_admitted"], bool):
        raise SchemaError("evidence_admitted")
    span = proj["admitted_passage_span"]
    if not isinstance(span, list) or len(span) != 2 or any(type(x) is not int for x in span):
        raise SchemaError("admitted_passage_span")
    for field in ("proposal", "assertion", "operator", "field_warrants", "composition", "aperture"):
        if not isinstance(proj[field], dict):
            raise SchemaError(field)
    required_fields = proj["required_fields"]
    if not isinstance(required_fields, list) or any(not isinstance(x, str) for x in required_fields):
        raise SchemaError("required_fields")


def _validate_prop_projection(proj: Any) -> None:
    if not isinstance(proj, dict) or set(proj) != set(PROP_PROJECTION_FIELDS):
        raise SchemaError("proposition projection fields")
    for field in PROP_PROJECTION_FIELDS:
        if not _is_nonempty_string(proj[field]):
            raise SchemaError(field)


def _validate_receipt_schema(receipt: Any, kind: str) -> None:
    try:
        _validate_ijson(receipt)
    except ValueError as exc:
        raise SchemaError("I-JSON profile") from exc
    if not isinstance(receipt, dict) or set(receipt) != ENVELOPE_FIELDS:
        raise SchemaError("envelope fields")
    if not isinstance(receipt["statement"], dict):
        raise SchemaError("statement")
    digest = receipt["statement_digest_sha256"]
    if not isinstance(digest, str) or HEX64_RE.fullmatch(digest) is None:
        raise SchemaError("digest")
    # The JSON Schema's signature regex is an encoding constraint. It is checked
    # at signature stage so malformed signatures produce SIGNATURE_INVALID_FORMAT,
    # preserving the specification's typed stage ordering.
    if not isinstance(receipt["signature_base64url"], str):
        raise SchemaError("signature type")

    statement = receipt["statement"]
    if kind == "atom":
        if set(statement) != ATOM_STATEMENT_FIELDS:
            raise SchemaError("atom statement fields")
        profile_constants = {
            "receipt_type": ATOM_RECEIPT_TYPE,
            "schema_major": SCHEMA_MAJOR,
            "context_id": CONTEXT_ID,
            "signature_profile": SIGNATURE_PROFILE,
            "authority_profile_id": AUTHORITY_PROFILE_ID,
        }
        for field, expected in profile_constants.items():
            if field not in statement:
                raise SchemaError(field)
            if statement[field] != expected:
                raise UnsupportedProfileError(field)
        if statement["authority_status"] != "WARRANTED":
            raise SchemaError("authority_status")
        if statement["authority_reason"] != "ALL_REQUIRED_WARRANT_ESTABLISHED":
            raise SchemaError("authority_reason")
        for field in ("issuer_key_id", "claim_id", "atom_id"):
            if not _is_nonempty_string(statement[field]):
                raise SchemaError(field)
        _validate_atom_projection(statement["atom_projection"])
    elif kind == "proposition":
        if set(statement) != PROP_STATEMENT_FIELDS:
            raise SchemaError("proposition statement fields")
        profile_constants = {
            "receipt_type": PROP_RECEIPT_TYPE,
            "schema_major": SCHEMA_MAJOR,
            "context_id": CONTEXT_ID,
            "signature_profile": SIGNATURE_PROFILE,
            "claim_namespace": CLAIM_NAMESPACE,
        }
        for field, expected in profile_constants.items():
            if statement[field] != expected:
                raise UnsupportedProfileError(field)
        for field in ("issuer_key_id", "claim_id"):
            if not _is_nonempty_string(statement[field]):
                raise SchemaError(field)
        _validate_prop_projection(statement["proposition_projection"])
    else:
        raise SchemaError("unknown receipt kind")


def _decode_base64url_no_padding(value: str, expected_len: int) -> bytes:
    if not isinstance(value, str) or "=" in value or B64URL_RE.fullmatch(value) is None:
        raise ValueError("invalid base64url alphabet/padding")
    pad = "=" * ((4 - len(value) % 4) % 4)
    try:
        decoded = base64.b64decode((value + pad).encode("ascii"), altchars=b"-_", validate=True)
    except Exception as exc:
        raise ValueError("invalid base64url") from exc
    if len(decoded) != expected_len:
        raise ValueError("wrong decoded length")
    canonical = base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
    if canonical != value:
        raise ValueError("non-canonical base64url")
    return decoded


def _validate_semantic_request(obj: Any) -> None:
    try:
        _validate_ijson(obj)
    except ValueError as exc:
        raise InvalidInputError("semantic input violates I-JSON") from exc
    if not isinstance(obj, dict) or set(obj) != {"context_id", "authority_case", "proposition"}:
        raise InvalidInputError("semantic request fields")
    if not isinstance(obj["context_id"], str):
        raise InvalidInputError("context_id")
    authority_case = obj["authority_case"]
    proposition = obj["proposition"]
    if not isinstance(authority_case, dict):
        raise InvalidInputError("authority_case")
    if not isinstance(proposition, dict) or set(proposition) != set(PROPOSITION_FIELDS):
        raise InvalidInputError("proposition fields")
    for field in PROPOSITION_FIELDS:
        if not _is_nonempty_string(proposition[field]):
            raise InvalidInputError(field)
    try:
        projection = {field: authority_case[field] for field in ATOM_PROJECTION_FIELDS}
    except KeyError as exc:
        raise InvalidInputError("missing authority projection field") from exc
    try:
        _validate_atom_projection(projection)
    except SchemaError as exc:
        raise InvalidInputError("invalid authority projection") from exc


def derive_atom_projection(semantic_request: dict[str, Any]) -> dict[str, Any]:
    authority_case = semantic_request["authority_case"]
    return {field: authority_case[field] for field in ATOM_PROJECTION_FIELDS}


def derive_proposition_projection(semantic_request: dict[str, Any]) -> dict[str, Any]:
    proposition = semantic_request["proposition"]
    return {field: proposition[field] for field in PROP_PROJECTION_FIELDS}


def _load_public_keys(obj: Any) -> dict[str, bytes]:
    try:
        _validate_ijson(obj)
    except ValueError as exc:
        raise InvalidInputError("public keys violate I-JSON") from exc
    if not isinstance(obj, dict) or set(obj) != {"key_set_version", "context_id", "signature_profile", "keys"}:
        raise InvalidInputError("public key set fields")
    if obj["key_set_version"] != "cal.rc5.public-keys.v1":
        raise InvalidInputError("key set version")
    if obj["context_id"] != CONTEXT_ID or obj["signature_profile"] != SIGNATURE_PROFILE:
        raise InvalidInputError("key set profile")
    if not isinstance(obj["keys"], list):
        raise InvalidInputError("keys")
    out: dict[str, bytes] = {}
    required = {
        "key_id",
        "algorithm",
        "public_key_encoding",
        "public_key_base64url",
        "public_key_sha256",
    }
    for entry in obj["keys"]:
        if not isinstance(entry, dict) or set(entry) != required:
            raise InvalidInputError("public key entry fields")
        key_id = entry["key_id"]
        if not _is_nonempty_string(key_id) or key_id in out:
            raise InvalidInputError("duplicate/invalid key id")
        if entry["algorithm"] != "Ed25519" or entry["public_key_encoding"] != "raw-32-byte/base64url-no-padding":
            raise InvalidInputError("public key profile")
        if not isinstance(entry["public_key_sha256"], str) or HEX64_RE.fullmatch(entry["public_key_sha256"]) is None:
            raise InvalidInputError("public key digest")
        try:
            raw_key = _decode_base64url_no_padding(entry["public_key_base64url"], 32)
        except ValueError as exc:
            raise InvalidInputError("public key encoding") from exc
        if hashlib.sha256(raw_key).hexdigest() != entry["public_key_sha256"]:
            raise InvalidInputError("public key fingerprint mismatch")
        out[key_id] = raw_key
    return out


def _load_trust_policy(obj: Any) -> list[dict[str, Any]]:
    try:
        _validate_ijson(obj)
    except ValueError as exc:
        raise InvalidInputError("trust policy violates I-JSON") from exc
    if not isinstance(obj, dict) or set(obj) != {"policy_version", "context_id", "default", "authorizations"}:
        raise InvalidInputError("trust policy fields")
    if obj["policy_version"] != "cal.rc5.trust-policy.v1" or obj["context_id"] != CONTEXT_ID or obj["default"] != "DENY":
        raise InvalidInputError("trust policy profile")
    authorizations = obj["authorizations"]
    if not isinstance(authorizations, list):
        raise InvalidInputError("authorizations")
    result: list[dict[str, Any]] = []
    for entry in authorizations:
        if not isinstance(entry, dict) or set(entry) != {"key_id", "receipt_type", "schema_major", "scope"}:
            raise InvalidInputError("authorization entry")
        if not _is_nonempty_string(entry["key_id"]) or type(entry["schema_major"]) is not int:
            raise InvalidInputError("authorization key/schema")
        if not isinstance(entry["receipt_type"], str) or not isinstance(entry["scope"], dict):
            raise InvalidInputError("authorization type/scope")
        if entry["receipt_type"] == ATOM_RECEIPT_TYPE:
            if set(entry["scope"]) != {"context_id", "authority_profile_id"}:
                raise InvalidInputError("atom authorization scope")
        elif entry["receipt_type"] == PROP_RECEIPT_TYPE:
            if set(entry["scope"]) != {"context_id", "claim_namespace"}:
                raise InvalidInputError("proposition authorization scope")
        else:
            raise InvalidInputError("unknown authorization receipt type")
        result.append(entry)
    return result


def _authorized(statement: dict[str, Any], authorizations: list[dict[str, Any]], kind: str) -> bool:
    for entry in authorizations:
        if entry["key_id"] != statement["issuer_key_id"]:
            continue
        if entry["receipt_type"] != statement["receipt_type"]:
            continue
        if entry["schema_major"] != statement["schema_major"]:
            continue
        scope = entry["scope"]
        if scope.get("context_id") != statement["context_id"]:
            continue
        if kind == "atom":
            if scope.get("authority_profile_id") != statement["authority_profile_id"]:
                continue
        else:
            if scope.get("claim_namespace") != statement["claim_namespace"]:
                continue
        return True
    return False


@dataclass
class ReceiptState:
    kind: str
    receipt: dict[str, Any]
    statement: dict[str, Any] | None = None
    canonical: bytes | None = None
    public_key: bytes | None = None


def _parse_receipt(raw: bytes | str, kind: str) -> tuple[ReceiptState | None, dict[str, str] | None]:
    try:
        obj = _parse_json(raw)
    except DuplicateKeyError:
        return None, _refuse("DUPLICATE_JSON_KEY")
    except JSONSyntaxError:
        return None, _refuse("INVALID_JSON")
    if not isinstance(obj, dict):
        return None, _refuse("INVALID_RECEIPT_SCHEMA")
    return ReceiptState(kind=kind, receipt=obj), None


def _schema_stage(state: ReceiptState) -> dict[str, str] | None:
    try:
        _validate_receipt_schema(state.receipt, state.kind)
    except UnsupportedProfileError:
        return _refuse("UNSUPPORTED_PROFILE")
    except SchemaError:
        return _refuse("INVALID_RECEIPT_SCHEMA")
    state.statement = state.receipt["statement"]
    return None


def _canonical_stage(state: ReceiptState) -> dict[str, str] | None:
    try:
        state.canonical = jcs_canonicalize(state.statement)
    except Exception:
        return _refuse("INVALID_RECEIPT_SCHEMA")
    return None


def _digest_stage(state: ReceiptState) -> dict[str, str] | None:
    assert state.canonical is not None
    digest = hashlib.sha256(state.canonical).hexdigest()
    if digest != state.receipt["statement_digest_sha256"]:
        return _refuse("STATEMENT_DIGEST_MISMATCH")
    return None


def _key_lookup_stage(state: ReceiptState, public_keys: dict[str, bytes]) -> dict[str, str] | None:
    assert state.statement is not None
    key = public_keys.get(state.statement["issuer_key_id"])
    if key is None:
        return _refuse("UNKNOWN_SIGNER")
    state.public_key = key
    return None


def _signature_stage(state: ReceiptState) -> dict[str, str] | None:
    assert state.public_key is not None and state.canonical is not None
    signature_text = state.receipt["signature_base64url"]
    try:
        signature = _decode_base64url_no_padding(signature_text, 64)
    except ValueError:
        return _refuse("SIGNATURE_INVALID_FORMAT")
    try:
        Ed25519PublicKey.from_public_bytes(state.public_key).verify(signature, state.canonical)
    except (InvalidSignature, ValueError):
        return _refuse("SIGNATURE_INVALID")
    return None


def _policy_stage(state: ReceiptState, authorizations: list[dict[str, Any]]) -> dict[str, str] | None:
    assert state.statement is not None
    if not _authorized(state.statement, authorizations, state.kind):
        return _refuse("UNAUTHORIZED_ISSUER_SCOPE")
    return None


def _binding_stage(state: ReceiptState, semantic: dict[str, Any]) -> dict[str, str] | None:
    assert state.statement is not None
    if state.kind == "atom":
        expected = derive_atom_projection(semantic)
        authority_case = semantic["authority_case"]
        if state.statement["atom_projection"] != expected:
            return _refuse("ATOM_BINDING_MISMATCH")
        if state.statement["claim_id"] != authority_case["raw_claim_id"]:
            return _refuse("ATOM_BINDING_MISMATCH")
        if state.statement["atom_id"] != authority_case["target_atom_id"]:
            return _refuse("ATOM_BINDING_MISMATCH")
    else:
        expected = derive_proposition_projection(semantic)
        proposition = semantic["proposition"]
        if state.statement["proposition_projection"] != expected:
            return _refuse("PROPOSITION_BINDING_MISMATCH")
        if state.statement["claim_id"] != proposition["claim_id"]:
            return _refuse("PROPOSITION_BINDING_MISMATCH")
    return None


def _parse_and_validate_support_inputs(
    semantic_json: bytes | str,
    public_keys_json: bytes | str,
    trust_policy_json: bytes | str,
) -> tuple[dict[str, Any] | None, dict[str, bytes] | None, list[dict[str, Any]] | None, dict[str, str] | None]:
    parsed: list[Any] = []
    for raw in (semantic_json, public_keys_json, trust_policy_json):
        try:
            parsed.append(_parse_json(raw))
        except DuplicateKeyError:
            return None, None, None, _refuse("DUPLICATE_JSON_KEY")
        except JSONSyntaxError:
            return None, None, None, _refuse("INVALID_INPUT")
    semantic, public_key_obj, trust_policy_obj = parsed
    try:
        _validate_semantic_request(semantic)
        public_keys = _load_public_keys(public_key_obj)
        authorizations = _load_trust_policy(trust_policy_obj)
    except InvalidInputError:
        return None, None, None, _refuse("INVALID_INPUT")
    return semantic, public_keys, authorizations, None


def verify_pair(
    semantic_json: bytes | str,
    atom_receipt_json: bytes | str,
    proposition_receipt_json: bytes | str,
    public_keys_json: bytes | str,
    trust_policy_json: bytes | str,
) -> dict[str, Any]:
    """Verify the frozen two-receipt pair and return the typed result object."""
    atom, error = _parse_receipt(atom_receipt_json, "atom")
    if error:
        return error
    prop, error = _parse_receipt(proposition_receipt_json, "proposition")
    if error:
        return error
    assert atom is not None and prop is not None

    semantic, public_keys, authorizations, error = _parse_and_validate_support_inputs(
        semantic_json, public_keys_json, trust_policy_json
    )
    if error:
        return error
    assert semantic is not None and public_keys is not None and authorizations is not None

    # Apply the receipt stages globally in specification order. Within one stage,
    # the atom slot is checked before the proposition slot for deterministic ties.
    stages: tuple[Callable[[ReceiptState], dict[str, str] | None], ...] = (
        _schema_stage,
        _canonical_stage,
        _digest_stage,
    )
    for stage in stages:
        for state in (atom, prop):
            error = stage(state)
            if error:
                return error

    for state in (atom, prop):
        error = _key_lookup_stage(state, public_keys)
        if error:
            return error
    for state in (atom, prop):
        error = _signature_stage(state)
        if error:
            return error
    for state in (atom, prop):
        error = _policy_stage(state, authorizations)
        if error:
            return error
    for state in (atom, prop):
        error = _binding_stage(state, semantic)
        if error:
            return error

    assert atom.statement is not None and prop.statement is not None
    if semantic["context_id"] != CONTEXT_ID:
        return _refuse("PAIR_CONTEXT_MISMATCH")
    if atom.statement["context_id"] != semantic["context_id"]:
        return _refuse("PAIR_CONTEXT_MISMATCH")
    if prop.statement["context_id"] != semantic["context_id"]:
        return _refuse("PAIR_CONTEXT_MISMATCH")

    claim_ids = {
        atom.statement["claim_id"],
        prop.statement["claim_id"],
        semantic["proposition"]["claim_id"],
        semantic["authority_case"]["raw_claim_id"],
    }
    if len(claim_ids) != 1:
        return _refuse("PAIR_CLAIM_MISMATCH")

    return {
        "decision": "ACCEPT",
        "code": "ACCEPT",
        "claim_id": prop.statement["claim_id"],
        "atom_id": atom.statement["atom_id"],
    }


def _verify_single(
    kind: str,
    semantic_json: bytes | str,
    receipt_json: bytes | str,
    public_keys_json: bytes | str,
    trust_policy_json: bytes | str,
) -> dict[str, Any]:
    state, error = _parse_receipt(receipt_json, kind)
    if error:
        return error
    assert state is not None
    semantic, public_keys, authorizations, error = _parse_and_validate_support_inputs(
        semantic_json, public_keys_json, trust_policy_json
    )
    if error:
        return error
    assert semantic is not None and public_keys is not None and authorizations is not None
    for stage in (_schema_stage, _canonical_stage, _digest_stage):
        error = stage(state)
        if error:
            return error
    error = _key_lookup_stage(state, public_keys)
    if error:
        return error
    error = _signature_stage(state)
    if error:
        return error
    error = _policy_stage(state, authorizations)
    if error:
        return error
    error = _binding_stage(state, semantic)
    if error:
        return error
    assert state.statement is not None
    result: dict[str, Any] = {"decision": "ACCEPT", "code": "ACCEPT", "claim_id": state.statement["claim_id"]}
    if kind == "atom":
        result["atom_id"] = state.statement["atom_id"]
    return result


def verify_atom_receipt(
    semantic_json: bytes | str,
    atom_receipt_json: bytes | str,
    public_keys_json: bytes | str,
    trust_policy_json: bytes | str,
) -> dict[str, Any]:
    return _verify_single("atom", semantic_json, atom_receipt_json, public_keys_json, trust_policy_json)


def verify_proposition_receipt(
    semantic_json: bytes | str,
    proposition_receipt_json: bytes | str,
    public_keys_json: bytes | str,
    trust_policy_json: bytes | str,
) -> dict[str, Any]:
    return _verify_single("proposition", semantic_json, proposition_receipt_json, public_keys_json, trust_policy_json)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a frozen CAL RC5 atom/proposition receipt pair")
    parser.add_argument("semantic_json")
    parser.add_argument("atom_receipt_json")
    parser.add_argument("proposition_receipt_json")
    parser.add_argument("public_keys_json")
    parser.add_argument("trust_policy_json")
    args = parser.parse_args(argv)
    try:
        payloads = [open(path, "rb").read() for path in (
            args.semantic_json,
            args.atom_receipt_json,
            args.proposition_receipt_json,
            args.public_keys_json,
            args.trust_policy_json,
        )]
    except OSError:
        print(json.dumps(_refuse("INVALID_INPUT"), separators=(",", ":")))
        return 2
    result = verify_pair(*payloads)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["decision"] == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main())
