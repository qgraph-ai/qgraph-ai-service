from random import Random

from src.services.planning import ALLOWED_MODES, choose_planning_mode


def test_planning_allowed_modes_are_fixed():
    assert set(ALLOWED_MODES) == {"sync", "async"}


def test_choose_planning_mode_returns_only_allowed_values():
    rng = Random(42)
    for _ in range(50):
        assert choose_planning_mode(rng=rng) in ALLOWED_MODES
