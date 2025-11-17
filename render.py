"""Barebones utility to populate the event template from a TSV file."""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_PATH = Path("template.html")


def parse_args() -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(
        description="Render a single event HTML file from a parameter/value TSV",
        add_help=True,
    )
    parser.add_argument(
        "tsv", type=Path, help="Path to the TSV file (parameter/value pairs)."
    )

    args = parser.parse_args()
    return args.tsv, Path("dist")


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
            if not key or key.lower() in {"parameter", "field", "name"}:
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
    base["location"] = {
        "institution": base.get("institution"),
        "room_name": base.get("room_name"),
        "room_link": base.get("room_link"),
        "address": base.get("address"),
        "minimal": False,
    }
    return base


def render_event(tsv_path: Path, output_dir: Path) -> Path:
    context = build_context(tsv_path)
    if "registration_link" not in context or not context["registration_link"]:
        context["registration_link"] = ""
        file_name = "no_registration"
    else:
        file_name = "index"
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_PATH.parent)),
        autoescape=select_autoescape(("html", "xml")),
    )
    template = env.get_template(TEMPLATE_PATH.name)

    output_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(context.get("event_id"), tsv_path.stem)
    output_path = output_dir / slug / f"{file_name}.html"
    if not os.path.exists(output_dir / slug):
        os.makedirs(output_dir / slug)

    output_path.write_text(template.render(**context), encoding="utf-8")

    if file_name == "index":
        context2 = {**context, "minimal": True}
        output_path2 = output_dir / slug / "minimal.html"
        output_path2.write_text(template.render(**context2), encoding="utf-8")
    return output_path


def main() -> None:
    tsv_path, output_dir = parse_args()
    output_path = render_event(tsv_path, output_dir)
    print(f"Rendered {output_path}")


if __name__ == "__main__":
    main()
