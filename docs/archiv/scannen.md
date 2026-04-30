# Scannen

Eine gute Eingangsqualität spart später Nacharbeit. Empfehlungen für scan-taugliches Material:

## Auflösung

| Verwendung | Empfehlung |
|---|---|
| Reines Druck-Archiv | 300 dpi |
| Mit OCR (`noten-verarbeitung`) | mindestens 300 dpi, gerne 400 dpi |
| Bildschirm-Anzeige am Tablet | 200 dpi reicht |

`noten-verarbeitung` rendert die OCR-Vorlage intern auf 300 dpi (konfigurierbar via `ocr.dpi`). Ein darunterliegender Eingangsscan in 150 dpi rauscht.

## Farbe

| Material | Empfehlung |
|---|---|
| Schwarz auf Weiß | Graustufen, 8 bit |
| Mit handschriftlichen Anmerkungen in Farbe | Farbe (24 bit) |
| Mit rotem Archivstempel | Farbe — `noten-verarbeitung` filtert rote Pixel vor der OCR heraus |

Reine Schwarzweiß-Modi (1 bit) verlieren Anti-Aliasing — OCR-Genauigkeit leidet messbar.

## Format

- **Pro Notensatz eine PDF.** Mehrere Stimmen in einer Datei, der Splitting-Algorithmus erkennt die Übergänge anhand der Header.
- **Konsistente Seitenausrichtung.** Wenn der Scanner gemischt rotiert, vorher [`noten-pdf-fix --no-rotate`](../anwendung/pdf-reparieren.md).

## Booklets

Wenn die Vorlage als A3-Booklet vorliegt (Mittelfaltung), gibt es zwei Wege:

1. **Booklet komplett auseinandernehmen** und alle A3-Blätter scannen. Anschließend [`noten-booklet partitur`](../anwendung/booklets.md) ausführen — löst das Booklet automatisch in A4 in der richtigen Reihenfolge auf.
2. **Stimmen einzeln** scannen, falls möglich. Aufwändiger im Scan, dafür kein Auflösungs-Schritt nötig.

!!! tip "Im Zweifel auseinandernehmen"
    Booklets nicht versuchen, in der Mitte aufgeschlagen zu scannen — die Schattenkante in der Mitte stört die OCR und das Format ist krumm.

## Vorbereitung am Eingang

Bevor ein Scan in `noten-verarbeitung` läuft, lohnt ein kurzer Sichtcheck:

- Sind alle Seiten in der richtigen Reihenfolge?
- Stehen alle Seiten richtig herum?
- Sind alle Seiten lesbar — keine fehlenden Ränder, kein abgeschnittener Stimmenbezeichnungs-Header?
- Ist das PDF strukturell intakt? (Lässt es sich im Viewer ohne Warnung öffnen?)

Bei Auffälligkeiten: erst [`noten-pdf-fix`](../anwendung/pdf-reparieren.md), dann weiter.
