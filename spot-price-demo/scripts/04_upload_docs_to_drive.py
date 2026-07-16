#!/usr/bin/env python3
"""Upload the bundled AEMO text docs to Google Drive as Google Docs, so OneChat's
Drive connector can read them (it reads Google-native files, not PDFs).

Auth: uses gcloud Application Default Credentials + a Databricks GCP quota
project (the fe-google-tools CLI path). Ensure you're logged in:
    gcloud auth application-default login
and that the quota project below is set / you have access.

Usage:
    python3 04_upload_docs_to_drive.py                 # creates a new folder
    python3 04_upload_docs_to_drive.py <existing_folder_id>
"""
import json
import os
import subprocess
import sys
import urllib.request

QUOTA_PROJECT = os.environ.get("GCP_QUOTA_PROJECT", "gcp-dev-field-eng-aiapiquota")
FOLDER_NAME = os.environ.get("DRIVE_FOLDER_NAME", "AEMO Docs — Genie One Energy Demo")
HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_DIR = os.path.join(HERE, "..", "docs", "aemo-source", "text")

DOCS = {
    "AEMO-QED-Q1-2026.txt": "AEMO Quarterly Energy Dynamics Q1 2026",
    "AEMO-QED-Q4-2025.txt": "AEMO Quarterly Energy Dynamics Q4 2025",
    "AEMO-NEM-Fact-Sheet.txt": "AEMO NEM Fact Sheet",
    "AEMO-Global-Settlement-Fact-Sheet.txt": "AEMO Global Settlement Fact Sheet",
}


def adc_token() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"]
    ).decode().strip()


def create_folder(tok: str) -> str:
    body = json.dumps({"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"}).encode()
    req = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/files?fields=id,name,webViewLink",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {tok}", "X-Goog-User-Project": QUOTA_PROJECT,
                 "Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req))
    print("folder:", r["name"], "->", r.get("webViewLink"))
    return r["id"]


def upload_as_gdoc(txt_path: str, title: str, folder_id: str, tok: str) -> None:
    # multipart: metadata (target mimeType = Google Doc) + text/plain body -> converted
    boundary = "===genie-one-boundary==="
    meta = json.dumps({"name": title, "parents": [folder_id],
                       "mimeType": "application/vnd.google-apps.document"})
    with open(txt_path, "rb") as f:
        content = f.read()
    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n".encode(),
        f"--{boundary}\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n".encode(),
        content,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    payload = b"".join(parts)
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {tok}", "X-Goog-User-Project": QUOTA_PROJECT,
                 "Content-Type": f"multipart/related; boundary={boundary}"},
    )
    r = json.load(urllib.request.urlopen(req))
    print(f"  created Doc: {r['name']} ({r['id']})")


def main() -> None:
    tok = adc_token()
    folder_id = sys.argv[1] if len(sys.argv) > 1 else create_folder(tok)
    for fname, title in DOCS.items():
        path = os.path.join(TEXT_DIR, fname)
        if not os.path.exists(path):
            print(f"  SKIP (missing): {fname}")
            continue
        upload_as_gdoc(path, title, folder_id, tok)
    print("\nDone. Share the folder (domain-wide reader for internal demos) and "
          "connect it in OneChat via the Google Drive connector (per-user OAuth).")


if __name__ == "__main__":
    main()
