# Third source: AEMO documents via OneChat's Google Drive connector

This adds the *unstructured* leg — real AEMO reports queried live in OneChat,
no ingestion, no vector store.

## Documents used (real AEMO PDFs)

| Doc | URL |
|---|---|
| Quarterly Energy Dynamics Q1 2026 | `https://www.aemo.com.au/-/media/files/major-publications/qed/2026/qed-q1-2026.pdf` |
| Quarterly Energy Dynamics Q4 2025 | `https://www.aemo.com.au/-/media/files/major-publications/qed/2025/qed-q4-2025.pdf` |
| NEM Fact Sheet | `https://www.aemo.com.au/-/media/Files/Electricity/NEM/National-Electricity-Market-Fact-Sheet.pdf` |
| Global Settlement Fact Sheet | `https://www.aemo.com.au/-/media/files/electricity/nem/5ms/program-information/2020/global-settlement-fact-sheet-updated-july2020.pdf` |

> AEMO's site is behind Cloudflare, so `curl`/automated fetch is blocked (403 /
> JS challenge). Download the PDFs from a normal **browser** session.

## CRITICAL gotcha: OneChat reads Google-native files only

OneChat's Google Drive connector can read **Google Docs / Sheets / Slides**, but
**NOT binary PDFs**. You must upload **Google Doc** versions.

Recommended: extract text locally and create Google Docs (cleaner than Drive's
PDF OCR for long reports):

```bash
# 1. Download the 4 PDFs to ~/Downloads (browser)
# 2. Extract text (needs poppler: `brew install poppler`)
for f in ~/Downloads/qed-q1-2026 ~/Downloads/qed-q4-2025 \
         ~/Downloads/National-Electricity-Market-Fact-Sheet \
         ~/Downloads/global-settlement-fact-sheet-updated-july2020; do
  pdftotext -layout "$f.pdf" "$f.txt"
done
```

Then create a Drive folder and upload each `.txt` as a Google Doc (Drive API
converts text/plain -> Google Doc when the target mimeType is
`application/vnd.google-apps.document`). Any Drive upload path works; the key is
the resulting file is a **Google Doc**, not a PDF.

## Connect it in OneChat

1. In Databricks One / OneChat on your workspace, add the **Google Drive**
   external source (Beta, preview-gated) and complete the **per-user Google
   OAuth**. This is per-user and cannot be granted centrally.
2. Share the Drive folder with your audience (domain-wide reader is simplest for
   internal demos).
3. Ask document questions, e.g. *"Per the AEMO QED Q1 2026 report, what drove
   wholesale prices and what share did batteries set?"*
