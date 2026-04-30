# Dokumentation

Die Doku liegt im `docs/`-Verzeichnis und wird mit [MkDocs](https://www.mkdocs.org/) und dem [Catppuccin-Theme](https://github.com/catppuccin/mkdocs) (basiert auf [Material](https://squidfunk.github.io/mkdocs-material/)) gerendert.

## Lokal bauen

```bash
pip install -e ".[docs]"
mkdocs serve   # Live-Preview auf http://127.0.0.1:8000
mkdocs build   # statische Site nach site/
```

## Auto-Deploy

Pushs auf `main` triggern via GitHub Actions einen Deploy auf GitHub Pages — siehe `.github/workflows/`.

## Struktur

| Bereich | Inhalt |
|---|---|
| `docs/index.md` | Startseite mit Grid Cards und Wegweiser |
| `docs/loslegen/` | Installation, Konfiguration, Erste Schritte |
| `docs/anwendung/` | Workflow-Übersicht und aufgabenorientierte Tool-Anleitungen |
| `docs/archiv/` | Tool-unabhängige Konventionen rund ums Notenarchiv |
| `docs/entwicklung/` | Diese Section |

## Konventionen

- **Aufgabenorientiert** vor tool-orientiert. Seitennamen beschreiben, was der Notenwart erreichen will, nicht welcher Befehl es technisch tut.
- **Admonitions** (`!!! tip`, `!!! warning`, `!!! note`) für Hinweise, die sonst im Fließtext untergehen.
- **Distro-spezifische Code-Blöcke** als `=== "Distro"`-Tabs, nicht als Bullet-Liste.
- **Mermaid** für Workflows, sparsam einsetzen.
- **Grid Cards** für Übersichtsseiten — nicht für Detail-Inhalte.
