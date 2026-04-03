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
