# Backup-Strategie

Ein digitales Notenarchiv ist nur so gut wie sein letzter Backup. Drei einfache Faustregeln.

## 3-2-1-Regel

- **3** Kopien deiner Daten,
- auf **2** verschiedenen Medien,
- davon **1** an einem anderen Ort.

Für ein Notenarchiv reicht das in der Praxis so:

| Kopie | Medium | Ort |
|---|---|---|
| Arbeitskopie | Cloud-Sync auf Laptop | dein Zuhause / Vereinsheim |
| Backup-Kopie | externe Festplatte / NAS | dein Zuhause |
| Off-Site | Cloud-Anbieter (oder zweite Festplatte beim Vereinsvorstand) | woanders |

## Was gehört ins Backup?

**Ja:**

- Der `Notenarchiv/`-Ordner mit allen Stimmen-PDFs
- Eingangsscans im `Eingang/` (zumindest bis sie verarbeitet sind)
- Stamm-Tabelle / Datenbank mit Metadaten
- `~/.config/noten-tools/learned_aliases.yaml`, falls du viele Aliase gelernt hast und sie noch nicht ins Repo zurückgespielt sind

**Nein:**

- `~/.cache/noten-tools/logs/` — neu generiert, kein Verlustrisiko
- Automatisch erzeugte `*.pdf.bak`-Dateien — nur kurzlebig

## Versionierung

Die wichtigste Eigenschaft eines Backups ist nicht das *Vorhandensein* einer Kopie, sondern die *Versionierung*. Wenn dein Sync versehentlich einen leeren Ordner überschreibt, hilft die Cloud-Spiegelung nichts — der leere Stand wird mitgespiegelt.

- Cloud-Anbieter mit Versionshistorie wählen (Nextcloud, Dropbox, OneDrive haben das).
- Bei externen Festplatten regelmäßig **Snapshots** anlegen (z. B. `borg`, `restic`, `Time Machine`), nicht nur einen rsync-Spiegel.

## Wiederherstellung üben

Einmal pro Jahr probehalber einen Notensatz aus dem Backup zurückspielen. Wenn das nicht klappt, ist der Backup-Prozess kaputt — nicht erst feststellen, wenn die Daten weg sind.

!!! tip "Klein anfangen"
    Wenn dir das alles zu viel ist: starte mit einem einzigen externen USB-Stick, der einmal im Monat den Stand kopiert und dann zu Hause im Schrank liegt. Besser ein einfaches Backup, das du wirklich machst, als ein elegantes, das du nie machst.
