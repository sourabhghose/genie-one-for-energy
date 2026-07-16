#!/usr/bin/env python3
"""Smoke-test a Genie Agent via the Conversation API (GA, scriptable).

Usage:
  python3 test_genie.py <space_id> "your question"
  python3 test_genie.py <space_id>          # runs a default live + historical pair
"""
import json
import sys
import time
import urllib.request

from _dbx import cfg, token


def _api(method, path, tok, host, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{host}{path}", data=data,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        method=method,
    )
    return json.load(urllib.request.urlopen(req))


def ask(space_id: str, question: str, c: dict, tok: str) -> None:
    host = c["host"]
    r = _api("POST", f"/api/2.0/genie/spaces/{space_id}/start-conversation", tok, host, {"content": question})
    conv, msg = r["conversation_id"], r["message_id"]
    print(f"\nQ: {question}")
    while True:
        m = _api("GET", f"/api/2.0/genie/spaces/{space_id}/conversations/{conv}/messages/{msg}", tok, host)
        st = m.get("status")
        if st in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(3)
    print("status:", st)
    for a in m.get("attachments", []):
        if "text" in a:
            print("TEXT:", a["text"].get("content", "")[:500])
        if "query" in a:
            print("SQL:", a["query"].get("query", "")[:400])
            res = _api("GET", f"/api/2.0/genie/spaces/{space_id}/conversations/{conv}/messages/{msg}/attachments/{a['attachment_id']}/query-result", tok, host)
            print("RESULT:", res.get("statement_response", {}).get("result", {}).get("data_array"))


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 test_genie.py <space_id> [question]")
    c = cfg()
    tok = token(c["profile"])
    space_id = sys.argv[1]
    if len(sys.argv) >= 3:
        ask(space_id, sys.argv[2], c, tok)
    else:
        ask(space_id, "What is the current live spot price and demand in SA1 right now?", c, tok)
        ask(space_id, "What was the average spot price in SA1 over the last 7 days?", c, tok)


if __name__ == "__main__":
    main()
