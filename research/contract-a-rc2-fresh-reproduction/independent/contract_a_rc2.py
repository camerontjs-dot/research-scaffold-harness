"""Independent Contract A RC2 consumer derived only from the frozen public SPEC/schema."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

SCHEMA_NAME = "contract-a-wire-candidate-rc2"
_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_NONBLANK_RE = re.compile(r".*\S.*", re.DOTALL)
_MEDIA_TYPES = {
    "text/plain; charset=utf-8",
    "text/markdown; charset=utf-8",
}


class ContractAValidationError(ValueError):
    """The candidate is not mechanically valid Contract A RC2 state."""


@dataclass(frozen=True)
class ContractA:
    """Validated payload wrapper. The payload is a defensive deep copy."""

    payload: dict[str, Any]

    def retrieval_targets(self) -> list[dict[str, Any]]:
        return retrieval_targets(self.payload)

    def source_contract_projection(self) -> dict[str, Any]:
        return source_contract_projection(self.payload)

    def supplied_sources(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self.payload["sources"])


def _fail(message: str) -> None:
    raise ContractAValidationError(message)


def _expect_object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{path} must be an object")
    return value


def _expect_exact_keys(value: Mapping[str, Any], required: set[str], path: str) -> None:
    keys = set(value.keys())
    missing = required - keys
    extra = keys - required
    if missing:
        _fail(f"{path} missing required field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(f"{path} contains unknown field(s): {', '.join(sorted(extra))}")


def _expect_nonblank(value: Any, path: str) -> str:
    if not isinstance(value, str) or _NONBLANK_RE.fullmatch(value) is None:
        _fail(f"{path} must be a non-blank string")
    return value


def _expect_hash_shape(value: Any, path: str) -> str:
    if not isinstance(value, str) or _HASH_RE.fullmatch(value) is None:
        _fail(f"{path} must be sha256:<64 lowercase hex>")
    return value


def sha256_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_proposition(value: Any, path: str, *, child: bool = False) -> None:
    obj = _expect_object(value, path)
    required = {"proposition_id", "text", "text_sha256"}
    if child:
        required.add("sequence")
    _expect_exact_keys(obj, required, path)
    _expect_nonblank(obj["proposition_id"], f"{path}.proposition_id")
    text = _expect_nonblank(obj["text"], f"{path}.text")
    supplied_hash = _expect_hash_shape(obj["text_sha256"], f"{path}.text_sha256")
    expected_hash = sha256_text(text)
    if supplied_hash != expected_hash:
        _fail(f"{path}.text_sha256 does not match UTF-8 proposition text")
    if child:
        sequence = obj["sequence"]
        if type(sequence) is not int or sequence < 1:
            _fail(f"{path}.sequence must be an integer >= 1")


def _validate_decomposition(value: Any, root_id: str) -> None:
    obj = _expect_object(value, "decomposition")
    if "state" not in obj:
        _fail("decomposition missing required field: state")
    state = obj["state"]
    if state in {"not_decomposed", "failed", "unknown"}:
        _expect_exact_keys(obj, {"state"}, "decomposition")
        return
    if state != "declared":
        _fail("decomposition.state must be not_decomposed, failed, unknown, or declared")

    _expect_exact_keys(
        obj,
        {"state", "decomposition_id", "operator", "children"},
        "decomposition",
    )
    _expect_nonblank(obj["decomposition_id"], "decomposition.decomposition_id")
    if obj["operator"] != "all_of":
        _fail("decomposition.operator must be all_of")
    children = obj["children"]
    if not isinstance(children, list):
        _fail("decomposition.children must be an array")
    if len(children) < 2:
        _fail("declared all_of decomposition requires at least two children")

    ids: set[str] = set()
    texts: set[str] = set()
    sequences: set[int] = set()
    for index, child in enumerate(children, start=1):
        path = f"decomposition.children[{index - 1}]"
        _validate_proposition(child, path, child=True)
        child_id = child["proposition_id"]
        text = child["text"]
        sequence = child["sequence"]
        if child_id == root_id:
            _fail(f"{path}.proposition_id may not equal root proposition_id")
        if child_id in ids:
            _fail("declared child proposition_id values must be unique")
        if text in texts:
            _fail("declared child text values must be unique")
        if sequence in sequences:
            _fail("declared child sequence values must be unique")
        if sequence != index:
            _fail("declared child sequence must be contiguous 1..N in list order")
        ids.add(child_id)
        texts.add(text)
        sequences.add(sequence)


def _validate_sources(value: Any) -> None:
    if not isinstance(value, list):
        _fail("sources must be an array")
    ids: set[str] = set()
    for index, source in enumerate(value):
        path = f"sources[{index}]"
        obj = _expect_object(source, path)
        _expect_exact_keys(
            obj,
            {"source_id", "media_type", "content", "content_sha256"},
            path,
        )
        source_id = _expect_nonblank(obj["source_id"], f"{path}.source_id")
        if source_id in ids:
            _fail("source_id values must be unique")
        ids.add(source_id)
        if obj["media_type"] not in _MEDIA_TYPES:
            _fail(f"{path}.media_type is not an allowed UTF-8 text representation")
        content = obj["content"]
        if not isinstance(content, str):
            _fail(f"{path}.content must be a string")
        supplied_hash = _expect_hash_shape(obj["content_sha256"], f"{path}.content_sha256")
        if supplied_hash != sha256_text(content):
            _fail(f"{path}.content_sha256 does not match UTF-8 source content")


def canonical_handoff_bytes(candidate: Mapping[str, Any]) -> bytes:
    """Serialize the bound payload used by handoff_sha256.

    Prereveal interpretation: emit non-ASCII characters directly and encode the
    resulting JSON as UTF-8 (ensure_ascii=False). See AMBIGUITIES.md.
    """
    obj = copy.deepcopy(dict(candidate))
    obj.pop("handoff_sha256", None)
    try:
        serialized = json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        _fail(f"candidate cannot be serialized for handoff integrity: {exc}")
    return serialized.encode("utf-8")


def compute_handoff_sha256(candidate: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_handoff_bytes(candidate)).hexdigest()


def validate_candidate(candidate: Any) -> None:
    obj = _expect_object(candidate, "$")
    required = {
        "schema",
        "handoff_id",
        "producer",
        "work",
        "root_proposition",
        "decomposition",
        "sources",
        "handoff_sha256",
    }
    _expect_exact_keys(obj, required, "$")
    if obj["schema"] != SCHEMA_NAME:
        _fail(f"schema must be {SCHEMA_NAME}")
    _expect_nonblank(obj["handoff_id"], "handoff_id")

    producer = _expect_object(obj["producer"], "producer")
    _expect_exact_keys(producer, {"producer_id", "producer_version"}, "producer")
    _expect_nonblank(producer["producer_id"], "producer.producer_id")
    _expect_nonblank(producer["producer_version"], "producer.producer_version")

    work = _expect_object(obj["work"], "work")
    _expect_exact_keys(work, {"work_id"}, "work")
    _expect_nonblank(work["work_id"], "work.work_id")

    _validate_proposition(obj["root_proposition"], "root_proposition")
    root_id = obj["root_proposition"]["proposition_id"]
    _validate_decomposition(obj["decomposition"], root_id)
    _validate_sources(obj["sources"])

    supplied_handoff_hash = _expect_hash_shape(obj["handoff_sha256"], "handoff_sha256")
    expected_handoff_hash = compute_handoff_sha256(obj)
    if supplied_handoff_hash != expected_handoff_hash:
        _fail("handoff_sha256 does not match canonical bound candidate payload")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ContractAValidationError(f"duplicate JSON object member: {key}")
        out[key] = value
    return out


def _reject_nonfinite(token: str) -> None:
    raise ContractAValidationError(f"non-JSON numeric constant is not allowed: {token}")


def parse_json(data: str | bytes | bytearray) -> ContractA:
    """Parse JSON without lossy duplicate-key behavior, validate, and preserve values."""
    if isinstance(data, (bytes, bytearray)):
        try:
            data = bytes(data).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContractAValidationError("input bytes must be UTF-8 JSON") from exc
    if not isinstance(data, str):
        raise TypeError("data must be str, bytes, or bytearray")
    try:
        value = json.loads(
            data,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except ContractAValidationError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractAValidationError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        _fail("top-level JSON value must be an object")
    validate_candidate(value)
    return ContractA(copy.deepcopy(value))


def retrieval_targets(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return exact proposition targets implied by the declared decomposition state."""
    validate_candidate(candidate)
    root = candidate["root_proposition"]
    decomposition = candidate["decomposition"]
    state = decomposition["state"]
    if state != "declared":
        return [
            {
                "proposition_id": root["proposition_id"],
                "text": root["text"],
                "text_sha256": root["text_sha256"],
                "decomposition_state": state,
            }
        ]
    return [
        {
            "proposition_id": child["proposition_id"],
            "text": child["text"],
            "text_sha256": child["text_sha256"],
            "decomposition_state": "declared",
            "decomposition_id": decomposition["decomposition_id"],
            "operator": "all_of",
            "sequence": child["sequence"],
            "root_proposition_id": root["proposition_id"],
        }
        for child in decomposition["children"]
    ]


def source_contract_projection(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Mechanical downstream proposition projection with no added semantic authority.

    The projection field names are local adapter API, not a Contract A wire extension.
    Existing Contract A identifiers, hashes, texts, order, and state are copied only.
    """
    validate_candidate(candidate)
    root = candidate["root_proposition"]
    decomposition = candidate["decomposition"]
    state = decomposition["state"]
    if state == "declared":
        reference_id = decomposition["decomposition_id"]
        operator = "all_of"
        atoms = [
            {
                "proposition_id": child["proposition_id"],
                "text": child["text"],
                "text_sha256": child["text_sha256"],
                "sequence": child["sequence"],
            }
            for child in decomposition["children"]
        ]
    else:
        reference_id = candidate["handoff_id"]
        operator = "single"
        atoms = [
            {
                "proposition_id": root["proposition_id"],
                "text": root["text"],
                "text_sha256": root["text_sha256"],
            }
        ]

    return {
        "origin": "source_contract",
        "reference_id": reference_id,
        "reference_sha256": candidate["handoff_sha256"],
        "decomposition_state": state,
        "root_proposition": copy.deepcopy(root),
        "operator": operator,
        "atoms": atoms,
    }
