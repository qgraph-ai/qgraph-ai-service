from fastapi import APIRouter

from src.api.schemas.search import (
    SearchExecuteRequest,
    SearchExecuteResponse,
    SearchPlanRequest,
    SearchPlanResponse,
)
from src.services.planning import build_planning_response
from src.services.search_service import build_search_execute_response

router = APIRouter(prefix="/v1/search", tags=["search"])


@router.post("/plan", response_model=SearchPlanResponse)
def search_plan(payload: SearchPlanRequest) -> SearchPlanResponse:
    return build_planning_response(payload)


@router.post("/execute", response_model=SearchExecuteResponse)
def search_execute(payload: SearchExecuteRequest) -> SearchExecuteResponse:
    return build_search_execute_response(payload)
