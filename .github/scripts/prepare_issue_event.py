"""Helper script that downloads a TSV attachment from an issue body."""

from __future__ import annotations

import os
import re
import sys
import urllib.request
from pathlib import Path

import render


def find_tsv_url(body: str) -> str:
    pattern = re.compile(r"(https?://[^\s)]+\.tsv)", re.IGNORECASE)
    match = pattern.search(body)
    if not match:
        raise RuntimeError("No `.tsv` attachment link found in the issue body.")
    return match.group(1).rstrip(").,")


def download_tsv(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)
    return destination


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")
    if not body:
        raise RuntimeError("ISSUE_BODY environment variable is empty.")

    raw_url = find_tsv_url(body)
    filename = Path(raw_url).name
    temp_path = download_tsv(raw_url, Path("data") / filename)

    context = render.build_context(temp_path)
    event_id = context.get("event_id") or temp_path.stem
    final_path = temp_path.with_name(f"{event_id}.tsv")
    if final_path.exists() and final_path != temp_path:
        final_path.unlink()
    temp_path.rename(final_path)

    output_path = Path(os.environ["GITHUB_OUTPUT"])
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(f"tsv_path={final_path}\n")
        handle.write(f"event_id={event_id}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - surfaced via GitHub Actions logs
        print(f"::error::{exc}")
        sys.exit(1)
