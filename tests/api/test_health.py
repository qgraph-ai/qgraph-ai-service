from src.config import get_settings


def test_health_endpoint_returns_minimal_shape(client):
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    settings = get_settings()
    assert payload == {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.service_version,
    }
