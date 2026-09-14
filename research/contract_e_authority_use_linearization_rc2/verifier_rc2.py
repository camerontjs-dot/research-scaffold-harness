#!/usr/bin/env python3
"""Independent direct-state verifier for authority/use linearization RC2.

This verifier does not import or call the RC2 executor. It reads only the
observed disposable SQLite database and correlation identifiers.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

TARGET_ID = "fixture-1"
FINAL_VERSION = 18
FINAL_STATE = "marked"


def verify(db_path: str | Path, *, intent_id: str, target_id: str = TARGET_ID) -> dict:
    result = {
        "schema": "cal-envelope-linearization-verification-rc2",
        "verification_pass": False,
        "authorization_established": False,
        "authenticated_actor_established": False,
        "intent_id": intent_id,
        "target_id": target_id,
        "observed_target": None,
        "observed_execution_record": None,
        "observed_intent_ledger": None,
        "failures": [],
    }
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
    except Exception as exc:
        result["failures"].append(f"database_open_failed:{type(exc).__name__}")
        return result
    try:
        target = conn.execute("SELECT id,version,state,marker FROM target WHERE id=?", (target_id,)).fetchone()
        ledger = conn.execute("SELECT * FROM intent_ledger WHERE intent_id=?", (intent_id,)).fetchone()
        record = conn.execute("SELECT * FROM execution_record WHERE intent_id=?", (intent_id,)).fetchone()
    except Exception as exc:
        result["failures"].append(f"database_read_failed:{type(exc).__name__}")
        conn.close()
        return result
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if target is not None:
        result["observed_target"] = dict(target)
    if ledger is not None:
        result["observed_intent_ledger"] = dict(ledger)
    if record is not None:
        result["observed_execution_record"] = dict(record)

    if target is None:
        result["failures"].append("target_missing")
    if ledger is None:
        result["failures"].append("intent_ledger_missing")
    if record is None:
        result["failures"].append("execution_record_missing")
    if result["failures"]:
        return result

    if ledger["execution_record_id"] != record["execution_record_id"]:
        result["failures"].append("ledger_record_id_mismatch")
    if ledger["intent_sha256"] != record["intent_sha256"]:
        result["failures"].append("ledger_record_intent_digest_mismatch")
    if ledger["committed_outcome"] != "committed" or record["committed_outcome"] != "committed":
        result["failures"].append("committed_outcome_mismatch")
    if record["intent_id"] != intent_id:
        result["failures"].append("record_intent_id_mismatch")
    if record["target_id"] != target_id:
        result["failures"].append("record_target_id_mismatch")
    if record["target_before_version"] != 17 or record["target_before_state"] != "ready":
        result["failures"].append("record_prestate_mismatch")
    if record["target_after_version"] != FINAL_VERSION or record["target_after_state"] != FINAL_STATE:
        result["failures"].append("record_poststate_mismatch")
    if target["version"] != FINAL_VERSION or target["state"] != FINAL_STATE or target["marker"] != intent_id:
        result["failures"].append("authoritative_target_poststate_mismatch")
    if not isinstance(record["authority_generation"], int) or record["authority_generation"] < 0:
        result["failures"].append("authority_generation_invalid")
    if not isinstance(record["authority_state_sha256"], str) or not record["authority_state_sha256"].startswith("sha256:"):
        result["failures"].append("authority_state_digest_invalid")

    result["verification_pass"] = not result["failures"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--intent-id", required=True)
    parser.add_argument("--target-id", default=TARGET_ID)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = verify(args.db, intent_id=args.intent_id, target_id=args.target_id)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["verification_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
