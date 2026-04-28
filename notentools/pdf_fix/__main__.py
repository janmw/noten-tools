"""CLI-Entrypoint für noten-pdf-fix.

Operationen (kombinierbar, fest in dieser Reihenfolge angewendet):
  1. --decrypt     : Passwortgeschütztes PDF entschlüsseln (Passwort-Prompt)
  2. --repair      : PDF neu serialisieren (heilt kleinere Strukturfehler)
  3. --no-rotate   : AutoRotatePages deaktivieren (gegen unerwünschte Drehungen in Viewern)
  4. --compress    : Mit Ghostscript komprimieren (--compress-level steuert Qualität)

Wenn keine Operation gewählt ist, wird --no-rotate angewendet (Default).

Auswahl: entweder direkt als Positional-Argumente oder per fzf-Mehrfachauswahl.
Backup: Standardmäßig kein Backup; Original wird direkt überschrieben.
  --backup   : '<datei>.pdf.bak' neben dem Original anlegen
  --out PATH : Ergebnis nach PATH schreiben, Original unangetastet (nur bei einer Datei)
"""

from __future__ import annotations

import argparse
import getpass
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pikepdf

from ..shared.logging import setup_logger
from ..verarbeitung.prompts import fzf_pick_pdf  # nicht ausreichend (single) – wir bauen Multi unten


COMPRESS_LEVELS = ("screen", "ebook", "printer", "prepress")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="noten-pdf-fix",
        description="PDF-Reparatur, Entschlüsselung, Rotations-Stop und Kompression.",
    )
    p.add_argument("files", nargs="*", type=Path, help="PDF(s) direkt angeben (sonst fzf-Mehrfachauswahl).")
    p.add_argument("--decrypt", action="store_true", help="Passwortgeschütztes PDF entschlüsseln.")
    p.add_argument("--repair", action="store_true", help="PDF neu serialisieren (kleine Fehler heilen).")
    p.add_argument("--no-rotate", action="store_true", help="AutoRotatePages deaktivieren.")
    p.add_argument("--compress", action="store_true", help="Mit Ghostscript komprimieren.")
    p.add_argument(
        "--compress-level",
        choices=COMPRESS_LEVELS,
        default="printer",
        help="Ghostscript PDFSETTINGS (Default: printer).",
    )
    p.add_argument("--backup", action="store_true", help="Vor Überschreiben '<datei>.pdf.bak' anlegen (Default: kein Backup).")
    p.add_argument("--out", type=Path, help="Ausgabe-Pfad (nur sinnvoll bei genau einer Datei).")
    p.add_argument("--verbose", action="store_true", help="Detaillierte Schritt-Logs.")
    p.add_argument("--quiet", action="store_true", help="Nur Warnungen und Fehler.")
    return p


def fzf_pick_pdfs_multi(cwd: Path) -> list[Path]:
    """Listet PDFs im CWD via fzf -m zur Mehrfachauswahl auf."""
    pdfs = sorted([p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])
    if not pdfs:
        return []
    if shutil.which("fzf") is None:
        # Fallback: einzelne Auswahl via questionary über das vorhandene Helper
        single = fzf_pick_pdf(cwd)
        return [single] if single else []
    proc = subprocess.run(
        [
            "fzf",
            "-m",
            "--prompt=PDFs fixen (TAB für Mehrfachauswahl, ENTER zum Starten)> ",
            "--height=40%",
            "--reverse",
        ],
        input="\n".join(p.name for p in pdfs),
        capture_output=True,
        text=True,
    )
    names = [n for n in proc.stdout.splitlines() if n.strip()]
    return [cwd / n for n in names]


def _ensure_gs_available() -> str:
    gs = shutil.which("gs")
    if gs is None:
        raise SystemExit(
            "Ghostscript ('gs') nicht gefunden. Bitte installieren — siehe README/install.sh."
        )
    return gs


def op_decrypt(src: Path, dst: Path, password: str) -> None:
    with pikepdf.open(src, password=password) as pdf:
        pdf.save(dst)


def op_repair(src: Path, dst: Path) -> None:
    with pikepdf.open(src) as pdf:
        pdf.save(dst)


def op_no_rotate(src: Path, dst: Path, gs: str) -> None:
    cmd = [
        gs, "-q", "-sDEVICE=pdfwrite",
        "-dNOPAUSE", "-dBATCH",
        "-dAutoRotatePages=/None",
        f"-sOutputFile={dst}",
        str(src),
    ]
    subprocess.run(cmd, check=True)


