"""Interaktive Prompts: Eingaben + Vorschau bei OCR-Unsicherheit."""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import tempfile
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


def _ancestor_pids() -> list[int]:
    """Sammelt die PID-Kette vom Elternprozess (Shell) bis init/systemd.

    Eine dieser PIDs ist normalerweise die des Terminal-Fensters — KWin/Hypr/etc.
    kennen Fenster über die Window-PID, daher reicht uns die Kette für den Refokus.
    """
    pids: list[int] = []
    try:
        pid = os.getppid()
        seen: set[int] = set()
        while pid > 1 and pid not in seen:
            pids.append(pid)
            seen.add(pid)
            ppid: int | None = None
            with open(f"/proc/{pid}/status") as fh:
                for line in fh:
                    if line.startswith("PPid:"):
                        ppid = int(line.split()[1])
                        break
            if ppid is None or ppid == pid:
                break
            pid = ppid
    except Exception:
        pass
    return pids


def _focus_kde_wayland(pids: list[int]) -> bool:
    """Aktiviert via KWin-Scripting das Fenster, dessen PID in der Kette vorkommt."""
    if not pids or shutil.which("qdbus6") is None:
        return False
    pid_array = "[" + ",".join(str(p) for p in pids) + "]"
    js = (
        "var pids = " + pid_array + ";\n"
        "var wins = (typeof workspace.windowList === 'function')\n"
        "    ? workspace.windowList() : workspace.windows;\n"
        "for (var i = 0; i < wins.length; i++) {\n"
        "    if (pids.indexOf(wins[i].pid) >= 0) {\n"
        "        workspace.activeWindow = wins[i];\n"
        "        break;\n"
        "    }\n"
        "}\n"
    )
    script_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".js", prefix="noten-focus-", delete=False
        ) as fh:
            fh.write(js)
            script_path = fh.name
        subprocess.run(
            ["qdbus6", "org.kde.KWin", "/Scripting",
             "org.kde.kwin.Scripting.loadScript", script_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3,
        )
        subprocess.run(
            ["qdbus6", "org.kde.KWin", "/Scripting",
             "org.kde.kwin.Scripting.start"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3,
        )
        # Skript läuft im KWin-Event-Loop — kurz warten, bevor wir entladen
        time.sleep(0.05)
        subprocess.run(
            ["qdbus6", "org.kde.KWin", "/Scripting",
             "org.kde.kwin.Scripting.unloadScript", script_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3,
        )
        return True
    except Exception:
        return False
    finally:
        if script_path:
            try:
                os.unlink(script_path)
            except Exception:
                pass


def _capture_active_window() -> str | None:
    """Liefert ein Token zur späteren Refokussierung des aufrufenden Fensters.

    Unterstützt Hyprland (hyprctl), KDE Plasma Wayland (qdbus6 + KWin-Scripting),
    und X11 (xdotool). Bei anderen Compositors ist Refokus best-effort und wird
    stillschweigend übersprungen.
    """
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
        try:
            out = subprocess.check_output(
                ["hyprctl", "activewindow"], text=True, timeout=2
            )
            first = out.splitlines()[0] if out else ""
            parts = first.split()
            if len(parts) >= 2 and parts[0] == "Window":
                return f"hypr:{parts[1]}"
        except Exception:
            pass
    is_kde = "kde" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
    if is_kde and is_wayland and shutil.which("qdbus6"):
        pids = _ancestor_pids()
        if pids:
            return "kde:" + ",".join(str(p) for p in pids)
    if shutil.which("xdotool"):
        try:
            wid = subprocess.check_output(
                ["xdotool", "getactivewindow"], text=True, timeout=2
            ).strip()
            if wid:
                return f"xdo:{wid}"
        except Exception:
            pass
    return None


def _focus_window(token: str | None) -> None:
    if not token:
        return
    try:
        if token.startswith("hypr:"):
            subprocess.run(
                ["hyprctl", "dispatch", "focuswindow", f"address:{token[5:]}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2,
            )
        elif token.startswith("kde:"):
            pids = [int(p) for p in token[4:].split(",") if p.strip()]
            _focus_kde_wayland(pids)
        elif token.startswith("xdo:"):
            subprocess.run(
                ["xdotool", "windowactivate", token[4:]],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2,
            )
    except Exception:
        pass


def open_preview(pdf_path: Path) -> subprocess.Popen | None:
    """Öffnet PDF mit xdg-open im Hintergrund.

    Merkt sich vorher das aktive Fenster (Terminal) und fokussiert es nach kurzer
    Wartezeit zurück, damit der User direkt weitertippen kann statt erst zurück
    in das Terminal klicken zu müssen.
    """
    if shutil.which("xdg-open") is None:
        return None
    saved_window = _capture_active_window()
    try:
        proc = subprocess.Popen(
            ["xdg-open", str(pdf_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Viewer Zeit zum Starten geben, dann Terminal zurück in den Fokus
        time.sleep(0.6)
        _focus_window(saved_window)
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
