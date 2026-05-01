"""Tests für Segmentbildung, Dedup und Header-Identifikation."""

from __future__ import annotations

from notentools.shared.instruments import Identification, InstrumentMapper
from notentools.verarbeitung.ocr import HeaderRead
from notentools.verarbeitung.split import (
    build_segments,
    dedup_consecutive_same_part,
    try_identify_header,
)


def _ident(code: str, instrument: str, nummer: str = "", zusatz: str = "") -> Identification:
    return Identification(code=code, instrument=instrument, nummer=nummer, zusatz=zusatz)


class TestSamePart:
    def test_equal_full(self):
        a = _ident("06", "Trompete", "1", "in B")
        b = _ident("06", "Trompete", "1", "in B")
        assert a.same_part(b)

    def test_equal_ignores_zusatz(self):
        # Stimmung kann je nach OCR mal erkannt sein, mal nicht — same_part
        # vergleicht nur (code, instrument, nummer).
        a = _ident("06", "Trompete", "1", "in B")
        b = _ident("06", "Trompete", "1", "")
        assert a.same_part(b)

    def test_different_nummer(self):
        a = _ident("03", "Klarinette", "1")
        b = _ident("03", "Klarinette", "2")
        assert not a.same_part(b)

    def test_different_instrument(self):
        a = _ident("01", "Flöte")
        b = _ident("02", "Oboe")
        assert not a.same_part(b)

    def test_none(self):
        a = _ident("01", "Flöte")
        assert not a.same_part(None)


class TestDedupConsecutiveSamePart:
    def test_peculiar_layout_multipage_same_voice(self):
        """Jede Seite hat einen 'kompletten' Header, alle erkennen K1.
        Erwartung: nur Seite 1 startet ein Segment."""
        k1 = _ident("03", "Klarinette", "1")
        flags = [True, True, True, True]
        cands = [k1, k1, k1, k1]
        assert dedup_consecutive_same_part(flags, cands) == [k1, None, None, None]

    def test_peculiar_layout_voice_change(self):
        """Drei Seiten K1, dann zwei Seiten K2 — beides peculiar."""
        k1 = _ident("03", "Klarinette", "1")
        k2 = _ident("03", "Klarinette", "2")
        flags = [True, True, True, True, True]
        cands = [k1, k1, k1, k2, k2]
        assert dedup_consecutive_same_part(flags, cands) == [k1, None, None, k2, None]

    def test_normal_layout_two_copies_same_voice(self):
        """Normale Layouts: Header nur auf Seite 1 und Seite 3 (zwei Drucke von K1).
        Beide bleiben getrennt, weil Vorgängerseite (Seite 2) keine Header-Seite war."""
        k1 = _ident("03", "Klarinette", "1")
        flags = [True, False, True, False]
        cands = [k1, None, k1, None]
        assert dedup_consecutive_same_part(flags, cands) == [k1, None, k1, None]

    def test_normal_layout_voice_transition(self):
        k1 = _ident("03", "Klarinette", "1")
        k2 = _ident("03", "Klarinette", "2")
        flags = [True, False, True, False]
        cands = [k1, None, k2, None]
        assert dedup_consecutive_same_part(flags, cands) == [k1, None, k2, None]

    def test_unidentified_header_stays_new(self):
        """Header-Seite ohne Identifikation bleibt als neuer Stimmenkandidat
        (Aufrufer prompted dann)."""
        flags = [True, True]
        cands = [None, None]
        # Erste Seite startet neu (None bleibt None aber als Marker, dass Header da war).
        # Zweite Seite: prev_was_new=True, aber prev_ident=None -> kein Dedup.
        assert dedup_consecutive_same_part(flags, cands) == [None, None]

    def test_continuation_resets_dedup_chain(self):
        """K1, Folge ohne Header, dann wieder K1 — die Continuation reißt
        die Dedup-Kette ab, sodass das zweite K1 ein neues Segment startet."""
        k1 = _ident("03", "Klarinette", "1")
        flags = [True, True, False, True]
        cands = [k1, k1, None, k1]
        assert dedup_consecutive_same_part(flags, cands) == [k1, None, None, k1]


