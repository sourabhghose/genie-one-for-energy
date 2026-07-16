-- Live AEMO tool: an HTTP connection + a table-valued UC function that fetches
-- the current NEM spot price/demand at query time (NO ingestion).
--
-- Replace {{CATALOG}} and {{SCHEMA}} before running (02_connection_and_function.py
-- does this substitution automatically from your config).
--
-- PREREQUISITE: STEP 1 needs CREATE CONNECTION on the metastore (metastore-admin
-- gated). If you lack it, ask an admin to run STEP 1 and GRANT you USE CONNECTION,
-- then you run STEP 2 yourself.

-- ============================================================================
-- STEP 1 — public AEMO HTTP connection (no auth).
-- bearer_token 'none' skips the OAuth DCR handshake that HTTP connections
-- attempt by default (which fails against public, unauthenticated APIs).
-- ============================================================================
CREATE CONNECTION IF NOT EXISTS aemo_live
  TYPE HTTP
  OPTIONS (
    host 'https://visualisations.aemo.com.au',
    port '443',
    base_path '/',
    bearer_token 'none'
  )
  COMMENT 'Public AEMO visualisations API (no auth) for live NEM summary.';

-- ============================================================================
-- STEP 2 — table-valued function. Table-valued (RETURNS TABLE) is REQUIRED so
-- it can be attached to a Genie Agent as a SQL-function tool.
-- ============================================================================
CREATE OR REPLACE FUNCTION {{CATALOG}}.{{SCHEMA}}.get_live_nem_price(region STRING)
RETURNS TABLE(region_id STRING, settlement_date STRING, price_aud_mwh DOUBLE, demand_mw DOUBLE, source STRING)
READS SQL DATA
COMMENT 'Live AEMO NEM spot price and operational demand for a NEM region (NSW1, QLD1, VIC1, SA1, TAS1), fetched from AEMO at call time via the aemo_live HTTP connection WITHOUT ingestion. Use for real-time / current / "right now" spot price and demand questions. Pass region as the AEMO region id.'
RETURN
  WITH resp AS (
    SELECT http_request(conn=>'aemo_live', method=>'POST',
      path=>'/aemo/apps/api/report/ELEC_NEM_SUMMARY',
      headers=>map('Content-Type','application/json','Accept','application/json'),
      json=>'{"timeScale":["30MIN"]}').text AS t
  ),
  parsed AS (
    SELECT from_json(t, 'STRUCT<ELEC_NEM_SUMMARY: ARRAY<STRUCT<SETTLEMENTDATE:STRING, REGIONID:STRING, PRICE:DOUBLE, TOTALDEMAND:DOUBLE>>>') AS j FROM resp
  ),
  rows AS (SELECT explode(j.ELEC_NEM_SUMMARY) AS r FROM parsed)
  SELECT r.REGIONID AS region_id,
         r.SETTLEMENTDATE AS settlement_date,
         round(r.PRICE, 2) AS price_aud_mwh,
         round(r.TOTALDEMAND, 0) AS demand_mw,
         'LIVE AEMO (fetched at call time, not ingested)' AS source
  FROM rows
  WHERE r.REGIONID = upper(region);

-- ============================================================================
-- STEP 3 — verify (should return one live row)
-- ============================================================================
-- SELECT * FROM {{CATALOG}}.{{SCHEMA}}.get_live_nem_price('SA1');
