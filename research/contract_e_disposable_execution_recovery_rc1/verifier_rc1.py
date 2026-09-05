#!/usr/bin/env python3
"""Independent post-state verifier for disposable execution/recovery RC1.

This verifier never imports or calls the executor candidate. It verifies only the
immutable plan, current target bytes, and durable journal evidence.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

import rfc8785

PLAN_SCHEMA = "cal-disposable-execution-plan-rc1"
EVENT_SCHEMA = "cal-disposable-execution-journal-event-rc1"
MARKER_NAME = ".contract-e-execution-rc1-disposable"
MARKER_BYTES = b"CONTRACT_E_EXECUTION_RC1_DISPOSABLE\n"
GENESIS = "0" * 64
_SHA = re.compile(r"^sha256:[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return rfc8785.dumps(value) + b"\n"


def plan_identity(plan: dict[str, Any]) -> str:
    body = {k: copy.deepcopy(v) for k, v in plan.items() if k != "operation_id"}
    return sha256_bytes(canonical_bytes(body))


def event_hash(event_without_hash: dict[str, Any]) -> str:
    raw = json.dumps(
        event_without_hash,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def relative_path(value: Any) -> PurePosixPath | None:
    if not isinstance(value, str) or "\\" in value:
        return None
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(part in {"", ".", ".."} for part in p.parts):
        return None
    if str(p) != value:
        return None
    return p


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_plan(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    failures: list[str] = []
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, ["plan_parse_error"]
    if not isinstance(plan, dict) or plan.get("schema") != PLAN_SCHEMA:
        return None, ["plan_schema_invalid"]
    op = plan.get("operation_id")
    if not isinstance(op, str) or _SHA.fullmatch(op) is None:
        failures.append("plan_operation_id_invalid")
    else:
        try:
            if plan_identity(plan) != op:
                failures.append("plan_identity_mismatch")
        except Exception:
            failures.append("plan_identity_uncomputable")
    try:
        post = base64.b64decode(plan.get("post_bytes_b64", "").encode("ascii"), validate=True)
    except Exception:
        failures.append("plan_post_bytes_invalid")
    else:
        if sha256_bytes(post) != plan.get("expected_post_sha256"):
            failures.append("plan_post_hash_mismatch")
    return plan, failures


def load_journal(path: Path, operation_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return [], ["journal_read_error"]
    events: list[dict[str, Any]] = []
    prev = GENESIS
    expected_sequence = 1
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except Exception:
            failures.append("journal_parse_error")
            break
        if not isinstance(event, dict):
            failures.append("journal_non_object")
            break
        if event.get("schema") != EVENT_SCHEMA:
            failures.append("journal_schema_invalid")
        if event.get("operation_id") != operation_id:
            failures.append("journal_operation_id_mismatch")
        if event.get("sequence") != expected_sequence:
            failures.append("journal_sequence_invalid")
        if event.get("prev_event_sha256") != prev:
            failures.append("journal_chain_invalid")
        claimed = event.get("event_sha256")
        if not isinstance(claimed, str) or re.fullmatch(r"[0-9a-f]{64}", claimed) is None:
            failures.append("journal_event_hash_invalid")
        else:
            body = {k: copy.deepcopy(v) for k, v in event.items() if k != "event_sha256"}
            if event_hash(body) != claimed:
                failures.append("journal_event_hash_mismatch")
            prev = claimed
        if event.get("authority_conferring") is not False:
            failures.append("journal_authority_conferring_invalid")
        events.append(event)
        expected_sequence += 1
    return events, failures


def verify(plan_path: Path, target_root: Path, journal_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "cal-disposable-execution-poststate-verification-rc1",
        "verification_pass": False,
        "authorization_established": False,
        "authenticated_actor_established": False,
        "operation_id": None,
        "current_target_sha256": None,
        "terminal_event": None,
        "post_state_exact": False,
        "journal_chain_valid": False,
        "execution_attribution": None,
        "failures": [],
    }

    plan, plan_failures = load_plan(plan_path)
    result["failures"].extend(plan_failures)
    if plan is None:
        return result
    result["operation_id"] = plan.get("operation_id")

    try:
        root = target_root.resolve(strict=True)
    except Exception:
        result["failures"].append("target_root_invalid")
        return result
    marker = root / MARKER_NAME
    try:
        if not marker.is_file() or marker.read_bytes() != MARKER_BYTES:
            result["failures"].append("non_disposable_root")
            return result
    except Exception:
        result["failures"].append("non_disposable_root")
        return result

    rel = relative_path(plan.get("target_relative_path"))
    if rel is None:
        result["failures"].append("target_relative_path_invalid")
        return result
    try:
        target = root.joinpath(*rel.parts).resolve(strict=True)
    except Exception:
        result["failures"].append("target_resolution_failed")
        return result
    if not within(target, root) or not target.is_file():
        result["failures"].append("target_outside_root_or_not_regular")
        return result
    try:
        current_hash = sha256_bytes(target.read_bytes())
    except Exception:
        result["failures"].append("target_read_failed")
        return result
    result["current_target_sha256"] = current_hash
    result["post_state_exact"] = current_hash == plan.get("expected_post_sha256")

    events, journal_failures = load_journal(journal_path, str(plan.get("operation_id")))
    result["failures"].extend(journal_failures)
    result["journal_chain_valid"] = not journal_failures
    if not events:
        result["failures"].append("journal_empty")
        return result

    seen_prepared = False
    seen_applied = False
    seen_recovered = False
    terminal: dict[str, Any] | None = None
    for event in events:
        et = event.get("event_type")
        if et == "PREPARED":
            if seen_applied or seen_recovered:
                result["failures"].append("prepared_after_terminal")
            seen_prepared = True
        elif et == "APPLIED":
            if not seen_prepared:
                result["failures"].append("applied_without_prepared")
            if event.get("target_sha256") != plan.get("expected_post_sha256"):
                result["failures"].append("applied_event_posthash_mismatch")
            if event.get("execution_attribution") != "this_invocation":
                result["failures"].append("applied_attribution_invalid")
            seen_applied = True
            terminal = event
        elif et == "RECOVERED_POSTSTATE":
            if not seen_prepared or seen_applied:
                result["failures"].append("recovered_event_order_invalid")
            if event.get("target_sha256") != plan.get("expected_post_sha256"):
                result["failures"].append("recovered_event_posthash_mismatch")
            if event.get("execution_attribution") != "unknown":
                result["failures"].append("recovered_attribution_must_be_unknown")
            seen_recovered = True
            terminal = event
        elif et == "ABORTED":
            terminal = event
        else:
            result["failures"].append("unknown_event_type")

    if terminal is None:
        result["failures"].append("no_terminal_event")
        return result
    result["terminal_event"] = terminal.get("event_type")

    if terminal.get("event_type") == "APPLIED":
        result["execution_attribution"] = "executor_journal_claim:this_invocation"
    elif terminal.get("event_type") == "RECOVERED_POSTSTATE":
        result["execution_attribution"] = "unknown"
    else:
        result["execution_attribution"] = None
        result["failures"].append("operation_aborted")

    if not result["post_state_exact"]:
        result["failures"].append("current_target_not_exact_poststate")

    result["verification_pass"] = not result["failures"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    result = verify(Path(args.plan), Path(args.target_root), Path(args.journal))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["verification_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
