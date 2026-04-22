# Noten-Tools
Eine Sammlung von Kommandozeilen-Werkzeugen für die automatisierte und schnelle Verarbeitung von PDF-Noten.

Eine Sammlung leistungsstarker Kommandozeilen-Skripte (Python & Shell) zur automatisierten Verarbeitung von digitalen Noten im PDF-Format (Scan oder digital gekuaft). Enthalten sind:
- **notenverarbeitung.py**: Automatisches splitten, bennen und stempeln einer großen Datei mit allen Stimmen.
- **notenstempel.py**: Stempeln und in A4-Skalieren einzener Dateien.
- **unbooklet.sh**: Automatisches trennen und umsortieren einer gescannten Partitur
- **fix-pdf.sh**: Korrigiert Probleme mit digital gekauften PDF-Dateien.

Die Python-Skripte werden in einer eigenen Umgebung ausgeführt. Alle Skripte können als Befehl (mit flags) für das Terminal verwendet werden. Alle Skripte nutzen *fuzzyfind* um eine oder mehrere Dateien auszuwählen.
<br>
<br>

>**Disclaimer:** <br>
>Ich bin **kein** professioneller Entwickler. Die Skripte wurden mithilfe von KI und meinem selbst erarbeiteten Wissen für mich selbst erstellt. Nutzt diese Skripte bitte mit Vorsicht und niemals an der einzigen Kopie eurer Daten. 
<br>
<br>

