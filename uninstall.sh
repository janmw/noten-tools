#!/usr/bin/env bash

set -e

# Farben für Output
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/share/noten-tools"
BIN_DIR="$HOME/.local/bin"
COMMANDS=("notenstempel" "notenverarbeitung" "entstempeln" "unbooklet" "pdf-fix" "stempel-finalisieren")

echo -e "${BLUE}=== Noten-Tools Uninstaller ===${NC}"
echo "Alle installierten Befehle und die Python-Umgebung werden gelöscht."
read -p "Möchtest du wirklich fortfahren? (j/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    echo "Abbruch."
    exit 0
fi

# 1. Wrapper-Skripte entfernen
echo -e "\n${BLUE}Entferne globale Befehle...${NC}"
for cmd in "${COMMANDS[@]}"; do
    if [ -f "$BIN_DIR/$cmd" ]; then
        rm "$BIN_DIR/$cmd"
        echo " -> $cmd entfernt"
    fi
done

# 2. Installationsverzeichnis entfernen
echo -e "\n${BLUE}Entferne Programmdateien...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo " -> $INSTALL_DIR gelöscht"
fi

echo -e "\n${RED}✅ Deinstallation abgeschlossen!${NC}"
