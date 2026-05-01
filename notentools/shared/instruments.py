"""Instrumenten-Mapping: OCR-Text -> (Code, Normalname, Nummer, Zusatz).

Hybrid-Schema:
  Dateiname-Endung = "{code} {instrument}{ ' ' + nummer if nummer}{ ' ' + zusatz if zusatz}"

Beispiele:
  "1st Trumpet in Bb"  -> ("06", "Trompete", "1", "in B")
  "Flöte"              -> ("01", "Flöte", "", "")
  "Drum Set"           -> ("10", "Drum Set", "", "")    # keep_original_name
  "Conductor's Score"  -> ("00", "Partitur", "", "")
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, replace as _dc_replace
from pathlib import Path

import yaml

from .paths import instruments_yaml, learned_aliases_file


@dataclass(frozen=True)
class Identification:
    code: str
    instrument: str
    nummer: str = ""
    zusatz: str = ""
    confidence: float = 1.0
    source_text: str = ""

    def filename_part(self) -> str:
        parts = [self.code, self.instrument]
        if self.nummer:
            parts.append(self.nummer)
        if self.zusatz:
            parts.append(self.zusatz)
        return " ".join(parts)

    def needs_pitch(self) -> bool:
        """True wenn das Instrument ohne Stimmung unvollständig ist (Aufrufer
        sollte dann manuell nachfragen)."""
        if self.code == "05" and not self.instrument.lower().endswith("-horn"):
            return True
        if self.code == "07" and self.instrument in {"Bariton", "Euphonium"}:
            return True
        return False

    def same_part(self, other: "Identification | None") -> bool:
        """True wenn beide Identifikationen dieselbe Stimme bezeichnen
        (Code, Instrumentenname, Nummer)."""
        if other is None:
            return False
        return (self.code, self.instrument, self.nummer) == (other.code, other.instrument, other.nummer)


_NUM_WORDS = {
    "1st": "1", "2nd": "2", "3rd": "3", "4th": "4", "5th": "5",
    "first": "1", "second": "2", "third": "3", "fourth": "4", "fifth": "5",
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "1.": "1", "2.": "2", "3.": "3", "4.": "4", "5.": "5",
    "erste": "1", "zweite": "2", "dritte": "3", "vierte": "4", "fünfte": "5",
    "1": "1", "2": "2", "3": "3", "4": "4", "5": "5",
}

# Default-Stimmung pro (Code, Normalname): wenn die erkannte Stimmung dieser
# entspricht (oder fehlt), wird sie nicht in den Filenamen geschrieben.
_DEFAULT_PITCH: dict[tuple[str, str], str] = {
    ("01", "Flöte"): "C",
    ("01", "Piccolo"): "C",
    ("02", "Oboe"): "C",
    ("02", "Fagott"): "C",
    ("03", "Bassklarinette"): "B",
    ("06", "Trompete"): "B",
    ("06", "Flügelhorn"): "B",
    ("06", "Kornett"): "B",
    ("07", "Tenorhorn"): "B",
    ("09", "Tuba"): "C",
    ("09", "Kontrabass"): "C",
}


_KEY_NORMAL = {
    "bb": "in B", "b": "in B",
    "eb": "in Es", "es": "in Es",
    "f": "in F",
    "c": "in C",
    "a": "in A",
    "d": "in D",
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    # OCR liest Umlaute oft fehlerhaft — auf Basisbuchstaben falten,
    # damit "Flöte"/"Flote"/"Flo te" alle den gleichen Index-Schlüssel haben.
    text = (text.replace("ä", "a")
                .replace("ö", "o")
                .replace("ü", "u")
                .replace("ß", "ss"))
    return text


def _strip_punct(text: str) -> str:
    return re.sub(r"[^\w\s\.\-äöüß]", " ", text, flags=re.UNICODE)


class InstrumentMapper:
    def __init__(self):
        self._index: dict[str, tuple[str, str, bool]] = {}
        self._codes: dict[str, dict] = {}
        self._learned: dict[str, str] = {}
        self._load_repo()
        self._load_learned()

    def _load_repo(self):
        with instruments_yaml().open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        self._codes = data
        for code, instruments in data.items():
            for normalname, info in (instruments or {}).items():
                keep_original = bool(info.get("keep_original_name", False))
                aliases = info.get("aliases", []) or []
                for alias in aliases:
                    self._index[_normalize(alias)] = (code, normalname, keep_original)
                self._index[_normalize(normalname)] = (code, normalname, keep_original)

    def _load_learned(self):
        path = learned_aliases_file()
        if not path.exists():
            return
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        for raw_text, identifier in data.items():
            self._learned[_normalize(raw_text)] = identifier

    def known_codes(self) -> list[str]:
        return sorted(self._codes.keys())

    def known_instruments(self) -> list[tuple[str, str]]:
        result = []
        for code in sorted(self._codes.keys()):
            for normalname in (self._codes[code] or {}).keys():
                result.append((code, normalname))
        return result

    def identify(self, raw_text: str) -> Identification | None:
        text = _normalize(raw_text)
        if not text:
            return None
        if text in self._learned:
            return self._post_process(self._parse_learned(text, raw_text))

        nummer, zusatz, leftover = self._extract_nummer_und_zusatz(text)
        instrument_match = self._find_instrument(leftover)
        if instrument_match is None:
            instrument_match = self._fuzzy_find_instrument(leftover)
        if instrument_match is None:
            return None
        code, normalname, keep_original = instrument_match
        instrument_name = self._format_instrument_name(raw_text, normalname, keep_original)
        ident = Identification(
            code=code,
            instrument=instrument_name,
            nummer=nummer,
            zusatz=zusatz,
            source_text=raw_text,
        )
        return self._post_process(ident)

    def _fuzzy_find_instrument(self, text: str) -> tuple[str, str, bool] | None:
        """Sucht den ähnlichsten Index-Eintrag bei kleinen OCR-Abweichungen."""
        if not text:
            return None
        candidates = list(self._index.keys())
        # cutoff 0.78 erwischt kleine Buchstabendreher / fehlende Buchstaben
        match = difflib.get_close_matches(text, candidates, n=1, cutoff=0.78)
        if not match:
            # Versuch über Token-Fenster, falls nur ein Teil ähnlich ist
            tokens = text.split()
            for size in range(min(3, len(tokens)), 0, -1):
                for start in range(0, len(tokens) - size + 1):
                    candidate = " ".join(tokens[start : start + size])
                    m = difflib.get_close_matches(candidate, candidates, n=1, cutoff=0.82)
                    if m:
                        return self._index[m[0]]
            return None
        return self._index[match[0]]

    def _post_process(self, ident: Identification) -> Identification:
        """Wendet Naming-Sonderregeln nach erfolgter Identifikation an.

        Regeln (Naming-Konvention):
          * Saxophone (04) und Schlagwerk (10): Stimmung wird nicht im Namen geführt.
          * Horn (05): Stimmung verschmilzt zum Präfix ("F-Horn", "Es-Horn"). Ohne
            erkannte Stimmung bleibt "Horn" und needs_pitch() liefert True.
          * Klarinette (03): in B normal -> kein Zusatz; in Es -> "Es-Klarinette".
          * Bassklarinette (03): in B normal -> kein Zusatz.
          * Trompete/Flügelhorn/Kornett (06): in B normal -> kein Zusatz.
          * Tenorhorn (07): in B normal -> kein Zusatz.
          * Bariton/Euphonium (07): in B -> "X TC", in C -> "X BC". Ohne
            Stimmung bleibt der Name und needs_pitch() liefert True.
          * Posaune (08): in C normal -> kein Zusatz; in B -> "B-Posaune".
          * Flöte/Piccolo (01), Oboe/Fagott (02), Tuba/Kontrabass (09): in C
            normal -> kein Zusatz.
          * Alle nicht-normalen Stimmungen: "Instrument [Nummer] in X" wie bisher.
        """
        code = ident.code
        name = ident.instrument
        zusatz = ident.zusatz
        pitch = zusatz[3:].strip() if zusatz.startswith("in ") else ""
        pitch_lower = pitch.lower()

        # Saxophone und Schlagwerk: Stimmung egal
        if code in {"04", "10"}:
            return _dc_replace(ident, zusatz="") if zusatz else ident

        # Horn: Stimmung als Präfix verschmelzen ("F-Horn", "Es-Horn")
        if code == "05" and name == "Horn":
            if pitch:
                return _dc_replace(ident, instrument=f"{pitch}-Horn", zusatz="")
            return ident  # ohne Stimmung -> Aufrufer behandelt als unsicher

        # Klarinette: in B default; in Es -> "Es-Klarinette"
        if code == "03" and name == "Klarinette":
            if pitch_lower in {"b", ""}:
                return _dc_replace(ident, zusatz="")
            if pitch_lower == "es":
                return _dc_replace(ident, instrument="Es-Klarinette", zusatz="")
            return ident

        # Posaune: in C default; in B -> "B-Posaune"
        if code == "08" and name == "Posaune":
            if pitch_lower in {"c", ""}:
                return _dc_replace(ident, zusatz="")
            if pitch_lower == "b":
                return _dc_replace(ident, instrument="B-Posaune", zusatz="")
            return ident

        # Bariton / Euphonium: TC (in B) / BC (in C); ohne Stimmung -> incomplete
        if code == "07" and name in {"Bariton", "Euphonium"}:
            if pitch_lower == "b":
                return _dc_replace(ident, instrument=f"{name} TC", zusatz="")
            if pitch_lower == "c":
                return _dc_replace(ident, instrument=f"{name} BC", zusatz="")
            return ident

        # Standard-Default-Stimmung: passende Stimmung -> zusatz dropen
        default_pitch = _DEFAULT_PITCH.get((code, name))
        if default_pitch is not None:
            if pitch_lower in {default_pitch.lower(), ""}:
                return _dc_replace(ident, zusatz="")
            return ident

        return ident

    def _parse_learned(self, normalized: str, raw_text: str) -> Identification:
        identifier = self._learned[normalized]
        m = re.match(r"^(\d{2})\s+(.*)$", identifier)
        if not m:
            return Identification(code="00", instrument=identifier, source_text=raw_text)
        code = m.group(1)
        rest = m.group(2).strip()
        m2 = re.match(r"^(.+?)(?:\s+(\d+))?(?:\s+(in [A-Za-zäöüß]+))?$", rest)
        if m2:
            return Identification(
                code=code,
                instrument=m2.group(1).strip(),
                nummer=m2.group(2) or "",
                zusatz=m2.group(3) or "",
                source_text=raw_text,
            )
        return Identification(code=code, instrument=rest, source_text=raw_text)

    def _extract_nummer_und_zusatz(self, text: str) -> tuple[str, str, str]:
        # Stimmung erkennen ("in B", "in Es", "in F", "in C", "in A", "in D")
        zusatz = ""
        m = re.search(r"\bin\s+(b\b|bb\b|es\b|eb\b|f\b|c\b|a\b|d\b)", text)
        if m:
            zusatz = "in " + _KEY_NORMAL.get(m.group(1).strip(), m.group(1).upper()).split()[-1]
            text = text[: m.start()] + " " + text[m.end():]
        # Suffix-Stimmung ohne "in" am Ende: "trumpet bb", "klarinette in b" — bereits behandelt
        m = re.search(r"\b(bb|eb)\b\s*$", text)
        if m and not zusatz:
            zusatz = "in " + _KEY_NORMAL.get(m.group(1), m.group(1).upper()).split()[-1]
            text = text[: m.start()] + " " + text[m.end():]
        # Präfix-Stimmung: "f-horn", "es-klarinette", "b-posaune" — auch mit
        # Leerzeichen als Trenner ("F HORN", "ES KLARINETTE"), wie es bei
        # vollständig groß geschriebenen Stimmenbezeichnungen vorkommt.
        m = re.match(r"^\s*(es|eb|bb|f|b|c|a|d)(?:\s*-\s*|\s+)(\S.*)$", text)
        if m:
            if not zusatz:
                pitch_token = m.group(1)
                zusatz = "in " + _KEY_NORMAL.get(pitch_token, pitch_token.upper()).split()[-1]
            text = m.group(2)
        # Schlüssel-Hinweis bei Bariton/Euphonium: "tc" -> in B, "bc" -> in C
        m = re.search(r"\b(tc|bc)\b", text)
        if m and not zusatz:
            zusatz = "in B" if m.group(1).lower() == "tc" else "in C"
            text = text[: m.start()] + " " + text[m.end():]
        # Nummern erkennen
        nummer = ""
        # "1st", "2nd", "first", "1.", "1", römisch
        text_clean = _strip_punct(text)
        tokens = text_clean.split()
        rest_tokens = []
        found = False
        for tok in tokens:
            if not found and tok in _NUM_WORDS:
                nummer = _NUM_WORDS[tok]
                found = True
                continue
            rest_tokens.append(tok)
        leftover = " ".join(rest_tokens).strip()
        return nummer, zusatz, leftover

    def _find_instrument(self, text: str) -> tuple[str, str, bool] | None:
        if not text:
            return None
        if text in self._index:
            return self._index[text]
        # Gleitfenster über die Tokens (längste Übereinstimmung gewinnt)
        tokens = text.split()
        best = None
        for size in range(len(tokens), 0, -1):
            for start in range(0, len(tokens) - size + 1):
                candidate = " ".join(tokens[start : start + size])
                if candidate in self._index:
                    if best is None or size > best[0]:
                        best = (size, self._index[candidate])
            if best:
                break
        return best[1] if best else None

    def _format_instrument_name(self, raw_text: str, normalname: str, keep_original: bool) -> str:
        if not keep_original:
            return normalname
        # Original-OCR-Text aufräumen, Titel-Case anwenden
        cleaned = re.sub(r"\s+", " ", raw_text.strip())
        cleaned = re.sub(r"^[\d\s\.\-]+", "", cleaned)  # führende Nummer/Pkt entfernen
        return cleaned if cleaned else normalname

    def learn(self, raw_text: str, identifier: str) -> None:
        """Speichert raw_text -> identifier (z.B. '06 Trompete 1 in B') in learned_aliases.yaml."""
        path = learned_aliases_file()
        data: dict[str, str] = {}
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        data[raw_text.strip()] = identifier
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=True, allow_unicode=True)
        self._learned[_normalize(raw_text)] = identifier
