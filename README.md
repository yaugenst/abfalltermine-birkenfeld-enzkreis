# Abfalltermine Birkenfeld (Enzkreis)

Dieses Repository erzeugt ICS-Kalenderdateien mit den Abfuhrterminen der Gemeinde Birkenfeld (Enzkreis). Die Rohdaten stammen aus dem offiziellen Abfallkalender der Gemeinde und werden automatisch in abonnierbare Kalender umgesetzt.

## Datenquelle
- Gemeinde Birkenfeld – Abfallkalender: <https://www.birkenfeld-enzkreis.de/abfallkalender/>

## Verfügbare Kalender
Nach dem Aktivieren von GitHub Pages (Branch `main`, Ordner `docs`) steht eine Übersichtsseite unter
<https://yaugenst.github.io/abfalltermine-birkenfeld-enzkreis/> bereit.

Direkt-URLs zu den ICS-Dateien:

- `https://yaugenst.github.io/abfalltermine-birkenfeld-enzkreis/alle.ics`
- `https://yaugenst.github.io/abfalltermine-birkenfeld-enzkreis/birkenfeld.ics`
- `https://yaugenst.github.io/abfalltermine-birkenfeld-enzkreis/grafenhausen.ics`
- `https://yaugenst.github.io/abfalltermine-birkenfeld-enzkreis/recyclinghof.ics`

## Kalender abonnieren (Beispiel Google Kalender)
1. In Google Kalender auf „Weitere Kalender“ → „Per URL“ klicken.
2. Die gewünschte ICS-URL aus der Liste oben einfügen.
3. Mit „Kalender hinzufügen“ bestätigen. Die Termine werden künftig automatisch synchronisiert.

## Automatische Aktualisierung
- Das Skript [`generate_ics.py`](./generate_ics.py) lädt die JSON-Daten aus dem CMS und erzeugt die Dateien in `docs/`.
- Ein GitHub Actions Workflow (`.github/workflows/update.yml`) läuft einmal täglich sowie bei manueller Auslösung und committed geänderte Dateien automatisch.

## Entwicklung
```bash
# Formatierung und Linting prüfen (uv holt die Dev-Abhängigkeiten)
uv run --extra dev ruff format --check .
uv run --extra dev ruff check .

# Kalender lokal erzeugen
python generate_ics.py
```
Die aktuellen ICS-Dateien werden dabei lokal in `docs/` aktualisiert.
