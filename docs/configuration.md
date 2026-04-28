# Konfiguration

## `~/.config/noten-tools/config.yaml`

Beim ersten Start wird die Datei mit Defaults angelegt. Dort lassen sich folgende Werte dauerhaft überschreiben:

* **Stempel-Position** — Logo + Archivnummer in pt vom Seitenrand
* **Logo-Pfad** und **Schriftart-Pfad**
* **OCR-Sprache** (`deu`, `eng`, `deu+eng`), **OCR-Confidence-Schwelle**, **OCR-DPI**
* **Default für `a5`** (true/false)

## Logo & Schriftart austauschen

Standard-Logo: `assets/logo.png`. Standard-Schrift: `assets/00_stamp.ttf`.

Drei Wege zum Tauschen:

* Datei im Repo direkt ersetzen — gilt für alle User des Repos
* In `~/.config/noten-tools/config.yaml` den `logo_path` / `font_path` auf eine eigene Datei setzen — gilt nur für dich
* Pro Aufruf `--logo /pfad/zum/logo.png` übergeben — einmalig pro Befehl

## Weitere Pfade

| Zweck | Ort |
|---|---|
| Gelernte Aliase | `~/.config/noten-tools/learned_aliases.yaml` |
| Logfiles | `~/.cache/noten-tools/logs/` |
