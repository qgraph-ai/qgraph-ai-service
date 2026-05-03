from hashlib import sha256

from src.api.schemas.search import SearchMode, SearchPlanRequest, SearchPlanResponse
from src.config import Settings, get_settings

ALLOWED_MODES: tuple[SearchMode, SearchMode] = ("sync", "async")


def _stable_bucket(value: str) -> int:
    digest = sha256(value.encode("utf-8")).digest()
    return digest[0]


def choose_planning_mode(
    query: str,
    output_preferences: dict | None = None,
) -> SearchMode:
    mock_mode = (output_preferences or {}).get("mock_mode")
    if mock_mode in ALLOWED_MODES:
        return mock_mode
    return ALLOWED_MODES[_stable_bucket(query) % len(ALLOWED_MODES)]


def build_planning_response(
    request: SearchPlanRequest,
    settings: Settings | None = None,
) -> SearchPlanResponse:
    cfg = settings if settings is not None else get_settings()
    mode = choose_planning_mode(request.query, request.output_preferences)
    return SearchPlanResponse(
        mode=mode,
        policy_label="mock_v1",
        policy_snapshot={},
        routing_metadata={},
        backend_name=cfg.service_name,
        backend_version=cfg.service_version,
    )
