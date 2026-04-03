from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

JsonObject = dict[str, Any]


class AyahTranslationInput(BaseModel):
    lang: str
    text: str


class AyahInput(BaseModel):
    id: int | None = None
    number_in_surah: int = Field(ge=1)
    text_ar: str | None = None
    translations: list[AyahTranslationInput] = Field(default_factory=list)


class SegmentationOptions(BaseModel):
    model_config = ConfigDict(extra="allow")

    granularity: str = "medium"
    max_segments: int = Field(default=20, ge=1)
    include_tags: bool = True
    include_summaries: bool = True


class SegmentationContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    workspace_slug: str | None = None
    requested_by_user_id: int | None = None


class SegmentationGenerateRequest(BaseModel):
    surah_id: int = Field(ge=1)
    ayahs: list[AyahInput] = Field(default_factory=list)
    options: SegmentationOptions = Field(default_factory=SegmentationOptions)
    context: SegmentationContext = Field(default_factory=SegmentationContext)


class SegmentTag(BaseModel):
    name: str
    color: str = "#22c55e"
    description: str = ""


class GeneratedSegment(BaseModel):
    start_ayah: int = Field(ge=1)
    end_ayah: int = Field(ge=1)
    title: str = ""
    summary: str = ""
    tags: list[SegmentTag] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_range(self) -> "GeneratedSegment":
        if self.start_ayah > self.end_ayah:
            raise ValueError("start_ayah must be less than or equal to end_ayah")
        return self


class SegmentationGenerateResponse(BaseModel):
    external_id: str
    model_name: str
    model_version: str
    params: JsonObject = Field(default_factory=dict)
    produced_at: datetime
    segments: list[GeneratedSegment] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_sorted_non_overlapping_segments(self) -> "SegmentationGenerateResponse":
        previous_end = 0
        for segment in self.segments:
            if segment.start_ayah <= previous_end:
                raise ValueError("segments must be sorted and non-overlapping")
            previous_end = segment.end_ayah
        return self
