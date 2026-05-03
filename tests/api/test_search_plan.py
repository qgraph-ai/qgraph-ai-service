def test_search_plan_endpoint_returns_expected_keys(client, search_plan_payload):
    response = client.post("/v1/search/plan", json=search_plan_payload)
    assert response.status_code == 200

    payload = response.json()
    assert set(payload) == {
        "mode",
        "policy_label",
        "policy_snapshot",
        "routing_metadata",
        "backend_name",
        "backend_version",
    }
    assert payload["mode"] in {"sync", "async"}


def test_search_plan_endpoint_returns_json_objects(client, search_plan_payload):
    response = client.post("/v1/search/plan", json=search_plan_payload)
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload["policy_snapshot"], dict)
    assert isinstance(payload["routing_metadata"], dict)


def test_search_plan_endpoint_returns_mock_v1_contract(client, search_plan_payload):
    response = client.post("/v1/search/plan", json=search_plan_payload)
    assert response.status_code == 200

    payload = response.json()
    assert payload == {
        "mode": "async",
        "policy_label": "mock_v1",
        "policy_snapshot": {},
        "routing_metadata": {},
        "backend_name": "qgraph-ai-service",
        "backend_version": "0.1.0",
    }


def test_search_plan_endpoint_is_deterministic_by_query(client, search_plan_payload):
    first_response = client.post("/v1/search/plan", json=search_plan_payload)
    second_response = client.post("/v1/search/plan", json=search_plan_payload)
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["mode"] == first_response.json()["mode"]


def test_search_plan_endpoint_supports_mock_mode_override(client, search_plan_payload):
    sync_response = client.post(
        "/v1/search/plan",
        json={
            **search_plan_payload,
            "output_preferences": {"mock_mode": "sync"},
        },
    )
    async_response = client.post(
        "/v1/search/plan",
        json={
            **search_plan_payload,
            "output_preferences": {"mock_mode": "async"},
        },
    )

    assert sync_response.status_code == 200
    assert async_response.status_code == 200
    assert sync_response.json()["mode"] == "sync"
    assert async_response.json()["mode"] == "async"
