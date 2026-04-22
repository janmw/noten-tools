#!/usr/bin/env bash

# Sucht alle PDFs im aktuellen Ordner und öffnet fzf mit Mehrfachauswahl (-m)
auswahl=$(find . -maxdepth 1 -type f -iname '*.pdf' | fzf -m --prompt="PDFs fixen (TAB für Mehrfachauswahl, ENTER zum Starten): ")

# Bricht ab, wenn nichts ausgewählt wurde
if [ -z "$auswahl" ]; then
    echo "Abbruch: Keine Datei ausgewählt."
    exit 0
fi

# Schleife: Geht jede ausgewählte Datei einzeln durch
echo "$auswahl" | while read -r datei; do
    echo "Verarbeite '$datei'..."
    
    # Ghostscript repariert die Datei über eine temporäre Datei
    gs -q -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dAutoRotatePages=/None -sOutputFile="temp_fix.pdf" "$datei"
    
    # Überschreibt das Original sicher
    mv "temp_fix.pdf" "$datei"
done

echo "Fertig! Alle PDFs wurden gefixt."
