#!/usr/bin/env bash

set -e

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/noten-tools"
BIN_DIR="$HOME/.local/bin"

echo -e "${BLUE}=== Noten-Tools Installer ===${NC}"

# 1. System-Abhängigkeiten checken
echo "Prüfe System-Abhängigkeiten..."
MISSING_PKGS=""
for cmd in fzf mutool qpdf gs tesseract; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_PKGS="$MISSING_PKGS $cmd"
    fi
done

if [ -n "$MISSING_PKGS" ]; then
    echo "⚠️ Warnung: Folgende System-Pakete fehlen eventuell:"
    echo -e "${GREEN}$MISSING_PKGS${NC}"
    echo "Stelle sicher, dass Tesseract (inkl. deu/eng) und Ghostscript installiert sind."
    read -p "Trotzdem fortfahren? (j/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# 2. Verzeichnisse anlegen und Dateien kopieren
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
cp -r src/* "$INSTALL_DIR/"

# 3. Python Venv erstellen
echo -e "\n${BLUE}Erstelle Python Virtual Environment...${NC}"
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
if [ -f "requirements.txt" ]; then
    "$INSTALL_DIR/.venv/bin/pip" install -r requirements.txt
else
    # Fallback falls keine requirements.txt da ist
    "$INSTALL_DIR/.venv/bin/pip" install PyMuPDF pytesseract opencv-python numpy Pillow
fi

# 4. Wrapper Skripte in ~/.local/bin erstellen
echo -e "\n${BLUE}Erstelle globale Befehle...${NC}"

create_wrapper() {
    local cmd_name=$1
    local script_name=$2
    local is_python=$3
    
    local wrapper_path="$BIN_DIR/$cmd_name"
    
    echo '#!/usr/bin/env bash' > "$wrapper_path"
    if [ "$is_python" = true ]; then
        echo "exec \"$INSTALL_DIR/.venv/bin/python\" \"$INSTALL_DIR/$script_name\" \"\$@\"" >> "$wrapper_path"
    else
        echo "exec \"$INSTALL_DIR/$script_name\" \"\$@\"" >> "$wrapper_path"
    fi
    chmod +x "$wrapper_path"
    chmod +x "$INSTALL_DIR/$script_name"
    echo " -> $cmd_name installiert"
}

# Python-Tools
create_wrapper "notenstempel" "notenstempel.py" true
create_wrapper "notenverarbeitung" "notenverarbeitung.py" true

# Shell-Tools
create_wrapper "unbooklet" "unbooklet.sh" false
create_wrapper "pdf-fix" "pdf-fix.sh" false
create_wrapper "stempel-finalisieren" "stempel-finalisieren.sh" false

echo -e "\n${GREEN}✅ Installation erfolgreich!${NC}"
echo "Du kannst die Tools nun global verwenden."
