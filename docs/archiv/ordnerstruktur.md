# Ordnerstruktur

Eine schlanke Ordnerstruktur ist auf Dauer wertvoller als eine clever verschachtelte. Empfehlung:

```
Notenarchiv/
├── Notensaetze/
│   ├── 0001 - Marsch der Medici/
│   │   ├── 0001 - Marsch der Medici - 00 Direktion.pdf
│   │   ├── 0001 - Marsch der Medici - 01 Flöte.pdf
│   │   └── …
│   ├── 0002 - Bahnfrei-Polka/
│   │   └── …
│   └── …
├── Eingang/
│   └── (Scans, die noch verarbeitet werden müssen)
└── Backup/
    └── (Ausgangsmaterial bei Bedarf)
```

## Warum so?

**Ein Ordner pro Notensatz, benannt mit `[Nr] - [Titel]`.**
:   Der Titel hilft beim Browsen, die Archivnummer beim Sortieren. Beim Auflisten erscheinen alle Notensätze automatisch numerisch in Eingangsreihenfolge.

**Stimmen flach im Ordner — keine Unterordner pro Instrumentenfamilie.**
:   Bei 12–20 Stimmen pro Notensatz wäre eine Unterordnerstruktur Overhead ohne Nutzen. Der Code-Präfix sortiert die Dateien ohnehin in Partiturreihenfolge.

**`Eingang/` als Wartezimmer.**
:   Frische Scans landen hier, bis du sie mit `noten-verarbeitung` aufgearbeitet hast. Hält das Archiv selbst sauber.

**Keine Genres / Schlagwörter im Ordnernamen.**
:   Verlockend, aber Genre-Zuordnungen sind subjektiv und ändern sich. Such-Tools (Volltextsuche, `fzf`, oder eine separate Datenbank/Tabelle) sind robuster.

## Cloud / Sync

`Notenarchiv/` liegt typischerweise in einem Cloud-synchronisierten Ordner (Nextcloud, Dropbox, OneDrive, Syncthing) — so haben mehrere Notenwarte denselben Stand und alles ist automatisch gesichert.

!!! warning "Vorsicht bei aktiver Bearbeitung"
    Wenn `noten-verarbeitung` läuft und Cloud-Sync gleichzeitig den Ordner abräumt, kann das zu unvollständig synchronisierten Stimmen-PDFs führen. Im Zweifel im Eingang arbeiten und erst nach erfolgreichem Durchlauf in den synchronisierten Bereich verschieben.

## Stamm-Tabelle

Parallel zur Ordnerstruktur lohnt sich eine separate Liste (Tabelle, Wiki, Datenbank) mit Metadaten, die nicht im Dateinamen stehen: Verlag, Komponist, Schwierigkeitsgrad, letzte Aufführung, Bemerkungen. Die Verbindung zur PDF läuft über die 4-stellige Archivnummer.
