"""Research-only point-of-use shadow enforcement candidate for Contract E envelope RC0.

This module performs no target mutation. It exists only to test ordering/binding
properties preregistered under research/contract_e_production_envelope_shadow_rc0.
"""

from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Callable

INTENT_SCHEMA = "cal-production-envelope-shadow-intent-rc0"
DISPOSABLE_MARKER = ".contract-e-shadow-rc0-disposable"
DISPOSABLE_MARKER_BYTES = b"CONTRACT_E_SHADOW_RC0_DISPOSABLE\n"
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

INTENT_KEYS = {
    "schema",
    "intent_id",
    "contract_d_sha256",
    "effect_id",
    "effect_version",
    "effect_params",
    "contract_d_target_kind",
    "contract_d_target_id",
    "target_root_id",
    "target_relative_path",
    "target_pre_state_sha256",
    "idempotency_key",
}


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _base_result() -> dict[str, Any]:
    return {
        "schema": "cal-production-envelope-shadow-decision-rc0",
        "shadow_allowed": False,
        "execution_occurred": False,
        "intent_id": None,
        "contract_d_sha256": None,
        "decision_identity": None,
        "target_sha256_before_authorization": None,
        "target_sha256_after_authorization": None,
        "contract_e_reference_authorized": None,
        "contract_e_independent_authorized": None,
        "idempotency_state": "not_checked",
        "failures": [],
        "diagnostics": [],
    }


def _deny(result: dict[str, Any], code: str, diagnostic: str | None = None) -> dict[str, Any]:
    if code not in result["failures"]:
        result["failures"].append(code)
    if diagnostic:
        result["diagnostics"].append(diagnostic)
    return result


def _intent_identity(intent: Any, canonical_bytes: Callable[[Any], bytes]) -> str | None:
    if not isinstance(intent, dict):
        return None
    try:
        payload = {key: copy.deepcopy(value) for key, value in intent.items() if key != "intent_id"}
        return _sha256_bytes(canonical_bytes(payload))
    except Exception:
        return None


def _validate_intent(
    intent: Any,
    *,
    canonical_bytes: Callable[[Any], bytes],
) -> tuple[bool, str | None]:
    if not isinstance(intent, dict) or set(intent) != INTENT_KEYS:
        return False, None
    if intent.get("schema") != INTENT_SCHEMA:
        return False, None
    scalar_fields = (
        "intent_id",
        "contract_d_sha256",
        "effect_id",
        "effect_version",
        "contract_d_target_kind",
        "contract_d_target_id",
        "target_root_id",
        "target_relative_path",
        "target_pre_state_sha256",
        "idempotency_key",
    )
    if not all(_nonempty_string(intent.get(key)) for key in scalar_fields):
        return False, None
    if not _is_sha256(intent["intent_id"]):
        return False, None
    if not _is_sha256(intent["contract_d_sha256"]):
        return False, None
    if not _is_sha256(intent["target_pre_state_sha256"]):
        return False, None
    if intent["effect_id"] != "knowledge.add_verified_tag" or intent["effect_version"] != "1":
        return False, None
    if intent["effect_params"] != {"scope": "claim"}:
        return False, None
    computed = _intent_identity(intent, canonical_bytes)
    return computed is not None and computed == intent["intent_id"], computed


def _normalized_relative_path(value: str) -> PurePosixPath | None:
    if "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts:
        return None
    if any(part in {"", ".", ".."} for part in path.parts):
        return None
    if str(path) != value:
        return None
    return path


