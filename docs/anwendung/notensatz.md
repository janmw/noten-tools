# Notensatz aufbereiten

Befehl: `noten-verarbeitung`

Splittet einen gescannten PDF-Notensatz für sinfonisches Blasorchester in einzelne Stimmen-PDFs, skaliert sie auf A4 (oder A5-quer) und stempelt sie optional digital mit Logo + Archivnummer.

```
noten-verarbeitung [PDF] [Flags]
```

## Workflow

1. PDF aus dem aktuellen Verzeichnis per `fzf` auswählen (oder als Argument übergeben).
2. Eingabe: 4-stellige Archivnummer + Titel + Stempeln (`j`/`n`).
3. OCR pro Seite (Tesseract `deu+eng`) auf den oberen 30 % der Seite. Rote Pixel werden vor der Erkennung gefiltert, damit ein roter Archivstempel nicht als Stimmenbezeichnung gelesen wird.
4. Eine neue Stimme beginnt, wenn alle drei Header-Blöcke gleichzeitig erkannt werden:
    * Titel mittig oben (groß)
    * Stimmenbezeichnung oben links
    * Komponist/Arrangeur oben rechts
5. Bei OCR-Unsicherheit (Confidence unter Schwelle oder Instrument unbekannt) öffnet sich die betroffene Seite via `xdg-open` zur Vorschau und das Terminal wird zurück in den Fokus geholt. Der User tippt die Stimme als Freitext ein (z. B. `Klarinette 2 in B`). Wenn die Eingabe einem bekannten Instrument entspricht, wird sie automatisch in Code/Name/Nummer/Zusatz zerlegt; ist das Instrument unbekannt, wird zusätzlich nur der Code (00–11) abgefragt. Die Zuordnung wird in `~/.config/noten-tools/learned_aliases.yaml` für die Zukunft gelernt.
6. Pro Stimme wird ein eigenes PDF erzeugt:
   ```
   [Archivnr] - [Titel]/
     [Archivnr] - [Titel] - [Code] [Instrument][ Nummer][ Zusatz].pdf
   ```
   Seiten, die zu keinem Stimmen-Segment zugeordnet werden konnten (z. B. Deckblatt, Inhalt, fehlerhafte Seiten am Anfang), landen gesammelt in `[Archivnr] - [Titel] - 99 Reste.pdf`.
7. Skalierung auf A4 hochkant (oder A5 quer mit `--a5`), fit-to-page mit weißen Rändern.
8. Stempel-Overlay (optional): Logo links oben, `Nr. XXXX` rechts oben.

## Flags

| Flag | Bedeutung |
|---|---|
| `--a5` | Ausgabeformat A5 quer statt A4 hochkant |
| `--no-stamp` | Stempel deaktivieren |
| `--logo PATH` | Alternatives Logo statt `assets/logo.png` |
| `--logo-offset X,Y` | Logo-Verschiebung in mm relativ zum Default (X = nach rechts, Y = nach unten) |
| `--archiv-offset X,Y` | Archivnummer-Verschiebung in mm relativ zum Default (X = nach links, Y = nach unten) |
| `--lang LANG` | OCR-Sprache, z. B. `deu`, `eng`, `deu+eng` |
| `--confidence N` | OCR-Confidence-Schwelle 0–100 (Default 50) |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |
| `--dry-run` | Nur erkennen, keine Dateien schreiben |

## Konventionen

Die Codes (00–11) und Stimmungs-Naming-Regeln, denen `noten-verarbeitung` beim Erzeugen von Dateinamen folgt, sind im Archiv-Bereich beschrieben:

- [Archivnummern & Codes](../archiv/nummern-und-codes.md)
- [Naming-Konventionen](../archiv/naming.md)

## Pipeline-Hinweise

- Wenn der Scan aus einem A3-Booklet stammt, vorher [`noten-booklet`](booklets.md) laufen lassen.
- Bei rotierten oder strukturell beschädigten Scans vorher [`noten-pdf-fix`](pdf-reparieren.md).
- Gelernte Aliase aus dem laufenden Betrieb können mit [`noten-tools-aliases`](aliase.md) ins Repo zurückgespielt werden.
