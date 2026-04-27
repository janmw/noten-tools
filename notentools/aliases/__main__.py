"""noten-tools-aliases — Verwaltung gelernter Aliase.

Subkommandos:
  list   — listet alle gelernten Aliase
  sync   — vergleicht learned_aliases.yaml mit data/instruments.yaml und schlägt
           Repo-fähige Ergänzungen vor (Ausgabe als YAML-Patch zur manuellen
           Übernahme oder als PR-Vorschlag).
  clear  — löscht alle gelernten Aliase
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from ..shared.paths import learned_aliases_file, instruments_yaml


def cmd_list(_args) -> int:
    path = learned_aliases_file()
    if not path.exists():
        print(f"Keine gelernten Aliase ({path} existiert nicht).")
        return 0
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not data:
        print("Keine gelernten Aliase.")
        return 0
    for raw, ident in sorted(data.items()):
        print(f"  {raw!r:40s} -> {ident}")
    return 0


def cmd_clear(_args) -> int:
    path = learned_aliases_file()
    if path.exists():
        path.unlink()
        print(f"Gelöscht: {path}")
    else:
        print("Nichts zu löschen.")
    return 0


def cmd_sync(_args) -> int:
    learned_path = learned_aliases_file()
    if not learned_path.exists():
        print("Keine learned_aliases.yaml gefunden.")
        return 0
    with learned_path.open("r", encoding="utf-8") as fh:
        learned = yaml.safe_load(fh) or {}
    if not learned:
        print("learned_aliases.yaml ist leer.")
        return 0

    with instruments_yaml().open("r", encoding="utf-8") as fh:
        repo = yaml.safe_load(fh) or {}

    suggestions: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    skipped: list[str] = []

    for raw_text, identifier in learned.items():
        m = re.match(r"^(\d{2})\s+(.+?)(?:\s+(\d+))?(?:\s+(in [A-Za-zäöüß]+))?$", identifier.strip())
        if not m:
            skipped.append(raw_text)
            continue
        code = m.group(1)
        instrument = m.group(2).strip()
        if code not in repo or instrument not in (repo[code] or {}):
            skipped.append(raw_text)
            continue
        existing_aliases = set(a.lower() for a in repo[code][instrument].get("aliases", []))
        if raw_text.lower() in existing_aliases:
            continue
        suggestions[code][instrument].append(raw_text)

    if not suggestions:
        print("Keine neuen Aliase, die ins Repo übernommen werden müssten.")
        if skipped:
            print(f"Hinweis: {len(skipped)} Einträge konnten keinem Repo-Instrument zugeordnet werden.")
        return 0

    print("# Vorschläge zur Aufnahme in data/instruments.yaml:")
    print("# (kopiere die jeweiligen Listeneinträge unter aliases: des Instruments)")
    print()
    for code in sorted(suggestions.keys()):
        for instrument in sorted(suggestions[code].keys()):
            print(f'"{code}":')
            print(f"  {instrument}:")
            print(f"    aliases:")
            for alias in sorted(set(suggestions[code][instrument])):
                print(f"      - {alias!r}")
            print()
    if skipped:
        print(f"# {len(skipped)} Einträge übersprungen (nicht zu Repo-Instrument zuordenbar):")
        for s in skipped:
            print(f"#   {s}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="noten-tools-aliases")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="Alle gelernten Aliase anzeigen")
    sub.add_parser("sync", help="Aliase als Repo-Patch-Vorschlag ausgeben")
    sub.add_parser("clear", help="Alle gelernten Aliase löschen")
    args = parser.parse_args(argv)
    handlers = {"list": cmd_list, "sync": cmd_sync, "clear": cmd_clear}
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
