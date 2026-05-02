"""OCR-Header-Erkennung: Pro Seite Titel (mittig oben), Stimme (links oben), Komp. (rechts oben)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from PIL import Image, ImageChops


@dataclass
class HeaderRead:
    page_index: int
    title_text: str = ""
    voice_text: str = ""
    composer_text: str = ""
    title_conf: float = 0.0
    voice_conf: float = 0.0
    composer_conf: float = 0.0
    is_new_part_start: bool = False  # alle drei erkannt -> neue Stimme

    def min_conf(self) -> float:
        return min(self.title_conf, self.voice_conf, self.composer_conf)


def _ocr_region(image: Image.Image, lang: str) -> list[dict]:
    import pytesseract  # deferred: pure-Bild-Helfer dieses Moduls sollen ohne Tesseract testbar bleiben
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    rows: list[dict] = []
    n = len(data["text"])
    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            conf = -1.0
        if conf < 0:
            continue
        rows.append({
            "text": text,
            "conf": conf,
            "left": int(data["left"][i]),
            "top": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "block_num": int(data["block_num"][i]),
            "par_num": int(data["par_num"][i]),
            "line_num": int(data["line_num"][i]),
        })
    return rows


def _aggregate_blocks(rows: list[dict]) -> list[dict]:
    """Bündelt Wörter zu Tesseract-Blöcken (block_num).

    Tesseracts Layout-Analyse legt für visuell getrennte Textbereiche eigene
    Blöcke an — für Notensätze typischerweise: Stimmen-Block oben links,
    Titel-Block oben mittig (groß), Komponisten-Block oben rechts. Wir nutzen
    diese Block-Trennung statt eigener Geometrie-Heuristik.
    """
    blocks: dict[int, dict] = {}
    for r in rows:
        key = r["block_num"]
        if key not in blocks:
            blocks[key] = {
                "text": r["text"],
                "conf_sum": r["conf"],
                "n": 1,
                "left": r["left"],
                "right": r["left"] + r["width"],
                "top": r["top"],
                "bottom": r["top"] + r["height"],
            }
        else:
            blocks[key]["text"] += " " + r["text"]
            blocks[key]["conf_sum"] += r["conf"]
            blocks[key]["n"] += 1
            blocks[key]["left"] = min(blocks[key]["left"], r["left"])
            blocks[key]["right"] = max(blocks[key]["right"], r["left"] + r["width"])
            blocks[key]["top"] = min(blocks[key]["top"], r["top"])
            blocks[key]["bottom"] = max(blocks[key]["bottom"], r["top"] + r["height"])
    out = []
    for v in blocks.values():
        v["avg_conf"] = v["conf_sum"] / max(v["n"], 1)
        v["center_x"] = (v["left"] + v["right"]) / 2
        v["height"] = v["bottom"] - v["top"]
        out.append(v)
    return out


def _normalize_for_match(s: str) -> str:
    """Großschrift, Buchstaben/Ziffern/Whitespace, Whitespace kollabiert."""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    return " ".join(s.split())


def _signal_tokens(s: str, min_len: int = 4) -> list[str]:
    """Tokens mit Mindestlänge — kurze Füllwörter wie 'OF'/'THE' fliegen raus."""
    return [t for t in _normalize_for_match(s).split() if len(t) >= min_len]


def title_matches_piece(ocr_title: str, piece_title: str) -> bool:
    """Token-basiertes Fuzzy-Matching: passt ocr_title plausibel zu piece_title?

    Cover-Seiten haben den Stücktitel groß und mittig — auch wenn das OCR
    Trümmer macht (verstümmelt, abgeschnitten), bleibt typischerweise genug
    übrig, um per Token-Überlappung wiedergefunden zu werden.

    Regel: mindestens 50 % der signifikanten Stücktitel-Tokens (>=4 Buchstaben)
    müssen im OCR-Titel als Substring oder Fuzzy-Match (SequenceMatcher
    Ratio > 0.7) vorkommen.
    """
    piece_tokens = _signal_tokens(piece_title)
    if not piece_tokens:
        return False
    ocr_tokens = _signal_tokens(ocr_title)
    if not ocr_tokens:
        return False
    matches = 0
    for pt in piece_tokens:
        for ot in ocr_tokens:
            if pt in ot or ot in pt:
                matches += 1
                break
            if SequenceMatcher(None, pt, ot).ratio() > 0.7:
                matches += 1
                break
    return matches / len(piece_tokens) >= 0.5


def has_arranged_marker(*texts: str) -> bool:
    """Ein 'Arranged by …'-Marker irgendwo im Header.

    Robuste Cover-Signatur in Druckausgaben — Folgeseiten tragen ihn nicht.
    Toleriert OCR-Verschmutzung (vor- und nachstehende Zeichen, Groß-/
    Kleinschreibung). Match nur als Wort-Anfang, damit 'Range' o.ä. nicht
    triggert.
    """
    for text in texts:
        if not text:
            continue
        norm = _normalize_for_match(text)
        if re.search(r"\bARRANGED\b", norm):
            return True
    return False


def _filter_color_stamps(image: Image.Image) -> Image.Image:
    """Setzt farbige Pixel auf Weiß. Schützt davor, dass farbige Archivstempel
    (rot, blau, …) als Stimmenbezeichnung gelesen werden — die Stimme selbst
    ist immer in Schwarz/Grau gedruckt, hat also keine Sättigung.

    Kriterium: max(R,G,B) − min(R,G,B) > Schwellwert. Schwarz und Grau erfüllen
    das nicht (alle Kanäle gleich) und bleiben erhalten.
    """
    img = image.convert("RGB")
    r, g, b = img.split()
    max_rgb = ImageChops.lighter(ImageChops.lighter(r, g), b)
    min_rgb = ImageChops.darker(ImageChops.darker(r, g), b)
    chroma = ImageChops.subtract(max_rgb, min_rgb)
    threshold = 30
    mask_color = chroma.point(lambda v: 255 if v > threshold else 0).convert("L")
    white = Image.new("RGB", img.size, (255, 255, 255))
    return Image.composite(white, img, mask_color)


def read_header(
    image: Image.Image,
    lang: str = "deu+eng",
    piece_title: str = "",
) -> HeaderRead:
    """Liest den oberen Bereich und extrahiert Titel / Stimme / Komponist anhand der Block-Position.

    Erwartetes Layout: Stimme oben links als eigener Textblock,
    Titel oben mittig (groß), Komponist/Arrangeur oben rechts.

    `piece_title` (z.B. 'Rock Classics of the Seventies') aktiviert die
    primäre Cover-Erkennung: jede Cover-Seite trägt diesen Stücktitel
    prominent oben mittig, Folgeseiten nicht. Per Token-Fuzzy-Match werden
    auch verstümmelte Varianten ('CKC ASSICS OF THE SEVENTIES') erkannt.
    Zusätzlich gilt 'Arranged by …' irgendwo im Header als Cover-Marker —
    fängt Layouts, in denen alle Header-Inhalte in einen Block kollabieren.

    Ohne `piece_title` greift der konservative Fallback: alle drei Blöcke
    nicht-leer.
    """
    image = _filter_color_stamps(image)
    img_w, img_h = image.size
    rows = _ocr_region(image, lang=lang)
    blocks = _aggregate_blocks(rows)

    third = img_w / 3
    # Block gehört nach links/rechts/mitte anhand seiner horizontalen Mitte
    left_blocks = [b for b in blocks if b["center_x"] < third]
    right_blocks = [b for b in blocks if b["center_x"] > 2 * third]
    middle_blocks = [b for b in blocks if third <= b["center_x"] <= 2 * third]

    # Stimme: oberster Block in der linken Spalte (Stimmenbezeichnung steht meist klein
    # über dem ersten System — sie ist NICHT der größte Text).
    voice = min(left_blocks, key=lambda b: b["top"]) if left_blocks else None
    # Komponist: oberster Block in der rechten Spalte
    composer = min(right_blocks, key=lambda b: b["top"]) if right_blocks else None
    # Titel: größter Block in der Mitte (Titel ist typischerweise der höchste Text)
    title = max(middle_blocks, key=lambda b: b["height"]) if middle_blocks else None

    voice_text = voice["text"] if voice else ""
    composer_text = composer["text"] if composer else ""
    title_text = title["text"] if title else ""

    voice_conf = voice["avg_conf"] if voice else 0.0
    composer_conf = composer["avg_conf"] if composer else 0.0
    title_conf = title["avg_conf"] if title else 0.0

    if piece_title:
        is_new = (
            title_matches_piece(title_text, piece_title)
            or has_arranged_marker(title_text, voice_text, composer_text)
        )
    else:
        is_new = bool(voice_text) and bool(composer_text) and bool(title_text)

    return HeaderRead(
        page_index=-1,
        title_text=title_text,
        voice_text=voice_text,
        composer_text=composer_text,
        title_conf=title_conf,
        voice_conf=voice_conf,
        composer_conf=composer_conf,
        is_new_part_start=is_new,
    )
