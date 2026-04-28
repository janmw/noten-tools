"""Interaktive Prompts: Eingaben + Vorschau bei OCR-Unsicherheit."""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import time
from pathlib import Path

import questionary

from ..shared.instruments import InstrumentMapper, Identification


def ask_archivnummer() -> str:
    while True:
        value = questionary.text(
            "Archivnummer (4-stellig):",
            validate=lambda v: bool(re.fullmatch(r"\d{4}", v.strip())) or "Bitte exakt 4 Ziffern eingeben.",
        ).ask()
        if value is None:
            raise SystemExit("Abbruch.")
        value = value.strip()
        if re.fullmatch(r"\d{4}", value):
            return value


def ask_titel() -> str:
    while True:
        value = questionary.text(
            "Titel des Stücks:",
            validate=lambda v: bool(v.strip()) or "Titel darf nicht leer sein.",
        ).ask()
        if value is None:
            raise SystemExit("Abbruch.")
        value = value.strip()
        if value:
            return value


def ask_stempel() -> bool:
    answer = questionary.confirm("Soll digital gestempelt werden (Logo + Archivnummer)?", default=True).ask()
    if answer is None:
        raise SystemExit("Abbruch.")
    return bool(answer)


def ask_replace_existing(folder: Path) -> bool:
    answer = questionary.confirm(
        f"Zielordner '{folder.name}' existiert bereits. Komplett ersetzen?",
        default=False,
    ).ask()
    if answer is None:
        raise SystemExit("Abbruch.")
    return bool(answer)


def fzf_pick_pdf(cwd: Path) -> Path | None:
    """Listet PDFs im CWD via fzf zur Auswahl auf."""
    pdfs = sorted([p for p in cwd.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"])
    if not pdfs:
        return None
    if shutil.which("fzf") is None:
        # Fallback: questionary-Auswahl
        choice = questionary.select(
            "PDF auswählen:",
            choices=[p.name for p in pdfs],
        ).ask()
        if choice is None:
            return None
        return cwd / choice
    proc = subprocess.run(
        ["fzf", "--prompt=PDF auswählen> ", "--height=40%", "--reverse"],
        input="\n".join(p.name for p in pdfs),
        capture_output=True,
        text=True,
    )
    name = proc.stdout.strip()
    if not name:
        return None
    return cwd / name


def open_preview(pdf_path: Path) -> subprocess.Popen | None:
    """Öffnet PDF mit xdg-open im Hintergrund. Gibt das Popen-Objekt zurück (zum späteren Beenden)."""
    if shutil.which("xdg-open") is None:
        return None
    try:
        proc = subprocess.Popen(
            ["xdg-open", str(pdf_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Kurz warten, damit der Viewer Zeit zum Starten hat
        time.sleep(0.4)
        return proc
    except Exception:
        return None


def close_preview(proc: subprocess.Popen | None, pdf_path: Path | None = None) -> None:
    """Beendet den Preview-Viewer.

    Schickt SIGTERM an die Prozessgruppe des gestarteten Prozesses. Da `xdg-open`
    den eigentlichen Viewer häufig per D-Bus an einen bestehenden Prozess delegiert,
    erwischt das nicht immer das richtige Fenster — als Fallback wird per `pkill -f`
    gezielt der Prozess gesucht, dessen Kommandozeile den (eindeutigen) Tempfile-Pfad
    enthält.
    """
    if proc is not None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass

    if pdf_path is not None and shutil.which("pkill") is not None:
        try:
            subprocess.run(
                ["pkill", "-f", str(pdf_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


def ask_manual_identification(
    mapper: InstrumentMapper,
    raw_text: str,
) -> Identification:
    """Lässt User die Stimme als Freitext eingeben (z.B. 'Klarinette 2 in B').

    Versucht zunächst, die Eingabe automatisch zu zerlegen (Code/Name/Nummer/Zusatz).
    Bei unbekanntem Instrument wird der Code separat abgefragt; der eingegebene Text
    wird dann direkt als Instrumenten-Name übernommen.
    """
    typed = questionary.text(
        f"Stimme manuell eingeben (OCR las: '{raw_text[:60]}'):",
        validate=lambda v: bool(v.strip()) or "Bitte etwas eingeben.",
    ).ask()
    if typed is None:
        raise SystemExit("Abbruch.")
    typed = typed.strip()

    ident = mapper.identify(typed)
    if ident is not None:
        return Identification(
            code=ident.code,
            instrument=ident.instrument,
            nummer=ident.nummer,
            zusatz=ident.zusatz,
            source_text=raw_text,
        )

    valid_codes = mapper.known_codes()
    code = questionary.text(
        f"Instrument unbekannt. Code (z.B. {', '.join(valid_codes[:4])}, …) für '{typed}':",
        validate=lambda v: v.strip() in valid_codes or f"Bitte einen gültigen Code eingeben: {', '.join(valid_codes)}",
    ).ask()
    if code is None:
        raise SystemExit("Abbruch.")
    code = code.strip()

    return Identification(
        code=code,
        instrument=typed,
        nummer="",
        zusatz="",
        source_text=raw_text,
    )