## Inhalt
- [❓ Was machen die Skripte?](#-was-machen-die-skripte)
- [🚀 Installation & Setup](#-installation--setup)
- [💻 Nutzung](#-Nutzung)
- [⚡ Vorgeschlagener Workflow](./workflow.md)

<br>
<br>
<br>

## ❓ Was machen die Skripte?

### >_ notenverarbeitung.py
Analysiert eingescannte PDFs mittels OCR (Texterkennung). Es erkennt automatisch das Instrument, trennt die Seiten passend auf, benennt die neuen PDFs korrekt und stempelt auf Wunsch direkt Logo und Archivnummer auf die erste Seite. Außerdem werden alle Seiten auf A4-skaliert.
Die Benennung findet nach der Nomenklatur statt, die ich nutze (ausgerichtet auf sinfonische Blasorchetser):
`[Archivnummer] - [Titel] - [Register-Code] [Instrument] [Stimme].pdf`
>**Beispiel**: 1368 - ABBA Gold - 05 F-Horn 1.pdf

Gespeichert werden die Dateien in einem Unterordner des aktuellen Ordners:
`[Archivnummer] - [Titel]`
>**Beispiel**: 1368 - ABBA Gold

**[Mehr zu Nomenklatur und Registercodes](./workflow.md#-Nomenklatur)

#### Hinweise & Einschränkungen zur Texterkennung
- Das Skript ist so geschrieben, dass die Partitur häufig nicht funktioniert, da hier die Struktur der Seite(n) meist anders ist. Die Partitur entferne ich meist vorher aus der Datei (pdfarranger).
- Die Stimmung (Bb, Es, C) wird im Normalfall miterkannt und an den Namen des Instruments angehängt. 
- Wenn die Zahl der Stimme als römische Zahl vorliegt (III statt 3) ist es häufig schwierig für die Texterkennung, das auseinanderzuhalten. 
- Schlagwerk wird nur sortiert nach "Drumset", "Pauken" & "Percussion" (Alles andere). Hier muss manuell sortiert werden.

<br>
<br>

### >_ notenstempel.py
Stempelt und skaliert (A4) bereits getrennte PDF-Dateien. Wie `notenverarbeitung.py` ohne Texterkennung und Trennen des Dokuments.

<br>
<br>

### >_ unbooklet.sh
Verarbeitet gescannte Partituren oder andere Booklets. Wird eine Partitur auseinandergenommen und doppelseitig (A3) gescannt, sind die Seiten komplett in flascher Reihenfolge. Dieses Skript teilt die Seiten in zwei DinA4 Seiten auf und sortiert sie so um, dass sie in der richtigen Reihenfolge sind. Funktioniert mit jedem booklet, welches so gescannt wurde. Am Ende entsteht eine DinA4-Datei in der richtigen Reihenfolge.

<br>
<br>

### >_ pdf-fix.sh
Korrigiert Probleme, die manchmal bei digital gekauften Noten entstehen (falsche drehung, Noten oder Text erscheinen beim Druck nicht...). Bereinigt auch Probleme, die beim bearbeiten mit grafischen tools wie pdf-arranger entstehen (drehung nur in Metadaten...). 

<br>
<br>
<br>

## 🚀 Installation & Setup

### Voraussetzungen

Diese Tools benötigen folgende Systempakete, die du über deinen Paketmanager installieren solltest:
`fzf`, `mupdf-tools` (für `mutool`), `qpdf`, `ghostscript` (`gs`), `tesseract-ocr` (mit deutschen und englischen Sprachpaketen) sowie einen einfachen Bildbetrachter (wie `feh`, `eog`, `imv` oder `gwenview`).

**Arch Linux / CachyOS / Manjaro:**
```bash
sudo pacman -S fzf mupdf-tools qpdf ghostscript tesseract tesseract-data-deu tesseract-data-eng feh git python
```

**Debian / Ubuntu / Mint:**
```bash
sudo apt install fzf mupdf-tools qpdf ghostscript tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng feh git python3.12-venv

```

<br>
<br>

### Installation

1. Klone das Repository:
```bash
git clone https://github.com/janmw/noten-tools
```
2. Wechsle in den Ordner:
```bash 
cd noten-tools
```
3. Mache das Installations-Skript ausführbar:
```bash
chmod +x install.sh
```
4. Und führe es aus: 
```
./install.sh
```
5. Je nach System musst du noch die folgende Zeile zu deiner rc hinzufügen (.bashrc / .zshrc ...)
```bash 
export PATH="$HOME/.local/bin:$PATH"
```


**Was das Installations-Skript macht:**
1. Es erstellt eine isolierte Python-Umgebung (`venv`) unter `~/.local/share/noten-tools`.
2. Es installiert alle nötigen Python-Abhängigkeiten (wie `PyMuPDF` und `OpenCV`), ohne dein System-Python zu verändern.
3. Es erstellt globale, Shell-unabhängige Wrapper-Skripte in `~/.local/bin`. 

Sobald die Installation abgeschlossen ist (und `~/.local/bin` in deinem `$PATH` liegt), kannst du die Tools aus jedem beliebigen Ordner in deinem Terminal aufrufen:

```bash
notenverarbeitung
notenstempel
unbooklet
pdf-fix
```

### Struktur für eigene Anpassungen

* Lege dein eigenes `logo.png` in den Ordner `src/`, bevor du das Installations-Skript ausführst, um deinen eigenen Stempel zu nutzen.
* Die Schriftart für den Stempel (`00_stamp.ttf`) kann ebenfalls in `src/` ausgetauscht werden.

## 💻 Nutzung
### Allgemeine Nutzung
1. Wechsle in den Ordner, in dem deine PDF-Dateien liegen
2. Starte den festgelegten Befehl[^1]
3. Wähle die Datei(en) aus
	- Du kannst nach Namen suchen, indem du einfach tippst
	- Du kannst mit den Pfeiltasten auswählen
	- mit `enter` wird die ausgewählte Datei verwendet
	- Mit `tab` wird eine Datei markiert. Du kannst mehrere Datein markieren und dann mit `enter` bestätigen 
4. Je nach Skript werden nun einige Dinge abgefragt, wie:
	- Titel des Stückes
	- Komponist (ein markanter Teil, z.B. Nachname; Hilft bei der identifizierung der neuen Stimme)
	- Archivnummer (für Ordner und Stempel)
	- ob gestempelt werden soll oder nicht [y/n]
5. Das Skript `notenverarbeitung` fragt nach, wenn es eine Stimme nicht erkennen kann (häufig bei Stimmen mit Umlauten). Ein Fenster mit Vorschau öffnet sich automatisch und im Terminal erscheint eine Eingabeaufforderung.

[^1]: Wenn kein Befehl integriert wurde, muss hier der komplette Pfad des Skriptes genutzt werden. 

### Flags
Sowohl `notenstempel.py` als auch `notenverarbeitung.py` unterstützen Parameter, um Stempel und Logo vertikal zu verschieben, falls Noten überdeckt werden:
```bash
notenverarbeitung.py --logo-runter 50 --stempel-runter 20
```
Die Zahlen sind dabei die Verschiebung nach unten in pt. 

<br>
<br>
<br>

## 📜 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
