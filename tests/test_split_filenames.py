"""Tests für Dateinamen-Bauen und Sanitizing."""

from __future__ import annotations

from notentools.shared.instruments import Identification
from notentools.verarbeitung.split import (
    build_filename,
    build_folder_name,
    sanitize_filename,
)


class TestSanitizeFilename:
    def test_replaces_filesystem_unsafe_chars(self):
        assert sanitize_filename("a/b\\c:d*e?f\"g<h>i|j") == "a_b_c_d_e_f_g_h_i_j"

    def test_collapses_whitespace(self):
        assert sanitize_filename("  hello   world  ") == "hello world"

    def test_keeps_umlauts(self):
        assert sanitize_filename("Flöte für Hörner") == "Flöte für Hörner"

    def test_keeps_punctuation(self):
        assert sanitize_filename("1234 - Titel - 03 Klarinette") == "1234 - Titel - 03 Klarinette"


class TestBuildFilename:
    def test_basic(self):
        ident = Identification(code="06", instrument="Trompete", nummer="1", zusatz="")
        assert build_filename("1234", "Test", ident) == "1234 - Test - 06 Trompete 1.pdf"

    def test_with_zusatz(self):
        ident = Identification(code="06", instrument="Trompete", nummer="2", zusatz="in C")
        assert build_filename("1234", "Test", ident) == "1234 - Test - 06 Trompete 2 in C.pdf"

    def test_without_nummer(self):
        ident = Identification(code="01", instrument="Flöte")
        assert build_filename("0042", "Marsch", ident) == "0042 - Marsch - 01 Flöte.pdf"

    def test_with_unsafe_titel(self):
        ident = Identification(code="01", instrument="Flöte")
        # Slashes im Titel werden zu Unterstrichen
        assert build_filename("1234", "A/B*C", ident) == "1234 - A_B_C - 01 Flöte.pdf"

    def test_with_horn_prefix_pitch(self):
        ident = Identification(code="05", instrument="F-Horn", nummer="1", zusatz="")
        assert build_filename("0042", "Test", ident) == "0042 - Test - 05 F-Horn 1.pdf"


class TestBuildFolderName:
    def test_basic(self):
        assert build_folder_name("1234", "Test Titel") == "1234 - Test Titel"

    def test_strips_unsafe(self):
        assert build_folder_name("1234", "Schloss/Strauss") == "1234 - Schloss_Strauss"
