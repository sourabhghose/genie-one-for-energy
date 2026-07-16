# Copy to config.sh and edit for your workspace, then: source config.sh
# All scripts in this folder read these environment variables.

# Databricks CLI profile (must be authenticated: `databricks auth login --profile <name>`)
export DBX_PROFILE="e2-demo-field-eng"

# Workspace host (used by the Statement Execution + Genie APIs)
export DBX_HOST="https://e2-demo-field-eng.cloud.databricks.com"

# A running Pro/Serverless SQL warehouse you have CAN USE on
export DBX_WAREHOUSE_ID="862f1d757f0424f7"

# Where the demo objects live. You need CREATE on the schema (a personal
# users.<you> schema works well). Connections are metastore-level and need
# CREATE CONNECTION on the metastore (metastore-admin gated).
export DBX_CATALOG="users"
export DBX_SCHEMA="sourabh_ghose"

# Genie Agent display name
export GENIE_TITLE="ANZ NEM Trading Intelligence"
