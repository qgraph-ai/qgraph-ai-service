from typing import Any

from src.api.schemas.segmentation import AyahInput


def run_segmentation_workflow(
    surah_id: int,
    ayahs: list[AyahInput],
    options: dict[str, Any],
) -> list[dict[str, Any]]:
    if ayahs:
        ayah_numbers = sorted({ayah.number_in_surah for ayah in ayahs})
        start_ayah = ayah_numbers[0]
        end_ayah = ayah_numbers[-1]
    else:
        start_ayah = 1
        end_ayah = 1

    include_tags = bool(options.get("include_tags", True))
    include_summaries = bool(options.get("include_summaries", True))

    return [
        {
            "start_ayah": start_ayah,
            "end_ayah": end_ayah,
            "title": f"Surah {surah_id} Segment 1",
            "summary": "Bootstrap placeholder segment summary" if include_summaries else "",
            "tags": (
                [
                    {
                        "name": "bootstrap-theme",
                        "color": "#22c55e",
                        "description": "Temporary AI tag placeholder",
                    }
                ]
                if include_tags
                else []
            ),
        }
    ]
