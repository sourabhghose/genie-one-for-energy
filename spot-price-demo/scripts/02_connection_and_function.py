#!/usr/bin/env python3
"""Create the aemo_live HTTP connection + the table-valued get_live_nem_price
function by running 02_connection_and_function.sql (with {{CATALOG}}/{{SCHEMA}}
substituted), then verify with a live call.

NOTE: creating the connection needs CREATE CONNECTION on the metastore. If you
lack it, this script will fail on STEP 1 — ask an admin to create `aemo_live`
and GRANT you USE CONNECTION, then re-run (STEP 1 is idempotent / IF NOT EXISTS).
"""
import os
import sys

from _dbx import cfg, run_sql, token

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    c = cfg()
    tok = token(c["profile"])
    sql = open(os.path.join(HERE, "02_connection_and_function.sql")).read()
    sql = sql.replace("{{CATALOG}}", c["catalog"]).replace("{{SCHEMA}}", c["schema"])

    # Strip SQL line comments (some contain the words "CREATE CONNECTION"), then
    # split on ';' into runnable statements; the Statement Execution API runs one
    # statement at a time.
    code = "\n".join(l for l in sql.splitlines() if not l.lstrip().startswith("--"))
    stmts = [s.strip() for s in code.split(";") if s.strip()]
    conn_stmt = next(s for s in stmts if s.upper().startswith("CREATE CONNECTION"))
    fn_stmt = next(s for s in stmts if s.upper().startswith("CREATE OR REPLACE FUNCTION"))

    for label, stmt in (("connection", conn_stmt), ("function", fn_stmt)):
        r = run_sql(stmt, c, tok)
        state = r["status"]["state"]
        print(f"{label}: {state}")
        if state != "SUCCEEDED":
            print(r.get("status", {}))
            sys.exit(1)

    # grant EXECUTE broadly (adjust principal to taste)
    run_sql(f"GRANT EXECUTE ON FUNCTION {c['catalog']}.{c['schema']}.get_live_nem_price TO `account users`", c, tok)

    for region in ("SA1", "NSW1"):
        r = run_sql(f"SELECT * FROM {c['catalog']}.{c['schema']}.get_live_nem_price('{region}')", c, tok)
        print(f"  {region} -> {r['status']['state']} {r.get('result', {}).get('data_array')}")


if __name__ == "__main__":
    main()
