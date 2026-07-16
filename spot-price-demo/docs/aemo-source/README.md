# AEMO source documents

Bundled here so the demo is self-contained (AEMO's site is Cloudflare-protected,
so automated download is blocked).

- `pdf/` — the original AEMO PDFs (source of truth).
- `text/` — plain text extracted via `pdftotext -layout`. **This is what you
  upload to Google Drive as Google Docs** — OneChat's Drive connector reads
  Google-native files, not binary PDFs.

## Sources (publicly available from aemo.com.au)

| File | Original URL |
|---|---|
| AEMO-QED-Q1-2026 | https://www.aemo.com.au/-/media/files/major-publications/qed/2026/qed-q1-2026.pdf |
| AEMO-QED-Q4-2025 | https://www.aemo.com.au/-/media/files/major-publications/qed/2025/qed-q4-2025.pdf |
| AEMO-NEM-Fact-Sheet | https://www.aemo.com.au/-/media/Files/Electricity/NEM/National-Electricity-Market-Fact-Sheet.pdf |
| AEMO-Global-Settlement-Fact-Sheet | https://www.aemo.com.au/-/media/files/electricity/nem/5ms/program-information/2020/global-settlement-fact-sheet-updated-july2020.pdf |

## Attribution / copyright
© AEMO. These are AEMO's publicly published reports, bundled here **only** for a
non-commercial internal demo. Do not redistribute externally. If in doubt, link
to the source URLs above instead of copying the files.

## Upload to Google Drive as Docs
Use `../../scripts/04_upload_docs_to_drive.py` (creates a Drive folder and
uploads each `text/*.txt` as a Google Doc). See `../aemo-drive-docs-setup.md`.
