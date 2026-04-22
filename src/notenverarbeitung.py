#!/home/jan/.scripts/notenverarbeitung/.venv/bin/python
import fitz  # PyMuPDF
import pytesseract
import re
import os
import sys
import subprocess
import difflib
import cv2          # OpenCV für professionelle Bildbearbeitung
import numpy as np  # Numpy für OpenCV-Matrizen
from PIL import Image
import argparse     # Für die Terminal-Flags

# --- DYNAMISCHE KONFIGURATION FÜR DOTFILES ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGO_DATEI = os.path.join(SCRIPT_DIR, "logo.png")
FONT_DATEI = os.path.join(SCRIPT_DIR, "00_stamp.ttf")

A4_BREITE = 595.28
A4_HOEHE = 841.89

# ==============================================================================
# INSTRUMENTEN-MAPPING (GEORDNET NACH KATEGORIEN)
# ==============================================================================
INSTRUMENT_MAP = {
    # --- 01 FLÖTEN ---
    "flote": ("01", "Flöte"), "flute": ("01", "Flöte"), "piccolo": ("01", "Flöte"),

    # --- 02 OBOE / FAGOTT ---
    "oboe": ("02", "Oboe"),
    "fagott": ("02", "Fagott"), "bassoon": ("02", "Fagott"), "basson": ("02", "Fagott"),

    # --- 03 KLARINETTEN ---
    "bassklarinette": ("03", "Bassklarinette"), "bass klarinette": ("03", "Bassklarinette"), "bass-klarinette": ("03", "Bassklarinette"),
    "bass clarinet": ("03", "Bassklarinette"), "bass-clarinet": ("03", "Bassklarinette"), "bassclarinet": ("03", "Bassklarinette"),
    "klarinette": ("03", "Klarinette"), "clarinet": ("03", "Klarinette"),

    # --- 04 SAXOPHONE ---
    "altsaxophon": ("04", "Altsaxophon"), "alto saxophone": ("04", "Altsaxophon"), "alto sax": ("04", "Altsaxophon"), "altsax": ("04", "Altsaxophon"), "alto-saxophone": ("04", "Altsaxophon"), "alt-saxophon": ("04", "Altsaxophon"),
    "tenorsaxophon": ("04", "Tenorsaxophon"), "tenor saxophone": ("04", "Tenorsaxophon"), "tenor sax": ("04", "Tenorsaxophon"), "tenorsax": ("04", "Tenorsaxophon"), "tenor-saxophone": ("04", "Tenorsaxophon"), "tenor-saxophon": ("04", "Tenorsaxophon"),
    "baritonsaxophon": ("04", "Baritonsaxophon"), "baritone saxophone": ("04", "Baritonsaxophon"), "baritone sax": ("04", "Baritonsaxophon"), "baritonsax": ("04", "Baritonsaxophon"), "baritone-saxophone": ("04", "Baritonsaxophon"), "bariton-saxophon": ("04", "Baritonsaxophon"),
    "sopransaxophon": ("04", "Sopransaxophon"), "soprano saxophone": ("04", "Sopransaxophon"), "soprano sax": ("04", "Sopransaxophon"), "sopransax": ("04", "Sopransaxophon"), "soprano-saxophone": ("04", "Sopransaxophon"), "sopran-saxophon": ("04", "Sopransaxophon"),
    "saxophone": ("04", "Saxophon"), "saxophon": ("04", "Saxophon"), "sax": ("04", "Saxophon"),

    # --- 05 HÖRNER ---
    "horn": ("05", "Horn"),

    # --- 06 TROMPETEN / FLÜGELHÖRNER ---
    "trompete": ("06", "Trompete"), "trumpet": ("06", "Trompete"), "cornet": ("06", "Trompete"), "kornett": ("06", "Trompete"),
    "flugelhorn": ("06", "Flügelhorn"),

    # --- 07 TENORHORN / BARITON / EUPHONIUM ---
    "tenorhorn": ("07", "Tenorhorn"), "bariton": ("07", "Bariton"), "baritone": ("07", "Bariton"), "euphonium": ("07", "Euphonium"),

    # --- 08 POSAUNEN ---
    "posaune": ("08", "Posaune"), "trombone": ("08", "Posaune"),

    # --- 09 TUBEN / BÄSSE ---
    "kontrabass": ("14", "Kontrabass"), "double bass": ("14", "Kontrabass"),
    "tuba": ("09", "Tuba"),
    "bass": ("09", "Bass"), 

    # --- 10 SCHLAGWERK ---
    "schlagzeug": ("10", "Drumset"), "drums": ("10", "Drumset"), "drum set": ("10", "Drumset"), "drumset": ("10", "Drumset"),
    "pauke": ("10", "Pauken"), "timpani": ("10", "Pauken"),
    "percussion": ("10", "Percussion"), "glockenspiel": ("10", "Percussion"), "xylophon": ("10", "Percussion"), "marimba": ("10", "Percussion"), "mallet": ("10", "Percussion"), "mallets": ("10", "Percussion"), "vibraphon": ("10", "Percussion"), "vibraphone": ("10", "Percussion"),

    # --- 11-14 STREICHER ---
    "violine": ("11", "Violine"), "violin": ("11", "Violine"),
    "viola": ("12", "Viola"), "bratsche": ("12", "Viola"),
    "cello": ("13", "Cello"), "violoncello": ("13", "Cello"),
    
    # --- 15 TASTENINSTRUMENTE ---
    "klavier": ("15", "Klavier"), "piano": ("15", "Klavier")
}

