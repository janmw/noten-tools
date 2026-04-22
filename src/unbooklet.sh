#!/usr/bin/env bash

# 1. Abhängigkeiten prüfen
for cmd in fzf mutool qpdf; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Fehler: '$cmd' ist nicht installiert."
        exit 1
    fi
done

# 2. PDF via fzf auswählen
PDF_FILE=$(find . -maxdepth 1 -iname "*.pdf" | fzf --prompt="📄 Wähle das gescannte Booklet: " --height=40% --layout=reverse)

if [[ -z "$PDF_FILE" ]]; then
    echo "Abbruch."
    exit 0
fi

BASENAME="${PDF_FILE%.*}"
OUTPUT_FILE="${BASENAME}_sortiert.pdf"
TMP_SPLIT=$(mktemp /tmp/pdf_split_XXXXXX.pdf)

echo "⚙️  Verarbeite: $PDF_FILE"

# 3. A3-Seiten exakt in der Mitte durchschneiden
echo "✂️  Halbiere A3-Seiten in A4..."
mutool poster -x 2 "$PDF_FILE" "$TMP_SPLIT"

# 4. Berechne die neue Seitenreihenfolge
echo "🧮 Berechne Booklet-Algorithmus..."
N=$(qpdf --show-npages "$TMP_SPLIT")

if (( N % 4 != 0 )); then
    echo "⚠️ Warnung: Die Seitenanzahl ($N) ist kein Vielfaches von 4."
fi

# Bash-kompatible Booklet-Mathematik
SEQ_STR=""
for (( i=1; i<=N/4; i++ )); do
    # Schema: Rückseite Rechts, Vorderseite Links, Vorderseite Rechts, Rückseite Links
    SEQ_STR+="$((N - 2*i + 2)),$((4*i - 3)),$((2*i - 1)),$((4*i - 2)),$((2*i)),$((4*i - 1)),$((N - 2*i + 1)),$((4*i)),"
done
SEQ_STR=${SEQ_STR%,} # Letztes Komma entfernen

# 5. Neusortierung und Erstellung des finalen PDFs
echo "🔄 Sortiere um und erstelle finales PDF..."
qpdf --empty --pages "$TMP_SPLIT" "$SEQ_STR" -- "$OUTPUT_FILE"

rm -f "$TMP_SPLIT"
echo -e "✅ Fertig! Gespeichert als: \e[1;32m$OUTPUT_FILE\e[0m"
