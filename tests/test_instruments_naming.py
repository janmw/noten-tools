"""Tests für die Naming-Konventionen aus _post_process und needs_pitch.

Deckt die Stadtkapelle-Regeln ab:
  - Klarinette in B → Default, in Es → "Es-Klarinette"
  - Posaune in C → Default, in B → "B-Posaune"
  - Horn → "F-Horn", "Es-Horn" verschmolzen
  - Bariton/Euphonium → " TC" (in B) / " BC" (in C)
  - Saxophone (04) und Schlagwerk (10) → keine Stimmung
  - Flöte/Piccolo, Oboe/Fagott, Tuba/Kontrabass → in C Default
  - Trompete/Flügelhorn/Kornett, Tenorhorn → in B Default
"""

from __future__ import annotations

import pytest

from notentools.shared.instruments import Identification, InstrumentMapper


@pytest.fixture(scope="module")
def mapper():
    return InstrumentMapper()


# ---------------------------------------------------------------------------
# _post_process: Stimmung wird nicht ausgegeben, wenn Standard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code,name,zusatz", [
    ("01", "Flöte", "in C"),
    ("01", "Piccolo", "in C"),
    ("02", "Oboe", "in C"),
    ("02", "Fagott", "in C"),
    ("03", "Klarinette", "in B"),
    ("03", "Bassklarinette", "in B"),
    ("06", "Trompete", "in B"),
    ("06", "Flügelhorn", "in B"),
    ("06", "Kornett", "in B"),
    ("07", "Tenorhorn", "in B"),
    ("08", "Posaune", "in C"),
    ("09", "Tuba", "in C"),
    ("09", "Kontrabass", "in C"),
])
def test_default_pitch_is_dropped(mapper, code, name, zusatz):
    ident = Identification(code=code, instrument=name, zusatz=zusatz)
    out = mapper._post_process(ident)
    assert out.zusatz == "", f"{name} {zusatz} sollte ohne Stimmung im Namen bleiben"
    assert out.instrument == name


# ---------------------------------------------------------------------------
# Sonderfälle mit eingebauter Stimmung
# ---------------------------------------------------------------------------


def test_klarinette_in_es_becomes_es_klarinette(mapper):
    ident = Identification(code="03", instrument="Klarinette", zusatz="in Es")
    out = mapper._post_process(ident)
    assert out.instrument == "Es-Klarinette"
    assert out.zusatz == ""


def test_klarinette_in_a_keeps_zusatz(mapper):
    ident = Identification(code="03", instrument="Klarinette", zusatz="in A")
    out = mapper._post_process(ident)
    assert out.instrument == "Klarinette"
    assert out.zusatz == "in A"


def test_posaune_in_b_becomes_b_posaune(mapper):
    ident = Identification(code="08", instrument="Posaune", zusatz="in B")
    out = mapper._post_process(ident)
    assert out.instrument == "B-Posaune"
    assert out.zusatz == ""


def test_horn_with_pitch_merges_to_prefix(mapper):
    ident = Identification(code="05", instrument="Horn", zusatz="in F")
    out = mapper._post_process(ident)
    assert out.instrument == "F-Horn"
    assert out.zusatz == ""


def test_horn_in_es_merges_to_es_horn(mapper):
    ident = Identification(code="05", instrument="Horn", zusatz="in Es")
    out = mapper._post_process(ident)
    assert out.instrument == "Es-Horn"
    assert out.zusatz == ""


def test_horn_without_pitch_stays_unsure(mapper):
    ident = Identification(code="05", instrument="Horn", zusatz="")
    out = mapper._post_process(ident)
    assert out.instrument == "Horn"
    assert out.needs_pitch() is True


def test_bariton_in_b_becomes_tc(mapper):
    ident = Identification(code="07", instrument="Bariton", zusatz="in B")
    out = mapper._post_process(ident)
    assert out.instrument == "Bariton TC"
    assert out.zusatz == ""


