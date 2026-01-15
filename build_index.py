"""Generate dist/index.html by globbing rendered events."""

from __future__ import annotations

import csv
from glob import glob
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

DIST_DIR = Path("dist")
TEMPLATE_PATH = Path("index_template.html")
DATA_DIR = Path("data")


def humanize(slug: str) -> str:
    return slug.replace("-", " ").title()


def load_metadata(slug: str) -> dict[str, str]:
    tsv_path = DATA_DIR / f"{slug}.tsv"
    if not tsv_path.exists():
        return {}
    metadata: dict[str, str] = {}
    with tsv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            key = row[0].strip()
            if not key or key.lower() in {"parameter", "field", "name"}:
                continue
            value = row[1].strip() if len(row) > 1 else ""
            metadata[key] = value
    return metadata


def gather_events() -> list[dict[str, str]]:
    events: dict[str, dict[str, str | None]] = {}
    for dir_path in glob(str(DIST_DIR / "*")):
        path = Path(dir_path)
        if not path.is_dir():
            continue
        slug = path.name
        events.setdefault(
            slug,
            {
                "label": humanize(slug).upper(),
                "index": None,
                "minimal": None,
                "no_registration": None,
                "event_date": None,
                "institution": None,
                "speaker_1": None,
                "speaker_1_talk": None,
                "speaker_2": None,
                "speaker_2_talk": None,
            },
        )
        for variant in ("index", "minimal", "no_registration"):
            file_path = path / f"{variant}.html"
            if file_path.exists():
                events[slug][variant] = f"./{slug}/{variant}.html"

        metadata = load_metadata(slug)
        if metadata:
            events[slug]["event_date"] = metadata.get("event_date")
            events[slug]["institution"] = metadata.get("institution")
            events[slug]["speaker_1"] = metadata.get("speaker_1_name")
            events[slug]["speaker_1_talk"] = metadata.get("speaker_1_talk_title")
            events[slug]["speaker_2"] = metadata.get("speaker_2_name")
            events[slug]["speaker_2_talk"] = metadata.get("speaker_2_talk_title")
    ordered = []
    for slug in sorted(events):
        event = events[slug]
        if any(event[key] for key in ("index", "minimal", "no_registration")):
            ordered.append(event)
    return ordered


def render_index(events: list[dict[str, str]]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_PATH.parent or ".")),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(TEMPLATE_PATH.name)
    return template.render(events=events[::-1])


def main() -> None:
    html = render_index(gather_events())
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "index.html").write_text(html, encoding="utf-8")
    print("Wrote dist/index.html")


if __name__ == "__main__":
    main()
