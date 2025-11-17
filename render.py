"""Barebones utility to populate the event template from a TSV file."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_PATH = Path("template.html")


def load_context(tsv_path: Path) -> dict[str, str]:
    if not tsv_path.exists():
        raise FileNotFoundError(f"Could not find TSV file: {tsv_path}")

    with tsv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        context: dict[str, str] = {}
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            key = row[0].strip()
            if not key:
                continue
            value = row[1].strip() if len(row) > 1 else ""
            context[key] = value
    if not context:
        raise ValueError(
            f"TSV file {tsv_path} did not contain any parameter/value pairs"
        )
    return context


def slugify(value: str | None, default: str) -> str:
    if not value:
        value = default
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def build_context(tsv_path: Path) -> dict[str, object]:
    base = load_context(tsv_path)
    base.setdefault("event_id", tsv_path.stem)
    base.setdefault("minimal", False)
    base["location"] = {
        "institution": base.get("institution"),
        "room_name": base.get("room_name"),
        "room_link": base.get("room_link"),
        "address": base.get("address"),
    }
    return base


def render_event(tsv_path: Path, output_dir: Path) -> Path:
    context = build_context(tsv_path)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_PATH.parent)),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(TEMPLATE_PATH.name)

    output_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(context.get("event_id"), tsv_path.stem)
    event_dir = output_dir / slug
    event_dir.mkdir(parents=True, exist_ok=True)
    output_path = event_dir / "index.html"

    output_path.write_text(template.render(**context), encoding="utf-8")

    # Minimal version for social media
    context2 = {**context, "minimal": True}
    output_path2 = event_dir / "minimal.html"
    output_path2.write_text(template.render(**context2), encoding="utf-8")

    # Without link for the event page
    context3 = {**context, "minimal": True, "registration_link": ""}
    output_path3 = event_dir / "no_registration.html"
    output_path3.write_text(template.render(**context3), encoding="utf-8")
    return output_path


def main() -> None:

    output_path = render_event(Path("data/lsn-12.tsv"), Path("dist"))
    print(f"Rendered {output_path}")


if __name__ == "__main__":
    main()