def _within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _read_fd_bytes(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def _same_file(a: os.stat_result, b: os.stat_result) -> bool:
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def _receipt_projection(receipt: Any) -> Any:
    if not isinstance(receipt, dict):
        return receipt
    return {key: copy.deepcopy(value) for key, value in receipt.items() if key != "diagnostics"}


def _verify_request_binds_intent(
    request: Any,
    intent_id: str,
    reference_identity: Callable[[str, str | None, str], str],
) -> bool:
    if not isinstance(request, dict):
        return False
    refs = request.get("references")
    jurisdiction = request.get("jurisdiction")
    if not isinstance(refs, list) or len(refs) != 1 or not isinstance(jurisdiction, dict):
        return False
    ref = refs[0]
    if not isinstance(ref, dict):
        return False
    expected_identity = reference_identity("cal.shadow-execution-intent", "rc0", intent_id)
    return (
        ref.get("kind") == "cal.shadow-execution-intent"
        and ref.get("version") == "rc0"
        and ref.get("immutable_id") == intent_id
        and ref.get("identity_sha256") == expected_identity
        and jurisdiction.get("target_ref") == expected_identity
    )


def _reserve_idempotency(
    journal_path: Path,
    *,
    root: Path,
    idempotency_key: str,
    intent_id: str,
) -> tuple[bool, str]:
    parent = journal_path.parent.resolve(strict=True)
    if not _within_root(parent, root):
        return False, "journal_outside_root"

    flags = os.O_CREAT | os.O_RDWR
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(journal_path, flags | nofollow, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        raw = _read_fd_bytes(fd)
        entries: list[dict[str, Any]] = []
        if raw:
            try:
                for line in raw.decode("utf-8").splitlines():
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if not isinstance(entry, dict):
                        return False, "journal_malformed"
                    entries.append(entry)
            except Exception:
                return False, "journal_malformed"
        if any(entry.get("idempotency_key") == idempotency_key for entry in entries):
            return False, "replayed"

        record = {
            "schema": "cal-production-envelope-shadow-journal-entry-rc0",
            "idempotency_key": idempotency_key,
            "intent_id": intent_id,
        }
        encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        os.lseek(fd, 0, os.SEEK_END)
        os.write(fd, encoded)
        os.fsync(fd)
        return True, "reserved"
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def shadow_evaluate(
    *,
    contract_d_bytes: bytes,
    applicability_expectation: Any,
    intent: Any,
    target_root: str | Path,
    authority_state: Any,
    authorization_request: Any,
    journal_path: str | Path,
    contract_d_require_canonical_bytes: Callable[[bytes], dict[str, Any]],
    contract_d_consume: Callable[[Any, Any], dict[str, Any]],
    contract_d_validate_effect: Callable[[Any], dict[str, Any]],
    contract_e_reference_evaluate: Callable[[Any, Any], dict[str, Any]],
    contract_e_independent_evaluate: Callable[[Any, Any], dict[str, Any]],
    intent_canonical_bytes: Callable[[Any], bytes],
    contract_e_reference_identity: Callable[[str, str | None, str], str],
    historical_receipt: Any = None,
    research_after_authorization_hook: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Return a research-only shadow point-of-use decision.

    ``historical_receipt`` is accepted only so receipt-as-permit negative cases can
    prove it is inert. It is deliberately never consulted for authorization.
    """

    del historical_receipt
    result = _base_result()

    valid_intent, computed_intent_id = _validate_intent(intent, canonical_bytes=intent_canonical_bytes)
    if not valid_intent:
        return _deny(result, "invalid_or_forged_intent")
    assert computed_intent_id is not None
    result["intent_id"] = computed_intent_id

    if not isinstance(contract_d_bytes, bytes):
        return _deny(result, "invalid_contract_d_bytes")
    observed_contract_d_sha = _sha256_bytes(contract_d_bytes)
    result["contract_d_sha256"] = observed_contract_d_sha
    if intent["contract_d_sha256"] != observed_contract_d_sha:
        return _deny(result, "contract_d_digest_mismatch")

    try:
        decision = contract_d_require_canonical_bytes(contract_d_bytes)
    except Exception as exc:
        return _deny(result, "contract_d_invalid", type(exc).__name__)

    try:
        applicability = contract_d_consume(decision, applicability_expectation)
    except Exception as exc:
        return _deny(result, "contract_d_consumer_error", type(exc).__name__)
    if isinstance(applicability, dict):
        result["decision_identity"] = applicability.get("decision_identity")
    if not isinstance(applicability, dict) or applicability.get("outcome") != "candidate_for_authorization":
        reason = applicability.get("outcome") if isinstance(applicability, dict) else "invalid_result"
        return _deny(result, "contract_d_not_candidate_for_authorization", str(reason))

    try:
        effect = contract_d_validate_effect(decision.get("effect"))
    except Exception as exc:
        return _deny(result, "contract_d_effect_invalid", type(exc).__name__)

    target = decision.get("target")
    if not isinstance(target, dict):
        return _deny(result, "contract_d_target_invalid")
    if (
        effect.get("type") != intent["effect_id"]
        or effect.get("version") != intent["effect_version"]
        or effect.get("params") != intent["effect_params"]
    ):
        return _deny(result, "contract_d_effect_intent_mismatch")
    if (
        target.get("kind") != intent["contract_d_target_kind"]
        or target.get("id") != intent["contract_d_target_id"]
        or target.get("content_sha256") != intent["target_pre_state_sha256"]
    ):
        return _deny(result, "contract_d_target_intent_mismatch")

    try:
        if not _verify_request_binds_intent(
            authorization_request, intent["intent_id"], contract_e_reference_identity
        ):
            return _deny(result, "authorization_request_intent_mismatch")
    except Exception as exc:
        return _deny(result, "authorization_request_intent_binding_error", type(exc).__name__)

    try:
        root = Path(target_root).resolve(strict=True)
    except Exception as exc:
        return _deny(result, "invalid_target_root", type(exc).__name__)
    marker = root / DISPOSABLE_MARKER
    try:
        if not marker.is_file() or marker.read_bytes() != DISPOSABLE_MARKER_BYTES:
            return _deny(result, "non_disposable_root")
    except Exception as exc:
        return _deny(result, "non_disposable_root", type(exc).__name__)

    rel = _normalized_relative_path(intent["target_relative_path"])
    if rel is None:
        return _deny(result, "invalid_target_relative_path")

    unresolved_target = root.joinpath(*rel.parts)
    try:
        resolved_target = unresolved_target.resolve(strict=True)
    except Exception as exc:
        return _deny(result, "target_resolution_failed", type(exc).__name__)
    if not _within_root(resolved_target, root):
        return _deny(result, "target_outside_disposable_root")
    if not resolved_target.is_file():
        return _deny(result, "target_not_regular_file")

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(resolved_target, os.O_RDONLY | nofollow)
    except Exception as exc:
        return _deny(result, "target_open_failed", type(exc).__name__)

    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        locked_stat = os.fstat(fd)

        try:
            rereso = unresolved_target.resolve(strict=True)
            current_stat = os.stat(rereso, follow_symlinks=False)
        except Exception as exc:
            return _deny(result, "target_reresolution_failed", type(exc).__name__)
        if rereso != resolved_target or not _same_file(locked_stat, current_stat):
            return _deny(result, "target_identity_changed_before_authorization")

        before = _sha256_bytes(_read_fd_bytes(fd))
        result["target_sha256_before_authorization"] = before
        if before != intent["target_pre_state_sha256"]:
            return _deny(result, "target_prestate_mismatch")

        try:
            ref_receipt = contract_e_reference_evaluate(authority_state, authorization_request)
            result["contract_e_reference_authorized"] = (
                ref_receipt.get("authorized") if isinstance(ref_receipt, dict) else None
            )
        except Exception as exc:
            return _deny(result, "contract_e_reference_error", type(exc).__name__)

        try:
            independent_receipt = contract_e_independent_evaluate(authority_state, authorization_request)
            result["contract_e_independent_authorized"] = (
                independent_receipt.get("authorized") if isinstance(independent_receipt, dict) else None
            )
        except Exception as exc:
            return _deny(result, "contract_e_independent_error", type(exc).__name__)

        if _receipt_projection(ref_receipt) != _receipt_projection(independent_receipt):
            return _deny(result, "contract_e_normative_disagreement")
        if result["contract_e_reference_authorized"] is not True:
            return _deny(result, "contract_e_denied")

        if research_after_authorization_hook is not None:
            research_after_authorization_hook(unresolved_target)

        try:
            post_resolved = unresolved_target.resolve(strict=True)
            post_stat = os.stat(post_resolved, follow_symlinks=False)
        except Exception as exc:
            return _deny(result, "target_post_authorization_resolution_failed", type(exc).__name__)
        if post_resolved != resolved_target or not _same_file(locked_stat, post_stat):
            return _deny(result, "target_identity_changed_after_authorization")

        try:
            post_fd = os.open(post_resolved, os.O_RDONLY | nofollow)
        except Exception as exc:
            return _deny(result, "target_post_authorization_open_failed", type(exc).__name__)
        try:
            after = _sha256_bytes(_read_fd_bytes(post_fd))
        finally:
            os.close(post_fd)
        result["target_sha256_after_authorization"] = after
        if after != before:
            return _deny(result, "target_content_changed_after_authorization")

        ok, state = _reserve_idempotency(
            Path(journal_path),
            root=root,
            idempotency_key=intent["idempotency_key"],
            intent_id=intent["intent_id"],
        )
        result["idempotency_state"] = state
        if not ok:
            return _deny(result, "idempotency_replay_or_journal_failure", state)

        result["shadow_allowed"] = True
        return result
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
