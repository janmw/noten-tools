"""Tests für noten-ausgabe: parser, Datum-Default und stamp_footer-Smoke."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from notentools.ausgabe.__main__ import build_parser
from notentools.shared.config import Config
from notentools.shared.stamp import stamp_footer


class TestParser:
    def test_basic(self):
        ns = build_parser().parse_args(["a.pdf"])
        assert ns.files == [Path("a.pdf")]
        assert ns.name is None
        assert ns.datum is None

    def test_with_name_and_datum(self):
        ns = build_parser().parse_args(["a.pdf", "--name", "Max M.", "--datum", "29.04.2026"])
        assert ns.name == "Max M."
        assert ns.datum == "29.04.2026"

    def test_offset(self):
        ns = build_parser().parse_args(["a.pdf", "--offset", "1,2"])
        assert ns.offset == (1.0, 2.0)

    def test_invalid_offset(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args(["a.pdf", "--offset", "abc"])

    def test_backup_default_off(self):
        ns = build_parser().parse_args(["a.pdf"])
        assert ns.backup is False


class TestDateFormat:
    def test_german_format_matches_dd_mm_yyyy(self):
        # Sicherstellen, dass strftime("%d.%m.%Y") immer Punkt-getrennt ist
        s = date.today().strftime("%d.%m.%Y")
        assert re.match(r"^\d{2}\.\d{2}\.\d{4}$", s) is not None


@pytest.fixture
def synthetic_a4_pdf(tmp_path):
    src = tmp_path / "src.pdf"
    c = canvas.Canvas(str(src), pagesize=A4)
    for i in range(3):
        c.setFontSize(40)
        c.drawString(100, 500, f"Seite {i + 1}")
        c.showPage()
    c.save()
    return src


class TestStampFooterSmoke:
    def test_stamp_footer_keeps_page_count(self, synthetic_a4_pdf, tmp_path):
        out = tmp_path / "out.pdf"
        cfg = Config.load()
        stamp_footer(synthetic_a4_pdf, out, text="Max M. - 29.04.2026", config=cfg)
        assert len(PdfReader(str(out)).pages) == 3

    def test_stamp_footer_does_not_change_mediabox(self, synthetic_a4_pdf, tmp_path):
        out = tmp_path / "out.pdf"
        cfg = Config.load()
        stamp_footer(synthetic_a4_pdf, out, text="Max M. - 29.04.2026", config=cfg)
        src = PdfReader(str(synthetic_a4_pdf))
        dst = PdfReader(str(out))
        for s, d in zip(src.pages, dst.pages):
            assert float(s.mediabox.width) == pytest.approx(float(d.mediabox.width))
            assert float(s.mediabox.height) == pytest.approx(float(d.mediabox.height))

    def test_stamp_footer_increases_file_size(self, synthetic_a4_pdf, tmp_path):
        # Overlay sollte mind. ein paar Bytes hinzufügen
        out = tmp_path / "out.pdf"
        cfg = Config.load()
        stamp_footer(synthetic_a4_pdf, out, text="Max M. - 29.04.2026", config=cfg)
        assert out.stat().st_size > synthetic_a4_pdf.stat().st_size
