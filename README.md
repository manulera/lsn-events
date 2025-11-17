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

## TSV schema

Each TSV uses a **two-column** layout:

```
parameter    value
event_id     lsn-12
event_date   Thursday the 4th of December
...
```

- The first column is the parameter name (each becomes a Jinja variable).
- The second column is the value.

| Parameter | Purpose |
| --- | --- |
| `event_id` | Used for filenames (fallback to TSV filename if omitted). |
| `event_date` / `event_time` | Display-ready strings (e.g. `Thursday the 4th of December`, `18:00`). |
| `institution`, `room_name`, `room_link`, `address` | Venue details with optional directions URL. |
| `registration_link` | CTA/link for sign-ups (optional). |
| `event_description` | Body copy that appears beneath the schedule. |
| `speaker_1_*`, `speaker_2_*` | Use suffixes like `name`, `org`, `lab`, `lab_link`, `emoji`, `talk_title`. |

Add more parameters as needed—every entry becomes available inside the template.
