"""OCR-Header-Erkennung: Pro Seite Titel (mittig oben), Stimme (links oben), Komp. (rechts oben)."""

from __future__ import annotations

from dataclasses import dataclass

import pytesseract
from PIL import Image


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


def _aggregate_lines(rows: list[dict]) -> list[dict]:
    """Bündelt Wörter zu Zeilen (block, par, line)."""
    lines: dict[tuple[int, int, int], dict] = {}
    for r in rows:
        key = (r["block_num"], r["par_num"], r["line_num"])
        if key not in lines:
            lines[key] = {
                "text": r["text"],
                "conf_sum": r["conf"],
                "n": 1,
                "left": r["left"],
                "right": r["left"] + r["width"],
                "top": r["top"],
                "bottom": r["top"] + r["height"],
            }
        else:
            lines[key]["text"] += " " + r["text"]
            lines[key]["conf_sum"] += r["conf"]
            lines[key]["n"] += 1
            lines[key]["left"] = min(lines[key]["left"], r["left"])
            lines[key]["right"] = max(lines[key]["right"], r["left"] + r["width"])
            lines[key]["top"] = min(lines[key]["top"], r["top"])
            lines[key]["bottom"] = max(lines[key]["bottom"], r["top"] + r["height"])
    out = []
    for v in lines.values():
        v["avg_conf"] = v["conf_sum"] / max(v["n"], 1)
        out.append(v)
    return out


def read_header(image: Image.Image, lang: str = "deu+eng") -> HeaderRead:
    """Liest die obere Bandfläche und extrahiert Titel / Stimme / Komponist anhand der x-Position."""
    img_w, img_h = image.size
    rows = _ocr_region(image, lang=lang)
    lines = _aggregate_lines(rows)

    third = img_w / 3
    left_lines = [l for l in lines if l["right"] <= third * 1.05]
    right_lines = [l for l in lines if l["left"] >= 2 * third * 0.95]
    middle_lines = [l for l in lines if l not in left_lines and l not in right_lines]

    def biggest(lns):
        if not lns:
            return None
        return max(lns, key=lambda x: (x["bottom"] - x["top"]) * x["avg_conf"])

    voice = biggest(left_lines)
    composer = biggest(right_lines)
    title = biggest(middle_lines)

    voice_text = voice["text"] if voice else ""
    composer_text = composer["text"] if composer else ""
    title_text = title["text"] if title else ""

    voice_conf = voice["avg_conf"] if voice else 0.0
    composer_conf = composer["avg_conf"] if composer else 0.0
    title_conf = title["avg_conf"] if title else 0.0

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
