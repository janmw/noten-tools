"""PDF-Operationen: Render zu Bildern, Split, Skalierung A4/A5-quer (fit-to-page)."""

from __future__ import annotations

import io
from pathlib import Path

import pikepdf
from pdf2image import convert_from_path
from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject


# DIN A4 Hochformat in Punkten (1 pt = 1/72 inch)
A4_PORTRAIT = (595.276, 841.890)  # 210 × 297 mm
# DIN A5 Querformat in Punkten
A5_LANDSCAPE = (595.276, 419.528)  # 210 × 148 mm


def target_size(a5: bool) -> tuple[float, float]:
    return A5_LANDSCAPE if a5 else A4_PORTRAIT


def render_pages_to_images(pdf_path: Path, dpi: int = 300) -> list[Image.Image]:
    """Rendert eine PDF zu PIL-Bildern. Eine Seite = ein Bild."""
    return convert_from_path(str(pdf_path), dpi=dpi)


def render_single_page_to_image(pdf_path: Path, page_index: int, dpi: int = 300) -> Image.Image:
    page_one_based = page_index + 1
    pages = convert_from_path(
        str(pdf_path),
        dpi=dpi,
        first_page=page_one_based,
        last_page=page_one_based,
    )
    if not pages:
        raise IndexError(f"Seite {page_index} in {pdf_path} nicht vorhanden")
    return pages[0]


def page_count(pdf_path: Path) -> int:
    with pikepdf.open(str(pdf_path)) as pdf:
        return len(pdf.pages)


def extract_pages_to_pdf(src: Path, page_indices: list[int], dst: Path) -> None:
    """Extrahiert die genannten Seiten (0-basiert) als neue PDF nach dst."""
    with pikepdf.open(str(src)) as source:
        out = pikepdf.Pdf.new()
        for idx in page_indices:
            out.pages.append(source.pages[idx])
        dst.parent.mkdir(parents=True, exist_ok=True)
        out.save(str(dst))


def scale_pdf_to_target(src: Path, dst: Path, a5: bool = False) -> None:
    """Skaliert jede Seite einer PDF auf das Zielformat (A4 oder A5-quer).

    Fit-to-page mit weißen Rändern: Seitenverhältnis wird beibehalten,
    der Inhalt wird zentriert, Restfläche bleibt weiß.
    """
    target_w, target_h = target_size(a5)
    reader = PdfReader(str(src))
    writer = PdfWriter()

    for page in reader.pages:
        media = page.mediabox
        src_w = float(media.width)
        src_h = float(media.height)
        if src_w <= 0 or src_h <= 0:
            continue
        scale = min(target_w / src_w, target_h / src_h)
        scaled_w = src_w * scale
        scaled_h = src_h * scale
        offset_x = (target_w - scaled_w) / 2
        offset_y = (target_h - scaled_h) / 2

        page.add_transformation(
            Transformation().scale(scale, scale).translate(offset_x, offset_y)
        )
        page.mediabox = RectangleObject((0, 0, target_w, target_h))
        page.cropbox = RectangleObject((0, 0, target_w, target_h))
        writer.add_page(page)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("wb") as fh:
        writer.write(fh)


def crop_top_band(image: Image.Image, fraction: float = 0.15) -> Image.Image:
    """Schneidet das obere `fraction`-Band des Bildes für die Header-OCR aus."""
    w, h = image.size
    band_h = int(h * fraction)
    return image.crop((0, 0, w, band_h))
