# Notes for Future Agents

This repository generates and publishes ICS calendars for die Gemeinde Birkenfeld (Enzkreis). The following points summarise conventions and gotchas discovered while putting the project together. Please keep them in mind when extending the repo.

## Coding Standards
- Target Python 3.10+. Use native generics (`list`, `dict`, etc.) and timezone-aware datetimes (`datetime.now(datetime.UTC)`).
- Keep the generator dependency-free; it currently relies only on the standard library.
- ICS events must remain all-day and marked as informational: include `TRANSP:TRANSPARENT`, `STATUS:CONFIRMED`, and a `LAST-MODIFIED` timestamp.
- Sanitize ICS text fields per RFC 5545 (escape `\`, `;`, `,`, newlines). Always emit CRLF line endings.
- Print concise CLI output summarising generated files; avoid noisy logging when running in GitHub Actions.

## Linting & Formatting
- Ruff handles both formatting and linting (`line-length = 100`, `target-version = py310`).
- Common dev commands:
  ```bash
  uv run --extra dev ruff format --check .
  uv run --extra dev ruff check .
  python generate_ics.py
  ```
- `.gitignore` already excludes `.venv/`, `.ruff_cache/`, `*.egg-info/`, `uv.lock`; don’t commit tooling artefacts.

## Automation
- `.github/workflows/update.yml` regenerates calendars daily at 04:00 UTC (and on manual dispatch) and commits changes automatically.
- `.github/workflows/ci.yml` runs Ruff + the generator on push/PR/manual runs. Keep workflows lightweight—no secrets required.

## Publishing & UX
- GitHub Pages serves from `docs/`; keep that layout unless you also change the Pages configuration.
- `docs/index.html` is intentionally framework-free. If you tweak the copy/JS, test the Google Calendar flow manually—Google still requires users to paste the URL.
- The page copies feed URLs to the clipboard and opens Google’s “Kalender per URL hinzufügen” screen; do not promise true one-click subscriptions (Google doesn’t support it).

## Data Source Notes
- API endpoint: `https://www.birkenfeld-enzkreis.de/api/cms/abfalltermine` with `seite`, `pro_seite`, and ``order[]=`datum` ASC``. The script fetches all pages.
- `abfuhrgebiet` currently includes `Birkenfeld`, `Gräfenhausen`, and `Recyclinghof`. Group events dynamically; don’t hardcode area names.
- Expect future years: the data presently covers late 2025. Handle empty or evolving schema gracefully.

## Collaboration
- During active iteration we amend & force-push; once stable, prefer additive commits for traceability.
- Keep README and the landing page instructions up to date—they are user-facing.
- When adding features, favour clarity over cleverness. The goal is a maintainable public feed, not a complex app.
