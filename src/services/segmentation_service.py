from datetime import datetime, timezone
from uuid import uuid4

from src.api.schemas.segmentation import (
    GeneratedSegment,
    SegmentationGenerateRequest,
    SegmentationGenerateResponse,
)
from src.config import Settings, get_settings
from src.workflows.segmentation_workflow import run_segmentation_workflow


def build_segmentation_generate_response(
    request: SegmentationGenerateRequest,
    settings: Settings | None = None,
) -> SegmentationGenerateResponse:
    cfg = settings if settings is not None else get_settings()

    workflow_segments = run_segmentation_workflow(
        surah_id=request.surah_id,
        ayahs=request.ayahs,
        options=request.options.model_dump(),
    )

    segments = [GeneratedSegment(**segment) for segment in workflow_segments]
    params = {
        "granularity": request.options.granularity,
        "max_segments": request.options.max_segments,
    }

    return SegmentationGenerateResponse(
        external_id=f"seg_{uuid4().hex[:12]}",
        model_name=cfg.segmentation_model_name,
        model_version=cfg.segmentation_model_version,
        params=params,
        produced_at=datetime.now(timezone.utc),
        segments=segments,
    )
