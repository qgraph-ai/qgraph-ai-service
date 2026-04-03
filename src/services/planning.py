import random
from random import Random

from src.api.schemas.search import SearchMode, SearchPlanRequest, SearchPlanResponse
from src.config import Settings, get_settings

ALLOWED_MODES: tuple[SearchMode, SearchMode] = ("sync", "async")


def choose_planning_mode(rng: Random | None = None) -> SearchMode:
    generator = rng if rng is not None else random
    return generator.choice(ALLOWED_MODES)


def build_planning_response(
    request: SearchPlanRequest,
    settings: Settings | None = None,
) -> SearchPlanResponse:
    cfg = settings if settings is not None else get_settings()
    mode = choose_planning_mode()
    return SearchPlanResponse(
        mode=mode,
        policy_label="router_v1",
        policy_snapshot={
            "ruleset": "router_v1",
            "thresholds": {"max_tokens_sync": 500},
        },
        routing_metadata={
            "reason": "bootstrap_random_mode",
            "model_route": "search-fast" if mode == "sync" else "search-slow",
            "query_preview": request.query[:32],
        },
        backend_name=cfg.search_backend_name,
        backend_version=cfg.search_backend_version,
    )
