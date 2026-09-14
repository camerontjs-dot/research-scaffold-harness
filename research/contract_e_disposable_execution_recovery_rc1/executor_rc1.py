"""Research-only disposable execution/recovery candidate for Contract E envelope RC1.

The candidate performs one exact byte replacement only inside an explicitly
marked disposable root. It does not implement knowledge-tag semantics.
"""

from __future__ import annotations

import base64
import copy
import fcntl
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable

PLAN_SCHEMA = "cal-disposable-execution-plan-rc1"
MARKER_NAME = ".contract-e-execution-rc1-disposable"
MARKER_BYTES = b"CONTRACT_E_EXECUTION_RC1_DISPOSABLE\n"
EVENT_SCHEMA = "cal-disposable-execution-journal-event-rc1"
GENESIS = "0" * 64
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

PLAN_KEYS = {
    "schema",
    "operation_id",
    "contract_d_sha256",
    "contract_d_target_kind",
    "contract_d_target_id",
    "effect_id",
    "effect_version",
    "effect_params",
    "target_root_id",
    "target_relative_path",
    "expected_pre_sha256",
    "expected_post_sha256",
    "post_bytes_b64",
    "authorization_subject_id",
    "authorization_domain",
    "authorization_operation",
    "authorization_scope",
    "authorization_target_class",
}


class InjectedInterruption(RuntimeError):
    """Research failpoint used to simulate interruption after a durable phase."""


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _plan_identity(plan: Any, canonical_bytes: Callable[[Any], bytes]) -> str | None:
    if not isinstance(plan, dict):
        return None
    try:
        payload = {k: copy.deepcopy(v) for k, v in plan.items() if k != "operation_id"}
        return _sha256_bytes(canonical_bytes(payload))
    except Exception:
        return None


def _decode_post_bytes(value: Any) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except Exception:
        return None


def _validate_plan(
    plan: Any,
    canonical_bytes: Callable[[Any], bytes],
) -> tuple[bool, str | None, bytes | None]:
    if not isinstance(plan, dict) or set(plan) != PLAN_KEYS:
        return False, None, None
    if plan.get("schema") != PLAN_SCHEMA:
        return False, None, None
    strings = (
        "operation_id",
        "contract_d_sha256",
        "contract_d_target_kind",
        "contract_d_target_id",
        "effect_id",
        "effect_version",
        "target_root_id",
        "target_relative_path",
        "expected_pre_sha256",
        "expected_post_sha256",
        "post_bytes_b64",
        "authorization_subject_id",
        "authorization_domain",
        "authorization_operation",
        "authorization_scope",
        "authorization_target_class",
    )
    if not all(_nonempty(plan.get(k)) for k in strings):
        return False, None, None
    if not all(_sha(plan.get(k)) for k in ("operation_id", "contract_d_sha256", "expected_pre_sha256", "expected_post_sha256")):
        return False, None, None
    if plan["effect_id"] != "knowledge.add_verified_tag" or plan["effect_version"] != "1":
        return False, None, None
    if plan["effect_params"] != {"scope": "claim"}:
        return False, None, None
    if plan["authorization_operation"] != "knowledge.add_verified_tag":
        return False, None, None
    if plan["authorization_target_class"] != "cal.disposable-execution-plan":
        return False, None, None
    post_bytes = _decode_post_bytes(plan["post_bytes_b64"])
    if post_bytes is None or _sha256_bytes(post_bytes) != plan["expected_post_sha256"]:
        return False, None, None
    computed = _plan_identity(plan, canonical_bytes)
    return computed is not None and computed == plan["operation_id"], computed, post_bytes


def _relative_path(value: str) -> PurePosixPath | None:
    if "\\" in value:
        return None
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(part in {"", ".", ".."} for part in p.parts):
        return None
    if str(p) != value:
        return None
    return p


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _read_fd(fd: int) -> bytes:
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


