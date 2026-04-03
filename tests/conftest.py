import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def search_plan_payload():
    return {
        "query": "verses about patience",
        "filters": {"surah_ids": [2]},
        "output_preferences": {"include_summary": True, "include_statistics": True},
    }


@pytest.fixture
def search_execute_payload():
    return {
        "query": "verses about patience",
        "filters": {"surah_ids": [2]},
        "output_preferences": {
            "include_summary": True,
            "include_statistics": True,
            "include_explanation": False,
        },
        "context": {"query_id": 123, "execution_id": 456},
    }


@pytest.fixture
def segmentation_generate_payload():
    return {
        "surah_id": 2,
        "ayahs": [
            {
                "id": 8,
                "number_in_surah": 1,
                "text_ar": "placeholder",
                "translations": [{"lang": "en", "text": "placeholder"}],
            },
            {
                "id": 9,
                "number_in_surah": 2,
                "text_ar": "placeholder",
                "translations": [{"lang": "en", "text": "placeholder"}],
            },
        ],
        "options": {
            "granularity": "medium",
            "max_segments": 20,
            "include_tags": True,
            "include_summaries": True,
        },
        "context": {
            "workspace_slug": "my-workspace",
            "requested_by_user_id": 42,
        },
    }