def test_bariton_in_c_becomes_bc(mapper):
    ident = Identification(code="07", instrument="Bariton", zusatz="in C")
    out = mapper._post_process(ident)
    assert out.instrument == "Bariton BC"


def test_euphonium_in_b_becomes_tc(mapper):
    ident = Identification(code="07", instrument="Euphonium", zusatz="in B")
    out = mapper._post_process(ident)
    assert out.instrument == "Euphonium TC"


def test_bariton_without_pitch_needs_pitch(mapper):
    ident = Identification(code="07", instrument="Bariton", zusatz="")
    assert ident.needs_pitch() is True


# ---------------------------------------------------------------------------
# Saxophone und Schlagwerk: Stimmung wird immer entfernt
# ---------------------------------------------------------------------------


def test_saxophone_drops_pitch(mapper):
    ident = Identification(code="04", instrument="Altsaxophon", zusatz="in Es")
    out = mapper._post_process(ident)
    assert out.zusatz == ""


def test_schlagwerk_drops_pitch(mapper):
    ident = Identification(code="10", instrument="Drum Set", zusatz="in C")
    out = mapper._post_process(ident)
    assert out.zusatz == ""


# ---------------------------------------------------------------------------
# needs_pitch
# ---------------------------------------------------------------------------


class TestNeedsPitch:
    def test_horn_without_pitch_needs(self):
        assert Identification(code="05", instrument="Horn").needs_pitch() is True

    def test_horn_with_pitch_does_not_need(self):
        assert Identification(code="05", instrument="F-Horn").needs_pitch() is False

    def test_bariton_without_suffix_needs(self):
        assert Identification(code="07", instrument="Bariton").needs_pitch() is True

    def test_bariton_with_tc_does_not_need(self):
        assert Identification(code="07", instrument="Bariton TC").needs_pitch() is False

    def test_euphonium_without_suffix_needs(self):
        assert Identification(code="07", instrument="Euphonium").needs_pitch() is True

    def test_tenorhorn_does_not_need(self):
        # Tenorhorn ist Code 07 aber NICHT in der needs_pitch-Liste
        assert Identification(code="07", instrument="Tenorhorn").needs_pitch() is False

    def test_klarinette_does_not_need(self):
        assert Identification(code="03", instrument="Klarinette").needs_pitch() is False


# ---------------------------------------------------------------------------
# End-to-End: identify() für ein paar typische OCR-Eingaben
# ---------------------------------------------------------------------------


class TestIdentifyEndToEnd:
    def test_trumpet_with_pitch_drops_default(self, mapper):
        ident = mapper.identify("1st Trumpet in Bb")
        assert ident is not None
        assert ident.code == "06"
        assert ident.instrument == "Trompete"
        assert ident.nummer == "1"
        assert ident.zusatz == ""

    def test_klarinette_in_es_renames(self, mapper):
        ident = mapper.identify("Es-Klarinette")
        assert ident is not None
        assert ident.code == "03"
        assert ident.instrument == "Es-Klarinette"

    def test_horn_in_f_merges(self, mapper):
        ident = mapper.identify("Horn in F")
        assert ident is not None
        assert ident.code == "05"
        assert ident.instrument == "F-Horn"

    def test_floete_with_umlaut(self, mapper):
        ident = mapper.identify("Flöte")
        assert ident is not None
        assert ident.code == "01"

    def test_floete_without_umlaut_via_ocr(self, mapper):
        # OCR liest oft "Flote" statt "Flöte" — sollte trotzdem matchen
        ident = mapper.identify("Flote")
        assert ident is not None
        assert ident.code == "01"

    def test_unknown_returns_none(self, mapper):
        ident = mapper.identify("Xyzzy42")
        assert ident is None

    def test_partitur_score(self, mapper):
        ident = mapper.identify("Conductor's Score")
        assert ident is not None
        assert ident.code == "00"
