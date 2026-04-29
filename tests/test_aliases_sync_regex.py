"""Test für das Identifier-Parsing-Regex in noten-tools-aliases sync."""

from __future__ import annotations

import re

# Identische Pattern wie in notentools/aliases/__main__.py:cmd_sync
PATTERN = re.compile(r"^(\d{2})\s+(.+?)(?:\s+(\d+))?(?:\s+(in [A-Za-zäöüß]+))?$")


class TestIdentifierPattern:
    def test_simple_identifier(self):
        m = PATTERN.match("01 Flöte")
        assert m is not None
        assert m.group(1) == "01"
        assert m.group(2) == "Flöte"
        assert m.group(3) is None
        assert m.group(4) is None

    def test_with_nummer(self):
        m = PATTERN.match("06 Trompete 2")
        assert m is not None
        assert m.group(1) == "06"
        assert m.group(2) == "Trompete"
        assert m.group(3) == "2"
        assert m.group(4) is None

    def test_with_nummer_and_zusatz(self):
        m = PATTERN.match("06 Trompete 1 in B")
        assert m is not None
        assert m.group(1) == "06"
        assert m.group(2) == "Trompete"
        assert m.group(3) == "1"
        assert m.group(4) == "in B"

    def test_with_zusatz_only(self):
        m = PATTERN.match("03 Klarinette in Es")
        assert m is not None
        assert m.group(1) == "03"
        assert m.group(2) == "Klarinette"
        assert m.group(3) is None
        assert m.group(4) == "in Es"

    def test_compound_instrument_name(self):
        m = PATTERN.match("05 F-Horn 1")
        assert m is not None
        assert m.group(1) == "05"
        assert m.group(2) == "F-Horn"
        assert m.group(3) == "1"

    def test_with_umlaut_in_zusatz(self):
        m = PATTERN.match("01 Flöte in Cß")
        assert m is not None
        assert m.group(4) == "in Cß"

    def test_invalid_no_code(self):
        assert PATTERN.match("Flöte") is None

    def test_invalid_one_digit_code(self):
        assert PATTERN.match("1 Flöte") is None
