#!/usr/bin/env python3
"""Fetch waste collection dates and generate ICS calendars."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any

API_URL = "https://www.birkenfeld-enzkreis.de/api/cms/abfalltermine"
WEBSITE_URL = "https://www.birkenfeld-enzkreis.de/abfallkalender/"
OUTPUT_DIR = Path("docs")
REQUEST_TIMEOUT = 30


def fetch_page(page: int, per_page: int) -> dict[str, Any]:
    params = {
        "seite": page,
        "pro_seite": per_page,
        "order[]": "`datum` ASC",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:
        payload = json.load(response)
    return payload


def fetch_all(per_page: int = 50) -> list[dict[str, Any]]:
    page = 1
    all_items: list[dict[str, Any]] = []
    while True:
        payload = fetch_page(page, per_page)
        all_items.extend(payload.get("data", []))
        if page >= payload.get("seiten", page):
            break
        page += 1
    return all_items


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.replace("/", "-")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug or "kalender"


def escape_ics_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")


def event_lines(item: dict[str, Any]) -> list[str]:
    event_date = dt.date.fromisoformat(item["datum"])
    dtstart = event_date.strftime("%Y%m%d")
    dtend = (event_date + dt.timedelta(days=1)).strftime("%Y%m%d")
    summary = item.get("abfuhrart", "Abfuhrtermin")
    remarks = item.get("bemerkung") or ""
    description_parts = [
        f"Abfuhrart: {summary}",
        f"Gebiet: {item.get('abfuhrgebiet', 'unbekannt')}",
    ]
    if remarks:
        description_parts.append(f"Hinweis: {remarks}")
    description_parts.append(f"Quelle: {WEBSITE_URL}")
    description = "\n".join(description_parts)
    uid = f"{item.get('id', '')}@abfalltermine-birkenfeld-enzkreis"
    timestamp_dt = dt.datetime.combine(event_date, dt.time(), tzinfo=dt.timezone.utc)
    timestamp = timestamp_dt.strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VEVENT",
        f"UID:{escape_ics_text(uid)}",
        f"SUMMARY:{escape_ics_text(summary)}",
        f"DTSTAMP:{timestamp}",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        "CATEGORIES:Abfallentsorgung",
        "TRANSP:TRANSPARENT",
        "X-MICROSOFT-CDO-BUSYSTATUS:FREE",
        f"DESCRIPTION:{escape_ics_text(description)}",
        "STATUS:CONFIRMED",
        f"URL:{escape_ics_text(WEBSITE_URL)}",
        "END:VEVENT",
    ]
    return lines


def build_calendar(title: str, items: Iterable[dict[str, Any]]) -> str:
    def sort_key(entry: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            entry.get("datum") or "",
            entry.get("abfuhrart") or "",
            entry.get("abfuhrgebiet") or "",
            str(entry.get("id") or ""),
        )

    items = sorted(items, key=sort_key)
    cal_desc = f"Abfuhrtermine – {title}"
    cal_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//yaugenst//abfalltermine-birkenfeld-enzkreis//DE",
        "CALSCALE:GREGORIAN",
        f"NAME:{escape_ics_text(title)}",
        f"X-WR-CALNAME:{escape_ics_text(title)}",
        f"X-WR-CALDESC:{escape_ics_text(cal_desc)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for item in items:
        cal_lines.extend(event_lines(item))
    cal_lines.append("END:VCALENDAR")
    return "\r\n".join(cal_lines) + "\r\n"


def write_calendars(items: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    by_area: dict[str, list[dict[str, Any]]] = {}
    for entry in items:
        area = entry.get("abfuhrgebiet", "Unbekannt")
        by_area.setdefault(area, []).append(entry)

    for area, entries in sorted(by_area.items()):
        title = f"Abfalltermine {area}"
        calendar_text = build_calendar(title, entries)
        filename = OUTPUT_DIR / f"{slugify(area)}.ics"
        filename.write_text(calendar_text, encoding="utf-8")

    all_calendar = build_calendar("Abfalltermine Birkenfeld (gesamt)", items)
    (OUTPUT_DIR / "alle.ics").write_text(all_calendar, encoding="utf-8")

    summary_lines = ["Generierte Kalender:"]
    for path in sorted(OUTPUT_DIR.glob("*.ics")):
        summary_lines.append(f"  - {path.as_posix()}")
    print("\n".join(summary_lines))


def main() -> int:
    try:
        items = fetch_all()
    except urllib.error.URLError as exc:  # pragma: no cover - network failure
        print(f"Fehler beim Abruf der Daten: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("Keine Termine gefunden", file=sys.stderr)
        return 1

    write_calendars(items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
