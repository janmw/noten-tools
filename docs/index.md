# 🎼 noten-tools

> **Hinweis:** Ich bin kein professioneller Entwickler, sondern Notenwart. Dieses Projekt ist mit Unterstützung von KI-Assistenten entstanden — Code-Qualität und Architektur können entsprechend Lücken haben. Bug-Reports und Verbesserungsvorschläge sind ausdrücklich willkommen.

Das Repo bündelt mehrere CLI-Befehle mit gemeinsamem Präfix `noten-`. Sie teilen sich eine Python-Bibliothek (`notentools/shared`), ein Instrumenten-Mapping (`data/instruments.yaml`), Stempel-Assets (`assets/`) und eine User-Konfiguration unter `~/.config/noten-tools/`.

## ✨ Übersicht

| Befehl | Was er macht |
|---|---|
| [`noten-verarbeitung`](noten-verarbeitung.md) | Notensatz-PDF in einzelne Stimmen splitten, skalieren, stempeln |
| [`noten-stempel`](noten-stempel.md) | Logo + Archivnummer auf die erste Seite stempeln |
| [`noten-pdf-fix`](noten-pdf-fix.md) | PDFs reparieren, entschlüsseln, komprimieren, Auto-Rotate stoppen |
| [`noten-booklet`](noten-booklet.md) | A3-Booklet-Scans in A4-Seiten in korrekter Reihenfolge auflösen |
| [`noten-ausgabe`](noten-ausgabe.md) | Kleinen Ausgabe-Stempel `[Name] - [Datum]` unten mittig auf jede Seite setzen |
| [`noten-tools-aliases`](noten-tools-aliases.md) | Gelernte OCR-Aliase verwalten und ins Repo zurückspielen |

## 📦 Installation

```bash
git clone https://github.com/janmw/noten-tools.git
cd noten-tools
./install.sh
```

Erkennt Arch/CachyOS, Debian/Ubuntu, Fedora und macOS automatisch und installiert System-Abhängigkeiten (`tesseract` + `deu`/`eng`, `poppler-utils`, `fzf`, `xdg-utils`, `ghostscript`) sowie das Python-Paket via `pipx`.

Details, manuelle Installation, Distro-spezifische Pakete: [Installation](installation.md).

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

## ⚙️ Konfiguration

Beim ersten Start wird `~/.config/noten-tools/config.yaml` mit Defaults angelegt. Dort lassen sich Stempel-Position, Logo-/Font-Pfad, OCR-Sprache und -Confidence dauerhaft überschreiben.

Details: [Konfiguration](configuration.md).

## 📄 Lizenz

MIT — siehe [LICENSE](https://github.com/janmw/noten-tools/blob/main/LICENSE).
