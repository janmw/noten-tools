# Installation

## Schnellinstallation

Empfohlen für alle, die nicht selbst entwickeln wollen. Das Skript erkennt Arch/CachyOS, Debian/Ubuntu, Fedora und macOS automatisch und installiert System-Pakete sowie das Python-Paket via `pipx`.

```bash
git clone https://github.com/janmw/noten-tools.git
cd noten-tools
./install.sh
```

!!! tip "Befehle nicht gefunden?"
    Falls `noten-*`-Befehle nach der Installation nicht im `PATH` sind, eine neue Shell öffnen oder `$(pipx environment --value PIPX_BIN_DIR)` zum `PATH` hinzufügen.

## Manuell

Falls du dem `install.sh`-Skript nicht traust oder eine nicht erkannte Distribution nutzt — die Schritte einzeln:

### 1. System-Pakete

=== "Arch / CachyOS"

    ```bash
    sudo pacman -S tesseract tesseract-data-deu tesseract-data-eng \
                   poppler fzf xdg-utils ghostscript imagemagick python-pipx
    ```

=== "Ubuntu / Debian"

    ```bash
    sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng \
                         poppler-utils fzf xdg-utils ghostscript imagemagick pipx
    ```

=== "Fedora"

    ```bash
    sudo dnf install tesseract tesseract-langpack-deu tesseract-langpack-eng \
                     poppler-utils fzf xdg-utils ghostscript ImageMagick pipx
    ```

=== "macOS (Homebrew)"

    ```bash
    brew install tesseract tesseract-lang poppler fzf ghostscript imagemagick pipx
    ```

### 2. Python-Paket

```bash
pipx install .
```

## Was wird installiert?

| Paket | Wofür |
|---|---|
| `tesseract` + `deu`/`eng` | OCR für `noten-verarbeitung` |
| `poppler-utils` | PDF-Rendering (`pdftoppm`) für OCR-Vorverarbeitung |
| `ghostscript` | Reparieren, Komprimieren, Auto-Rotate-Stop in `noten-pdf-fix` |
| `imagemagick` | Bilder zurück zu PDF in `noten-scantailor` |
| `fzf` | Interaktive Datei-Auswahl, wenn ein Befehl ohne Argumente aufgerufen wird |
| `xdg-utils` | PDF-Vorschau bei OCR-Unsicherheit (Linux) |
| `pipx` | Isoliertes Python-Environment für `noten-tools` |

## Nächster Schritt

→ [Konfiguration](konfiguration.md) anpassen, oder direkt mit den [ersten Schritten](erste-schritte.md) loslegen.
