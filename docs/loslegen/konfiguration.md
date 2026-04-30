# Konfiguration

Beim ersten Start wird `~/.config/noten-tools/config.yaml` mit sinnvollen Defaults angelegt. Du kannst sie ohne Einschränkung bearbeiten — fehlende Werte werden zur Laufzeit aus den Defaults ergänzt.

## Was lässt sich konfigurieren?

| Bereich | Schlüssel | Bedeutung |
|---|---|---|
| Stempel | `stamp.logo_offset_pt`, `stamp.archiv_offset_pt` | Logo- und Archivnummern-Position in pt vom Seitenrand |
| Stempel | `logo_path`, `font_path` | Eigene Logo-Datei und Schriftart |
| OCR | `ocr.lang` | `deu`, `eng` oder `deu+eng` (Default) |
| OCR | `ocr.min_confidence` | Schwelle 0–100, ab welcher OCR-Lesungen akzeptiert werden (Default 50) |
| OCR | `ocr.dpi` | Render-Auflösung für die OCR (Default 300) |
| Format | `default_a5` | Default-Ausgabeformat von `noten-verarbeitung`: `false` = A4 hochkant, `true` = A5 quer |
| Ausgabe | `ausgabe_name` | Zuletzt verwendeter Name für `noten-ausgabe` (wird automatisch gepflegt) |
| Ausgabe | `mono_font_path` | Alternative Monospace-Schriftart für den Ausgabe-Stempel |
| Ausgabe | `footer.bottom_pt`, `footer.font_size_pt` | Position und Größe des Ausgabe-Stempels |

## Logo & Schriftart austauschen

Standard-Logo: `assets/logo.png` (im Repo). Standard-Schrift: `assets/00_stamp.ttf`.

Drei Wege zum Tauschen, mit zunehmender Reichweite:

1. **Pro Aufruf** — `--logo /pfad/zum/logo.png` als Flag übergeben. Einmalig.
2. **Pro User** — `logo_path: /pfad/zum/logo.png` in `~/.config/noten-tools/config.yaml`. Gilt für dich auf diesem Rechner.
3. **Pro Repo** — `assets/logo.png` direkt im Klon ersetzen. Gilt für alle, die diesen Klon benutzen.

## Wichtige Pfade

| Zweck | Ort |
|---|---|
| User-Konfiguration | `~/.config/noten-tools/config.yaml` |
| Gelernte OCR-Aliase | `~/.config/noten-tools/learned_aliases.yaml` |
| Logfiles | `~/.cache/noten-tools/logs/` |

!!! tip "Aliase-Datei"
    `learned_aliases.yaml` wird automatisch von `noten-verarbeitung` gepflegt. Manuelles Bearbeiten ist möglich, in der Regel aber unnötig — siehe [OCR-Aliase pflegen](../anwendung/aliase.md).
