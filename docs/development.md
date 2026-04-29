# Entwicklung

## Editierbare Installation in einer venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
noten-verarbeitung --help
```

## Schnelles Re-Install via pipx

Nach Code-Änderungen am eigenen Klon:

```bash
pipx install --force .
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Oder direkt im pipx-venv:

```bash
$(pipx environment --value PIPX_HOME)/venvs/noten-tools/bin/python -m pip install pytest
$(pipx environment --value PIPX_HOME)/venvs/noten-tools/bin/python -m pytest
```

Abgedeckt sind:

* `noten-booklet` — Reordering-Logik (`partitur_ordering`, `noten_ordering`) + Mediabox-Splitting
* `notentools.shared.instruments` — Naming-Konvention (`_post_process`), `needs_pitch()`, `identify()` end-to-end
* `notentools.verarbeitung.split` — `sanitize_filename`, `build_filename`, `build_folder_name`
* `noten-tools-aliases` — Identifier-Pattern für `sync`

OCR und interaktive Prompts sind bewusst nicht abgedeckt.

## Doku lokal bauen

Die Doku im `docs/`-Verzeichnis wird mit [MkDocs](https://www.mkdocs.org/) und dem [Catppuccin-Theme](https://github.com/catppuccin/mkdocs) gerendert.

```bash
pip install -e ".[docs]"
mkdocs serve   # Live-Preview auf http://127.0.0.1:8000
mkdocs build   # statische Site nach site/
```

## Repo-Struktur

```
noten-tools/
├── bin/
├── notentools/
│   ├── shared/        # geteilte Bibliothek (config, logging, instruments, pdf_io, stamp, paths)
│   ├── verarbeitung/  # noten-verarbeitung CLI
│   ├── pdf_fix/       # noten-pdf-fix CLI
│   ├── stempel/       # noten-stempel CLI
│   ├── booklet/       # noten-booklet CLI
│   └── aliases/       # noten-tools-aliases CLI
├── data/instruments.yaml
├── assets/{logo.png, 00_stamp.ttf}
├── tests/
├── install.sh
├── pyproject.toml
└── README.md
```
