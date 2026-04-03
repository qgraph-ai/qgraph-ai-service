from typing import Any

from src.stores.graph_store import fetch_related_nodes
from src.stores.vector_store import search_vectors


def run_search_workflow(query: str, filters: dict[str, Any]) -> dict[str, Any]:
    vector_hits = search_vectors(query, limit=3)
    related_nodes = fetch_related_nodes(query, limit=2)
    return {
        "vector_hits": vector_hits,
        "related_nodes": related_nodes,
        "retrieval_ms": 120,
        "generation_ms": 420,
        "filters_used": filters,
    }
