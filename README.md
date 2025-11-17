# lsn-events

Generate plain HTML event announcements by combining a TSV data file with the
existing `template.html` (exported from Word). The project uses Poetry for
dependency management and Jinja2 for templating, but the actual rendering tool
is a single script (`render.py`) that only needs two arguments: the TSV file and
output directory.

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/) 1.8+

## Installation

```bash
cd /Users/manu/Documents/mini_projects/lsn_templates
poetry install
```

The install step creates the virtualenv, locks dependencies, and exposes the
`render-events` script.

## Usage

1. Create a TSV file per event (see the schema below). Two examples live under
   `data/`.
2. Update `template.html` if you need new placeholders. The file stays plain
   HTML—Jinja only acts at render time.
3. Render a page:

```bash
poetry run python render.py data/building-trustworthy-ai.tsv dist
```

Each TSV produces `dist/<event_id>.html`. The script never mutates
`template.html`, so you can keep editing that Word-exported file independently.

## TSV schema

Each TSV uses a **two-column** structure:

```
parameter    value
event_id   building-trustworthy-ai
event_date   Thursday the 4th of December
...

event_id   biodesign-for-planetary-health
...
```

- The first column is the parameter name (each becomes a Jinja variable).
- The second column is the value.
- One file equals one event—create a new TSV whenever you need another page.

| Parameter | Purpose |
| --- | --- |
| `event_id` | Used for filenames (fallback to TSV filename if omitted). |
| `event_date` / `event_time` | Display-ready strings (e.g. `Thursday the 4th of December`, `18:00`). |
| `institution` | Partner org or host school. |
| `room_name`, `room_link`, `address` | Venue details with optional directions URL. |
| `registration_link` | CTA/link for sign-ups. |
| `event_description` | Rich text blurb appearing in the body copy. |
| `speaker_1_*`, `speaker_2_*` | Use suffixes `name`, `org`, `talk_title`. |

Add more parameters as needed—every entry becomes available inside the template.

### Speaker blocks

Columns that follow the pattern `speaker_<n>_<field>` are grouped into a
`speakers` list within the template context. Example usage inside
`template.html`:

```
{% for speaker in speakers %}
  <p>{{ speaker.name }} — {{ speaker.title }} ({{ speaker.org }})</p>
{% endfor %}
```

You still get the flat column names (`speaker_1_name`, etc.) if you prefer not
to loop.

### Location helper

A nested `location` object is also provided:

```
{{ location.campus }} • {{ location.room_name }}
<a href="{{ location.room_link }}">{{ location.address }}</a>
```

## Development notes

- `src/lsn_events/cli.py` contains the TSV parsing + rendering workflow.
- The CLI never mutates `template.html`; it simply loads it as a Jinja template
  and renders it for each row in the TSV file.
- Additional dependencies can be added via `poetry add <package>` as needed.
