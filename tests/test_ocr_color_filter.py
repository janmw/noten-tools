"""Tests für den Farbstempel-Filter im OCR-Vorlauf.

Sicherstellt, dass farbige Archivstempel (rot, blau, …) vor der Texterkennung
auf Weiß gesetzt werden, während schwarze/graue Notentext-Pixel erhalten
bleiben.
"""

from __future__ import annotations

from PIL import Image

from notentools.verarbeitung.ocr import _filter_color_stamps


def _solid(color: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGB", (4, 4), color)


def _pixel(img: Image.Image, xy: tuple[int, int] = (0, 0)) -> tuple[int, int, int]:
    return img.getpixel(xy)  # type: ignore[return-value]


class TestFilterColorStamps:
    def test_red_stamp_becomes_white(self):
        out = _filter_color_stamps(_solid((220, 30, 30)))
        assert _pixel(out) == (255, 255, 255)

    def test_blue_stamp_becomes_white(self):
        out = _filter_color_stamps(_solid((30, 30, 220)))
        assert _pixel(out) == (255, 255, 255)

    def test_green_stamp_becomes_white(self):
        out = _filter_color_stamps(_solid((30, 200, 60)))
        assert _pixel(out) == (255, 255, 255)

    def test_purple_stamp_becomes_white(self):
        out = _filter_color_stamps(_solid((150, 30, 150)))
        assert _pixel(out) == (255, 255, 255)

    def test_black_text_is_kept(self):
        out = _filter_color_stamps(_solid((0, 0, 0)))
        assert _pixel(out) == (0, 0, 0)

    def test_dark_grey_text_is_kept(self):
        out = _filter_color_stamps(_solid((40, 40, 40)))
        assert _pixel(out) == (40, 40, 40)

    def test_light_grey_paper_is_kept(self):
        out = _filter_color_stamps(_solid((230, 230, 230)))
        assert _pixel(out) == (230, 230, 230)

    def test_near_neutral_warm_grey_is_kept(self):
        # Scanner-Artefakte sind oft minimal warm/kühl getönt; unter dem
        # Schwellwert dürfen sie nicht weggefiltert werden.
        out = _filter_color_stamps(_solid((130, 120, 115)))
        assert _pixel(out) == (130, 120, 115)

    def test_mixed_image_filters_only_colored_pixels(self):
        img = Image.new("RGB", (3, 1), (255, 255, 255))
        img.putpixel((0, 0), (0, 0, 0))         # Notentext
        img.putpixel((1, 0), (220, 30, 30))     # roter Stempel
        img.putpixel((2, 0), (30, 30, 220))     # blauer Stempel
        out = _filter_color_stamps(img)
        assert _pixel(out, (0, 0)) == (0, 0, 0)
        assert _pixel(out, (1, 0)) == (255, 255, 255)
        assert _pixel(out, (2, 0)) == (255, 255, 255)
