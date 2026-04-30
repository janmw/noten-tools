# Naming-Konventionen

## Grundschema

```
[Archivnr] - [Titel] - [Code] [Instrument][ Nummer][ Zusatz].pdf
```

Beispiele:

| Dateiname | Stimme |
|---|---|
| `1234 - Bahnfrei-Polka - 03 Klarinette 1.pdf` | Klarinette 1 (in B, Standard) |
| `1234 - Bahnfrei-Polka - 03 Es-Klarinette.pdf` | Es-Klarinette (Sonderfall) |
| `1234 - Bahnfrei-Polka - 05 F-Horn 1.pdf` | F-Horn 1 (Stimmung immer im Namen) |
| `1234 - Bahnfrei-Polka - 07 Bariton TC.pdf` | Bariton im Tenorschlüssel |

## Stimmungs-Regeln

Stimmung wird im Dateinamen nur dann mitgeführt, wenn sie *nicht* der im Verein üblichen entspricht. So bleibt der Standardfall kurz; Abweichungen fallen sofort auf.

| Instrument | Standard (kein Zusatz) | Sonderfall im Namen |
|---|---|---|
| Flöte / Piccolo, Oboe / Fagott | in C | mit „in X" |
| Klarinette | in B | `Es-Klarinette` (in Es) |
| Bassklarinette | in B | mit „in X" |
| Saxophone | – (Stimmung egal, durch Sopran/Alt/Tenor/Bariton definiert) | – |
| Horn | – (Stimmung **immer** im Namen) | `F-Horn`, `Es-Horn`, … |
| Trompete / Flügelhorn / Kornett | in B | mit „in X" |
| Tenorhorn | in B | mit „in X" |
| Bariton / Euphonium | – (Schlüssel **immer** im Namen) | `Bariton TC` (in B), `Bariton BC` (in C); analog Euphonium |
| Posaune | in C | `B-Posaune` (in B) |
| Tuba / Kontrabass | in C | mit „in X" |
| Schlagwerk | – (Stimmung egal) | – |

!!! note "OCR-Verhalten bei Hörnern und Bariton/Euphonium"
    Bei Hörnern und Bariton/Euphonium ohne erkennbare Stimmung im OCR-Text wird die Identifikation als unsicher gewertet — `noten-verarbeitung` fragt dann interaktiv um die Stimmung, weil die Information für den Dateinamen zwingend gebraucht wird.

## Stimmen-Nummerierung

Wenn es mehrere Stimmen des gleichen Instruments gibt (typisch: Klarinette 1/2/3, Trompete 1/2/3), folgt die Nummer direkt nach dem Instrumentnamen:

```
03 Klarinette 1
03 Klarinette 2
03 Klarinette 3
```

Eine einzige Stimme bekommt **keine** Nummer (also `01 Flöte` statt `01 Flöte 1`).

## Code-Trennung

Der 2-stellige Code (`00`–`11`) ist immer mit einem Leerzeichen vom Instrumentnamen getrennt — nicht mit Bindestrich. Erleichtert das visuelle Scannen.

→ Code-Definitionen: [Archivnummern & Codes](nummern-und-codes.md).
