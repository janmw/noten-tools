# Archivnummern & Codes

## Archivnummer

Jeder Notensatz bekommt eine **4-stellige Archivnummer** (`0000`–`9999`). Sie ist die einzige Identität des Notensatzes; Titel können sich ändern (Schreibweise, Umlaute, Sonderzeichen), die Nummer bleibt.

Verwendung:

- Ordnername: `1234 - Bahnfrei-Polka/`
- Stempel oben rechts auf jeder ersten Seite jeder Stimme: `Nr. 1234`
- Dateinamen: `1234 - Bahnfrei-Polka - 03 Klarinette 1.pdf`

!!! tip "Nummernvergabe"
    Vergib Nummern fortlaufend und lückenlos beim **Eingang** ins Archiv (nicht alphabetisch oder nach Genre). Lückenlosigkeit hilft, vergessene Notensätze sofort zu erkennen. Ein eingegangenes Stück darf seine Nummer nie wieder ändern, auch wenn es später aussortiert wird.

## Instrumenten-Codes

Vorne im Stimmen-Dateinamen steht ein **2-stelliger Code** (`00`–`11`), der die Instrumentenfamilie kennzeichnet:

| Code | Familie |
|---|---|
| 00 | Direktion / Partitur |
| 01 | Flöten & Piccolo |
| 02 | Oboe, Fagott und andere Doppelrohrbläser |
| 03 | Klarinetten (alle Arten) |
| 04 | Saxophone (alle Arten) |
| 05 | Hörner |
| 06 | Trompeten, Flügelhörner, Kornette |
| 07 | Tenorhörner, Bariton, Euphonium |
| 08 | Posaunen |
| 09 | Tuben & Bässe |
| 10 | Schlagwerk |
| 11 | Streicher und Sonstiges |

Der Code sortiert die Stimmen-Dateien automatisch in der Partitur-Reihenfolge — Direktion oben, Streicher unten.

## Sonderfälle

- **Reste-Stimme** `99 Reste`: Seiten, die `noten-verarbeitung` keinem Stimmen-Segment zuordnen konnte (Deckblatt, Inhalt, fehlerhafte Seiten). Beim Erstdurchlauf prüfen und entweder als eigene Stimme rausziehen oder verwerfen.
- **Code-Erweiterungen**: Das Schema ist auf 00–11 ausgelegt. Wenn du Familien benötigst, die hier nicht abgebildet sind (z. B. exotische Schlaginstrumente getrennt führen), erweiterst du `data/instruments.yaml` lokal.

## Beispiel

Notensatz `1234 - Bahnfrei-Polka` ergibt einen Ordner mit etwa folgenden Dateien:

```
1234 - Bahnfrei-Polka/
├── 1234 - Bahnfrei-Polka - 00 Direktion.pdf
├── 1234 - Bahnfrei-Polka - 01 Flöte.pdf
├── 1234 - Bahnfrei-Polka - 03 Klarinette 1.pdf
├── 1234 - Bahnfrei-Polka - 03 Klarinette 2.pdf
├── 1234 - Bahnfrei-Polka - 04 Saxophon Alt.pdf
├── 1234 - Bahnfrei-Polka - 05 F-Horn 1.pdf
├── 1234 - Bahnfrei-Polka - 06 Trompete 1.pdf
├── 1234 - Bahnfrei-Polka - 07 Bariton TC.pdf
├── 1234 - Bahnfrei-Polka - 08 Posaune 1.pdf
├── 1234 - Bahnfrei-Polka - 09 Tuba.pdf
└── 1234 - Bahnfrei-Polka - 10 Schlagwerk.pdf
```

Die genaue Schreibweise pro Instrument folgt den [Naming-Konventionen](naming.md).
