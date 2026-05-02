# Scans säubern

Befehl: `noten-scantailor`

Wrapper um den manuellen Scan-Tailor-Advanced-Workflow:

1. PDF in einzelne PNG-Seiten zerlegen (300 dpi)
2. Mit Scan Tailor Advanced bereinigen (Deskew, Crop, Margins, Output → TIFF)
3. TIFFs zurück in eine PDF zusammenfassen

Dieselben Schritte als Einzelaufrufe oder als Komplett-Workflow `run`.

## Subcommands

```
noten-scantailor extract  PDF  [--out-dir DIR] [--dpi 300] [--force]
noten-scantailor assemble DIR  [--out PDF]    [--glob "*.tif"]
noten-scantailor run      PDF  [--workdir DIR] [--out PDF]
                               [--dpi 300] [--glob "*.tif"]
                               [--no-launch]  [--force]
```

## extract

Zerlegt das PDF mit `pdftoppm -png -r <dpi>` in Einzelseiten.

- Ohne `--out-dir` landet das Ergebnis in `<stem>-pages/` neben der PDF.
- Dateinamen folgen dem Schema `Seite-001.png`, `Seite-002.png`, …
- Ohne `pdf`-Argument öffnet sich `fzf` zur Auswahl.

```bash
noten-scantailor extract scan.pdf
# → scan-pages/Seite-001.png …

noten-scantailor extract scan.pdf --out-dir /tmp/seventies --dpi 600
```

## assemble

Fasst alle Bilder im Ordner per `magick` zu einer PDF zusammen.

- Default-Glob: `*.tif` (Scan-Tailor-Output).
- Ohne `--out` landet das Ergebnis als `<ordnername>.pdf` neben dem Ordner.
- Dateien werden alphabetisch sortiert eingefügt — Scan Tailor benennt
  konsistent durch (`…-001.tif` etc.), das passt von selbst.

```bash
noten-scantailor assemble scan-pages/
# → scan-pages.pdf

noten-scantailor assemble scan-pages/ --out scan-clean.pdf --glob "*.png"
```

## run

Komplett-Workflow in einem Aufruf:

1. `extract` in `<stem>-pages/` (oder `--workdir`)
2. Scan Tailor Advanced wird automatisch mit dem Ordner geöffnet
   (sofern `scantailor-advanced` o.ä. im PATH ist; sonst Hinweis)
3. Tool wartet auf ENTER — du speicherst in Scan Tailor wie gewohnt
   die Ausgabe (Default: TIFF) in denselben Ordner
4. `assemble` baut die PDF zusammen, Default: `<stem>-scantailor.pdf`
   neben der Eingabe — das Original bleibt unangetastet

```bash
noten-scantailor run scan.pdf
# Scan Tailor öffnet sich, du arbeitest, drückst ENTER → scan-scantailor.pdf

noten-scantailor run scan.pdf --no-launch     # Scan Tailor selbst starten
noten-scantailor run scan.pdf --out clean.pdf # Zielname festlegen
```

## Flags

| Flag | Subcommand | Bedeutung |
|---|---|---|
| `--out-dir DIR` | extract | Zielordner für PNGs |
| `--workdir DIR` | run | Arbeitsordner (PNGs vor + TIFFs nach Scan Tailor) |
| `--out PATH` | assemble, run | Ergebnis-PDF |
| `--dpi N` | extract, run | pdftoppm-Auflösung (Default: 300) |
| `--glob MUSTER` | assemble, run | Datei-Muster für Scan-Tailor-Output (Default: `*.tif`) |
| `--no-launch` | run | Scan Tailor nicht automatisch starten |
| `--force` | extract, run | Auch in einen nicht-leeren Zielordner schreiben |
| `--verbose` / `--quiet` | alle | Mehr/weniger Konsolen-Logs |

## Voraussetzungen

- `pdftoppm` (poppler-utils)
- `magick` (ImageMagick) — wird über `install.sh` mitinstalliert
- Scan Tailor Advanced — auf Arch via AUR (`scantailor-advanced`),
  auf Debian/Ubuntu `scantailor`, sonst über die Releases auf GitHub.
  Wird beim `run`-Subcommand automatisch im PATH gesucht; ohne Fund
  startet das Tool nicht automatisch und du öffnest es manuell.
