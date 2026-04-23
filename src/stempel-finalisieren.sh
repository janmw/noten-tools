#!/usr/bin/env bash

# Prüfen, ob überhaupt Dateien mit dem Suffix existieren
shopt -s nullglob
files=(*_gestempelt*)

if [ ${#files[@]} -eq 0 ]; then
    echo "Keine Dateien mit '_gestempelt' im aktuellen Ordner gefunden."
    exit 0
fi

echo "Finalisiere Namen für ${#files[@]} Dateien..."

for file in "${files[@]}"; do
    new_name="${file/_gestempelt/}"
    
    # mv -f überschreibt bestehende Dateien ohne Rückfrage
    mv -f "$file" "$new_name"
    echo "✅ $file -> $new_name"
done

echo "Fertig!"
