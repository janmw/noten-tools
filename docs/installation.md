# Installation

## Schnellinstallation (Linux & macOS)

```bash
git clone https://github.com/janmw/noten-tools.git
cd noten-tools
./install.sh
```

`install.sh` erkennt automatisch die Distribution (Arch/CachyOS, Debian/Ubuntu, Fedora, macOS) und installiert die System-Abhängigkeiten (`tesseract` mit `deu`+`eng`-Sprachdaten, `poppler-utils`, `fzf`, `xdg-utils`, `ghostscript`) sowie das Python-Paket via `pipx`.

## Manuell

System-Pakete:

* **Arch / CachyOS**: `pacman -S tesseract tesseract-data-deu tesseract-data-eng poppler fzf xdg-utils ghostscript python-pipx`
* **Ubuntu / Debian**: `apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng poppler-utils fzf xdg-utils ghostscript pipx`
* **Fedora**: `dnf install tesseract tesseract-langpack-deu tesseract-langpack-eng poppler-utils fzf xdg-utils ghostscript pipx`
* **macOS** (Homebrew): `brew install tesseract tesseract-lang poppler fzf ghostscript pipx`

Python-Paket:

```bash
pipx install .
```

Falls `noten-*`-Befehle nach der Installation nicht gefunden werden, eine neue Shell öffnen oder `$(pipx environment --value PIPX_BIN_DIR)` zum `PATH` hinzufügen.
