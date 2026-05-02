"""CLI-Entrypoint für noten-verarbeitung.

Workflow:
  1. fzf-Auswahl einer PDF aus dem CWD
  2. Prompts: Archivnummer, Titel, Stempeln?
  3. Render + OCR pro Seite
  4. Header-Heuristik -> Segmente; bei Unsicherheit Vorschau + manuelle Zuordnung
  5. Split + Skalierung + optionaler Stempel
  6. Ablage in ./[Archivnr] - [Titel]/
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from ..shared.config import Config
from ..shared.instruments import InstrumentMapper, Identification
from ..shared.logging import setup_logger
from ..shared import pdf_io
from ..shared.stamp import stamp_pdf
from . import prompts
from .ocr import HeaderRead, read_header
from .split import (
    Segment,
    build_segments,
    build_filename,
    build_folder_name,
    dedup_consecutive_same_part,
    sanitize_filename,
    try_identify_header,
)


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
        prog="noten-verarbeitung",
        description="Splittet einen gescannten Notensatz in Einzel-Stimmen mit Stempel und A4/A5-Skalierung.",
    )
    p.add_argument("pdf", nargs="?", type=Path, help="Optional: PDF direkt angeben (sonst fzf-Auswahl).")
    p.add_argument("--a5", action="store_true", help="Ausgabeformat A5 quer statt A4.")
    p.add_argument("--no-stamp", action="store_true", help="Keinen Stempel anbringen.")
    p.add_argument("--logo", type=Path, help="Alternatives Logo (überschreibt Default).")
    p.add_argument("--logo-offset", type=_parse_offset, default=(0.0, 0.0),
                   help="Logo-Verschiebung relativ zu Default in mm: 'X,Y' (X=rechts, Y=unten).")
    p.add_argument("--archiv-offset", type=_parse_offset, default=(0.0, 0.0),
                   help="Archivnummer-Verschiebung relativ zu Default in mm: 'X,Y' (X=links, Y=unten).")
    p.add_argument("--lang", default=None, help="OCR-Sprache (deu, eng, deu+eng). Default aus Config.")
    p.add_argument("--confidence", type=int, default=None,
                   help="OCR-Confidence-Schwelle (0-100). Default aus Config.")
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")
    p.add_argument("--dry-run", action="store_true", help="Nur erkennen, nichts schreiben.")
    return p


def select_pdf(arg_pdf: Path | None, log) -> Path:
    if arg_pdf is not None:
        if not arg_pdf.exists():
            log.error(f"PDF '{arg_pdf}' nicht gefunden.")
            sys.exit(1)
        return arg_pdf
    cwd = Path.cwd()
    pdf = prompts.fzf_pick_pdf(cwd)
    if pdf is None:
        log.error("Keine PDF im aktuellen Verzeichnis oder Auswahl abgebrochen.")
        sys.exit(1)
    return pdf


def identify_pages(
    pdf_path: Path,
    config: Config,
    mapper: InstrumentMapper,
    lang: str,
    confidence_threshold: int,
    log,
    piece_title: str = "",
) -> tuple[list[HeaderRead], list[Identification | None]]:
    """OCR jeder Seite + Identifikation des Instruments. Bei Unsicherheit interaktiv nachfragen.

    Ablauf:
      1. OCR pro Seite -> HeaderRead
      2. Kandidaten-Identifikation pro Header-Seite (multi-block, ohne Prompts)
      3. Dedup adjacent same-part: aufeinanderfolgende Header-Seiten mit gleichem
         Instrument werden zu Folgeseiten zusammengezogen
      4. Für die übrig gebliebenen "echten" neuen Stimmen ggf. manuell nachfragen
    """
    log.info(f"Rendere PDF zu Bildern (DPI {config.ocr_dpi}) …")
    images = pdf_io.render_pages_to_images(pdf_path, dpi=config.ocr_dpi)
    log.info(f"Erkannt: {len(images)} Seiten. Starte OCR …")

    # Pass 1: OCR
    headers: list[HeaderRead] = []
    for idx, img in enumerate(images):
        band = pdf_io.crop_top_band(img, fraction=0.30)
        hdr = read_header(band, lang=lang, piece_title=piece_title)
        hdr.page_index = idx
        headers.append(hdr)
        log.debug(
            f"Seite {idx + 1}: title='{hdr.title_text}' (c={hdr.title_conf:.0f}) "
            f"voice='{hdr.voice_text}' (c={hdr.voice_conf:.0f}) "
            f"composer='{hdr.composer_text}' (c={hdr.composer_conf:.0f}) "
            f"new_part={hdr.is_new_part_start}"
        )

    # Sicherheitsnetz: wenn piece_title gesetzt war, aber kein einziger Cover
    # erkannt wurde, ist vermutlich der eingegebene Titel zu weit weg von dem,
    # was im Scan steht. Warnung loggen — die Reste-Datei wird sonst alles
    # auffangen, was leicht zu übersehen ist.
    if piece_title and not any(h.is_new_part_start for h in headers):
        log.warning(
            f"Stücktitel '{piece_title}' matcht keine einzige Seite — "
            "Cover-Erkennung fällt komplett aus. Tippfehler im Titel?"
        )

    # Pass 2: Kandidaten ermitteln (ohne Prompts)
    candidate_pairs: list[tuple[Identification | None, float]] = []
    for hdr in headers:
        if hdr.is_new_part_start:
            candidate_pairs.append(try_identify_header(mapper, hdr))
        else:
            candidate_pairs.append((None, 0.0))
    candidate_idents = [pair[0] for pair in candidate_pairs]
    candidate_confs = [pair[1] for pair in candidate_pairs]

    # Pass 3: Dedup
    is_new_flags = [hdr.is_new_part_start for hdr in headers]
    accepted = dedup_consecutive_same_part(is_new_flags, candidate_idents)

    # Pass 4: Endgültige Identifikation (mit Prompt für Unsichere)
    idents: list[Identification | None] = []
    for idx, (hdr, acc, cand_ident, cand_conf) in enumerate(
        zip(headers, accepted, candidate_idents, candidate_confs)
    ):
        if not hdr.is_new_part_start:
            idents.append(None)
            continue
        if acc is None:
            # durch Dedup zur Fortsetzung degradiert
            log.debug(f"Seite {idx + 1}: gleiche Stimme wie Vorgängerseite — Fortsetzung")
            idents.append(None)
            continue

        unsure = (
            cand_ident is None
            or cand_conf < confidence_threshold
            or cand_ident.needs_pitch()
        )
        if unsure:
            ident = _resolve_unsure(pdf_path, idx, hdr, mapper, log)
            mapper.learn(hdr.voice_text, ident.filename_part() if ident else "")
            log.info(f"Seite {idx + 1}: manuell zugeordnet -> {ident.filename_part()}")
        else:
            ident = cand_ident
            log.info(f"Seite {idx + 1}: erkannt -> {ident.filename_part()}")
        idents.append(ident)

    return headers, idents


def _resolve_unsure(
    pdf_path: Path,
    page_index: int,
    hdr: HeaderRead,
    mapper: InstrumentMapper,
    log,
) -> Identification:
    """Öffnet Vorschau der Seite, fragt User, beendet Vorschau."""
    with tempfile.NamedTemporaryFile(prefix="noten-vorschau-", suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        pdf_io.extract_pages_to_pdf(pdf_path, [page_index], tmp_path)
        proc = prompts.open_preview(tmp_path)
        try:
            ident = prompts.ask_manual_identification(mapper, hdr.voice_text)
        finally:
            prompts.close_preview(proc, pdf_path=tmp_path)
        return ident
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def _unique_in(directory: Path, filename: str, taken: set[Path]) -> Path:
    """Pfad in `directory` mit `filename`; bei Kollision -2, -3, … anhängen."""
    candidate = directory / filename
    if candidate not in taken and not candidate.exists():
        taken.add(candidate)
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    i = 2
    while True:
        candidate = directory / f"{stem}-{i}{suffix}"
        if candidate not in taken and not candidate.exists():
            taken.add(candidate)
            return candidate
        i += 1


def write_output(
    pdf_path: Path,
    out_dir: Path,
    archivnummer: str,
    titel: str,
    config: Config,
    do_stamp: bool,
    a5: bool,
    logo_offset: tuple[float, float],
    archiv_offset: tuple[float, float],
    segments: list[Segment],
    log,
    dry_run: bool,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    duplicate_dir = out_dir / sanitize_filename(f"{archivnummer} - Reste")

    def _write_pages(pages: list[int], target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="noten-split-") as tmp:
            tmp_dir = Path(tmp)
            extracted = tmp_dir / "extract.pdf"
            scaled = tmp_dir / "scaled.pdf"
            pdf_io.extract_pages_to_pdf(pdf_path, pages, extracted)
            pdf_io.scale_pdf_to_target(extracted, scaled, a5=a5)
            if do_stamp:
                stamp_pdf(
                    scaled,
                    target,
                    archivnummer=archivnummer,
                    config=config,
                    logo_offset_mm=logo_offset,
                    archiv_offset_mm=archiv_offset,
                )
            else:
                shutil.copy2(scaled, target)

    written_names: set[str] = set()
    duplicate_taken: set[Path] = set()
    rest_pages: list[int] = []
    for seg in segments:
        if seg.identification is None:
            rest_pages.extend(seg.page_indices)
            continue
        filename = build_filename(archivnummer, titel, seg.identification)
        if filename in written_names:
            target = _unique_in(duplicate_dir, filename, duplicate_taken)
            log.warning(
                f"Duplikat: {filename} → {duplicate_dir.name}/{target.name}  "
                f"(Seiten {[i + 1 for i in seg.page_indices]})"
            )
        else:
            target = out_dir / filename
            written_names.add(filename)
            log.info(f"Stimme: {filename}  (Seiten {[i + 1 for i in seg.page_indices]})")
        if dry_run:
            continue
        _write_pages(seg.page_indices, target)

    if rest_pages:
        rest_filename = sanitize_filename(f"{archivnummer} - {titel} - 99 Reste") + ".pdf"
        rest_target = out_dir / rest_filename
        log.info(f"Reste: {rest_filename}  (Seiten {[i + 1 for i in rest_pages]})")
        if not dry_run:
            _write_pages(rest_pages, rest_target)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log = setup_logger(verbose=args.verbose, quiet=args.quiet)

    Config.write_default_if_missing()
    config = Config.load()

    if args.lang:
        config.ocr_lang = args.lang
    if args.confidence is not None:
        config.ocr_confidence = args.confidence
    if args.a5:
        config.a5 = True
    if args.logo:
        config.logo_path = str(args.logo.expanduser().resolve())

    pdf_path = select_pdf(args.pdf, log)
    log.info(f"PDF: {pdf_path}")

    archivnummer = prompts.ask_archivnummer()
    titel = prompts.ask_titel()
    do_stamp = (not args.no_stamp) and prompts.ask_stempel()

    folder_name = build_folder_name(archivnummer, titel)
    out_dir = pdf_path.parent / folder_name
    if out_dir.exists():
        if not prompts.ask_replace_existing(out_dir):
            log.warning("Abbruch: Zielordner bleibt unverändert.")
            return 1
        shutil.rmtree(out_dir)

    mapper = InstrumentMapper()
    headers, idents = identify_pages(
        pdf_path,
        config,
        mapper,
        lang=config.ocr_lang,
        confidence_threshold=config.ocr_confidence,
        log=log,
        piece_title=titel,
    )
    segments = build_segments(idents)
    log.info(f"Erkannt: {len(segments)} Stimmen-Segmente.")

    write_output(
        pdf_path=pdf_path,
        out_dir=out_dir,
        archivnummer=archivnummer,
        titel=titel,
        config=config,
        do_stamp=do_stamp,
        a5=config.a5,
        logo_offset=args.logo_offset,
        archiv_offset=args.archiv_offset,
        segments=segments,
        log=log,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        log.info("Dry-Run beendet — keine Dateien geschrieben.")
    else:
        log.info(f"Fertig. Ausgabe: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
