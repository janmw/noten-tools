# 🎼 Noten-Tools

Eine Sammlung leistungsstarker Kommandozeilen-Skripte (Python & Shell) zur automatisierten und schnellen Verarbeitung von digitalen Noten im PDF-Format (Scans oder digital gekaufte Versionen). Alle Skripte nutzen *Fuzzyfind*, um eine oder mehrere Dateien komfortabel im Terminal auszuwählen. Die Python-Skripte werden dabei in einer eigenen, isolierten Umgebung ausgeführt.

> **Disclaimer:**
> Ich bin **kein** professioneller Entwickler. Die Skripte wurden mithilfe von KI und meinem selbst erarbeiteten Wissen für meinen eigenen Gebrauch erstellt. Nutzt diese Skripte bitte mit Vorsicht und wendet sie niemals an der einzigen Kopie eurer Daten an!

## 📑 Inhalt
- [❓ Was machen die Skripte?](#-was-machen-die-skripte)
- [🚀 Installation & Setup](#-installation--setup)
- [💻 Nutzung](#-nutzung)
- [⚡ Vorgeschlagener Workflow](./workflow.md)

<br>

---

## ❓ Was machen die Skripte?

Hier ist eine Übersicht der enthaltenen Werkzeuge:

| Skript | Beschreibung |
| :--- | :--- |
| **`notenverarbeitung.py`** | Analysiert eingescannte PDFs mittels OCR (Texterkennung). Erkennt automatisch das Instrument, trennt die Seiten, benennt die PDFs nach Nomenklatur, skaliert auf A4 und stempelt auf Wunsch Logo und Archivnummer auf die erste Seite. |
| **`notenstempel.py`** | Stempelt und skaliert (A4) bereits getrennte PDF-Dateien. Funktioniert wie *notenverarbeitung.py*, jedoch ohne Texterkennung und Dokumententrennung. |
| **`unbooklet.sh`** | Trennt und umsortiert gescannte Partituren oder Booklets. Teilt doppelseitige A3-Scans (die oft in falscher Reihenfolge vorliegen) in zwei A4-Seiten auf und sortiert sie in die korrekte Reihenfolge. |
| **`pdf-fix.sh`** | Korrigiert Probleme mit digital gekauften PDFs (z. B. falsche Drehung oder fehlende Noten/Texte beim Druck). Bereinigt auch Metadaten-Fehler, die durch grafische Tools wie *pdf-arranger* entstehen können. |

### 🔍 Details zur `notenverarbeitung.py`

Die Benennung der generierten Dateien folgt einer festen Nomenklatur (ausgerichtet auf sinfonische Blasorchester):
`[Archivnummer] - [Titel] - [Register-Code] [Instrument] [Stimme].pdf`
**Beispiel:** `1368 - ABBA Gold - 05 F-Horn 1.pdf`

Die Speicherung erfolgt in einem automatisch erstellten Unterordner: `[Archivnummer] - [Titel]` <br>
*[Mehr zu Nomenklatur und Registercodes findest du im Workflow-Guide.](./workflow.md#-Nomenklatur)*

**Hinweise & Einschränkungen zur Texterkennung (OCR):**
* Partituren funktionieren oft nicht, da die Seitenstruktur hier abweicht. Es empfiehlt sich, die Partitur vorab manuell zu entfernen (z. B. mit pdfarranger).
* Die Stimmung (Bb, Es, C) wird im Regelfall erkannt und an den Instrumentennamen angehängt.
* Römische Zahlen (z. B. III statt 3) sind für die Texterkennung oft schwer zu differenzieren.
* Schlagwerk wird grob in "Drumset", "Pauken" & "Percussion" unterteilt – hier ist oft manuelles Nachsortieren gefragt.

<br>

---

## 🚀 Installation & Setup

### Voraussetzungen
Die Skripte benötigen einige Systempakete, die du über deinen Paketmanager installieren solltest:

**Arch Linux / CachyOS / Manjaro:**
```bash
sudo pacman -S fzf mupdf-tools qpdf ghostscript tesseract tesseract-data-deu tesseract-data-eng feh git python
```

**Debian / Ubuntu / Mint:**
```bash
sudo apt install fzf mupdf-tools qpdf ghostscript tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng feh git python3.12-venv
```

### Installation durchführen
1. **Repository klonen:** 
```bash
git clone https://github.com/janmw/noten-tools
```
2. **Ordner wechseln:** 
```
cd noten-tools
```
3. **Rechte vergeben:** 
```
chmod +x install.sh
```
4. **Skript ausführen:** 
```
./install.sh
```
5. **Pfad anpassen:** 
Je nach System musst du `export PATH="$HOME/.local/bin:$PATH"` zu deiner Shell-Konfiguration (`.bashrc` / `.zshrc`) hinzufügen.

**Was passiert im Hintergrund?**
Das Installations-Skript erstellt eine isolierte Python-Umgebung (`venv`) unter `~/.local/share/noten-tools` und installiert alle Abhängigkeiten, ohne dein System-Python zu berühren. Zudem werden globale Wrapper-Skripte in `~/.local/bin` erstellt. Danach können die Tools (`notenverarbeitung`, `notenstempel`, `unbooklet`, `pdf-fix`) aus jedem Ordner heraus aufgerufen werden.

### Eigene Anpassungen (Logo & Schriftart)
* Lege dein eigenes `logo.png` in den Ordner `src/`, bevor du das Installations-Skript ausführst, um einen individuellen Stempel zu nutzen.
* Die Schriftart für den Stempel (`00_stamp.ttf`) kann ebenfalls im Ordner `src/` ausgetauscht werden.

<br>

---

## 💻 Nutzung

### Allgemeine Schritte
1. **Ordner wählen:** Wechsle im Terminal in den Ordner mit deinen PDF-Dateien.
2. **Skript starten:** Führe den gewünschten Befehl aus. Falls das Tool nicht im Pfad liegt, nutze den kompletten Pfad zum Skript.
3. **Dateien auswählen:** Tippe, um nach Namen zu suchen, oder navigiere mit den Pfeiltasten. Drücke `Enter`, um eine Datei zu bestätigen. Möchtest du mehrere Dateien wählen, markiere sie zunächst mit `Tab` und drücke am Ende `Enter`.
4. **Metadaten eingeben:** Je nach Skript wirst du nun nach dem Titel, dem Komponisten (am besten ein markanter Teil wie der Nachname für die Erkennung), der Archivnummer und dem Stempel-Wunsch (`y/n`) gefragt.
5. **Konflikte lösen:** Kann eine Stimme nicht erkannt werden (z. B. durch Umlaute), öffnet sich automatisch ein Vorschaufenster und das Terminal bittet um eine manuelle Zuordnung.

### Optionale Parameter (Flags)
Sowohl `notenstempel.py` als auch `notenverarbeitung.py` unterstützen Parameter, um den Stempel und das Logo vertikal zu verschieben (in *pt*), falls wichtige Noten verdeckt werden:
```bash
notenverarbeitung.py --logo-runter 50 --stempel-runter 20
```

---

## 📜 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
