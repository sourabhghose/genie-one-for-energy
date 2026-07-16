# Third source: AEMO documents via OneChat's Google Drive connector

This adds the *unstructured* leg — real AEMO reports queried live in OneChat,
no ingestion, no vector store.

## Documents used (real AEMO reports)

The source documents are **bundled in this repo** at
[`aemo-source/`](aemo-source/) — both the original PDFs (`pdf/`) and the extracted
text (`text/`). Source URLs and attribution are in
[`aemo-source/README.md`](aemo-source/README.md).

> AEMO's site is behind Cloudflare, so `curl`/automated fetch is blocked (403 /
> JS challenge) — that's why the docs are bundled rather than downloaded at setup.

## CRITICAL gotcha: OneChat reads Google-native files only

OneChat's Google Drive connector can read **Google Docs / Sheets / Slides**, but
**NOT binary PDFs**. You must upload **Google Doc** versions. The bundled
`text/*.txt` files (extracted via `pdftotext -layout`) become those Google Docs.

## Upload as Google Docs (scripted)

```bash
gcloud auth application-default login    # if not already
cd ../scripts
python3 04_upload_docs_to_drive.py       # creates a Drive folder, uploads text/ as Google Docs
# or target an existing folder:
python3 04_upload_docs_to_drive.py <folder_id>
```

The script uploads each `text/*.txt` with target mimeType
`application/vnd.google-apps.document`, so Drive converts them to Google Docs.

## Connect it in OneChat

1. In Databricks One / OneChat on your workspace, add the **Google Drive**
   external source (Beta, preview-gated) and complete the **per-user Google
   OAuth**. This is per-user and cannot be granted centrally.
2. Share the Drive folder with your audience (domain-wide reader is simplest for
   internal demos).
3. Ask document questions, e.g. *"Per the AEMO QED Q1 2026 report, what drove
   wholesale prices and what share did batteries set?"*
