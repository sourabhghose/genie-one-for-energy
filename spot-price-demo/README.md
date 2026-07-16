# Spot Price Demo — NEM Trading Intelligence

A Genie One / Databricks One demo where **one agent answers across three source
types**, none of it pre-ingested into a vector store:

| Source | What | How |
|---|---|---|
| Structured history | 14 days of 5-min NEM spot prices, demand, generation-by-fuel | Genie Agent over UC tables |
| Live external API | current AEMO spot price + demand | `get_live_nem_price` UC function → AEMO HTTP connection, at query time |
| Unstructured docs | AEMO reports (QED, fact sheets) | Google Docs queried live via OneChat's Drive connector |

OneChat auto-routes: "right now" → the live function, trends/spikes → the tables,
"why / what does AEMO say" → the documents.

## Prerequisites
- Databricks workspace with **Genie** enabled and a **Pro/Serverless SQL warehouse**.
- **Databricks One / OneChat** enabled (for the full 3-source experience; Beta/preview).
- `databricks` CLI authenticated: `databricks auth login --profile <name>`.
- `CREATE` on a schema (a personal `users.<you>` schema is ideal).
- **`CREATE CONNECTION` on the metastore** for the live function (metastore-admin
  gated). On shared internal metastores you may not have this — see Troubleshooting.
- `brew install poppler` (for `pdftotext`, used in the docs step).

## Setup

```bash
cd scripts
cp config.example.sh config.sh   # edit for your workspace
source config.sh

python3 01_setup_data.py                 # schema + 3 synthetic tables
python3 02_connection_and_function.py    # aemo_live connection + live UC function (verifies with a live call)
python3 03_create_genie_agent.py         # Genie Agent (tables + function tool + sample questions) -> prints space_id

# smoke-test routing (live + historical) via the Conversation API
python3 test_genie.py <space_id>
```

Then add the documents (third source): follow [`docs/aemo-drive-docs-setup.md`](docs/aemo-drive-docs-setup.md).

Finally, in **OneChat**: connect Google Drive (per-user OAuth), and use the
"Choose another space" control to select this Genie Agent if OneChat routes elsewhere.

## Sample questions
See [`sample_questions.md`](sample_questions.md) — single-source, two-source,
three-source, and causal "why" questions, plus the hero question.

## Troubleshooting / gotchas
- **`CREATE CONNECTION` denied** — shared internal metastores gate this. Use a
  workspace where you own the metastore, or have an admin create `aemo_live` and
  `GRANT` you `USE CONNECTION`, then run STEP 2 of `02_connection_and_function.sql`.
- **Genie can't call the function** — it must be **table-valued** (`RETURNS TABLE`)
  and attached under `instructions.sql_functions` (not `data_sources`). Handled by
  the scripts.
- **OneChat won't read the PDFs** — it reads Google-native files only; upload
  **Google Docs**, not PDFs. See the docs guide.
- **OneChat routes to the wrong agent** — there's no pre-question agent picker;
  it auto-routes across all agents you can access. Use the post-answer
  "Choose another space" control, or scope permissions to a dedicated demo user,
  or drive via the Conversation API with `force_space_id`.
- **HTTP connection OAuth error** — add `bearer_token 'none'` (done) so it skips
  the OAuth DCR handshake for public, unauthenticated APIs.
