"""Regression tests: dream specialists honor the configured tool-iteration limit.

Deduction and Induction used to hardcode their caps (12 and 10), silently
ignoring ``settings.DREAM.MAX_TOOL_ITERATIONS`` even though the config field is
documented as the shared dream agent iteration limit and ``CardRefreshSpecialist``
already honored it. These tests pin the shared behavior so the knob cannot go
dead again for the two specialists that generate dream load.
"""

import pytest

from src.config import settings
from src.dreamer.specialists import (
    CardRefreshSpecialist,
    DeductionSpecialist,
    InductionSpecialist,
)


def test_deduction_honors_configured_limit(monkeypatch: pytest.MonkeyPatch):
    spec = DeductionSpecialist()
    default = settings.DREAM.MAX_TOOL_ITERATIONS
    # Below the ceiling the configured value wins outright.
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 20)
    assert spec.get_max_iterations() == 20
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 12)
    assert spec.get_max_iterations() == 12
    # At/above the ceiling the ceiling binds.
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 50)
    assert spec.get_max_iterations() == min(spec.MAX_ITERATIONS_CEILING, 50)
    # Sanity: the shipped default is at least the old hardcoded value.
    assert default >= 12


def test_induction_honors_configured_limit(monkeypatch: pytest.MonkeyPatch):
    spec = InductionSpecialist()
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 20)
    assert spec.get_max_iterations() == 20
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 10)
    assert spec.get_max_iterations() == 10
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 50)
    assert spec.get_max_iterations() == min(spec.MAX_ITERATIONS_CEILING, 50)


def test_card_refresh_unaffected(monkeypatch: pytest.MonkeyPatch):
    spec = CardRefreshSpecialist()
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 20)
    assert spec.get_max_iterations() == min(6, 20)
    monkeypatch.setattr(settings.DREAM, "MAX_TOOL_ITERATIONS", 4)
    assert spec.get_max_iterations() == 4