def _event_hash(event_without_hash: dict[str, Any]) -> str:
    encoded = json.dumps(event_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_journal(fd: int, operation_id: str) -> tuple[list[dict[str, Any]], str | None]:
    raw = _read_fd(fd)
    if not raw:
        return [], None
    events: list[dict[str, Any]] = []
    prev = GENESIS
    try:
        for index, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                return [], "journal_non_object"
            if event.get("schema") != EVENT_SCHEMA or event.get("operation_id") != operation_id:
                return [], "journal_identity_mismatch"
            if event.get("sequence") != index:
                return [], "journal_sequence_invalid"
            if event.get("prev_event_sha256") != prev:
                return [], "journal_chain_invalid"
            claimed = event.get("event_sha256")
            if not isinstance(claimed, str) or not re.fullmatch(r"[0-9a-f]{64}", claimed):
                return [], "journal_event_hash_invalid"
            body = {k: copy.deepcopy(v) for k, v in event.items() if k != "event_sha256"}
            computed = _event_hash(body)
            if computed != claimed:
                return [], "journal_event_hash_mismatch"
            prev = claimed
            events.append(event)
    except Exception:
        return [], "journal_parse_error"
    return events, None


def _append_event(
    fd: int,
    events: list[dict[str, Any]],
    *,
    operation_id: str,
    event_type: str,
    target_sha256: str | None,
    authorization_receipt_id: str | None = None,
    execution_attribution: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    prev = events[-1]["event_sha256"] if events else GENESIS
    event = {
        "schema": EVENT_SCHEMA,
        "operation_id": operation_id,
        "sequence": len(events) + 1,
        "event_type": event_type,
        "target_sha256": target_sha256,
        "authorization_receipt_id": authorization_receipt_id,
        "authority_conferring": False,
        "execution_attribution": execution_attribution,
        "reason": reason,
        "prev_event_sha256": prev,
    }
    event["event_sha256"] = _event_hash(event)
    encoded = (json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    os.lseek(fd, 0, os.SEEK_END)
    os.write(fd, encoded)
    os.fsync(fd)
    events.append(event)
    return event


def _request_binds_plan(
    request: Any,
    plan: dict[str, Any],
    reference_identity: Callable[[str, str | None, str], str],
) -> bool:
    if not isinstance(request, dict):
        return False
    refs = request.get("references")
    jur = request.get("jurisdiction")
    if not isinstance(refs, list) or len(refs) != 1 or not isinstance(jur, dict):
        return False
    ref = refs[0]
    if not isinstance(ref, dict):
        return False
    expected = reference_identity("cal.disposable-execution-plan", "rc1", plan["operation_id"])
    return (
        ref.get("kind") == "cal.disposable-execution-plan"
        and ref.get("version") == "rc1"
        and ref.get("immutable_id") == plan["operation_id"]
        and ref.get("identity_sha256") == expected
        and jur.get("target_ref") == expected
        and request.get("subject_id") == plan["authorization_subject_id"]
        and jur.get("domain") == plan["authorization_domain"]
        and jur.get("operation") == plan["authorization_operation"]
        and jur.get("scope") == plan["authorization_scope"]
        and jur.get("target_class") == plan["authorization_target_class"]
    )


def _receipt_projection(receipt: Any) -> Any:
    if not isinstance(receipt, dict):
        return receipt
    return {k: copy.deepcopy(v) for k, v in receipt.items() if k != "diagnostics"}


def _fresh_authorize(
    *,
    authority_state: Any,
    request: Any,
    ref_eval: Callable[[Any, Any], dict[str, Any]],
    ind_eval: Callable[[Any, Any], dict[str, Any]],
) -> tuple[bool, str | None, str | None]:
    try:
        rr = ref_eval(authority_state, request)
    except Exception as exc:
        return False, None, f"contract_e_reference_error:{type(exc).__name__}"
    try:
        ir = ind_eval(authority_state, request)
    except Exception as exc:
        return False, None, f"contract_e_independent_error:{type(exc).__name__}"
    if _receipt_projection(rr) != _receipt_projection(ir):
        return False, None, "contract_e_normative_disagreement"
    if not isinstance(rr, dict) or rr.get("authorized") is not True:
        return False, rr.get("receipt_id") if isinstance(rr, dict) else None, "contract_e_denied"
    return True, rr.get("receipt_id"), None


def _result() -> dict[str, Any]:
    return {
        "schema": "cal-disposable-execution-observation-rc1",
        "allowed": False,
        "performed_write": False,
        "execution_attribution": None,
        "operation_id": None,
        "target_sha256": None,
        "journal_terminal_event": None,
        "fresh_authorization_performed": False,
        "failures": [],
        "diagnostics": [],
    }


def _deny(result: dict[str, Any], code: str, detail: str | None = None) -> dict[str, Any]:
    if code not in result["failures"]:
        result["failures"].append(code)
    if detail:
        result["diagnostics"].append(detail)
    return result


def _atomic_replace_exact(path: Path, post_bytes: bytes, expected_mode: int) -> None:
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".rc1.tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(post_bytes)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.chmod(tmp_path, stat.S_IMODE(expected_mode))
        os.replace(tmp_path, path)
        tmp_path = None
        try:
            pfd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(pfd)
            finally:
                os.close(pfd)
        except OSError:
            pass
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass


def execute(
    *,
    plan: Any,
    contract_d_bytes: bytes,
    applicability_expectation: Any,
    target_root: str | Path,
    journal_path: str | Path,
    authority_state: Any,
    authorization_request: Any,
    contract_d_require_canonical_bytes: Callable[[bytes], dict[str, Any]],
    contract_d_consume: Callable[[Any, Any], dict[str, Any]],
    contract_d_validate_effect: Callable[[Any], dict[str, Any]],
    contract_e_reference_evaluate: Callable[[Any, Any], dict[str, Any]],
    contract_e_independent_evaluate: Callable[[Any, Any], dict[str, Any]],
    canonical_bytes: Callable[[Any], bytes],
    contract_e_reference_identity: Callable[[str, str | None, str], str],
    failpoint: str | None = None,
    research_before_replace_hook: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Execute/recover one exact disposable byte transition."""

    result = _result()
    valid, operation_id, post_bytes = _validate_plan(plan, canonical_bytes)
    if not valid or operation_id is None or post_bytes is None:
        return _deny(result, "invalid_or_forged_plan")
    result["operation_id"] = operation_id

    if not isinstance(contract_d_bytes, bytes) or _sha256_bytes(contract_d_bytes) != plan["contract_d_sha256"]:
        return _deny(result, "contract_d_digest_mismatch")
    try:
        decision = contract_d_require_canonical_bytes(contract_d_bytes)
        app = contract_d_consume(decision, applicability_expectation)
    except Exception as exc:
        return _deny(result, "contract_d_invalid_or_consumer_error", type(exc).__name__)
    if not isinstance(app, dict) or app.get("outcome") != "candidate_for_authorization":
        return _deny(result, "contract_d_not_candidate_for_authorization", str(app.get("outcome") if isinstance(app, dict) else None))
    try:
        effect = contract_d_validate_effect(decision.get("effect"))
    except Exception as exc:
        return _deny(result, "contract_d_effect_invalid", type(exc).__name__)
    target = decision.get("target")
    if not isinstance(target, dict):
        return _deny(result, "contract_d_target_invalid")
    if (
        effect.get("type") != plan["effect_id"]
        or effect.get("version") != plan["effect_version"]
        or effect.get("params") != plan["effect_params"]
        or target.get("kind") != plan["contract_d_target_kind"]
        or target.get("id") != plan["contract_d_target_id"]
        or target.get("content_sha256") != plan["expected_pre_sha256"]
    ):
        return _deny(result, "contract_d_plan_binding_mismatch")

    try:
        if not _request_binds_plan(authorization_request, plan, contract_e_reference_identity):
            return _deny(result, "authorization_request_plan_mismatch")
    except Exception as exc:
        return _deny(result, "authorization_request_plan_binding_error", type(exc).__name__)

    try:
        root = Path(target_root).resolve(strict=True)
    except Exception as exc:
        return _deny(result, "invalid_target_root", type(exc).__name__)
    marker = root / MARKER_NAME
    try:
        if not marker.is_file() or marker.read_bytes() != MARKER_BYTES:
            return _deny(result, "non_disposable_root")
    except Exception as exc:
        return _deny(result, "non_disposable_root", type(exc).__name__)

    rel = _relative_path(plan["target_relative_path"])
    if rel is None:
        return _deny(result, "invalid_target_relative_path")
    unresolved = root.joinpath(*rel.parts)
    try:
        resolved = unresolved.resolve(strict=True)
    except Exception as exc:
        return _deny(result, "target_resolution_failed", type(exc).__name__)
    if not _within(resolved, root) or not resolved.is_file():
        return _deny(result, "target_outside_root_or_not_regular")

    journal = Path(journal_path)
    try:
        journal_parent = journal.parent.resolve(strict=True)
    except Exception as exc:
        return _deny(result, "journal_parent_invalid", type(exc).__name__)
    if not _within(journal_parent, root):
        return _deny(result, "journal_outside_root")

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        jfd = os.open(journal, os.O_CREAT | os.O_RDWR | nofollow, 0o600)
    except Exception as exc:
        return _deny(result, "journal_open_failed", type(exc).__name__)

    try:
        fcntl.flock(jfd, fcntl.LOCK_EX)
        events, journal_error = _load_journal(jfd, operation_id)
        if journal_error:
            return _deny(result, "journal_invalid", journal_error)

        terminal = next((e for e in reversed(events) if e.get("event_type") in {"APPLIED", "RECOVERED_POSTSTATE", "ABORTED"}), None)

        try:
            tfd = os.open(resolved, os.O_RDONLY | nofollow)
        except Exception as exc:
            return _deny(result, "target_open_failed", type(exc).__name__)
        try:
            fcntl.flock(tfd, fcntl.LOCK_EX)
            locked_stat = os.fstat(tfd)
            try:
                reresolved = unresolved.resolve(strict=True)
                current_stat = os.stat(reresolved, follow_symlinks=False)
            except Exception as exc:
                return _deny(result, "target_reresolution_failed", type(exc).__name__)
            if reresolved != resolved or not _same_file(locked_stat, current_stat):
                return _deny(result, "target_identity_changed")
            current_hash = _sha256_bytes(_read_fd(tfd))
            result["target_sha256"] = current_hash

            if terminal is not None:
                result["journal_terminal_event"] = terminal.get("event_type")
                if terminal.get("event_type") == "ABORTED":
                    return _deny(result, "operation_previously_aborted")
                if current_hash != plan["expected_post_sha256"]:
                    return _deny(result, "terminal_journal_poststate_mismatch")
                result["allowed"] = True
                result["performed_write"] = False
                result["execution_attribution"] = terminal.get("execution_attribution")
                return result

            prepared = any(e.get("event_type") == "PREPARED" for e in events)

            if prepared and current_hash == plan["expected_post_sha256"]:
                event = _append_event(
                    jfd,
                    events,
                    operation_id=operation_id,
                    event_type="RECOVERED_POSTSTATE",
                    target_sha256=current_hash,
                    execution_attribution="unknown",
                    reason="exact_post_state_observed_without_durable_applied_event",
                )
                result["allowed"] = True
                result["performed_write"] = False
                result["execution_attribution"] = "unknown"
                result["journal_terminal_event"] = event["event_type"]
                return result

            if current_hash != plan["expected_pre_sha256"]:
                if prepared:
                    _append_event(
                        jfd,
                        events,
                        operation_id=operation_id,
                        event_type="ABORTED",
                        target_sha256=current_hash,
                        execution_attribution=None,
                        reason="prepared_operation_target_is_neither_exact_pre_nor_exact_post",
                    )
                return _deny(result, "target_not_exact_prestate")

            # Any path from exact pre-state to a new mutation requires fresh current authority,
            # including retries after a durable PREPARED event.
            result["fresh_authorization_performed"] = True
            ok, receipt_id, auth_error = _fresh_authorize(
                authority_state=authority_state,
                request=authorization_request,
                ref_eval=contract_e_reference_evaluate,
                ind_eval=contract_e_independent_evaluate,
            )
            if not ok:
                if prepared:
                    _append_event(
                        jfd,
                        events,
                        operation_id=operation_id,
                        event_type="ABORTED",
                        target_sha256=current_hash,
                        authorization_receipt_id=receipt_id,
                        reason=auth_error or "fresh_authorization_failed",
                    )
                return _deny(result, "fresh_authorization_failed", auth_error)

            prepared_event = _append_event(
                jfd,
                events,
                operation_id=operation_id,
                event_type="PREPARED",
                target_sha256=current_hash,
                authorization_receipt_id=receipt_id,
                execution_attribution=None,
                reason="fresh_point_of_use_authorization_succeeded",
            )
            if failpoint == "after_prepared":
                raise InjectedInterruption("after_prepared")

            if research_before_replace_hook is not None:
                research_before_replace_hook(unresolved)

            try:
                before_replace_resolved = unresolved.resolve(strict=True)
                before_replace_stat = os.stat(before_replace_resolved, follow_symlinks=False)
            except Exception as exc:
                return _deny(result, "target_before_replace_resolution_failed", type(exc).__name__)
            if before_replace_resolved != resolved or not _same_file(locked_stat, before_replace_stat):
                return _deny(result, "target_identity_changed_before_replace")
            try:
                bfd = os.open(before_replace_resolved, os.O_RDONLY | nofollow)
                try:
                    before_replace_hash = _sha256_bytes(_read_fd(bfd))
                finally:
                    os.close(bfd)
            except Exception as exc:
                return _deny(result, "target_before_replace_read_failed", type(exc).__name__)
            if before_replace_hash != plan["expected_pre_sha256"]:
                _append_event(
                    jfd,
                    events,
                    operation_id=operation_id,
                    event_type="ABORTED",
                    target_sha256=before_replace_hash,
                    authorization_receipt_id=prepared_event.get("authorization_receipt_id"),
                    reason="target_changed_after_authorization_before_replace",
                )
                return _deny(result, "target_changed_after_authorization_before_replace")

            _atomic_replace_exact(resolved, post_bytes, locked_stat.st_mode)
            if failpoint == "after_replace_before_applied":
                raise InjectedInterruption("after_replace_before_applied")

            try:
                post_resolved = unresolved.resolve(strict=True)
                pfd = os.open(post_resolved, os.O_RDONLY | nofollow)
                try:
                    post_hash = _sha256_bytes(_read_fd(pfd))
                finally:
                    os.close(pfd)
            except Exception as exc:
                return _deny(result, "poststate_read_failed", type(exc).__name__)
            result["target_sha256"] = post_hash
            if post_hash != plan["expected_post_sha256"]:
                return _deny(result, "poststate_mismatch_after_replace")

            applied = _append_event(
                jfd,
                events,
                operation_id=operation_id,
                event_type="APPLIED",
                target_sha256=post_hash,
                authorization_receipt_id=receipt_id,
                execution_attribution="this_invocation",
                reason="atomic_replace_completed_and_exact_post_state_observed",
            )
            result["allowed"] = True
            result["performed_write"] = True
            result["execution_attribution"] = "this_invocation"
            result["journal_terminal_event"] = applied["event_type"]
            if failpoint == "after_applied":
                raise InjectedInterruption("after_applied")
            return result
        finally:
            try:
                fcntl.flock(tfd, fcntl.LOCK_UN)
            finally:
                os.close(tfd)
    finally:
        try:
            fcntl.flock(jfd, fcntl.LOCK_UN)
        finally:
            os.close(jfd)
