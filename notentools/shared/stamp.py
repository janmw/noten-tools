"""Stempel-Overlay: Logo links oben + Archivnummer rechts oben.

Wird über jede Seite einer PDF gelegt. Original-Inhalt bleibt unangetastet.
"""

from __future__ import annotations

import io
from pathlib import Path

import pikepdf
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .config import Config, StampPosition

MM_PER_PT = 72.0 / 25.4  # ≈ 2.835


def _mm_to_pt(mm: float) -> float:
    return mm * MM_PER_PT


_FONT_REGISTERED: dict[str, str] = {}


def _ensure_font(font_path: Path) -> str:
    key = str(font_path)
    if key in _FONT_REGISTERED:
        return _FONT_REGISTERED[key]
    font_name = f"NotenStamp_{abs(hash(key)) & 0xFFFF}"
    pdfmetrics.registerFont(TTFont(font_name, key))
    _FONT_REGISTERED[key] = font_name
    return font_name


def _build_overlay(
    page_width: float,
    page_height: float,
    archivnummer: str,
    logo_path: Path | None,
    font_path: Path,
    stamp: StampPosition,
    logo_offset_mm: tuple[float, float] = (0.0, 0.0),
    archiv_offset_mm: tuple[float, float] = (0.0, 0.0),
) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Logo (links oben)
    if logo_path is not None and logo_path.exists():
        logo_x = stamp.logo_left_pt + _mm_to_pt(logo_offset_mm[0])
        logo_top_offset_pt = stamp.logo_top_pt + _mm_to_pt(-logo_offset_mm[1])
        logo_y = page_height - logo_top_offset_pt - stamp.logo_height_pt
        try:
            c.drawImage(
                str(logo_path),
                logo_x,
                logo_y,
                width=stamp.logo_width_pt,
                height=stamp.logo_height_pt,
                mask="auto",
                preserveAspectRatio=False,
            )
        except Exception:
            pass

    # Archivnummer (rechts oben)
    text = f"Nr. {archivnummer}"
    font_name = _ensure_font(font_path)
    c.setFont(font_name, stamp.archiv_font_size_pt)
    c.setFillColor(black)
    archiv_right_pt = stamp.archiv_right_pt + _mm_to_pt(-archiv_offset_mm[0])
    archiv_top_pt = stamp.archiv_top_pt + _mm_to_pt(-archiv_offset_mm[1])
    text_x = page_width - archiv_right_pt
    text_y = page_height - archiv_top_pt - stamp.archiv_font_size_pt
    c.drawString(text_x, text_y, text)

    c.showPage()
    c.save()
    return buffer.getvalue()


def stamp_pdf(
    src: Path,
    dst: Path,
    archivnummer: str,
    config: Config,
    logo_offset_mm: tuple[float, float] = (0.0, 0.0),
    archiv_offset_mm: tuple[float, float] = (0.0, 0.0),
) -> None:
    """Legt einen Stempel über jede Seite von src und schreibt nach dst."""
    logo_path = Path(config.logo_path) if config.logo_path else None
    font_path = Path(config.font_path)

    src_pdf = pikepdf.open(str(src))
    out = pikepdf.Pdf.new()
    for page in src_pdf.pages:
        # Seitengröße
        mediabox = page.mediabox
        page_w = float(mediabox[2]) - float(mediabox[0])
        page_h = float(mediabox[3]) - float(mediabox[1])

        overlay_bytes = _build_overlay(
            page_w,
            page_h,
            archivnummer,
            logo_path,
            font_path,
            config.stamp,
            logo_offset_mm,
            archiv_offset_mm,
        )
        overlay_pdf = pikepdf.open(io.BytesIO(overlay_bytes))
        # Inhalt der Originalseite + Overlay zusammenführen
        new_page = out.copy_foreign(page)
        out.pages.append(new_page)
        out.pages[-1].add_overlay(overlay_pdf.pages[0])

    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(dst))
    src_pdf.close()