def op_compress(src: Path, dst: Path, gs: str, level: str) -> None:
    cmd = [
        gs, "-q", "-sDEVICE=pdfwrite",
        "-dNOPAUSE", "-dBATCH",
        f"-dPDFSETTINGS=/{level}",
        "-dCompatibilityLevel=1.4",
        f"-sOutputFile={dst}",
        str(src),
    ]
    subprocess.run(cmd, check=True)


def process_file(
    src: Path,
    *,
    operations: list[str],
    out: Path | None,
    backup: bool,
    compress_level: str,
    password_cache: dict[Path, str],
    gs_path: str | None,
    log,
) -> bool:
    if not src.exists():
        log.error(f"Datei nicht gefunden: {src}")
        return False
    if src.suffix.lower() != ".pdf":
        log.warning(f"Überspringe (keine .pdf): {src.name}")
        return False

    log.info(f"[bold]Verarbeite[/] {src.name} – Operationen: {', '.join(operations)}")

    # Passwort vorab holen, falls Decrypt gewünscht ist
    password = ""
    if "decrypt" in operations:
        if src in password_cache:
            password = password_cache[src]
        else:
            password = getpass.getpass(f"Passwort für '{src.name}': ")
            password_cache[src] = password

    # Pipeline mit temporären Dateien
    with tempfile.TemporaryDirectory(prefix="noten-pdf-fix-") as tmp_root:
        tmp = Path(tmp_root)
        current = src
        step = 0

        for opname in operations:
            step += 1
            stage_out = tmp / f"step_{step:02d}_{opname}.pdf"
            try:
                if opname == "decrypt":
                    op_decrypt(current, stage_out, password)
                elif opname == "repair":
                    op_repair(current, stage_out)
                elif opname == "no-rotate":
                    op_no_rotate(current, stage_out, gs_path)
                elif opname == "compress":
                    op_compress(current, stage_out, gs_path, compress_level)
                else:
                    log.error(f"Unbekannte Operation: {opname}")
                    return False
            except subprocess.CalledProcessError as exc:
                log.error(f"Ghostscript-Fehler bei '{opname}' ({src.name}): {exc}")
                return False
            except pikepdf.PasswordError:
                log.error(f"Falsches Passwort für {src.name}.")
                return False
            except Exception as exc:
                log.error(f"Fehler bei '{opname}' ({src.name}): {exc}")
                return False

            if not stage_out.exists() or stage_out.stat().st_size == 0:
                log.error(f"Schritt '{opname}' lieferte keine gültige Ausgabe für {src.name}.")
                return False
            current = stage_out

        # Zielpfad bestimmen + Backup
        if out is not None:
            target = out
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current, target)
            log.info(f"[green]→ Ergebnis:[/] {target}")
        else:
            if backup:
                backup_path = src.with_suffix(src.suffix + ".bak")
                shutil.copy2(src, backup_path)
                log.info(f"Backup angelegt: {backup_path.name}")
            shutil.copy2(current, src)
            log.info(f"[green]→ Aktualisiert:[/] {src.name}")

    return True


def main() -> None:
    args = build_parser().parse_args()

    log = setup_logger(verbose=args.verbose, quiet=args.quiet, name="noten-pdf-fix")

    # Operationen sammeln (feste Reihenfolge!)
    operations: list[str] = []
    if args.decrypt:
        operations.append("decrypt")
    if args.repair:
        operations.append("repair")
    if args.no_rotate:
        operations.append("no-rotate")
    if args.compress:
        operations.append("compress")

    if not operations:
        operations = ["no-rotate"]
        log.info("Keine Operation gewählt – Default: --no-rotate")

    # Ghostscript-Verfügbarkeit nur prüfen, wenn benötigt
    gs_path = None
    if "no-rotate" in operations or "compress" in operations:
        gs_path = _ensure_gs_available()

    # Dateien bestimmen
    if args.files:
        files = [f.resolve() for f in args.files]
    else:
        files = fzf_pick_pdfs_multi(Path.cwd())

    if not files:
        log.warning("Keine Datei ausgewählt — Abbruch.")
        return

    if args.out is not None and len(files) > 1:
        log.error("--out ist nur bei genau einer Eingabedatei zulässig.")
        sys.exit(2)

    password_cache: dict[Path, str] = {}
    successes = 0
    for f in files:
        ok = process_file(
            f,
            operations=operations,
            out=args.out,
            backup=args.backup,
            compress_level=args.compress_level,
            password_cache=password_cache,
            gs_path=gs_path,
            log=log,
        )
        if ok:
            successes += 1

    total = len(files)
    if successes == total:
        log.info(f"[bold green]Fertig.[/] {successes}/{total} Datei(en) verarbeitet.")
    else:
        log.warning(f"Abgeschlossen mit Fehlern: {successes}/{total} erfolgreich.")
        sys.exit(1)


if __name__ == "__main__":
    main()
