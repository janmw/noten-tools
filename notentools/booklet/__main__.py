"""CLI-Entrypoint für noten-booklet.

Löst A3-Booklet-Scans in A4-Seiten in korrekter Reihenfolge auf.

Modi:
  partitur  — gesamtes PDF ist ein Multi-Sheet-Booklet (Klassischer Partitur-Scan)
  noten     — pro A3-Blatt entweder Single-Sheet-Booklet (4 A4) oder fortlaufend (1|2 / 3|4)

Erwartet pro A3-Blatt zwei aufeinanderfolgende Eingabe-Seiten (Vorderseite, Rückseite).
Eingabe muss eine gerade Anzahl Seiten haben.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

from ..shared.logging import setup_logger
from ..verarbeitung.prompts import fzf_pick_pdf


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="noten-booklet",
        description="A3-Booklet-Scans in A4-Reihenfolge auflösen.",
    )
    sub = p.add_subparsers(dest="mode", required=True)

    p_part = sub.add_parser(
        "partitur",
        help="Multi-Sheet-Booklet (klassischer Partitur-Scan).",
        description="Gesamtes PDF ist ein einziger Booklet-Satz mit N A3-Blättern → 4N A4-Seiten.",
    )
    _add_common_args(p_part)

    p_noten = sub.add_parser(
        "noten",
        help="Pro A3-Blatt Booklet oder fortlaufend.",
        description="Jedes A3-Blatt ist unabhängig: entweder 4-Seiten-Booklet oder fortlaufend (1|2 / 3|4).",
    )
    _add_common_args(p_noten)
    grp = p_noten.add_mutually_exclusive_group()
    grp.add_argument(
        "--all-booklet", action="store_true",
        help="Alle Blätter als Single-Sheet-Booklet behandeln (überspringt die Frage).",
    )
    grp.add_argument(
        "--all-continuous", action="store_true",
        help="Alle Blätter als fortlaufend behandeln (überspringt die Frage).",
    )
    return p


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", nargs="?", type=Path,
                   help="A3-Scan-PDF (ohne Argument: fzf-Auswahl im aktuellen Verzeichnis).")
    p.add_argument("--out", type=Path,
                   help="Ausgabe-Pfad (Default: Eingabedatei wird überschrieben).")
    p.add_argument("--backup", action="store_true",
                   help="Vor Überschreiben '<datei>.pdf.bak' anlegen (Default: kein Backup).")
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")


# ---------------------------------------------------------------------------
# Reordering-Logik
# ---------------------------------------------------------------------------


def partitur_ordering(num_input_pages: int) -> list[tuple[int, str]]:
    """Multi-Sheet-Booklet: ganzer Notensatz ist EIN Booklet.

    num_input_pages = 2 * S Blätter, ergibt N = 4 * S logische A4-Seiten.
    Imposition pro Blatt i (1..S):
        front_L = N + 2 - 2i,  front_R = 2i - 1
        back_L  = 2i,          back_R  = N + 1 - 2i
    """
    if num_input_pages % 2 != 0:
        raise ValueError("Anzahl Seiten muss gerade sein (Vorder- + Rückseite jedes Blatts).")
    s = num_input_pages // 2
    n = 4 * s
    mapping: dict[int, tuple[int, str]] = {}
    for i in range(1, s + 1):
        front_idx = 2 * (i - 1)
        back_idx = 2 * (i - 1) + 1
        mapping[n + 2 - 2 * i] = (front_idx, "L")
        mapping[2 * i - 1] = (front_idx, "R")
        mapping[2 * i] = (back_idx, "L")
        mapping[n + 1 - 2 * i] = (back_idx, "R")
    return [mapping[k] for k in range(1, n + 1)]


def noten_ordering(sheet_modes: list[str]) -> list[tuple[int, str]]:
    """Noten-Modus: pro A3-Blatt eigene Reihenfolge.

    sheet_modes[i] ∈ {"B", "C"} für Booklet bzw. fortlaufend.
    Booklet pro Blatt:    front_L=4, front_R=1, back_L=2, back_R=3
    Fortlaufend pro Blatt: front_L=1, front_R=2, back_L=3, back_R=4
    """
    out: list[tuple[int, str]] = []
    for sheet_i, mode in enumerate(sheet_modes):
        front_idx = 2 * sheet_i
        back_idx = 2 * sheet_i + 1
        if mode == "B":
            out += [(front_idx, "R"), (back_idx, "L"), (back_idx, "R"), (front_idx, "L")]
        elif mode == "C":
            out += [(front_idx, "L"), (front_idx, "R"), (back_idx, "L"), (back_idx, "R")]
        else:
            raise ValueError(f"Unbekannter Modus '{mode}' (erwartet 'B' oder 'C').")
    return out


# ---------------------------------------------------------------------------
# PDF-Splitting (MediaBox/CropBox auf eine Hälfte setzen)
# ---------------------------------------------------------------------------


def split_halves(input_path: Path, output_path: Path,
                 ordered_halves: list[tuple[int, str]]) -> None:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for orig_idx, half in ordered_halves:
        src_page = reader.pages[orig_idx]
        new_page = writer.add_page(src_page)
        mb = new_page.mediabox
        left = float(mb.left)
        bottom = float(mb.bottom)
        right = float(mb.right)
        top = float(mb.top)
        mid = left + (right - left) / 2

        if half == "L":
            new_box = RectangleObject((left, bottom, mid, top))
        else:
            new_box = RectangleObject((mid, bottom, right, top))

        new_page.mediabox = new_box
        new_page.cropbox = new_box
        new_page.trimbox = new_box
        new_page.bleedbox = new_box
        new_page.artbox = new_box

    with open(output_path, "wb") as fh:
        writer.write(fh)


# ---------------------------------------------------------------------------
# Interaktive Pro-Blatt-Auswahl im Noten-Modus
# ---------------------------------------------------------------------------


def ask_sheet_modes(num_sheets: int, input_path: Path, log) -> list[str]:
    """Fragt pro A3-Blatt: Booklet (default) oder fortlaufend.

    Tasten:  ENTER = Booklet, f = fortlaufend, v = Vorschau, z = zurück, q = abbrechen
    """
    print(f"\nNotensatz hat {num_sheets} A3-Blatt(e) (= {4 * num_sheets} A4-Seiten).")
    print("ENTER = Booklet (Default)   f = fortlaufend   v = Vorschau   z = zurück   q = abbrechen\n")

    preview_files: list[Path] = []
    modes: list[str] = []
    i = 0
    while i < num_sheets:
        prefix = f"Blatt {i + 1}/{num_sheets}"
        prev_hint = f" (zurück: z)" if i > 0 else ""
        ans = input(f"{prefix}{prev_hint} > ").strip().lower()
        if ans == "" or ans == "b":
            modes.append("B")
            i += 1
        elif ans == "f":
            modes.append("C")
            i += 1
        elif ans == "v":
            pf = _open_sheet_preview(input_path, i + 1, log)
            if pf is not None:
                preview_files.append(pf)
        elif ans == "z":
            if i > 0:
                i -= 1
                modes.pop()
            else:
                print("  Schon am Anfang — nichts zum Zurückgehen.")
        elif ans == "q":
            _cleanup_previews(preview_files)
            raise KeyboardInterrupt
        else:
            print(f"  Unbekannt: '{ans}'. ENTER/b = Booklet, f = fortlaufend, v = Vorschau, z = zurück, q = abbrechen.")

    booklet_count = modes.count("B")
    cont_count = modes.count("C")
    print(f"\n→ {booklet_count} Booklet, {cont_count} fortlaufend.")
    _cleanup_previews(preview_files)
    return modes


def _open_sheet_preview(input_path: Path, sheet_idx: int, log) -> Path | None:
    """Schreibt Vorder + Rückseite des gewählten Blatts in eine Temp-PDF und öffnet xdg-open."""
    try:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        front_idx = 2 * (sheet_idx - 1)
        back_idx = front_idx + 1
        writer.add_page(reader.pages[front_idx])
        writer.add_page(reader.pages[back_idx])

        tmp = tempfile.NamedTemporaryFile(
            prefix=f"booklet-vorschau-blatt{sheet_idx:02d}-",
            suffix=".pdf",
            delete=False,
        )
        tmp.close()
        with open(tmp.name, "wb") as fh:
            writer.write(fh)

        subprocess.Popen(
            ["xdg-open", tmp.name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return Path(tmp.name)
    except Exception as exc:
        log.warning(f"Vorschau Blatt {sheet_idx} konnte nicht geöffnet werden: {exc}")
        return None


def _cleanup_previews(preview_files: list[Path]) -> None:
    for pf in preview_files:
        try:
            pf.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = setup_logger(verbose=args.verbose, quiet=args.quiet, name="noten-booklet")

    if args.file:
        src = args.file.expanduser().resolve()
    else:
        picked = fzf_pick_pdf(Path.cwd())
        if picked is None:
            log.warning("Keine Datei ausgewählt — Abbruch.")
            return 0
        src = picked

    if not src.exists():
        log.error(f"Datei nicht gefunden: {src}")
        return 1
    if src.suffix.lower() != ".pdf":
        log.error(f"Keine .pdf-Datei: {src}")
        return 2

    reader = PdfReader(str(src))
    num_pages = len(reader.pages)
    if num_pages < 2 or num_pages % 2 != 0:
        log.error(
            f"Eingabe-PDF hat {num_pages} Seiten — gerade Anzahl ≥ 2 erforderlich "
            "(je A3-Blatt eine Vorder- und eine Rückseite)."
        )
        return 2
    num_sheets = num_pages // 2

    if args.mode == "partitur":
        log.info(f"Partitur-Modus: {num_sheets} A3-Blatt → {4 * num_sheets} A4-Seiten")
        ordered = partitur_ordering(num_pages)
    else:
        if args.all_booklet:
            log.info(f"Noten-Modus: alle {num_sheets} Blätter als Booklet")
            modes = ["B"] * num_sheets
        elif args.all_continuous:
            log.info(f"Noten-Modus: alle {num_sheets} Blätter als fortlaufend")
            modes = ["C"] * num_sheets
        else:
            try:
                modes = ask_sheet_modes(num_sheets, src, log)
            except KeyboardInterrupt:
                log.warning("Abgebrochen durch Benutzer.")
                return 130
        ordered = noten_ordering(modes)

    with tempfile.TemporaryDirectory(prefix="noten-booklet-") as tmp_root:
        result = Path(tmp_root) / "result.pdf"
        try:
            split_halves(src, result, ordered)
        except Exception as exc:
            log.error(f"Fehler beim Splitten: {exc}")
            return 1

        if args.out is not None:
            target = args.out.expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(result, target)
            log.info(f"[green]→ Ergebnis:[/] {target}")
        else:
            if args.backup:
                bak = src.with_suffix(src.suffix + ".bak")
                shutil.copy2(src, bak)
                log.info(f"Backup angelegt: {bak.name}")
            shutil.copy2(result, src)
            log.info(f"[green]→ Aktualisiert:[/] {src.name}")

    log.info(f"[bold green]Fertig.[/] {len(ordered)} A4-Seiten geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
