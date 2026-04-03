from typing import Any


def fetch_related_nodes(query: str, *, limit: int = 2) -> list[dict[str, Any]]:
    token_count = len([token for token in query.split() if token])
    return [
        {
            "node_id": f"topic-{index + 1}",
            "relation": "related",
            "weight": round(0.8 - (index * 0.1), 2),
            "token_count": token_count,
        }
        for index in range(limit)
    ]
