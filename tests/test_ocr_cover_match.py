"""Tests für die Cover-Erkennungs-Heuristik in ocr.py.

Datenpunkte stammen aus dem realen Verbose-Lauf von 'Rock Classics of the
Seventies' — Cover- und Folgeseiten getestet gegen ihre tatsächlichen
OCR-Title-Strings (samt Verstümmelung).
"""

from __future__ import annotations

import pytest

from notentools.verarbeitung.ocr import (
    has_arranged_marker,
    title_matches_piece,
)


PIECE = "Rock Classics of the Seventies"


class TestTitleMatchesPiece:
    @pytest.mark.parametrize(
        "ocr_title",
        [
            "ROCK CLASSICS OF THE SEVENTIES",
            "ROCK CLASSICS OF THE SEVEN",  # rechtsseitig abgeschnitten
            "ROCK CLASSICS OF THE SEVENTI",
            "ROCK CLASSICS OF THE SEVENTIE",
            "ROCK CLASSICS OF THE SEVENT",
            "CKC ASSICS OF THE SEVENTIES",  # links abgeschnitten + verstümmelt
            "SSICS OF THE SEVENTI",
            "ROCK QLASS_ICS OF THE SEVENTIES",  # OCR-Müllzeichen mittendrin
            "ROCK CLASSICS OF THE SEVENI",
        ],
    )
    def test_real_cover_variants_match(self, ocr_title):
        assert title_matches_piece(ocr_title, PIECE)

    @pytest.mark.parametrize(
        "ocr_title",
        [
            "FLUTE 1",
            "B CLARINET 1",
            "B' CLARINET 2",
            "B> CLARINET 3",
            "E) ALTO CLARINET",
            "E> ALTO SAXOPHONE 2",
            "B' TENOR SAXOPHONE",
            "B' TRUMPET 2",
            "F HORN 1",
            "F HORN 2",
            "TROMBONE 1",
            "TROMBONE 2",
            "BASSOON",
            "B> BASS CLARINET",
            "Moderate Folk Ballad",
            '"Dust In The Wind" Moderate Folk Ballad',
            "Somewhat Faster Rock Ballad",
            "Heavy Rock IZ' e ]",
            '"Smoke On The Water" / Heavy Rock IE_]',
            "L} . ---—-———- -—_-A (a z ( E Ea s",
            "Bb",
            "Eb",
            "7",
        ],
    )
    def test_continuation_pages_do_not_match(self, ocr_title):
        assert not title_matches_piece(ocr_title, PIECE)

    def test_empty_inputs(self):
        assert not title_matches_piece("", PIECE)
        assert not title_matches_piece("ROCK CLASSICS OF THE SEVENTIES", "")
        assert not title_matches_piece("", "")

    def test_piece_with_no_signal_tokens_returns_false(self):
        # Stücktitel ohne Token >=4 Buchstaben — keine Diskriminierung möglich.
        assert not title_matches_piece("anything", "Adagio in C")  # nur ein Token >=4

    def test_short_piece_title_strict(self):
        # 'Tequila' hat nur 1 Signal-Token; passt entweder ganz oder gar nicht.
        assert title_matches_piece("TEQUILA - Trumpet 1", "Tequila")
        assert not title_matches_piece("TRUMPET 1", "Tequila")


class TestHasArrangedMarker:
    def test_classic_arranged_by(self):
        assert has_arranged_marker("Arranged by TED RICKETTS")

    def test_lowercase(self):
        assert has_arranged_marker("arranged by foo bar")

    def test_in_title_block_dump(self):
        # Page 54 im Seventies-Lauf: alles in title kollabiert.
        title = (
            "PERCUSSION 2 Cowbell. Cabasa, Mark Tree, Shaker, Sus. Cym "
            "Arranged by TED RICKETTS \"Smoke On The Water\" Heavy Rock"
        )
        assert has_arranged_marker(title)

    def test_multiple_arguments_any_match(self):
        assert has_arranged_marker("", "", "Arranged by X")
        assert has_arranged_marker("Arranged by Y", "", "")

    def test_no_marker(self):
        assert not has_arranged_marker("FLUTE 1", '"Dust In The Wind"', "")
        assert not has_arranged_marker("")

    def test_word_boundary(self):
        # 'Range' o.ä. dürfen nicht triggern.
        assert not has_arranged_marker("Long range trumpet")
        # 'Arr.' (Abkürzung) triggert nicht — bewusst, um false positives in
        # Liedtexten zu vermeiden. Bei Bedarf kann das später erweitert werden.
        assert not has_arranged_marker("Arr. by someone")
