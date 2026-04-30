# Setup & Tests

## Editierbare Installation in einer venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
noten-verarbeitung --help
```

Code-Änderungen wirken sofort — kein Re-Install nötig.

## Schnelles Re-Install via pipx

Wenn du nicht mit der venv arbeiten willst, sondern dein lokal modifiziertes Paket direkt im System installieren:

```bash
pipx install --force .
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Oder direkt im pipx-venv:

```bash
$(pipx environment --value PIPX_HOME)/venvs/noten-tools/bin/python -m pip install pytest
$(pipx environment --value PIPX_HOME)/venvs/noten-tools/bin/python -m pytest
```

### Was abgedeckt ist

- `noten-booklet` — Reordering-Logik (`partitur_ordering`, `noten_ordering`) + Mediabox-Splitting
- `notentools.shared.instruments` — Naming-Konvention (`_post_process`), `needs_pitch()`, `identify()` end-to-end
- `notentools.verarbeitung.split` — `sanitize_filename`, `build_filename`, `build_folder_name`
- `noten-tools-aliases` — Identifier-Pattern für `sync`

OCR und interaktive Prompts sind bewusst nicht abgedeckt, weil sie nicht deterministisch testbar sind.
