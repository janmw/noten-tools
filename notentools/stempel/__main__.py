"""CLI-Entrypoint für noten-stempel.

Stempelt Logo + Archivnummer auf die erste Seite einer oder mehrerer PDFs.
Keine Skalierung, kein Splitting — nur Stempel-Overlay.

Auswahl: Datei-Argumente oder fzf-Mehrfachauswahl im aktuellen Verzeichnis.
Archivnummer wird einmalig abgefragt und gilt für alle Eingabedateien.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from ..shared.config import Config
from ..shared.logging import setup_logger
from ..shared.stamp import stamp_pdf
from ..verarbeitung.prompts import ask_archivnummer
from ..pdf_fix.__main__ import fzf_pick_pdfs_multi


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
        prog="noten-stempel",
        description="Stempelt Logo + Archivnummer auf die erste Seite von PDFs.",
    )
    p.add_argument("files", nargs="*", type=Path,
                   help="PDF(s) direkt angeben (sonst fzf-Mehrfachauswahl).")
    p.add_argument("--nr", type=str, default=None,
                   help="Archivnummer (4-stellig). Ohne Flag: interaktiver Prompt.")
    p.add_argument("--logo", type=Path,
                   help="Alternatives Logo (überschreibt Default aus Config).")
    p.add_argument("--logo-offset", type=_parse_offset, default=(0.0, 0.0),
                   help="Logo-Verschiebung relativ zu Default in mm: 'X,Y' (X=rechts, Y=unten).")
    p.add_argument("--archiv-offset", type=_parse_offset, default=(0.0, 0.0),
                   help="Archivnummer-Verschiebung relativ zu Default in mm: 'X,Y' (X=links, Y=unten).")
    p.add_argument("--backup", action="store_true",
                   help="Vor Überschreiben '<datei>.pdf.bak' anlegen (Default: kein Backup).")
    p.add_argument("--out", type=Path,
                   help="Ausgabe-Pfad (nur sinnvoll bei genau einer Datei).")
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = setup_logger(verbose=args.verbose, quiet=args.quiet, name="noten-stempel")

    Config.write_default_if_missing()
    config = Config.load()
    if args.logo:
        config.logo_path = str(args.logo.expanduser().resolve())

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

    if args.nr is not None:
        nr = args.nr.strip()
        if len(nr) != 4 or not nr.isdigit():
            log.error("--nr muss exakt 4 Ziffern sein.")
            return 2
        archivnummer = nr
    else:
        archivnummer = ask_archivnummer()

    successes = 0
    for src in files:
        if not src.exists():
            log.error(f"Datei nicht gefunden: {src}")
            continue
        if src.suffix.lower() != ".pdf":
            log.warning(f"Überspringe (keine .pdf): {src.name}")
            continue

        log.info(f"[bold]Stempel[/] {src.name} – Nr. {archivnummer}")

        with tempfile.TemporaryDirectory(prefix="noten-stempel-") as tmp:
            stamped = Path(tmp) / "stamped.pdf"
            try:
                stamp_pdf(
                    src,
                    stamped,
                    archivnummer=archivnummer,
                    config=config,
                    logo_offset_mm=args.logo_offset,
                    archiv_offset_mm=args.archiv_offset,
                    first_page_only=True,
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
