from src.services.planning import ALLOWED_MODES, choose_planning_mode


def test_planning_allowed_modes_are_fixed():
    assert set(ALLOWED_MODES) == {"sync", "async"}


def test_choose_planning_mode_returns_only_allowed_values():
    for query in ["verses about patience", "mercy", "justice", "light"]:
        assert choose_planning_mode(query) in ALLOWED_MODES


def test_choose_planning_mode_is_deterministic_for_query():
    assert choose_planning_mode("verses about patience") == choose_planning_mode(
        "verses about patience"
    )


def test_choose_planning_mode_supports_mock_mode_override():
    assert choose_planning_mode("verses about patience", {"mock_mode": "sync"}) == "sync"
    assert choose_planning_mode("justice", {"mock_mode": "async"}) == "async"
    assert choose_planning_mode("justice", {"mock_mode": "invalid"}) == "sync"
