"""CLI-Entrypoint für noten-ausgabe.

Stempelt '[Name] - [Datum]' in 7 pt JetBrains Mono unten mittig auf jede Seite einer
oder mehrerer PDFs. Datum-Default: heute im deutschen Format (TT.MM.JJJJ).
Name wird interaktiv abgefragt; der zuletzt verwendete Name wird in der Config
gecached und als Default-Vorschlag angezeigt.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

from ..pdf_fix.__main__ import fzf_pick_pdfs_multi
from ..shared.config import Config
from ..shared.logging import setup_logger
from ..shared.stamp import stamp_footer


def _parse_offset(value: str) -> tuple[float, float]:
    if not value:
        return (0.0, 0.0)
    parts = [p.strip() for p in value.replace(";", ",").split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Offset muss als 'X,Y' in mm angegeben werden")
    try:
        return (float(parts[0]), float(parts[1]))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="noten-ausgabe",
        description="Kleinen Ausgabe-Stempel '[Name] - [Datum]' unten mittig auf jede Seite stempeln.",
    )
    p.add_argument("files", nargs="*", type=Path,
                   help="PDF(s) direkt angeben (sonst fzf-Mehrfachauswahl).")
    p.add_argument("--name", type=str, default=None,
                   help="Name direkt setzen (sonst interaktiver Prompt).")
    p.add_argument("--datum", type=str, default=None,
                   help="Datum direkt setzen, wörtlich gestempelt (Default: heute TT.MM.JJJJ).")
    p.add_argument("--offset", type=_parse_offset, default=(0.0, 0.0),
                   help="Position-Verschiebung in mm: 'X,Y' (X=rechts, Y=oben).")
    p.add_argument("--font", type=Path,
                   help="Alternative TTF-Datei für den Stempel.")
    p.add_argument("--backup", action="store_true",
                   help="Vor Überschreiben '<datei>.pdf.bak' anlegen (Default: kein Backup).")
    p.add_argument("--out", type=Path,
                   help="Ausgabe-Pfad (nur sinnvoll bei genau einer Datei).")
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")
    return p


def _ask_name(default: str) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        ans = input(f"Name{suffix}: ").strip()
        if ans:
            return ans
        if default:
            return default
        print("  Bitte einen Namen eingeben.")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = setup_logger(verbose=args.verbose, quiet=args.quiet, name="noten-ausgabe")

    Config.write_default_if_missing()
    config = Config.load()

    if args.files:
        files = [f.expanduser().resolve() for f in args.files]
    else:
        files = fzf_pick_pdfs_multi(Path.cwd())

    if not files:
        log.warning("Keine Datei ausgewählt — Abbruch.")
        return 0

    if args.out is not None and len(files) > 1:
        log.error("--out ist nur bei genau einer Eingabedatei zulässig.")
        return 2

    # Name bestimmen
    if args.name is not None:
        name = args.name.strip()
        if not name:
            log.error("--name darf nicht leer sein.")
            return 2
    else:
        name = _ask_name(default=config.ausgabe_name)

    # Cache aktualisieren, wenn sich der Name geändert hat
    if name != config.ausgabe_name:
        config.ausgabe_name = name
        try:
            config.save()
        except Exception as exc:
            log.warning(f"Name konnte nicht in Config gespeichert werden: {exc}")

    # Datum bestimmen
    if args.datum is not None:
        datum_str = args.datum.strip()
        if not datum_str:
            log.error("--datum darf nicht leer sein.")
            return 2
    else:
        datum_str = date.today().strftime("%d.%m.%Y")

    text = f"{name} - {datum_str}"
    log.info(f"[bold]Stempel-Text:[/] {text!r}")

    successes = 0
    for src in files:
        if not src.exists():
            log.error(f"Datei nicht gefunden: {src}")
            continue
        if src.suffix.lower() != ".pdf":
            log.warning(f"Überspringe (keine .pdf): {src.name}")
            continue

        log.info(f"[bold]Stempel[/] {src.name}")

        with tempfile.TemporaryDirectory(prefix="noten-ausgabe-") as tmp:
            stamped = Path(tmp) / "stamped.pdf"
            try:
                stamp_footer(
                    src,
                    stamped,
                    text=text,
                    config=config,
                    offset_mm=args.offset,
                    font_path=args.font,
                )
            except Exception as exc:
                log.error(f"Stempel fehlgeschlagen für {src.name}: {exc}")
                continue

            if args.out is not None:
                target = args.out.expanduser().resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(stamped, target)
                log.info(f"[green]→ Ergebnis:[/] {target}")
            else:
                if args.backup:
                    backup = src.with_suffix(src.suffix + ".bak")
                    shutil.copy2(src, backup)
                    log.info(f"Backup angelegt: {backup.name}")
                shutil.copy2(stamped, src)
                log.info(f"[green]→ Aktualisiert:[/] {src.name}")
            successes += 1

    total = len(files)
    if successes == total:
        log.info(f"[bold green]Fertig.[/] {successes}/{total} Datei(en) gestempelt.")
        return 0
    log.warning(f"Abgeschlossen mit Fehlern: {successes}/{total} erfolgreich.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
