"""Integration-Test für noten-booklet split_halves: Mediabox stimmt nach dem Split."""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas

from notentools.booklet.__main__ import (
    noten_ordering,
    partitur_ordering,
    split_halves,
)


def _build_synthetic_a3_scan(path: Path, num_pages: int) -> None:
    w, h = landscape(A3)
    c = canvas.Canvas(str(path), pagesize=landscape(A3))
    for i in range(num_pages):
        c.setFontSize(120)
        c.drawCentredString(w * 0.25, h * 0.5, f"P{i}L")
        c.drawCentredString(w * 0.75, h * 0.5, f"P{i}R")
        c.showPage()
    c.save()


@pytest.fixture
def synthetic_a3_4pages(tmp_path):
    src = tmp_path / "scan.pdf"
    _build_synthetic_a3_scan(src, num_pages=4)
    return src


def test_split_halves_partitur_produces_correct_page_count(tmp_path, synthetic_a3_4pages):
    out = tmp_path / "out.pdf"
    split_halves(synthetic_a3_4pages, out, partitur_ordering(4))
    assert PdfReader(str(out)).pages
    assert len(PdfReader(str(out)).pages) == 8


def test_split_halves_each_output_page_is_half_width_a4_portrait(tmp_path, synthetic_a3_4pages):
    out = tmp_path / "out.pdf"
    split_halves(synthetic_a3_4pages, out, partitur_ordering(4))

    reader = PdfReader(str(out))
    src = PdfReader(str(synthetic_a3_4pages))
    src_w = float(src.pages[0].mediabox.width)
    src_h = float(src.pages[0].mediabox.height)

    for page in reader.pages:
        out_w = float(page.mediabox.width)
        out_h = float(page.mediabox.height)
        # Output-Höhe entspricht Input-Höhe (Hochkant gewordenes A4 aus A3-quer)
        assert out_h == pytest.approx(src_h)
        # Output-Breite ist genau die halbe Input-Breite
        assert out_w == pytest.approx(src_w / 2)
        # A4-Portrait-Verhältnis (≈ 1:√2)
        assert out_h > out_w


def test_split_halves_left_and_right_have_distinct_mediabox(tmp_path, synthetic_a3_4pages):
    out = tmp_path / "out.pdf"
    # 1 Sheet fortlaufend → output [(0,L), (0,R), (1,L), (1,R)]
    split_halves(synthetic_a3_4pages, out, noten_ordering(["C", "C"]))
    reader = PdfReader(str(out))

    page0_left = float(reader.pages[0].mediabox.left)
    page1_left = float(reader.pages[1].mediabox.left)
    # Linke und rechte Hälfte unterscheiden sich im linken Mediabox-Rand
    assert page0_left == pytest.approx(0.0)
    assert page1_left > page0_left


def test_noten_mode_consecutive_halves_alternate_sides(tmp_path, synthetic_a3_4pages):
    """Bei fortlaufendem Layout sollten Output-Seiten 1,2 von Input-Seite 0 kommen
    und 3,4 von Input-Seite 1 — sichtbar an wechselnden Mediabox-Linksrändern."""
    out = tmp_path / "out.pdf"
    split_halves(synthetic_a3_4pages, out, noten_ordering(["C"]))
    reader = PdfReader(str(out))
    lefts = [float(p.mediabox.left) for p in reader.pages]
    # Pattern für [C]: (0,L), (0,R), (1,L), (1,R) → lefts: 0, mid, 0, mid
    assert lefts[0] == pytest.approx(lefts[2])
    assert lefts[1] == pytest.approx(lefts[3])
    assert lefts[0] != pytest.approx(lefts[1])
