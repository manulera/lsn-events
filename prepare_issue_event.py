"""Helper script that downloads a TSV attachment from an issue body."""

from __future__ import annotations

import os
import re
import sys
import urllib.request
from pathlib import Path

from render import render_event


def find_tsv_url(body: str) -> str:
    pattern = re.compile(r"(https?://[^\s)]+\.tsv)", re.IGNORECASE)
    match = pattern.search(body)
    if not match:
        raise RuntimeError("No `.tsv` attachment link found in the issue body.")
    return match.group(1).rstrip(").,")


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")
    if not body:
        raise RuntimeError("ISSUE_BODY environment variable is empty.")

    raw_url = find_tsv_url(body)
    filename = Path(raw_url).name
    destination = Path("data") / filename
    if destination.exists():
        raise RuntimeError(f"File {destination} already exists in data/")

    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(raw_url, destination)
    print(f"Downloaded {filename} to data/")

    render_event(destination, Path("dist"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - surfaced via GitHub Actions logs
        print(f"::error::{exc}")
        sys.exit(1)
