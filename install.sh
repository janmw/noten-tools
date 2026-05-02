#!/usr/bin/env bash
# noten-tools — Installation
#
# Erkennt die Distribution und installiert:
#   - System-Pakete: tesseract (+deu/eng), poppler-utils, fzf, xdg-utils,
#     ghostscript, imagemagick, pipx
#   - Python-Paket via pipx aus diesem Repo

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

color() { printf '\033[%sm%s\033[0m\n' "$1" "$2"; }
info()  { color '1;34' "==> $*"; }
ok()    { color '1;32' "✓ $*"; }
warn()  { color '1;33' "! $*"; }
fail()  { color '1;31' "✗ $*"; exit 1; }

detect_os() {
    case "$(uname -s)" in
        Darwin) echo "macos"; return ;;
    esac
    if [[ -r /etc/os-release ]]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        case "${ID:-}${ID_LIKE:-}" in
            *arch*|*cachyos*|*manjaro*) echo "arch"; return ;;
            *debian*|*ubuntu*)          echo "debian"; return ;;
            *fedora*|*rhel*|*centos*)   echo "fedora"; return ;;
        esac
    fi
    echo "unknown"
}

install_packages_arch() {
    info "Arch/CachyOS erkannt — installiere via pacman"
    sudo pacman -S --needed --noconfirm \
        tesseract tesseract-data-deu tesseract-data-eng \
        poppler fzf xdg-utils ghostscript imagemagick python-pipx
}

install_packages_debian() {
    info "Debian/Ubuntu erkannt — installiere via apt"
    sudo apt-get update
    sudo apt-get install -y \
        tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng \
        poppler-utils fzf xdg-utils ghostscript imagemagick pipx
}

install_packages_fedora() {
    info "Fedora erkannt — installiere via dnf"
    sudo dnf install -y \
        tesseract tesseract-langpack-deu tesseract-langpack-eng \
        poppler-utils fzf xdg-utils ghostscript ImageMagick pipx
}

install_packages_macos() {
    info "macOS erkannt — installiere via Homebrew"
    if ! command -v brew >/dev/null 2>&1; then
        fail "Homebrew nicht installiert (https://brew.sh)"
    fi
    brew install tesseract tesseract-lang poppler fzf ghostscript imagemagick pipx
}

main() {
    local os
    os="$(detect_os)"
    case "$os" in
        arch)    install_packages_arch ;;
        debian)  install_packages_debian ;;
        fedora)  install_packages_fedora ;;
        macos)   install_packages_macos ;;
        *) fail "Unbekannte Distribution. Bitte installiere die System-Abhängigkeiten manuell (siehe README)." ;;
    esac

    info "Stelle pipx-Pfad sicher"
    pipx ensurepath >/dev/null || true

    info "Installiere noten-tools (Python) via pipx"
    if pipx list 2>/dev/null | grep -q '^package noten-tools'; then
        pipx upgrade --force "$REPO_DIR" || pipx install --force "$REPO_DIR"
    else
        pipx install --force "$REPO_DIR"
    fi

    ok "Installation abgeschlossen."
    echo
    echo "Verfügbare Befehle:"
    echo "  noten-verarbeitung       — Notensatz in Stimmen splitten"
    echo "  noten-pdf-fix            — PDF reparieren / entschlüsseln / komprimieren / Auto-Rotate stoppen"
    echo "  noten-stempel            — Logo + Archivnummer auf erste Seite stempeln"
    echo "  noten-booklet            — A3-Booklet-Scans in A4-Reihenfolge auflösen"
    echo "  noten-ausgabe            — Ausgabe-Stempel '[Name] - [Datum]' unten mittig"
    echo "  noten-scantailor         — Scan-Tailor-Workflow: PDF → PNGs → (Scan Tailor) → PDF"
    echo "  noten-tools-aliases sync — Gelernte Aliase als Repo-Patch ausgeben"
    echo
    echo "Tipp: Falls die Befehle nicht gefunden werden, neue Shell öffnen oder"
    echo "      \$(pipx environment --value PIPX_BIN_DIR) zum PATH hinzufügen."
}

main "$@"
