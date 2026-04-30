# Entwicklung

Für alle, die am Code mithelfen, Tests laufen lassen oder die Dokumentation lokal bauen wollen.

<div class="grid cards" markdown>

-   :material-laptop: __[Setup & Tests](setup.md)__

    ---

    Editierbare venv, schnelles Re-Install via `pipx`, Test-Suite ausführen.

-   :material-book-edit-outline: __[Dokumentation](doku.md)__

    ---

    Diese Doku lokal bauen und live previewen.

-   :material-folder-text-outline: __[Repo-Struktur](repo.md)__

    ---

    Wo liegt was im Repo? Modul-Layout, geteilte Bibliothek, Assets.

</div>

## Beitragen

Issues und Pull Requests sind willkommen — speziell:

- **Bug-Reports** mit minimalem Reproduktionsbeispiel (Eingabe-PDF, Befehl, erwartetes vs. tatsächliches Verhalten).
- **Aliase-Vorschläge**: wenn `noten-tools-aliases sync` einen YAML-Patch ausgibt, der nicht im Repo ist, gerne als PR oder Issue mit dem YAML-Block einreichen — siehe [OCR-Aliase pflegen](../anwendung/aliase.md).
- **Distro-Support**: `install.sh` deckt Arch/CachyOS, Debian/Ubuntu, Fedora und macOS ab. Andere Distributionen sind möglich, brauchen aber Tests.
