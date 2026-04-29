# 🎼 noten-tools

> **Hinweis:** Ich bin kein professioneller Entwickler, sondern Notenwart. Dieses Projekt ist mit Unterstützung von KI-Assistenten entstanden — Code-Qualität und Architektur können entsprechend Lücken haben. Bug-Reports und Verbesserungsvorschläge sind ausdrücklich willkommen.

Das Repo bündelt mehrere CLI-Befehle mit gemeinsamem Präfix `noten-`. Sie teilen sich eine Python-Bibliothek (`notentools/shared`), ein Instrumenten-Mapping (`data/instruments.yaml`), Stempel-Assets (`assets/`) und eine User-Konfiguration unter `~/.config/noten-tools/`.

## ✨ Übersicht

| Befehl | Was er macht | Doku |
|---|---|---|
| `noten-verarbeitung` | Notensatz-PDF in einzelne Stimmen splitten, skalieren, stempeln | [docs/noten-verarbeitung.md](docs/noten-verarbeitung.md) |
| `noten-stempel` | Logo + Archivnummer auf die erste Seite stempeln | [docs/noten-stempel.md](docs/noten-stempel.md) |
| `noten-pdf-fix` | PDFs reparieren, entschlüsseln, komprimieren, Auto-Rotate stoppen | [docs/noten-pdf-fix.md](docs/noten-pdf-fix.md) |
| `noten-booklet` | A3-Booklet-Scans in A4-Seiten in korrekter Reihenfolge auflösen | [docs/noten-booklet.md](docs/noten-booklet.md) |
| `noten-ausgabe` | Kleinen Ausgabe-Stempel `[Name] - [Datum]` unten mittig auf jede Seite setzen | [docs/noten-ausgabe.md](docs/noten-ausgabe.md) |
| `noten-tools-aliases` | Gelernte OCR-Aliase verwalten und ins Repo zurückspielen | [docs/noten-tools-aliases.md](docs/noten-tools-aliases.md) |

## 📦 Installation

```bash
git clone https://github.com/janmw/noten-tools.git
cd noten-tools
./install.sh
```

Erkennt Arch/CachyOS, Debian/Ubuntu, Fedora und macOS automatisch und installiert System-Abhängigkeiten (`tesseract` + `deu`/`eng`, `poppler-utils`, `fzf`, `xdg-utils`, `ghostscript`) sowie das Python-Paket via `pipx`.

Details, manuelle Installation, Distro-spezifische Pakete: [docs/installation.md](docs/installation.md).

## 🚀 Schnellstart

```bash
# Notensatz in Einzel-Stimmen splitten + stempeln
noten-verarbeitung scan.pdf

# Logo + Archivnummer auf erste Seite einer fertigen Stimme stempeln
noten-stempel stimme.pdf --nr 1234

# PDF reparieren und gleichzeitig komprimieren
noten-pdf-fix scan.pdf --repair --compress

# A3-Booklet-Scan einer Partitur zu A4 in richtiger Reihenfolge auflösen
noten-booklet partitur scan.pdf
```

Volle Workflow- und Flag-Doku jeweils in `docs/<befehl>.md`.

## ⚙️ Konfiguration

Beim ersten Start wird `~/.config/noten-tools/config.yaml` mit Defaults angelegt. Dort lassen sich Stempel-Position, Logo-/Font-Pfad, OCR-Sprache und -Confidence dauerhaft überschreiben.

Details: [docs/configuration.md](docs/configuration.md).

## 🛣️ Roadmap

Aktuell keine offenen Punkte.

Entwicklungs-Setup (venv, editierbare Installation, lokale Tests): [docs/development.md](docs/development.md).

## 📄 Lizenz

MIT — siehe [LICENSE](LICENSE).
