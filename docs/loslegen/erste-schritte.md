# Erste Schritte

Geführtes End-to-End-Beispiel: ein gescannter Notensatz wird zu einem Ordner mit einzelnen, gestempelten A4-Stimmen-PDFs. Du brauchst eine PDF eines Notensatzes für sinfonisches Blasorchester. Beispiel: eine Polka mit 12 Stimmen.

!!! info "Voraussetzungen"
    [Installation](installation.md) ist durch. `noten-verarbeitung --help` gibt eine Hilfe aus.

## 1. Vorbereitung: ist die PDF in Ordnung?

Wenn der Scan aus einem A3-Booklet stammt, muss er erst in A4 in der richtigen Reihenfolge zerlegt werden:

```bash
noten-booklet partitur scan-booklet.pdf
```

Wenn die PDF passwortgeschützt ist, sich beim Öffnen merkwürdig dreht, oder strukturell beschädigt scheint:

```bash
noten-pdf-fix scan.pdf --decrypt --repair --no-rotate
```

Nicht alles davon ist immer nötig. Im Zweifel ist `noten-pdf-fix scan.pdf` (Default: `--no-rotate`) ein guter erster Reflex.

→ Details: [Booklets auflösen](../anwendung/booklets.md), [PDFs reparieren](../anwendung/pdf-reparieren.md).

## 2. Splitting + Stempeln in einem Rutsch

Hauptbefehl. PDF wird in einzelne Stimmen-PDFs zerlegt, auf A4 skaliert, mit Logo + Archivnummer gestempelt:

```bash
noten-verarbeitung scan.pdf
```

Du wirst dann gefragt:

1. **Archivnummer** (4-stellig, z. B. `1234`)
2. **Titel** (z. B. `Bahnfrei-Polka`)
3. **Stempeln?** (`j`/`n`)

Anschließend läuft OCR pro Seite. Bei sicherer Erkennung passiert nichts; bei unsicherer Erkennung öffnet sich die Seite zur Vorschau und du tippst die Stimmenbezeichnung als Freitext ein:

```
Klarinette 2 in B
```

`noten-verarbeitung` zerlegt das automatisch in Code, Instrument, Nummer und Stimmung — und merkt sich diese Lesung für die Zukunft in `~/.config/noten-tools/learned_aliases.yaml`.

## 3. Ergebnis

Im aktuellen Verzeichnis liegt jetzt ein Ordner:

```
1234 - Bahnfrei-Polka/
  1234 - Bahnfrei-Polka - 00 Direktion.pdf
  1234 - Bahnfrei-Polka - 01 Flöte.pdf
  1234 - Bahnfrei-Polka - 03 Klarinette 1.pdf
  1234 - Bahnfrei-Polka - 03 Klarinette 2.pdf
  ...
  1234 - Bahnfrei-Polka - 99 Reste.pdf   (falls Seiten nicht zugeordnet werden konnten)
```

Jede Stimme ist auf A4 skaliert und trägt oben links das Logo und oben rechts `Nr. 1234`.

→ Konventionen für Codes und Naming: [Archivnummern & Codes](../archiv/nummern-und-codes.md), [Naming-Konventionen](../archiv/naming.md).

## 4. Nachträgliche Bearbeitung

### Eine Stimme nachstempeln

Wenn du eine fertige Stimme aus einer anderen Quelle hast, die nur noch Logo + Archivnummer braucht:

```bash
noten-stempel klarinette.pdf --nr 1234
```

→ [Stimmen stempeln](../anwendung/stempeln.md).

### Bei der Ausgabe an einen Musiker

Beim Verleihen von Noten kann ein kleiner Vermerk auf jede Seite gesetzt werden:

```bash
noten-ausgabe klarinette.pdf
```

Du wirst nach deinem Namen gefragt, das Datum ist heute. Beides landet in 7 pt unten mittig auf jeder Seite.

→ [Ausgabe-Vermerk](../anwendung/ausgabe.md).

## Was als Nächstes?

- Mehr Tools im Detail: [Anwendung](../anwendung/index.md).
- Wie organisierst du dein Archiv sinnvoll? [Notenarchiv aufbauen](../archiv/index.md).
- Konfiguration anpassen (Stempel-Position, eigenes Logo): [Konfiguration](konfiguration.md).
