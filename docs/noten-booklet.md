# `noten-booklet`

Löst A3-Booklet-Scans in A4-Seiten in korrekter Lesereihenfolge auf. Erwartet pro A3-Blatt zwei aufeinanderfolgende Eingabe-Seiten (Vorderseite, Rückseite).

```
noten-booklet partitur [PDF] [Flags]
noten-booklet noten    [PDF] [Flags]
```

## Wann welcher Modus?

| Modus | Wann nutzen? |
|---|---|
| `partitur` | Klassischer Partitur-Scan: Booklet wurde komplett auseinandergenommen, alle A3-Blätter zusammen sind **ein** Multi-Sheet-Booklet. |
| `noten` | A3-Notenscans gemischter Art: jedes A3-Blatt ist unabhängig — entweder Single-Sheet-Booklet (4 A4 = 1 A3-Blatt) oder fortlaufend (1\|2 vorne, 3\|4 hinten). |

## Eingabe-Voraussetzungen

* Eingabe-PDF hat eine **gerade Anzahl Seiten** (Vorder- und Rückseite jedes A3-Blatts).
* Eingabe-Seiten sollten landscape A3 sein (oder zumindest doppelt so breit wie hoch — die Mitte wird halbiert).
* Bei rotiertem Scan vorher `noten-pdf-fix --no-rotate` laufen lassen.

## Modus `partitur`

Die ganze PDF wird als **ein** Booklet behandelt. Bei N A3-Blättern ergibt das 4·N A4-Seiten in dieser Imposition:

```
Blatt 1 vorne:  [N    | 1]      Blatt 1 hinten:  [2     | N-1]
Blatt 2 vorne:  [N-2  | 3]      Blatt 2 hinten:  [4     | N-3]
…
```

Kein Nachfragen — ein Befehl, fertig.

```bash
noten-booklet partitur scan.pdf
```

## Modus `noten`

Jedes A3-Blatt wird einzeln behandelt. Pro Blatt:

| Layout | Vorne (links \| rechts) | Hinten (links \| rechts) |
|---|---|---|
| Booklet (Single-Sheet) | 4 \| 1 | 2 \| 3 |
| Fortlaufend            | 1 \| 2 | 3 \| 4 |

Standardmäßig fragt das Tool pro Blatt:

```
Blatt 1/8 > [ENTER für Booklet, f für fortlaufend, v für Vorschau, q zum Abbrechen]
```

Tasten:

| Eingabe | Wirkung |
|---|---|
| `ENTER` oder `b` | Aktuelles Blatt als Booklet markieren |
| `f` | Aktuelles Blatt als fortlaufend markieren |
| `v` | Vorder- und Rückseite des aktuellen Blatts in der PDF-Anzeige öffnen |
| `z` | Ein Blatt zurückspringen |
| `q` | Abbrechen |

Wenn schon vorher klar ist, dass alle Blätter gleich sind, lässt sich die Frage überspringen:

```bash
noten-booklet noten scan.pdf --all-booklet
noten-booklet noten scan.pdf --all-continuous
```

## Flags

| Flag | Bedeutung |
|---|---|
| `--out PATH` | Ausgabe-Pfad (Default: Eingabedatei wird überschrieben) |
| `--backup` | Vor Überschreiben `<datei>.pdf.bak` anlegen (Default: kein Backup) |
| `--all-booklet` | (nur `noten`) Alle Blätter als Single-Sheet-Booklet — keine Frage |
| `--all-continuous` | (nur `noten`) Alle Blätter als fortlaufend — keine Frage |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |

## Beispiele

```bash
# Partitur-Scan auflösen (überschreibt Original)
noten-booklet partitur partitur-scan.pdf

# Mit Backup
noten-booklet partitur partitur-scan.pdf --backup

# In neue Datei schreiben, Original behalten
noten-booklet partitur partitur-scan.pdf --out partitur-A4.pdf

# Notenscan mit gemischten Blättern: pro Blatt entscheiden
noten-booklet noten noten-scan.pdf

# Notenscan, alle Blätter sind fortlaufend (keine Frage)
noten-booklet noten noten-scan.pdf --all-continuous

# Ohne Argument: fzf-Auswahl im aktuellen Verzeichnis
noten-booklet partitur
```

## Pipeline-Tipp

`noten-booklet` produziert eine A4-PDF mit Stimmen oder Partitur in korrekter Reihenfolge — danach kann direkt `noten-verarbeitung` darauf angewandt werden, um die Stimmen einzeln zu trennen und zu stempeln.

```bash
noten-booklet noten scan.pdf --all-continuous
noten-verarbeitung scan.pdf
```
