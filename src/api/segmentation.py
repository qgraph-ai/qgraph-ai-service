from fastapi import APIRouter

from src.api.schemas.segmentation import (
    SegmentationGenerateRequest,
    SegmentationGenerateResponse,
)
from src.services.segmentation_service import build_segmentation_generate_response

router = APIRouter(prefix="/v1/segmentation", tags=["segmentation"])


@router.post("/generate", response_model=SegmentationGenerateResponse)
def segmentation_generate(
    payload: SegmentationGenerateRequest,
) -> SegmentationGenerateResponse:
    return build_segmentation_generate_response(payload)