def normalize_text(t):
    if not t: return ""
    t = t.lower()
    t = t.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
    return t

def fuzzy_match(search_words, text, cutoff=0.65):
    if not search_words or not text:
        return False
    text_words = text.split()
    for sw in search_words:
        if sw in text:
            return True
        if difflib.get_close_matches(sw, text_words, n=1, cutoff=cutoff):
            return True
    return False

def preprocess_for_ocr(pil_image):
    r_channel = pil_image.convert('RGB').split()[0]
    img_cv = np.array(r_channel)
    img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, binary_img = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return Image.fromarray(binary_img)

def erkenne_instrument(text_l, titel_woerter, full_header_text):
    kombi_text = text_l + " " + full_header_text
    text_lower = kombi_text.lower().replace('\n', ' ')
    full_header_lower = full_header_text.lower().replace('\n', ' ')
    
    for w in titel_woerter:
        if len(w) > 3:
            text_lower = re.sub(r'\b' + re.escape(w) + r'\b', '', text_lower)
            
    text_lower = re.sub(r'(doubles|doubling|dbl\.).*', '', text_lower, flags=re.DOTALL)

    text_lower = re.sub(r'\b([1-6])\s*(st|nd|rd|th)\b', r' \1 ', text_lower)
    text_lower = text_lower.replace("1.", " 1 ").replace("2.", " 2 ").replace("3.", " 3 ")
    text_lower = text_lower.replace("7", " 1 ")
    text_lower = re.sub(r'\bist\b', ' 1 ', text_lower) 

    stimmung = ""
    stimmung_match = re.search(r'\bin\s+(b|bb|c|es|eb|f|d|g|a)\b', text_lower)
    if stimmung_match:
        val = stimmung_match.group(1).capitalize()
        if val == "Eb": val = "Es"
        if val == "Bb": val = "B"
        stimmung = f" in {val}"

    gefunden = None
    nummer = ""
    num_pattern = r'([1-6]|i{1,3}|iv|v|vi|l{1,3}|il|li|ill|lli|lil|iil|lii)'

    for sw in sorted(INSTRUMENT_MAP.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(sw) + r'\b', text_lower):
            if sw in ["saxophon", "saxophone", "sax"]:
                if not any(x in text_lower for x in ["alto", "alt", "tenor", "bariton", "sopran", "baritone", "soprano"]):
                    return {"kategorie": "SAX_UNKLAR", "basis": "", "nummer": "", "stimmung": ""}

            gefunden = INSTRUMENT_MAP[sw]
            
            if stimmung == "":
                prefix_match = re.search(r'\b(b|bb|c|es|eb|f)\b[\-\s]*' + re.escape(sw) + r'\b', text_lower)
                if prefix_match:
                    val = prefix_match.group(1).capitalize()
                    if val == "Eb": val = "Es"
                    if val == "Bb": val = "B"
                    stimmung = f" in {val}"

            match_before = re.search(r'\b' + num_pattern + r'(?:\.)?\s*' + re.escape(sw) + r'\b', text_lower)
            match_after = re.search(r'\b' + re.escape(sw) + r'[\s\.\-]*' + num_pattern + r'\b', text_lower)
            match_attached = re.search(r'\b' + re.escape(sw) + num_pattern + r'\b', text_lower)

            raw_num = None
            if match_before: raw_num = match_before.group(1)
            elif match_after: raw_num = match_after.group(1)
            elif match_attached: raw_num = match_attached.group(1)
            
            if raw_num:
                NUM_MAP = {
                    "1": "1", "i": "1", "l": "1",
                    "2": "2", "ii": "2", "ll": "2", "il": "2", "li": "2",
                    "3": "3", "iii": "3", "lll": "3", "ill": "3", "lli": "3", "lil": "3", "iil": "3", "lii": "3",
                    "4": "4", "iv": "4", 
                    "5": "5", "v": "5", 
                    "6": "6", "vi": "6"
                }
                nummer = NUM_MAP.get(raw_num, "")
            break

    if not gefunden: return None
    
    basisname = gefunden[1]
    
    if basisname == "Violine" and "viola" in full_header_lower:
        nummer = "3"
        
    return {"kategorie": gefunden[0], "basis": basisname, "nummer": nummer, "stimmung": stimmung}

