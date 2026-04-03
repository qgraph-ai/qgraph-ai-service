def test_search_execute_endpoint_returns_schema_shape(client, search_execute_payload):
    response = client.post("/v1/search/execute", json=search_execute_payload)
    assert response.status_code == 200

    payload = response.json()
    assert set(payload) == {
        "title",
        "overall_confidence",
        "render_schema_version",
        "metadata",
        "blocks",
    }
    assert isinstance(payload["metadata"], dict)
    assert isinstance(payload["blocks"], list)
    assert payload["blocks"]


def test_search_execute_block_orders_are_unique(client, search_execute_payload):
    response = client.post("/v1/search/execute", json=search_execute_payload)
    assert response.status_code == 200

    payload = response.json()
    orders = [block["order"] for block in payload["blocks"]]
    assert len(orders) == len(set(orders))


def test_search_execute_item_ranks_are_unique_within_each_block(client, search_execute_payload):
    response = client.post("/v1/search/execute", json=search_execute_payload)
    assert response.status_code == 200

    payload = response.json()
    for block in payload["blocks"]:
        items = block["items"]
        ranks = [item["rank"] for item in items]
        assert len(ranks) == len(set(ranks))
