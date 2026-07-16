#!/usr/bin/env python3
"""Create the schema and 3 synthetic NEM market tables (the 'ingested history').

Synthetic data modelled on AEMO NEMWEB: 14 days of 5-minute spot prices and
demand across the 5 NEM regions, plus 7 days of generation-by-fuel.
"""
import sys

from _dbx import cfg, run_sql, token


def statements(catalog: str, schema: str) -> list[str]:
    s = f"{catalog}.{schema}"
    return [
        f"""CREATE OR REPLACE TABLE {s}.nem_prices_5min
        COMMENT 'NEM 5-minute regional spot prices (RRP, $/MWh). Synthetic demo data modelled on AEMO NEMWEB.' AS
        WITH ints AS (SELECT explode(sequence(0,4031)) AS i),
          regions AS (SELECT col AS region_id, base FROM VALUES ('NSW1',78.0),('QLD1',68.0),('VIC1',82.0),('SA1',95.0),('TAS1',62.0) AS t(col,base)),
          grid AS (SELECT r.region_id,r.base, date_trunc('DAY',current_timestamp())-INTERVAL 14 DAYS + make_interval(0,0,0,0,0,i*5,0) AS settlement_date FROM ints CROSS JOIN regions r),
          priced AS (SELECT region_id,settlement_date,base,
            28.0*sin(2*pi()*((hour(settlement_date)+minute(settlement_date)/60.0)-18)/24.0) AS daily,
            (rand()-0.5)*18 AS noise, CASE WHEN rand()<0.012 THEN rand()*3800 ELSE 0 END AS spike,
            CASE WHEN (hour(settlement_date) BETWEEN 10 AND 14) AND rand()<0.05 THEN -(rand()*90) ELSE 0 END AS neg FROM grid)
        SELECT region_id,settlement_date, round(greatest(-1000.0,least(16600.0,base+daily+noise+spike+neg)),2) AS rrp,
          CASE WHEN spike>500 THEN true ELSE false END AS price_spike_flag FROM priced""",

        f"""CREATE OR REPLACE TABLE {s}.nem_demand_5min
        COMMENT 'NEM 5-minute regional operational demand (MW). Synthetic demo data.' AS
        WITH ints AS (SELECT explode(sequence(0,4031)) AS i),
          regions AS (SELECT col AS region_id, base FROM VALUES ('NSW1',8200.0),('QLD1',6400.0),('VIC1',5600.0),('SA1',1500.0),('TAS1',1100.0) AS t(col,base)),
          grid AS (SELECT r.region_id,r.base, date_trunc('DAY',current_timestamp())-INTERVAL 14 DAYS + make_interval(0,0,0,0,0,i*5,0) AS settlement_date FROM ints CROSS JOIN regions r)
        SELECT region_id,settlement_date, round(base*(1+0.18*sin(2*pi()*((hour(settlement_date)+minute(settlement_date)/60.0)-18)/24.0))+(rand()-0.5)*base*0.06,1) AS demand_mw FROM grid""",

        f"""CREATE OR REPLACE TABLE {s}.nem_generation_by_fuel
        COMMENT 'NEM generation output by fuel type (MW), 5-min. Synthetic demo data.' AS
        WITH ints AS (SELECT explode(sequence(0,2015)) AS i),
          regions AS (SELECT explode(array('NSW1','QLD1','VIC1','SA1','TAS1')) AS region_id),
          fuels AS (SELECT col AS fuel_type, cap FROM VALUES ('Coal',4500.0),('Gas',1800.0),('Hydro',1600.0),('Wind',2600.0),('Solar',3200.0),('Battery',700.0) AS t(col,cap)),
          grid AS (SELECT r.region_id,f.fuel_type,f.cap, date_trunc('DAY',current_timestamp())-INTERVAL 7 DAYS + make_interval(0,0,0,0,0,i*5,0) AS settlement_date FROM ints CROSS JOIN regions r CROSS JOIN fuels f)
        SELECT region_id,fuel_type,settlement_date, round(greatest(0.0, CASE fuel_type
            WHEN 'Solar' THEN cap*greatest(0,sin(pi()*((hour(settlement_date)+minute(settlement_date)/60.0)-6)/12.0))*(0.6+rand()*0.4)
            WHEN 'Wind' THEN cap*(0.2+rand()*0.6) WHEN 'Coal' THEN cap*(0.7+rand()*0.2)
            WHEN 'Gas' THEN cap*(0.1+rand()*0.5) WHEN 'Hydro' THEN cap*(0.2+rand()*0.5)
            ELSE cap*(rand()*0.8-0.4) END),1) AS output_mw FROM grid""",
    ]


def main() -> None:
    c = cfg()
    tok = token(c["profile"])
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {c['catalog']}.{c['schema']}", c, tok)
    for i, stmt in enumerate(statements(c["catalog"], c["schema"]), 1):
        r = run_sql(stmt, c, tok)
        state = r["status"]["state"]
        label = stmt.strip().split("\n")[0][:60]
        print(f"[{i}] {state}: {label}")
        if state != "SUCCEEDED":
            print(r.get("status", {}))
            sys.exit(1)
    # verify
    for tbl in ("nem_prices_5min", "nem_demand_5min", "nem_generation_by_fuel"):
        r = run_sql(f"SELECT count(*) FROM {c['catalog']}.{c['schema']}.{tbl}", c, tok)
        print(f"  {tbl}: {r.get('result', {}).get('data_array')}")


if __name__ == "__main__":
    main()
