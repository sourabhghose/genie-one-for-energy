#!/usr/bin/env python3
"""Create the Genie Agent (space): 3 tables + the live get_live_nem_price
function attached as a SQL-function tool + routing instructions + sample
questions. Prints the space_id.

KEY GOTCHAS baked in here:
  * A UC function attaches under instructions.sql_functions (NOT data_sources).
    data_sources only supports `tables` and `volumes`.
  * Each sql_functions / text_instructions / sample_questions entry needs an
    `id` = lowercase 32-hex UUID (no hyphens), or the API rejects the payload.
  * get-space omits serialized_space unless you pass --include-serialized-space;
    update-space takes --serialized-space (a flag, not a positional arg).
"""
import json
import subprocess
import uuid

from _dbx import cfg

SAMPLE_QUESTIONS = [
    "Is SA1's live spot price above or below its 7-day average?",
    "Which region has the biggest gap between its live price right now and its 14-day average?",
    "Is current demand in VIC1 higher than its typical demand over the last two weeks?",
    "Why is SA1's price higher than QLD1's right now?",
    "We saw price spikes in NSW1 this week - what was happening with demand and generation when they hit?",
    "When solar output was highest this week, what happened to prices?",
    "Find the biggest price spike in the last 14 days and explain what likely drove it using demand and fuel mix.",
    "Show the top 5 price spikes in NSW1 this week.",
    "What's the average generation by fuel type in VIC1 over the last week?",
    "Which region had the most volatile prices over the past 14 days?",
    "What's the current spot price in SA1?",
    "What's the live demand in Queensland right now?",
]

INSTRUCTIONS = (
    "Route real-time / current / 'right now' spot price or demand questions to the "
    "get_live_nem_price SQL function (one region at a time: NSW1, QLD1, VIC1, SA1, TAS1). "
    "Route historical, trend, average, spike, volatility, or generation-mix questions to "
    "the tables. Prices are RRP in AUD/MWh; demand in MW; price_spike_flag marks spike intervals."
)


def serialized_space(catalog: str, schema: str) -> str:
    s = f"{catalog}.{schema}"
    # tables must be sorted alphabetically by identifier
    tables = sorted([
        f"{s}.nem_demand_5min",
        f"{s}.nem_generation_by_fuel",
        f"{s}.nem_prices_5min",
    ])
    space = {
        "version": 2,
        "config": {
            "sample_questions": [{"id": uuid.uuid4().hex, "question": [q]} for q in SAMPLE_QUESTIONS]
        },
        "data_sources": {
            "tables": [{"identifier": t} for t in tables]
        },
        "instructions": {
            "text_instructions": [{"id": uuid.uuid4().hex, "content": [INSTRUCTIONS]}],
            "sql_functions": [{"id": uuid.uuid4().hex, "identifier": f"{s}.get_live_nem_price"}],
        },
    }
    return json.dumps(space)


def main() -> None:
    c = cfg()
    ser = serialized_space(c["catalog"], c["schema"])
    out = subprocess.check_output([
        "databricks", "genie", "create-space", c["warehouse_id"], ser,
        "--title", c["genie_title"],
        "--description", "AEMO NEM spot prices, demand, generation-by-fuel (last 2 weeks) + LIVE AEMO price lookup.",
        "--profile", c["profile"],
    ])
    res = json.loads(out)
    print("space_id:", res["space_id"])
    print("title:", res["title"])
    obj = json.loads(res["serialized_space"])
    print("tables:", len(obj["data_sources"]["tables"]),
          "| sql_functions:", [f["identifier"] for f in obj["instructions"]["sql_functions"]],
          "| sample_questions:", len(obj["config"]["sample_questions"]))
    print("\nOpen it in the workspace, then optionally grant `account users` CAN_RUN:")
    print(f"  databricks api patch /api/2.0/permissions/genie/{res['space_id']} "
          f"--json '{{\"access_control_list\":[{{\"group_name\":\"account users\",\"permission_level\":\"CAN_RUN\"}}]}}' "
          f"--profile {c['profile']}")


if __name__ == "__main__":
    main()
