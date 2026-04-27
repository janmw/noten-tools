# noten-tools

Werkzeuge für die digitale Notenarchiv-Verwaltung der Stadtkapelle.

Das Repo bündelt mehrere CLI-Befehle mit dem gemeinsamen Präfix `noten-`. Sie teilen sich eine Python-Bibliothek (`notentools/shared`), ein Instrumenten-Mapping (`data/instruments.yaml`), Stempel-Assets (`assets/`) und eine User-Konfiguration unter `~/.config/noten-tools/`.

## Befehle

### `noten-verarbeitung`

Splittet einen gescannten PDF-Notensatz für sinfonisches Blasorchester in einzelne Stimmen-PDFs, skaliert sie auf A4 (oder A5-quer) und stempelt sie optional digital mit Logo + Archivnummer.

```
noten-verarbeitung [PDF] [Flags]
```

**Workflow** (interaktiv):

1. PDF aus dem aktuellen Verzeichnis per `fzf` auswählen (oder als Argument übergeben).
2. Eingabe: 4-stellige Archivnummer + Titel + Stempeln (j/n).
3. OCR pro Seite (Tesseract `deu+eng`) auf den oberen 18 % der Seite.
4. Eine neue Stimme beginnt, wenn alle drei Header gleichzeitig erkannt werden:
   * Titel mittig oben (groß)
   * Stimmenbezeichnung oben links
   * Komponist/Arrangeur oben rechts
5. Bei OCR-Unsicherheit (Confidence unter Schwelle oder Instrument unbekannt) öffnet sich die betroffene Seite via `xdg-open` zur Vorschau, der User wählt das Instrument aus einer Liste, gibt Nummer + Zusatz (z. B. `in B`) ein. Die Zuordnung wird in `~/.config/noten-tools/learned_aliases.yaml` für die Zukunft gelernt.
6. Pro Stimme wird ein eigenes PDF erzeugt:
   ```
   [Archivnr] - [Titel]/
     [Archivnr] - [Titel] - [Code] [Instrument][ Nummer][ Zusatz].pdf
   ```
7. Skalierung auf A4 hochkant (oder A5 quer mit `--a5`), fit-to-page mit weißen Rändern.
8. Stempel-Overlay (optional): Logo links oben, `Nr. XXXX` rechts oben.

**Flags**

| Flag | Bedeutung |
|---|---|
| `--a5` | Ausgabeformat A5 quer statt A4 hochkant |
| `--no-stamp` | Stempel deaktivieren |
| `--logo PATH` | Alternatives Logo statt `assets/logo.png` |
| `--logo-offset X,Y` | Logo-Verschiebung in mm relativ zum Default (X = nach rechts, Y = nach unten) |
| `--archiv-offset X,Y` | Archivnummer-Verschiebung in mm relativ zum Default (X = nach links, Y = nach unten) |
| `--lang LANG` | OCR-Sprache, z. B. `deu`, `eng`, `deu+eng` |
| `--confidence N` | OCR-Confidence-Schwelle 0–100 (Default 70) |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |
| `--dry-run` | Nur erkennen, keine Dateien schreiben |

### Instrumenten-Codes

| Code | Familie |
|---|---|
| 00 | Direktion / Partitur |
| 01 | Flöten & Piccolo |
| 02 | Oboe, Fagott und andere Doppelrohrbläser |
| 03 | Klarinetten (alle Arten) |
| 04 | Saxophone (alle Arten) |
| 05 | Hörner |
| 06 | Trompeten, Flügelhörner, Kornette |
| 07 | Tenorhörner, Bariton, Euphonium |
| 08 | Posaunen |
| 09 | Tuben & Bässe |
| 10 | Schlagwerk |
| 11 | Streicher und Sonstiges |

### `noten-tools-aliases`

Verwaltung der gelernten Aliase aus interaktiven Sitzungen:

```
noten-tools-aliases list    # alle gelernten Aliase anzeigen
noten-tools-aliases sync    # Vorschläge zur Repo-Aufnahme als YAML ausgeben (PR-fähig)
noten-tools-aliases clear   # gelernte Aliase löschen
```

`sync` vergleicht `~/.config/noten-tools/learned_aliases.yaml` mit dem Repo-Mapping und schlägt Repo-fähige Ergänzungen vor — die Ausgabe lässt sich direkt in `data/instruments.yaml` einfügen und als PR vorschlagen.

## Installation

### Schnellinstallation (Linux & macOS)

```bash
git clone https://github.com/<dein-account>/noten-tools.git
cd noten-tools
./install.sh
```

`install.sh` erkennt automatisch die Distribution (Arch/CachyOS, Debian/Ubuntu, Fedora, macOS) und installiert die System-Abhängigkeiten (`tesseract` mit `deu`+`eng`-Sprachdaten, `poppler-utils`, `fzf`, `xdg-utils`) sowie das Python-Paket via `pipx`.

### Manuell

System-Pakete:

* **Arch / CachyOS**: `pacman -S tesseract tesseract-data-deu tesseract-data-eng poppler fzf xdg-utils python-pipx`
* **Ubuntu / Debian**: `apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng poppler-utils fzf xdg-utils pipx`
* **Fedora**: `dnf install tesseract tesseract-langpack-deu tesseract-langpack-eng poppler-utils fzf xdg-utils pipx`
* **macOS** (Homebrew): `brew install tesseract tesseract-lang poppler fzf pipx`

Python-Paket:

```bash
pipx install .
```

## Konfiguration

Beim ersten Start werden Defaults nach `~/.config/noten-tools/config.yaml` geschrieben. Du kannst dort dauerhaft folgende Werte überschreiben:

* Stempel-Position (Logo + Archivnummer in pt vom Seitenrand)
* Logo-Pfad und Schriftart-Pfad
* OCR-Sprache, OCR-Confidence-Schwelle, OCR-DPI
* Default für `a5` (true/false)

Gelernte Aliase liegen in `~/.config/noten-tools/learned_aliases.yaml`. Logfiles in `~/.cache/noten-tools/logs/`.

## Logo & Schriftart austauschen

Standard-Logo: `assets/logo.png`. Standard-Schrift: `assets/00_stamp.ttf`.

Zum Tauschen entweder:

* Datei im Repo direkt ersetzen (gilt für alle User des Repos), **oder**
* In `~/.config/noten-tools/config.yaml` den `logo_path` / `font_path` auf eine eigene Datei setzen (gilt nur für dich), **oder**
* Pro Aufruf `--logo /pfad/zum/logo.png` übergeben.

## Repo-Struktur

```
noten-tools/
├── bin/
├── notentools/
│   ├── shared/        # geteilte Bibliothek (config, logging, instruments, pdf_io, stamp, paths)
│   ├── verarbeitung/  # noten-verarbeitung CLI
│   └── aliases/       # noten-tools-aliases CLI
├── data/instruments.yaml
├── assets/{logo.png, 00_stamp.ttf}
├── install.sh
├── pyproject.toml
└── README.md
```

## Geplante weitere Befehle

* `noten-stempel` — eigenständiger Stempel-Befehl ohne Splitting
* `noten-fix` — PDF-Bereinigung
* `noten-unbooklet` — Booklet-Layout auflösen

## Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
noten-verarbeitung --help
```

## Lizenz

MIT.
