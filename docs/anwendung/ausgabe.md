# Ausgabe-Vermerk

Befehl: `noten-ausgabe`

Stempelt einen kleinen Ausgabe-Vermerk `[Name] - [Datum]` in 7 pt JetBrains Mono unten mittig auf **jede Seite** einer oder mehrerer PDFs.

```
noten-ausgabe [PDF...] [Flags]
```

## Workflow

1. PDF-Auswahl: eine oder mehrere Dateien als Argumente, oder ohne Argumente per `fzf`-Mehrfachauswahl (TAB markieren, ENTER startet).
2. Name interaktiv abfragen — der zuletzt verwendete Name wird in `~/.config/noten-tools/config.yaml` (`ausgabe_name`) gecached und als Default-Vorschlag angezeigt. Mit `--name "..."` direkt setzen.
3. Datum: heute im deutschen Format `TT.MM.JJJJ`. Mit `--datum "..."` einen beliebigen String wörtlich stempeln.
4. Pro Datei wird auf jeder Seite der Text mittig unten platziert (≈ 3 mm Abstand zum unteren Rand).
5. Standardmäßig wird das Original überschrieben. Mit `--backup` wird vorher `<datei>.pdf.bak` daneben angelegt; mit `--out PATH` (nur bei einer einzelnen Datei) bleibt das Original unangetastet.

## Flags

| Flag | Bedeutung |
|---|---|
| `--name "..."` | Name direkt setzen (sonst Prompt mit gecachtem Default) |
| `--datum "..."` | Datum-String wörtlich stempeln (sonst heute `TT.MM.JJJJ`) |
| `--offset X,Y` | Position-Verschiebung in mm: X = nach rechts, Y = nach oben |
| `--font PATH` | Alternative TTF (Default: `assets/JetBrainsMono-Regular.ttf`) |
| `--backup` | Vor Überschreiben `<datei>.pdf.bak` anlegen (Default: kein Backup) |
| `--out PATH` | Ergebnis nach PATH schreiben (nur bei genau einer Eingabedatei) |
| `--verbose` / `--quiet` | Mehr/weniger Konsolen-Logs |

## Beispiele

```bash
# Eine Datei stempeln (Name interaktiv, Datum heute)
noten-ausgabe stimme.pdf

# Mehrere Dateien direkt mit Name + Datum
noten-ausgabe *.pdf --name "Max M." --datum "29.04.2026"

# fzf-Mehrfachauswahl
noten-ausgabe --name "Max M."

# Mit Backup
noten-ausgabe stimme.pdf --backup

# Ausgabe in andere Datei
noten-ausgabe stimme.pdf --out stimme-mit-vermerk.pdf

# Stempel etwas höher setzen (z. B. 2 mm nach oben)
noten-ausgabe stimme.pdf --offset 0,2
```

## Konfiguration

In `~/.config/noten-tools/config.yaml`:

```yaml
ausgabe_name: "Max M."     # zuletzt verwendeter Name (automatisch gepflegt)
mono_font_path: ""          # leer = JetBrains Mono aus assets/
footer:
  bottom_pt: 8.5            # Abstand Baseline → unterer Rand (≈ 3 mm)
  font_size_pt: 7.0
```

→ Vollständige Übersicht: [Konfiguration](../loslegen/konfiguration.md).
