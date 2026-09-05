#!/usr/bin/env python3
"""Independent direct-state verifier for authority/use linearization RC2."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def verify(db_path: str | Path, *, intent_id: str, target_id: str = "fixture-1") -> dict:
    out = {
        "schema": "cal-envelope-linearization-verification-rc2",
        "verification_pass": False,
        "authorization_established": False,
        "authenticated_actor_established": False,
        "intent_id": intent_id,
        "target_id": target_id,
        "observed_target": None,
        "observed_ledger": None,
        "observed_execution_record": None,
        "observed_current_authority_generation": None,
        "failures": [],
    }
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        target = conn.execute("SELECT id,version,state,marker FROM target WHERE id=?", (target_id,)).fetchone()
        ledger = conn.execute("SELECT * FROM intent_ledger WHERE intent_id=?", (intent_id,)).fetchone()
        record = conn.execute("SELECT * FROM execution_record WHERE intent_id=?", (intent_id,)).fetchone()
        current = conn.execute("SELECT epoch,generation,authority_state_sha256 FROM authority_current WHERE singleton=1").fetchone()
        history = None
        if record is not None:
            history = conn.execute(
                "SELECT authority_state_id,authority_state_sha256 FROM authority_history WHERE epoch=? AND generation=?",
                (record["authority_epoch"], record["authority_generation"]),
            ).fetchone()
    except Exception as exc:
        out["failures"].append(f"database_read_failed:{type(exc).__name__}")
        try: conn.close()
        except Exception: pass
        return out
    finally:
        try: conn.close()
        except Exception: pass

    if target is not None: out["observed_target"] = dict(target)
    if ledger is not None: out["observed_ledger"] = dict(ledger)
    if record is not None: out["observed_execution_record"] = dict(record)
    if current is not None: out["observed_current_authority_generation"] = current["generation"]

    if target is None: out["failures"].append("target_missing")
    if ledger is None: out["failures"].append("intent_ledger_missing")
    if record is None: out["failures"].append("execution_record_missing")
    if current is None: out["failures"].append("authority_current_missing")
    if out["failures"]: return out

    if ledger["execution_record_id"] != record["execution_record_id"]:
        out["failures"].append("ledger_execution_record_mismatch")
    if ledger["intent_sha256"] != record["intent_sha256"]:
        out["failures"].append("intent_digest_mismatch")
    if ledger["committed_outcome"] != "committed" or record["committed_outcome"] != "committed":
        out["failures"].append("outcome_not_committed")
    if record["intent_id"] != intent_id:
        out["failures"].append("record_intent_mismatch")
    if record["target_id"] != target_id:
        out["failures"].append("record_target_mismatch")
    if record["target_before_version"] != 17 or record["target_before_state"] != "ready":
        out["failures"].append("record_prestate_mismatch")
    if record["target_after_version"] != 18 or record["target_after_state"] != "marked":
        out["failures"].append("record_poststate_mismatch")
    if target["version"] != 18 or target["state"] != "marked" or target["marker"] != intent_id:
        out["failures"].append("authoritative_target_disagrees")
    if history is None:
        out["failures"].append("used_authority_history_missing")
    else:
        if history["authority_state_id"] != record["authority_state_id"]:
            out["failures"].append("used_authority_id_mismatch")
        if history["authority_state_sha256"] != record["authority_state_sha256"]:
            out["failures"].append("used_authority_digest_mismatch")
    if current["generation"] < record["authority_generation"]:
        out["failures"].append("current_authority_generation_regressed_below_execution")

    out["verification_pass"] = not out["failures"]
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--intent-id", required=True)
    p.add_argument("--target-id", default="fixture-1")
    p.add_argument("--output")
    a = p.parse_args()
    result = verify(a.db, intent_id=a.intent_id, target_id=a.target_id)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.output: Path(a.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["verification_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