class TestBuildSegments:
    def test_simple_two_voices(self):
        k1 = _ident("03", "Klarinette", "1")
        k2 = _ident("03", "Klarinette", "2")
        segs = build_segments([k1, None, k2, None])
        assert len(segs) == 2
        assert segs[0].page_indices == [0, 1]
        assert segs[0].identification == k1
        assert segs[1].page_indices == [2, 3]
        assert segs[1].identification == k2

    def test_first_page_unidentified_starts_reste(self):
        k1 = _ident("03", "Klarinette", "1")
        segs = build_segments([None, None, k1, None])
        assert len(segs) == 2
        assert segs[0].identification is None
        assert segs[0].page_indices == [0, 1]
        assert segs[1].identification == k1
        assert segs[1].page_indices == [2, 3]

    def test_all_continuation(self):
        segs = build_segments([None, None, None])
        assert len(segs) == 1
        assert segs[0].identification is None
        assert segs[0].page_indices == [0, 1, 2]

    def test_two_separate_same_voice_segments(self):
        """build_segments respektiert die Eingabe — wenn zwei Segmente mit
        gleicher Identifikation kommen, bleiben sie getrennt."""
        k1a = _ident("03", "Klarinette", "1")
        k1b = _ident("03", "Klarinette", "1")
        segs = build_segments([k1a, None, k1b, None])
        assert len(segs) == 2
        assert segs[0].page_indices == [0, 1]
        assert segs[1].page_indices == [2, 3]


class TestTryIdentifyHeader:
    def test_picks_voice_when_present(self):
        mapper = InstrumentMapper()
        hdr = HeaderRead(
            page_index=0,
            voice_text="Klarinette 1",
            title_text="Marsch",
            composer_text="Mustermann",
            voice_conf=85.0,
            title_conf=70.0,
            composer_conf=60.0,
            is_new_part_start=True,
        )
        ident, conf = try_identify_header(mapper, hdr)
        assert ident is not None
        assert ident.code == "03"
        assert ident.instrument == "Klarinette"
        assert ident.nummer == "1"
        assert conf == 85.0  # voice-Block lieferte den Treffer

    def test_falls_back_to_title_when_voice_garbage(self):
        """Layout: Instrument oben mittig — voice_text ist Rauschen, title_text
        enthält das Instrument."""
        mapper = InstrumentMapper()
        hdr = HeaderRead(
            page_index=0,
            voice_text="p.",  # Rauschen
            title_text="Trompete 2 in B",
            composer_text="Op. 14",
            voice_conf=40.0,
            title_conf=88.0,
            composer_conf=50.0,
            is_new_part_start=True,
        )
        ident, conf = try_identify_header(mapper, hdr)
        assert ident is not None
        assert ident.code == "06"
        assert ident.instrument == "Trompete"
        assert ident.nummer == "2"
        assert conf == 88.0  # title-Block lieferte den Treffer

    def test_returns_none_when_nothing_matches(self):
        mapper = InstrumentMapper()
        hdr = HeaderRead(
            page_index=0,
            voice_text="xxx",
            title_text="yyy",
            composer_text="zzz",
            voice_conf=10.0,
            title_conf=10.0,
            composer_conf=10.0,
            is_new_part_start=True,
        )
        ident, conf = try_identify_header(mapper, hdr)
        assert ident is None
        assert conf == 0.0

    def test_skips_empty_blocks(self):
        mapper = InstrumentMapper()
        hdr = HeaderRead(
            page_index=0,
            voice_text="",
            title_text="",
            composer_text="Flöte",
            voice_conf=0.0,
            title_conf=0.0,
            composer_conf=72.0,
            is_new_part_start=True,
        )
        ident, conf = try_identify_header(mapper, hdr)
        assert ident is not None
        assert ident.instrument == "Flöte"
        assert conf == 72.0
