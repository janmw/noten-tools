"""PDF-Splitting nach erkannten Stimmen-Segmenten."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..shared.instruments import Identification


@dataclass
class Segment:
    page_indices: list[int] = field(default_factory=list)
    identification: Identification | None = None


def build_segments(headers: list, identifications: list[Identification | None]) -> list[Segment]:
    """Baut Segmente: jede neue Stimme (is_new_part_start) startet ein neues Segment.

    Folgeseiten ohne kompletten Header werden dem aktuellen Segment angehängt.
    """
    assert len(headers) == len(identifications)
    segments: list[Segment] = []
    current: Segment | None = None
    for idx, (hdr, ident) in enumerate(zip(headers, identifications)):
        is_start = bool(getattr(hdr, "is_new_part_start", False))
        if is_start or current is None:
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
