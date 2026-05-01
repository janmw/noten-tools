"""PDF-Splitting nach erkannten Stimmen-Segmenten."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..shared.instruments import Identification, InstrumentMapper
from .ocr import HeaderRead


@dataclass
class Segment:
    page_indices: list[int] = field(default_factory=list)
    identification: Identification | None = None


def try_identify_header(
    mapper: InstrumentMapper, hdr: HeaderRead
) -> tuple[Identification | None, float]:
    """Versucht die Stimme aus dem Header zu erkennen.

    Probiert nacheinander Stimmen-, Titel-, Komponisten-Block — der erste, der
    auf ein bekanntes Instrument resolvet, gewinnt. Damit werden auch Layouts
    erkannt, in denen das Instrument oben mittig (statt links) steht.

    Liefert (Identification | None, source_confidence). source_confidence ist
    die OCR-Confidence des Blocks, aus dem identifiziert wurde.
    """
    for text, conf in (
        (hdr.voice_text, hdr.voice_conf),
        (hdr.title_text, hdr.title_conf),
        (hdr.composer_text, hdr.composer_conf),
    ):
        if not text:
            continue
        ident = mapper.identify(text)
        if ident is not None:
            return ident, conf
    return None, 0.0


def dedup_consecutive_same_part(
    is_new_flags: list[bool],
    candidate_idents: list[Identification | None],
) -> list[Identification | None]:
    """Strikte Dedup-Regel: eine Seite startet nur dann ein neues Segment, wenn
    ihre Identifikation sich von der direkt vorhergehenden Header-Seite
    unterscheidet.

    Zwei aufeinanderfolgende Header-Seiten mit gleicher Identifikation
    (gleiches (code, instrument, nummer)) werden zur Fortsetzung der vorigen
    Stimme zusammengeführt — typisch für Layouts, in denen jede Seite einer
    mehrseitigen Stimme einen vollständigen Kopf trägt.

    Header-Seiten, deren Vorgänger keine Header-Seite war (`is_new_flags[i-1]`
    war False), starten immer ein neues Segment — auch bei gleichem Instrument.
    Damit bleiben zwei separate Drucke desselben Instruments getrennt.
    """
    assert len(is_new_flags) == len(candidate_idents)
    out: list[Identification | None] = []
    prev_was_new = False
    prev_ident: Identification | None = None
    for is_new, ident in zip(is_new_flags, candidate_idents):
        if not is_new:
            out.append(None)
            prev_was_new = False
            prev_ident = None
            continue
        if (
            ident is not None
            and prev_was_new
            and prev_ident is not None
            and ident.same_part(prev_ident)
        ):
            out.append(None)
            # prev_was_new und prev_ident bleiben — die Kette setzt sich fort
            continue
        out.append(ident)
        prev_was_new = True
        prev_ident = ident
    return out


def build_segments(identifications: list[Identification | None]) -> list[Segment]:
    """Baut Segmente aus einer Liste von Identifikationen pro Seite.

    Eine Seite mit Identification startet ein neues Segment. Eine Seite mit
    None ist Fortsetzung des vorhergehenden Segments. Hat das erste Element
    None, wird ein "Reste"-Segment ohne Identifikation eröffnet.
    """
    segments: list[Segment] = []
    current: Segment | None = None
    for idx, ident in enumerate(identifications):
        if ident is not None or current is None:
            current = Segment(page_indices=[idx], identification=ident)
            segments.append(current)
        else:
            current.page_indices.append(idx)
    return segments


def sanitize_filename(name: str) -> str:
    bad = '/\\:*?"<>|'
    out = "".join("_" if c in bad else c for c in name)
    out = " ".join(out.split())
    return out.strip()


def build_filename(archivnummer: str, titel: str, ident: Identification) -> str:
    base = f"{archivnummer} - {titel} - {ident.filename_part()}"
    return sanitize_filename(base) + ".pdf"


def build_folder_name(archivnummer: str, titel: str) -> str:
    return sanitize_filename(f"{archivnummer} - {titel}")
