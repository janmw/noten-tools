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


def close_preview(proc: subprocess.Popen | None) -> None:
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass


def ask_manual_identification(
    mapper: InstrumentMapper,
    raw_text: str,
) -> Identification:
    """Lässt User Code+Instrument auswählen + Nummer/Zusatz eingeben."""
    instruments = mapper.known_instruments()
    choices = [f"{code}  {name}" for code, name in instruments]
    pick = questionary.autocomplete(
        f"Stimme manuell zuordnen (OCR las: '{raw_text[:60]}'). Instrument:",
        choices=choices,
        match_middle=True,
        validate=lambda v: v in choices or "Bitte aus der Liste wählen.",
    ).ask()
    if pick is None:
        raise SystemExit("Abbruch.")
    code, name = pick.split("  ", 1)

    nummer = questionary.text(
        "Nummer (z.B. 1, 2, 3 — leer lassen wenn keine):",
        validate=lambda v: not v or v.strip().isdigit() or "Bitte Ziffer oder leer.",
    ).ask()
    if nummer is None:
        raise SystemExit("Abbruch.")
    nummer = (nummer or "").strip()

    zusatz = questionary.text(
        "Zusatz (z.B. 'in B', 'in Es' — leer lassen wenn keiner):",
    ).ask()
    if zusatz is None:
        raise SystemExit("Abbruch.")
    zusatz = (zusatz or "").strip()

    instrument_name = name
    # Bei keep_original_name darf der OCR-Text als Name fließen — wir bieten an
    code_info = mapper._codes.get(code, {}).get(name, {})
    if code_info.get("keep_original_name"):
        custom = questionary.text(
            f"Originalname aus Stimme verwenden? (Enter = '{name}', oder eigene Eingabe)",
        ).ask()
        if custom and custom.strip():
            instrument_name = custom.strip()

    return Identification(
        code=code,
        instrument=instrument_name,
        nummer=nummer,
        zusatz=zusatz,
        source_text=raw_text,
    )
