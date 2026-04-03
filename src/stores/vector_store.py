from typing import Any


def search_vectors(query: str, *, limit: int = 3) -> list[dict[str, Any]]:
    terms = [term.strip(" ,.") for term in query.lower().split() if term.strip(" ,.")]
    if not terms:
        terms = ["query"]

    hits: list[dict[str, Any]] = []
    for index in range(limit):
        term = terms[index % len(terms)]
        hits.append(
            {
                "ref": f"ayah-{index + 1}",
                "term": term,
                "score": round(0.93 - (index * 0.07), 2),
            }
        )
    return hits
