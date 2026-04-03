from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

JsonObject = dict[str, Any]
SearchMode = Literal["sync", "async"]


class SearchPlanRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: JsonObject = Field(default_factory=dict)
    output_preferences: JsonObject = Field(default_factory=dict)


class SearchPlanResponse(BaseModel):
    mode: SearchMode
    policy_label: str
    policy_snapshot: JsonObject = Field(default_factory=dict)
    routing_metadata: JsonObject = Field(default_factory=dict)
    backend_name: str
    backend_version: str


class SearchExecuteRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: JsonObject = Field(default_factory=dict)
    output_preferences: JsonObject = Field(default_factory=dict)
    context: JsonObject = Field(default_factory=dict)


class SearchResultItem(BaseModel):
    rank: int = Field(ge=1)
    result_type: str
    score: float = Field(ge=0.0, le=1.0)
    title: str
    snippet_text: str
    highlighted_text: str
    match_metadata: JsonObject = Field(default_factory=dict)
    explanation: str = ""
    provenance: JsonObject = Field(default_factory=dict)


class SearchResponseBlock(BaseModel):
    order: int = Field(ge=1)
    block_type: str
    title: str
    payload: JsonObject = Field(default_factory=dict)
    explanation: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: JsonObject = Field(default_factory=dict)
    warning_text: str = ""
    items: list[SearchResultItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_item_ranks(self) -> "SearchResponseBlock":
        ranks = [item.rank for item in self.items]
        if len(ranks) != len(set(ranks)):
            raise ValueError("items.rank must be unique within each block")
        return self


class SearchExecuteResponse(BaseModel):
    title: str
    overall_confidence: float = Field(ge=0.0, le=1.0)
    render_schema_version: str
    metadata: JsonObject = Field(default_factory=dict)
    blocks: list[SearchResponseBlock] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_block_orders(self) -> "SearchExecuteResponse":
        orders = [block.order for block in self.blocks]
        if len(orders) != len(set(orders)):
            raise ValueError("blocks.order must be unique")
        return self
