"""Shared helpers: read config from env, run SQL via the Statement Execution API."""
import json
import os
import subprocess
import time
import urllib.request


def cfg() -> dict:
    """Load required config from environment (see config.example.sh)."""
    required = ["DBX_PROFILE", "DBX_HOST", "DBX_WAREHOUSE_ID", "DBX_CATALOG", "DBX_SCHEMA"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Missing env vars: {missing}. Run: source config.sh")
    return {
        "profile": os.environ["DBX_PROFILE"],
        "host": os.environ["DBX_HOST"].rstrip("/"),
        "warehouse_id": os.environ["DBX_WAREHOUSE_ID"],
        "catalog": os.environ["DBX_CATALOG"],
        "schema": os.environ["DBX_SCHEMA"],
        "genie_title": os.environ.get("GENIE_TITLE", "ANZ NEM Trading Intelligence"),
    }


def token(profile: str) -> str:
    out = subprocess.check_output(["databricks", "auth", "token", "--profile", profile])
    return json.loads(out)["access_token"]


def run_sql(stmt: str, c: dict, tok: str) -> dict:
    """Run one SQL statement, block until terminal state, return the response."""
    body = json.dumps({
        "warehouse_id": c["warehouse_id"],
        "statement": stmt,
        "wait_timeout": "50s",
        "on_wait_timeout": "CONTINUE",
    }).encode()
    req = urllib.request.Request(
        f"{c['host']}/api/2.0/sql/statements",
        data=body,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        method="POST",
    )
    resp = json.load(urllib.request.urlopen(req))
    sid = resp["statement_id"]
    state = resp["status"]["state"]
    while state in ("PENDING", "RUNNING"):
        time.sleep(2)
        g = urllib.request.Request(
            f"{c['host']}/api/2.0/sql/statements/{sid}",
            headers={"Authorization": f"Bearer {tok}"},
        )
        resp = json.load(urllib.request.urlopen(g))
        state = resp["status"]["state"]
    return resp
