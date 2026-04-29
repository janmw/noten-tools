"""Tests für die Reordering-Logik in noten-booklet."""

from __future__ import annotations

import pytest

from notentools.booklet.__main__ import noten_ordering, partitur_ordering


class TestPartiturOrdering:
    def test_single_sheet_partitur(self):
        # 2 input pages = 1 sheet = 4 logical pages
        # Sheet 1 front: 4|1, back: 2|3
        # Output (logical 1..4): (0,R), (1,L), (1,R), (0,L)
        assert partitur_ordering(2) == [
            (0, "R"),
            (1, "L"),
            (1, "R"),
            (0, "L"),
        ]

    def test_two_sheet_partitur(self):
        # 4 input pages = 2 sheets = 8 logical pages
        # Sheet 1 front: 8|1, back: 2|7
        # Sheet 2 front: 6|3, back: 4|5
        assert partitur_ordering(4) == [
            (0, "R"),  # logical 1 = sheet 1 front right
            (1, "L"),  # logical 2 = sheet 1 back left
            (2, "R"),  # logical 3 = sheet 2 front right
            (3, "L"),  # logical 4 = sheet 2 back left
            (3, "R"),  # logical 5 = sheet 2 back right
            (2, "L"),  # logical 6 = sheet 2 front left
            (1, "R"),  # logical 7 = sheet 1 back right
            (0, "L"),  # logical 8 = sheet 1 front left
        ]

    def test_three_sheet_partitur_yields_12_pages(self):
        order = partitur_ordering(6)
        assert len(order) == 12
        # Alle 12 logischen Seiten kommen vor — aus 3 input pages × 2 halves × 2 sides = 12
        assert sorted(order) == sorted(
            [(p, h) for p in range(6) for h in ("L", "R")]
        )

    def test_odd_input_pages_raises(self):
        with pytest.raises(ValueError):
            partitur_ordering(3)


class TestNotenOrdering:
    def test_single_booklet_sheet(self):
        # 1 sheet, Booklet: front_R, back_L, back_R, front_L
        assert noten_ordering(["B"]) == [
            (0, "R"),
            (1, "L"),
            (1, "R"),
            (0, "L"),
        ]

    def test_single_continuous_sheet(self):
        # 1 sheet, fortlaufend: front_L, front_R, back_L, back_R
        assert noten_ordering(["C"]) == [
            (0, "L"),
            (0, "R"),
            (1, "L"),
            (1, "R"),
        ]

    def test_mixed_continuous_and_booklet(self):
        # Sheet 0: continuous (input pages 0+1)
        # Sheet 1: booklet    (input pages 2+3)
        assert noten_ordering(["C", "B"]) == [
            (0, "L"), (0, "R"), (1, "L"), (1, "R"),  # sheet 0 fortlaufend
            (2, "R"), (3, "L"), (3, "R"), (2, "L"),  # sheet 1 booklet
        ]

    def test_each_sheet_yields_four_pages(self):
        for n in range(1, 6):
            modes = ["B"] * n
            assert len(noten_ordering(modes)) == 4 * n

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            noten_ordering(["X"])

    def test_single_sheet_booklet_matches_partitur_single_sheet(self):
        # Ein Single-Sheet-Booklet im Noten-Modus muss die gleiche Reihenfolge
        # liefern wie Partitur mit einem Blatt.
        assert noten_ordering(["B"]) == partitur_ordering(2)