def main():
    parser = argparse.ArgumentParser(description="Noten-Verarbeitung")
    parser.add_argument("--logo-runter", type=float, default=0, help="Verschiebt das Logo um X Punkte nach unten (z.B. 50)")
    parser.add_argument("--stempel-runter", type=float, default=0, help="Verschiebt den Text-Stempel um X Punkte nach unten (z.B. 50)")
    
    args = parser.parse_args()
    shift_logo = args.logo_runter
    shift_stamp = args.stempel_runter

    print("=== Noten-Verarbeitung ===")
    
    print("Bitte wähle die zu verarbeitende PDF-Datei aus...")
                    try:
                        # Führt fzf über die Shell aus und fängt AUSSCHLIESSLICH das Ergebnis (stdout) ab, 
                        # damit fzf sein Menü ungestört im Terminal aufbauen kann.
                        fzf_cmd = 'find . -maxdepth 1 -type f -iname "*.pdf" | fzf'
                        result = subprocess.run(fzf_cmd, shell=True, stdout=subprocess.PIPE, text=True)
                        
                        selected_file = result.stdout.strip()
                                    
        if selected_file:
            if selected_file.startswith("./"):
                selected_file = selected_file[2:]
            pdf_datei = selected_file
            print(f"Ausgewählte Datei: {pdf_datei}\n")
        else:
            print("Abbruch: Keine Datei ausgewählt.")
            sys.exit(0)
            
    except FileNotFoundError:
        print("\nFehler: 'fzf' ist nicht installiert oder nicht gefunden.")
        sys.exit(1)

    if not os.path.exists(pdf_datei):
        print(f"Fehler: '{pdf_datei}' fehlt."); sys.exit(1)

    titel = input("Titel: ")
    komponist = input("Komponist (ein markantes Wort, z.B. Nachname): ")
    archiv_nr = input("Archiv-Nr: ")
    stempel_abfrage = input("Stempel & Logo? (j/n): ").lower()
    mit_stempel = (stempel_abfrage == 'j')

    ausgabe_ordner = f"{archiv_nr} - {titel}"
    os.makedirs(ausgabe_ordner, exist_ok=True)

    titel_woerter = [normalize_text(w) for w in titel.split() if len(w) > 3]
    komp_woerter = [normalize_text(w) for w in komponist.split() if len(w) > 2]

    print(f"Verarbeite '{pdf_datei}'...")
    pdf_dokument = fitz.open(pdf_datei)

    aktuelles_dict = None
    gesammelte_seiten = []
    
    alle_stimmen = []
    instrument_counters = {}
    SUPER_KLEBER = ["Klavier", "Percussion", "Drumset", "Pauken"]

    gesamt_seiten = len(pdf_dokument)

    for i in range(gesamt_seiten):
        print(f"Lese Seite {i+1}/{gesamt_seiten}...", end='\r')
        
        page = pdf_dokument[i]
        pix = page.get_pixmap(dpi=250, alpha=False)
        bild = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        w, h = bild.size

        crop_links = bild.crop((0, 0, w * 0.4, h * 0.2))
        crop_oben = bild.crop((0, 0, w, h * 0.25))

        img_links = preprocess_for_ocr(crop_links)
        img_oben = preprocess_for_ocr(crop_oben)

        text_l = pytesseract.image_to_string(img_links, lang='deu+eng', config='--psm 6')
        full_header = pytesseract.image_to_string(img_oben, lang='deu+eng', config='--psm 6')
        
        full_header_norm = normalize_text(full_header)

        hat_titel = fuzzy_match(titel_woerter, full_header_norm)
        hat_komp = fuzzy_match(komp_woerter, full_header_norm)
        
        ist_seite_eins = hat_komp or (hat_titel and hat_komp)

        original_titel_woerter = [w.lower() for w in titel.split() if len(w) > 3]
        res = erkenne_instrument(text_l, original_titel_woerter, full_header)

        neue_stimme_erkannt = False
        manuell_abfragen = False

        if res:
            if res["kategorie"] == "SAX_UNKLAR":
                neue_stimme_erkannt = True
                manuell_abfragen = True
            elif aktuelles_dict is None:
                neue_stimme_erkannt = True
            elif res["basis"] in SUPER_KLEBER and aktuelles_dict["basis"] == res["basis"]:
                neue_stimme_erkannt = False
            else:
                if ist_seite_eins:
                    neue_stimme_erkannt = True
                elif res["basis"] != aktuelles_dict["basis"]:
                    neue_stimme_erkannt = True
                elif res["nummer"] != "" and res["nummer"] != aktuelles_dict["nummer"]:
                    neue_stimme_erkannt = True
                elif res["stimmung"] != "" and res["stimmung"] != aktuelles_dict["stimmung"]:
                    neue_stimme_erkannt = True
        else:
            if ist_seite_eins or i == 0:
                neue_stimme_erkannt = True
                manuell_abfragen = True

        if neue_stimme_erkannt:
            if gesammelte_seiten:
                if aktuelles_dict is not None:
                    alle_stimmen.append({
                        "dict": aktuelles_dict.copy(),
                        "seiten": list(gesammelte_seiten)
                    })
                else:
                    alle_stimmen.append({
                        "dict": {"kategorie": "00", "basis": "Deckblatt", "nummer": "", "stimmung": ""},
                        "seiten": list(gesammelte_seiten)
                    })
                gesammelte_seiten = []

            if manuell_abfragen:
                print(f"\n[!] Seite {i+1}: Stimme unklar oder unvollständig.")
                bild.thumbnail((800, 800)); bild.save("tmp.png")
                proc = subprocess.Popen(["gwenview", "tmp.png"], stderr=subprocess.DEVNULL)
                eingabe = input("Stimme manuell (z.B. '04 Altsaxophon 1') [Enter für Deckblatt]: ")
                proc.terminate()
                
                if eingabe.strip() == "":
                    res_to_use = {"kategorie": "00", "basis": "Deckblatt", "nummer": "", "stimmung": ""}
                else:
                    dummy_res = erkenne_instrument(eingabe, [], eingabe)
                    if dummy_res and dummy_res["kategorie"] != "SAX_UNKLAR":
                        res_to_use = dummy_res
                    else:
                        match = re.match(r'^(\d{2})\s+(.*)$', eingabe.strip())
                        if match:
                            kat = match.group(1) 
                            basis = match.group(2)
                        else:
                            kat = "" 
                            basis = eingabe.strip()
                        res_to_use = {"kategorie": kat, "basis": basis, "nummer": "", "stimmung": ""}
            else:
                res_to_use = res.copy()

            basis = res_to_use["basis"]
            ocr_num = res_to_use["nummer"]

            if basis not in SUPER_KLEBER and basis != "SAX_UNKLAR" and basis != "" and basis != "Deckblatt":
                if basis not in instrument_counters:
                    instrument_counters[basis] = 0

                if ocr_num:
                    try:
                        num_val = int(ocr_num)
                        instrument_counters[basis] = max(instrument_counters[basis], num_val)
                    except ValueError:
                        pass
                else:
                    instrument_counters[basis] += 1
                    res_to_use["nummer"] = str(instrument_counters[basis])

            aktuelles_dict = res_to_use

        gesammelte_seiten.append((i, ist_seite_eins))

    if gesammelte_seiten:
        if aktuelles_dict is not None:
            alle_stimmen.append({
                "dict": aktuelles_dict.copy(),
                "seiten": list(gesammelte_seiten)
            })
        else:
            alle_stimmen.append({
                "dict": {"kategorie": "00", "basis": "Deckblatt", "nummer": "", "stimmung": ""},
                "seiten": list(gesammelte_seiten)
            })

    print("\n\nOptimiere Dateinamen...")
    for stimme in alle_stimmen:
        d = stimme["dict"]
        b = d["basis"]
        if b in instrument_counters and instrument_counters[b] == 1:
            d["nummer"] = ""

    print("Erstelle PDF-Dateien...\n")
    for stimme in alle_stimmen:
        d = stimme["dict"]
        seiten = stimme["seiten"]
        
        name = f"{d['basis']} {d['nummer']}".strip() if d['nummer'] else d['basis']
        aktuelles_instrument = f"{d['kategorie']} {name}{d['stimmung']}".strip()
        
        basis_dateiname = f"{archiv_nr} - {titel} - {aktuelles_instrument}"
        dateipfad = os.path.join(ausgabe_ordner, f"{basis_dateiname}.pdf")
        
        zaehler = 2
        while os.path.exists(dateipfad):
            dateipfad = os.path.join(ausgabe_ordner, f"{basis_dateiname} ({zaehler}).pdf")
            zaehler += 1
            
        finaler_dateiname = os.path.basename(dateipfad)
        neues_pdf = fitz.open()

        for idx, (s_idx, is_title) in enumerate(seiten):
            src_page = pdf_dokument[s_idx]
            neue_seite = neues_pdf.new_page(width=A4_BREITE, height=A4_HOEHE)

            ratio = min(A4_BREITE / src_page.rect.width, A4_HOEHE / src_page.rect.height)
            rect = fitz.Rect(0, 0, src_page.rect.width * ratio, src_page.rect.height * ratio)
            rect.x1 = (A4_BREITE + rect.width) / 2; rect.x0 = rect.x1 - rect.width 

            neue_seite.show_pdf_page(rect, pdf_dokument, s_idx)

            if mit_stempel and (idx == 0 or is_title):
                fnt = "courier"
                if os.path.exists(FONT_DATEI):
                    neue_seite.insert_font(fontname="jb", fontfile=FONT_DATEI); fnt="jb"
                
                neue_seite.insert_text(fitz.Point(A4_BREITE - 120, 40 + shift_stamp), f"Nr. {archiv_nr}", color=(1,0,0), fontsize=24, fontname=fnt)
                
                if os.path.exists(LOGO_DATEI):
                    neue_seite.insert_image(fitz.Rect(20, 0 + shift_logo, 100, 60 + shift_logo), filename=LOGO_DATEI)

        neues_pdf.save(dateipfad)
        print(f"-> Gespeichert: {finaler_dateiname}")

    if os.path.exists("tmp.png"): os.remove("tmp.png")
    print("\nFertig! Alle Stimmen wurden sauber getrennt und benannt.")

if __name__ == "__main__":
    main()
