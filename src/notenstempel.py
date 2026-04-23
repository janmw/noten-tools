#!/usr/bin/env python3
import fitz  # PyMuPDF
import os
import sys
import subprocess
import argparse

# --- DYNAMISCHE KONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGO_DATEI = os.path.join(SCRIPT_DIR, "logo.png")
FONT_DATEI = os.path.join(SCRIPT_DIR, "00_stamp.ttf")

def stempel_datei(input_pfad, archiv_nr, shift_logo, shift_stamp, h_shift, ziel_breite, ziel_hoehe):
    doc = fitz.open(input_pfad)
    output_pfad = input_pfad.replace(".pdf", "_gestempelt.pdf")
    new_doc = fitz.open()

    for i in range(len(doc)):
        src_page = doc[i]
        page = new_doc.new_page(width=ziel_breite, height=ziel_hoehe)
        
        # Skalieren auf Zielformat
        ratio = min(ziel_breite / src_page.rect.width, ziel_hoehe / src_page.rect.height)
        rect = fitz.Rect(0, 0, src_page.rect.width * ratio, src_page.rect.height * ratio)
        rect.x1 = (ziel_breite + rect.width) / 2
        rect.x0 = rect.x1 - rect.width 
        page.show_pdf_page(rect, doc, i)

        # Nur auf der ersten Seite stempeln
        if i == 0:
            fnt = "courier"
            if os.path.exists(FONT_DATEI):
                page.insert_font(fontname="jb", fontfile=FONT_DATEI)
                fnt = "jb"
            
            # Archiv-Nummer stempeln
            page.insert_text(
                fitz.Point(ziel_breite - 120, 40 + shift_stamp), 
                f"Nr. {archiv_nr}", 
                color=(1,0,0), fontsize=24, fontname=fnt
            )
            
            # Logo stempeln mit horizontalem Shift
            if os.path.exists(LOGO_DATEI):
                page.insert_image(
                    fitz.Rect(20 + h_shift, 0 + shift_logo, 100 + h_shift, 60 + shift_logo), 
                    filename=LOGO_DATEI
                )

    new_doc.save(output_pfad)
    print(f"   -> Erstellt: {os.path.basename(output_pfad)}")

def main():
    parser = argparse.ArgumentParser(description="PDFs formatieren und stempeln.")
    parser.add_argument("--logo-runter", type=float, default=0)
    parser.add_argument("--stempel-runter", type=float, default=0)
    parser.add_argument("--logo-rechts", type=float, default=0)
    parser.add_argument("--logo-links", type=float, default=0)
    parser.add_argument("--a5", action="store_true", help="Auf A5 statt A4 skalieren")
    parser.add_argument("--quer", action="store_true", help="Querformat (Landscape) nutzen")
    args = parser.parse_args()

    h_shift = args.logo_rechts - args.logo_links

    # Format-Berechnung
    ziel_breite = 420.94 if args.a5 else 595.28
    ziel_hoehe = 595.28 if args.a5 else 841.89

    if args.quer:
        ziel_breite, ziel_hoehe = ziel_hoehe, ziel_breite

    print("=== Notenstempler ===")
    
    # Auswahl-Modus abfragen
    print("[1] Alle PDF-Dateien im Ordner verarbeiten")
    print("[2] Dateien manuell mit fzf auswählen")
    wahl = input("Wahl (1/2): ")

    dateien = []
    if wahl == "1":
        dateien = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    else:
        try:
            ps = subprocess.Popen(['find', '.', '-maxdepth', '1', '-type', 'f', '-iname', '*.pdf'], stdout=subprocess.PIPE)
            result = subprocess.run(
                ['fzf', '-m', '--prompt', 'Dateien wählen (TAB): '], 
                stdin=ps.stdout, 
                stdout=subprocess.PIPE, 
                text=True
            )
            
            if result.stdout.strip():
                dateien = result.stdout.strip().split('\n')
            else:
                dateien = []
        except FileNotFoundError:
            print("Fehler: fzf nicht gefunden."); sys.exit(1)

    if not dateien or (len(dateien) == 1 and dateien[0] == ''):
        print("Abbruch: Keine Dateien gewählt."); sys.exit(0)

    archiv_nr = input("Archiv-Nr: ")
    
    print(f"\nVerarbeite {len(dateien)} Dateien...")
    for f in dateien:
        if f.startswith("./"): f = f[2:]
        stempel_datei(f, archiv_nr, args.logo_runter, args.stempel_runter, h_shift, ziel_breite, ziel_hoehe)

    print("\nFertig!")

if __name__ == "__main__":
    main()
