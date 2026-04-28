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

## Repo-Struktur

```
noten-tools/
├── bin/
├── notentools/
│   ├── shared/        # geteilte Bibliothek (config, logging, instruments, pdf_io, stamp, paths)
│   ├── verarbeitung/  # noten-verarbeitung CLI
│   ├── pdf_fix/       # noten-pdf-fix CLI
│   ├── stempel/       # noten-stempel CLI
│   └── aliases/       # noten-tools-aliases CLI
├── data/instruments.yaml
├── assets/{logo.png, 00_stamp.ttf}
├── install.sh
├── pyproject.toml
└── README.md
```
