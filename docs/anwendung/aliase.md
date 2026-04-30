# OCR-Aliase pflegen

Befehl: `noten-tools-aliases`

Verwaltet die gelernten OCR-Aliase (`~/.config/noten-tools/learned_aliases.yaml`) und schlägt sie zur Aufnahme ins Repo (`data/instruments.yaml`) vor.

[`noten-verarbeitung`](notensatz.md) lernt OCR-Lesungen, die nicht direkt einem Instrument zugeordnet werden konnten, automatisch in die User-Datei. Mit diesem Tool lassen sich diese Einträge anzeigen, wieder löschen oder als YAML-Patch zur dauerhaften Aufnahme ins Repo ausgeben.

```
noten-tools-aliases <subcommand>
```

## Subkommandos

| Befehl | Bedeutung |
|---|---|
| `list` | Alle gelernten Aliase anzeigen (`raw -> code instrument [nummer] [in X]`) |
| `sync` | Aliase mit dem Repo abgleichen und neue Einträge als YAML-Patch ausgeben |
| `clear` | Alle gelernten Aliase löschen (`learned_aliases.yaml` entfernen) |

## Beispiele

```bash
# Was hat noten-verarbeitung bisher gelernt?
noten-tools-aliases list

# Patch-Vorschlag für data/instruments.yaml ausgeben
noten-tools-aliases sync

# Alle gelernten Aliase verwerfen
noten-tools-aliases clear
```

## `sync` im Detail

`sync` prüft jeden Eintrag in `learned_aliases.yaml`:

- Wenn der gelernte Identifier (z. B. `03 Klarinette 2 in B`) zu einem im Repo existierenden Instrument passt und der Roh-Text dort noch nicht als Alias eingetragen ist, wird er als Vorschlag ausgegeben.
- Einträge, die zu keinem bekannten Repo-Instrument passen, werden am Ende als Hinweis aufgelistet (z. B. unbekannte Stimmen, die manuell in `instruments.yaml` ergänzt werden müssen).

Die Ausgabe ist gültiges YAML, gruppiert nach Code und Instrument:

```yaml
"03":
  Klarinette:
    aliases:
      - 'Clarinet'
      - 'Klar.'
```

Die Listeneinträge können direkt unter `aliases:` des jeweiligen Instruments in `data/instruments.yaml` ergänzt werden — entweder per Pull Request oder direkt im lokalen Klon.
