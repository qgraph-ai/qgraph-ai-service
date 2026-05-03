from hashlib import sha256

from src.api.schemas.search import (
    SearchExecuteRequest,
    SearchExecuteResponse,
    SearchResponseBlock,
)
from src.config import Settings, get_settings

DEFAULT_SURAH_DISTRIBUTION = (1, 2, 7)
MOCK_SURAH_VALUES = {
    1: 3,
    2: 17,
    7: 5,
}


def _coerce_surah_ids(filters: dict) -> list[int]:
    raw_surahs = filters.get("surahs")
    if raw_surahs is None:
        raw_surahs = filters.get("surah_ids")
    if not isinstance(raw_surahs, list):
        return []

    surah_ids: list[int] = []
    seen: set[int] = set()
    for value in raw_surahs:
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        if value < 1 or value > 114 or value in seen:
            continue
        surah_ids.append(value)
        seen.add(value)
    return surah_ids


def _mock_surah_value(surah_id: int) -> int:
    if surah_id in MOCK_SURAH_VALUES:
        return MOCK_SURAH_VALUES[surah_id]
    return ((surah_id * 7) % 19) + 1


def _build_surah_distribution_values(filters: dict) -> list[dict[str, int]]:
    surah_ids = _coerce_surah_ids(filters)
    if not surah_ids:
        surah_ids = list(DEFAULT_SURAH_DISTRIBUTION)
    return [
        {
            "surah": surah_id,
            "value": _mock_surah_value(surah_id),
        }
        for surah_id in surah_ids
    ]


def _stable_bucket(value: str) -> int:
    digest = sha256(value.encode("utf-8")).digest()
    return digest[0]


def _should_include_surah_distribution(request: SearchExecuteRequest) -> bool:
    if _coerce_surah_ids(request.filters):
        return True
    return _stable_bucket(request.query) % 2 == 0


def _build_markdown_content() -> str:
    return (
        "## Why this theme matters\n\n"
        "The roots **r-h-m** and **gh-f-r** are common in discussions of mercy and "
        "forgiveness.\n\n"
        "### Mock observations\n\n"
        "- Mercy language appears near openings, prayers, and prophetic narratives.\n"
        "- The mock counts are synthetic, but the shape is useful for frontend testing.\n"
        "- Prefer the chart block for numeric distribution.\n"
        "- [x] supported by the mock\n\n"
        "Use `r-h-m` as the mock root marker.\n\n"
        "| Surah | Mock mentions | Note |\n"
        "| --- | ---: | --- |\n"
        "| Al-Fatihah | 3 | Opening formula |\n"
        "| Al-Baqarah | 17 | Dense legal and narrative material |\n"
        "| Maryam | 14 | Strong mercy motif |\n\n"
        "> This block is synthetic and exists to test Markdown rendering.\n\n"
        "```json\n"
        "{\n"
        '  "root": "r-h-m",\n'
        '  "mock": true,\n'
        '  "renderer": "markdown"\n'
        "}\n"
        "```\n\n"
        "See also [Quran Corpus](https://corpus.quran.com)."
    )


def _build_markdown_block(order: int) -> SearchResponseBlock:
    return SearchResponseBlock(
        order=order,
        block_type="markdown",
        title="Structured explanation",
        payload={
            "headline": "Mock markdown overview",
            "content": _build_markdown_content(),
        },
        explanation="Synthetic markdown block for renderer testing.",
        confidence=0.8,
        provenance={"backend": "mock"},
        warning_text="",
        items=[],
    )


def build_search_execute_response(
    request: SearchExecuteRequest,
    settings: Settings | None = None,
) -> SearchExecuteResponse:
    cfg = settings if settings is not None else get_settings()

    blocks = [
        SearchResponseBlock(
            order=0,
            block_type="text",
            title="Mercy across the Qur'an",
            payload={
                "headline": "Mock thematic overview",
                "details": (
                    "This mock response summarizes the requested theme in plain text so "
                    "Django can persist typed v1 blocks and the frontend can render them."
                    "\n\n"
                    "The content is synthetic and intended only for end-to-end wiring tests."
                ),
            },
            explanation="Synthetic prose block for end-to-end wiring tests.",
            confidence=0.88,
            provenance={"backend": "mock"},
            warning_text="",
            items=[],
        ),
    ]
    blocks.append(_build_markdown_block(len(blocks)))

    if _should_include_surah_distribution(request):
        surah_values = _build_surah_distribution_values(request.filters)
        blocks.append(
            SearchResponseBlock(
                order=len(blocks),
                block_type="surah_distribution",
                title="Where this theme appears",
                payload={
                    "values": surah_values,
                    "y_label": "Mock mentions",
                    "max_value": max(value["value"] for value in surah_values),
                },
                explanation="Synthetic counts for end-to-end wiring tests.",
                confidence=0.74,
                provenance={"backend": "mock"},
                warning_text="",
                items=[],
            )
        )

    return SearchExecuteResponse(
        title=f"Search results for {request.query}",
        overall_confidence=0.82,
        render_schema_version=cfg.render_schema_version,
        metadata={"mock": True},
        blocks=blocks,
    )
