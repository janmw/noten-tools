# `noten-pdf-fix`

Repariert, entschlüsselt, komprimiert PDFs und stoppt Auto-Rotate in Viewern. Operationen sind kombinierbar und werden in fester Reihenfolge angewendet:

1. `--decrypt` — Passwort-geschütztes PDF entschlüsseln (Passwort-Prompt)
2. `--repair` — PDF neu serialisieren (heilt kleinere Strukturfehler)
3. `--no-rotate` — `AutoRotatePages` deaktivieren (gegen unerwünschte Drehungen in Viewern)
4. `--compress` — mit Ghostscript komprimieren

Wenn keine Operation gewählt wird, läuft `--no-rotate` (Default).

```
noten-pdf-fix [PDF...] [Flags]
```

## Workflow

1. PDF-Auswahl:
   * Eine oder mehrere Dateien als Argumente, **oder**
   * ohne Argumente: `fzf`-Mehrfachauswahl im aktuellen Verzeichnis (TAB markieren, ENTER startet).
2. Bei `--decrypt`: Passwort-Prompt pro Datei (gecached für gleiche Eingabedateien).
3. Pipeline läuft in einem temporären Verzeichnis, jede Operation produziert eine Zwischendatei.
4. Standardmäßig wird das Original überschrieben. Mit `--backup` wird vorher `<datei>.pdf.bak` daneben angelegt; mit `--out PATH` (nur bei einer einzelnen Datei) bleibt das Original unangetastet.

## Flags

| Flag | Bedeutung |
|---|---|
| `--decrypt` | Passwortgeschütztes PDF entschlüsseln |
| `--repair` | PDF neu serialisieren (kleine Fehler heilen) |
| `--no-rotate` | `AutoRotatePages=/None` setzen (Default-Operation) |
| `--compress` | Mit Ghostscript komprimieren |
| `--compress-level LEVEL` | Ghostscript `PDFSETTINGS`: `screen`, `ebook`, `printer` (Default), `prepress` |
| `--backup` | Vor dem Überschreiben `<datei>.pdf.bak` anlegen (Default: kein Backup) |
| `--out PATH` | Ergebnis nach PATH schreiben, Original unangetastet (nur bei genau einer Eingabedatei) |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |

## Compress-Levels

| Level | Ungefähre Zielqualität |
|---|---|
| `screen` | 72 dpi, sehr klein, für Bildschirm |
| `ebook` | 150 dpi, mittel |
| `printer` | 300 dpi, gut druckbar (Default) |
| `prepress` | 300 dpi, hochwertig, druckvorstufentauglich |

## Beispiele

```bash
# Default: AutoRotate stoppen
noten-pdf-fix scan.pdf

# Reparieren + komprimieren
noten-pdf-fix scan.pdf --repair --compress

# Mehrere Dateien per fzf entschlüsseln + reparieren
noten-pdf-fix --decrypt --repair

# Kompression auf "ebook" reduzieren
noten-pdf-fix scan.pdf --compress --compress-level ebook

# Mit Backup arbeiten
noten-pdf-fix scan.pdf --repair --backup

# Ausgabe in andere Datei schreiben
noten-pdf-fix scan.pdf --compress --out scan-klein.pdf
```

## Voraussetzungen

`--no-rotate` und `--compress` benötigen `ghostscript` (`gs`). Wird über `install.sh` automatisch mitinstalliert; bei manueller Installation siehe [installation.md](installation.md).
