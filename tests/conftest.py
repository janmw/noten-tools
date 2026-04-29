"""Gemeinsame pytest-Fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_learned_aliases(tmp_path, monkeypatch):
    """Verhindert, dass die persönliche learned_aliases.yaml Tests beeinflusst."""
    fake = tmp_path / "no-learned-aliases.yaml"
    monkeypatch.setattr(
        "notentools.shared.paths.learned_aliases_file",
        lambda: fake,
    )
    monkeypatch.setattr(
        "notentools.shared.instruments.learned_aliases_file",
        lambda: fake,
    )
    yield fake
