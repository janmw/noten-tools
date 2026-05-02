"""CLI-Entrypoint für noten-scantailor.

Drei Subcommands rund um den Scan-Tailor-Advanced-Workflow:

  extract   PDF -> PNGs im gewählten Ordner (via pdftoppm)
  assemble  Ordner mit Scan-Tailor-Ausgabe (TIFF/PNG) -> PDF (via ImageMagick)
  run       extract -> Scan Tailor öffnen -> auf ENTER warten -> assemble

Externe Werkzeuge: pdftoppm (poppler-utils), magick (ImageMagick),
optional scantailor-advanced. Verfügbarkeit wird beim ersten Aufruf
geprüft, mit Hinweis auf install.sh / Distri-Pakete.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from ..shared.logging import setup_logger
from ..verarbeitung.prompts import fzf_pick_pdf


SCANTAILOR_BINS = ("scantailor-advanced", "scantailor", "ScanTailor-Advanced")
DEFAULT_EXTRACT_GLOB = "*.tif"


# ---------------------------------------------------------------------------
# Externe Tools
# ---------------------------------------------------------------------------


def _which_or_die(binary: str, hint: str) -> str:
    path = shutil.which(binary)
    if path is None:
        raise SystemExit(f"'{binary}' nicht gefunden. {hint}")
    return path


def _find_scantailor() -> str | None:
    for name in SCANTAILOR_BINS:
        path = shutil.which(name)
        if path is not None:
            return path
    return None


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------


def run_pdftoppm(pdf: Path, out_dir: Path, dpi: int, log) -> None:
    """PDF -> PNGs in out_dir (Prefix 'Seite', identisch zum manuellen Workflow)."""
    pdftoppm = _which_or_die(
        "pdftoppm",
        "Benötigt aus 'poppler-utils' (Arch: poppler, Debian: poppler-utils).",
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "Seite"
    cmd = [pdftoppm, "-png", "-r", str(dpi), str(pdf), str(prefix)]
    log.info(f"pdftoppm {pdf.name} → {out_dir} (dpi={dpi})")
    subprocess.run(cmd, check=True)


def cmd_extract(args, log) -> int:
    src = _resolve_input_pdf(args.pdf, log)
    if src is None:
        return 2

    out_dir = _resolve_extract_dir(args.out_dir, src)
    if out_dir.exists() and any(out_dir.iterdir()) and not args.force:
        log.error(
            f"Zielordner '{out_dir}' nicht leer. Mit --force überschreiben "
            "oder anderen --out-dir wählen."
        )
        return 1

    try:
        run_pdftoppm(src, out_dir, args.dpi, log)
    except subprocess.CalledProcessError as exc:
        log.error(f"pdftoppm-Fehler: {exc}")
        return 1

    pages = sorted(out_dir.glob("Seite-*.png"))
    log.info(f"[bold green]Fertig.[/] {len(pages)} PNG(s) in {out_dir}")
    return 0


# ---------------------------------------------------------------------------
# assemble
# ---------------------------------------------------------------------------


def run_magick(images: list[Path], out_pdf: Path, log) -> None:
    """Bilder -> Output-PDF via ImageMagick."""
    magick = _which_or_die(
        "magick",
        "Benötigt 'ImageMagick' (Arch: imagemagick, Debian: imagemagick).",
    )
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [magick, *[str(p) for p in images], str(out_pdf)]
    log.info(f"magick → {out_pdf} ({len(images)} Bilder)")
    subprocess.run(cmd, check=True)


def cmd_assemble(args, log) -> int:
    src_dir = args.dir.expanduser().resolve()
    if not src_dir.is_dir():
        log.error(f"Ordner nicht gefunden: {src_dir}")
        return 2

    images = sorted(src_dir.glob(args.glob))
    if not images:
        log.error(
            f"Keine Bilder mit Muster '{args.glob}' in {src_dir}. "
            "Anderen --glob versuchen, z.B. '*.png'."
        )
        return 1

    out_pdf = _resolve_assemble_out(args.out, src_dir)
    try:
        run_magick(images, out_pdf, log)
    except subprocess.CalledProcessError as exc:
        log.error(f"magick-Fehler: {exc}")
        return 1

    log.info(f"[bold green]Fertig.[/] {out_pdf}")
    return 0


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


def cmd_run(args, log) -> int:
    src = _resolve_input_pdf(args.pdf, log)
    if src is None:
        return 2

    workdir = _resolve_extract_dir(args.workdir, src)
    if workdir.exists() and any(workdir.iterdir()) and not args.force:
        log.error(
            f"Workdir '{workdir}' nicht leer. Mit --force überschreiben "
            "oder anderen --workdir wählen."
        )
        return 1

    try:
        run_pdftoppm(src, workdir, args.dpi, log)
    except subprocess.CalledProcessError as exc:
        log.error(f"pdftoppm-Fehler: {exc}")
        return 1

    pages = sorted(workdir.glob("Seite-*.png"))
    log.info(f"{len(pages)} PNG(s) extrahiert in {workdir}")

    if not args.no_launch:
        st_path = _find_scantailor()
        if st_path is None:
            log.warning(
                "Scan Tailor nicht gefunden — bitte manuell starten und den "
                f"Ordner {workdir} öffnen."
            )
        else:
            log.info(f"Starte {Path(st_path).name} …")
            try:
                subprocess.Popen(
                    [st_path, str(workdir)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError as exc:
                log.warning(f"Scan Tailor konnte nicht gestartet werden: {exc}")

    print(
        f"\nScan Tailor bearbeiten und Ausgabe in '{workdir}' ablegen "
        f"(erwartetes Muster: {args.glob}).\n"
        "Wenn fertig: ENTER drücken — q + ENTER bricht ab."
    )
    try:
        ans = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        log.warning("Abgebrochen.")
        return 130
    if ans == "q":
        log.warning("Abgebrochen durch Benutzer.")
        return 130

    images = sorted(workdir.glob(args.glob))
    if not images:
        log.error(
            f"Keine Bilder mit Muster '{args.glob}' in {workdir}. "
            "Wurde Scan Tailor ausgeführt? --glob anpassen, oder "
            "'noten-scantailor assemble' separat aufrufen."
        )
        return 1

    out_pdf = _resolve_run_out(args.out, src)
    try:
        run_magick(images, out_pdf, log)
    except subprocess.CalledProcessError as exc:
        log.error(f"magick-Fehler: {exc}")
        return 1

    log.info(f"[bold green]Fertig.[/] {out_pdf}")
    return 0


# ---------------------------------------------------------------------------
# Pfad-Auflösung
# ---------------------------------------------------------------------------


def _resolve_input_pdf(arg: Path | None, log) -> Path | None:
    if arg is not None:
        src = arg.expanduser().resolve()
    else:
        picked = fzf_pick_pdf(Path.cwd())
        if picked is None:
            log.warning("Keine Datei ausgewählt — Abbruch.")
            return None
        src = picked
    if not src.exists():
        log.error(f"Datei nicht gefunden: {src}")
        return None
    if src.suffix.lower() != ".pdf":
        log.error(f"Keine .pdf-Datei: {src}")
        return None
    return src


def _resolve_extract_dir(arg: Path | None, src: Path) -> Path:
    """Default: <src-stem>-pages/ neben der Eingabedatei."""
    if arg is not None:
        return arg.expanduser().resolve()
    return (src.parent / f"{src.stem}-pages").resolve()


def _resolve_assemble_out(arg: Path | None, src_dir: Path) -> Path:
    """Default: <ordnername>.pdf neben dem Ordner."""
    if arg is not None:
        return arg.expanduser().resolve()
    return (src_dir.parent / f"{src_dir.name}.pdf").resolve()


def _resolve_run_out(arg: Path | None, src_pdf: Path) -> Path:
    """Default: <src-stem>-scantailor.pdf neben der Eingabedatei.

    Original wird bewusst nicht überschrieben — der gesamte Sinn des
    Workflows ist eine bereinigte Zweitfassung."""
    if arg is not None:
        return arg.expanduser().resolve()
    return (src_pdf.parent / f"{src_pdf.stem}-scantailor.pdf").resolve()


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="noten-scantailor",
        description="Scan-Tailor-Workflow: PDF -> PNGs -> (Scan Tailor) -> PDF.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ex = sub.add_parser(
        "extract",
        help="PDF in PNGs auflösen.",
        description="PDF mit pdftoppm in einen Ordner mit PNG-Seiten zerlegen.",
    )
    p_ex.add_argument("pdf", nargs="?", type=Path,
                      help="Eingabe-PDF (ohne Argument: fzf-Auswahl im aktuellen Verzeichnis).")
    p_ex.add_argument("--out-dir", type=Path,
                      help="Zielordner für PNGs (Default: <stem>-pages/ neben der PDF).")
    p_ex.add_argument("--dpi", type=int, default=300,
                      help="Auflösung in dpi (Default: 300).")
    p_ex.add_argument("--force", action="store_true",
                      help="Auch in einen nicht-leeren Zielordner schreiben.")
    _add_log_flags(p_ex)

    p_as = sub.add_parser(
        "assemble",
        help="Ordner mit Bildern zu einer PDF zusammenfassen.",
        description="Alle Bilder im Ordner (Default-Glob: *.tif) per ImageMagick zu einer PDF zusammenfassen.",
    )
    p_as.add_argument("dir", type=Path, help="Ordner mit Scan-Tailor-Output.")
    p_as.add_argument("--out", type=Path,
                      help="Ausgabe-PDF (Default: <ordnername>.pdf neben dem Ordner).")
    p_as.add_argument("--glob", default=DEFAULT_EXTRACT_GLOB,
                      help=f"Datei-Muster für Eingabebilder (Default: {DEFAULT_EXTRACT_GLOB}).")
    _add_log_flags(p_as)

    p_run = sub.add_parser(
        "run",
        help="Komplett-Workflow: extract -> Scan Tailor -> assemble.",
        description="extract, dann Scan Tailor öffnen, auf ENTER warten und anschließend assemble.",
    )
    p_run.add_argument("pdf", nargs="?", type=Path,
                       help="Eingabe-PDF (ohne Argument: fzf-Auswahl im aktuellen Verzeichnis).")
    p_run.add_argument("--workdir", type=Path,
                       help="Arbeitsordner für PNGs/TIFFs (Default: <stem>-pages/ neben der PDF).")
    p_run.add_argument("--out", type=Path,
                       help="Ergebnis-PDF (Default: <stem>-scantailor.pdf neben der Eingabe).")
    p_run.add_argument("--dpi", type=int, default=300,
                       help="pdftoppm-Auflösung in dpi (Default: 300).")
    p_run.add_argument("--glob", default=DEFAULT_EXTRACT_GLOB,
                       help=f"Datei-Muster für Scan-Tailor-Output (Default: {DEFAULT_EXTRACT_GLOB}).")
    p_run.add_argument("--no-launch", action="store_true",
                       help="Scan Tailor nicht automatisch starten.")
    p_run.add_argument("--force", action="store_true",
                       help="Auch in einen nicht-leeren Workdir schreiben.")
    _add_log_flags(p_run)

    return p


def _add_log_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = setup_logger(verbose=args.verbose, quiet=args.quiet, name="noten-scantailor")

    try:
        if args.cmd == "extract":
            return cmd_extract(args, log)
        if args.cmd == "assemble":
            return cmd_assemble(args, log)
        if args.cmd == "run":
            return cmd_run(args, log)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        log.warning("Abgebrochen durch Benutzer.")
        return 130

    return 2


if __name__ == "__main__":
    sys.exit(main())
