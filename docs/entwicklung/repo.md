# Repo-Struktur

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
├── data/
│   └── instruments.yaml      # Mapping Instrumentname → Code, Aliase, Stimmungs-Default
├── assets/
│   ├── logo.png
│   ├── 00_stamp.ttf
│   └── JetBrainsMono-Regular.ttf
├── docs/                     # diese Doku
├── tests/
├── install.sh
├── pyproject.toml
├── mkdocs.yml
└── README.md
```

## Modul-Layout

Jedes CLI-Tool hat sein eigenes Submodul unter `notentools/`. Geteilter Code liegt in `notentools.shared`:

| Modul | Verantwortung |
|---|---|
| `shared.config` | Laden und Default-Auffüllen von `~/.config/noten-tools/config.yaml` |
| `shared.logging` | Konsolen- und File-Logging, gemeinsame Format-Konventionen |
| `shared.instruments` | Instrument-Identifikation aus OCR-Text, Naming-Postprocessing |
| `shared.pdf_io` | PDF-Lesen/-Schreiben, Format-Helfer |
| `shared.stamp` | Logo + Archivnummer-Overlay (von `verarbeitung` und `stempel` genutzt) |
| `shared.paths` | Pfad-Helfer für `~/.config/`, `~/.cache/`, `assets/` |

## Daten

- `data/instruments.yaml` — die kanonische Instrumenten-Datenbank: Code, Standard-Stimmung, Aliase. Wird von `noten-verarbeitung` und `noten-tools-aliases` gelesen.
- `~/.config/noten-tools/learned_aliases.yaml` — User-spezifische OCR-Lesungen, die noch nicht ins Repo zurückgespielt sind. Siehe [OCR-Aliase pflegen](../anwendung/aliase.md).
