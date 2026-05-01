# Stimmen stempeln

Befehl: `noten-stempel`

Stempelt Logo + Archivnummer auf die **erste Seite** einer oder mehrerer fertiger Stimmen-PDFs. Kein OCR, kein Splitting, keine Skalierung — nur das Stempel-Overlay.

```
noten-stempel [PDF...] [Flags]
```

## Workflow

1. PDF-Auswahl: eine oder mehrere Dateien als Argumente, oder ohne Argumente per `fzf`-Mehrfachauswahl (TAB markieren, ENTER startet).
2. Archivnummer wird einmal abgefragt — alle ausgewählten PDFs bekommen die **gleiche** Nummer. Alternativ direkt per `--nr 1234`.
3. Pro Datei wird die erste Seite mit Logo (oben links) und `Nr. XXXX` (oben rechts) versehen.
4. Standardmäßig wird das Original überschrieben. Mit `--backup` wird vorher `<datei>.pdf.bak` daneben angelegt; mit `--out PATH` (nur bei einer einzelnen Datei) bleibt das Original unangetastet.

## Flags

| Flag | Bedeutung |
|---|---|
| `--nr 1234` | Archivnummer direkt setzen statt interaktiv abzufragen |
| `--logo PATH` | Alternatives Logo statt `assets/logo.png` |
| `--logo-offset X,Y` | Logo-Verschiebung in mm relativ zum Default (X = nach rechts, Y = nach unten) |
| `--archiv-offset X,Y` | Archivnummer-Verschiebung in mm relativ zum Default (X = nach links, Y = nach unten) |
| `--backup` | Vor dem Überschreiben `<datei>.pdf.bak` anlegen (Default: kein Backup) |
| `--out PATH` | Ergebnis nach PATH schreiben, Original unangetastet (nur bei genau einer Eingabedatei) |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |

## Beispiele

```bash
# Eine Datei stempeln (Nummer interaktiv abfragen)
noten-stempel stimme.pdf

# Mehrere Dateien direkt mit der gleichen Nummer
noten-stempel klarinette1.pdf klarinette2.pdf trompete.pdf --nr 1234

# fzf-Mehrfachauswahl im aktuellen Verzeichnis
noten-stempel --nr 1234

# Mit Backup
noten-stempel stimme.pdf --nr 1234 --backup

# Ausgabe in andere Datei schreiben (nur einzelne Datei)
noten-stempel stimme.pdf --nr 1234 --out gestempelt.pdf

# Logo etwas nach rechts und unten verschieben
noten-stempel stimme.pdf --nr 1234 --logo-offset 3,2
```

!!! tip "Wann lieber `noten-verarbeitung`?"
    `noten-stempel` ist für **fertige** Einzelstimmen gedacht, die aus anderen Quellen kommen oder bei denen sich nur die Archivnummer geändert hat. Beim erstmaligen Aufbereiten eines kompletten Notensatzes ist [`noten-verarbeitung`](notensatz.md) der richtige Einstieg, da dort Splitting und Stempeln in einem Rutsch passieren.
