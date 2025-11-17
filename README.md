# lsn-events

Generate plain HTML event announcements by combining a TSV data file with the
existing `template.html` (exported from Word). The workflow is intentionally
minimal: `render.py` accepts the TSV path plus an output directory and writes
`dist/<event_id>/index.html` along with a stripped-down `minimal.html`.

```bash
poetry install
poetry run python render.py data/lsn-12.tsv dist
```

## Usage

1. Create a TSV file following the schema shown in `data/lsn-12.tsv` (one file
   per event).
2. Render it to HTML (outputs land in the directory you pass as the second
   argument, typically `dist/`):

```bash
poetry run python render.py data/lsn-12.tsv dist
```

## Automation

Opening an issue with a `.tsv` attachment triggers
`.github/workflows/render-issue.yml`. The workflow downloads the attachment,
saves it under `data/<event_id>.tsv`, runs `render.py`, and opens a pull request
with the newly generated HTML + TSV. Make sure the attachment follows the schema
below so the workflow can detect the `event_id`.

