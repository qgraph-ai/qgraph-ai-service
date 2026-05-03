def test_search_job_create_endpoint_returns_expected_shape(client, search_job_create_payload):
    response = client.post("/v1/search/jobs", json=search_job_create_payload)
    assert response.status_code == 202

    payload = response.json()
    assert set(payload) == {"job_id", "status", "created_at", "poll_after_seconds"}
    assert payload["job_id"].startswith("job_")
    assert payload["status"] == "queued"
    assert payload["poll_after_seconds"] >= 0


def test_search_job_create_endpoint_reuses_active_job_for_same_idempotency_key(
    client,
    search_job_create_payload,
):
    first_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    second_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    assert first_response.status_code == 202
    assert second_response.status_code == 202

    first_payload = first_response.json()
    second_payload = second_response.json()
    assert second_payload["job_id"] == first_payload["job_id"]


def test_search_job_status_endpoint_returns_expected_shape(client, search_job_create_payload):
    create_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    job_id = create_response.json()["job_id"]

    response = client.get(f"/v1/search/jobs/{job_id}")
    assert response.status_code == 200
    response = client.get(f"/v1/search/jobs/{job_id}")
    assert response.status_code == 200

    payload = response.json()
    assert set(payload) == {
        "job_id",
        "status",
        "created_at",
        "started_at",
        "completed_at",
        "poll_after_seconds",
        "result_available",
        "error",
        "progress",
    }
    assert payload["status"] in {"queued", "running", "succeeded", "failed", "canceled"}
    assert {"stage", "percent"} <= set(payload["progress"])
    assert payload["progress"] == {"stage": "mock_search", "percent": 50}


def test_search_job_result_endpoint_returns_409_while_job_is_not_ready(
    client,
    search_job_create_payload,
):
    create_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    job_id = create_response.json()["job_id"]

    response = client.get(f"/v1/search/jobs/{job_id}/result")
    assert response.status_code == 409
    payload = response.json()
    assert payload["error"] == "http_error"
    assert payload["detail"]["message"] == "Search job result not ready"
    assert payload["detail"]["job_id"] == job_id


def test_search_job_result_endpoint_returns_execute_payload_when_job_is_ready(
    client,
    search_job_create_payload,
):
    create_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    job_id = create_response.json()["job_id"]

    for _ in range(4):
        response = client.get(f"/v1/search/jobs/{job_id}")
        assert response.status_code == 200

    result_response = client.get(f"/v1/search/jobs/{job_id}/result")
    assert result_response.status_code == 200
    payload = result_response.json()
    assert set(payload) == {
        "title",
        "overall_confidence",
        "render_schema_version",
        "metadata",
        "blocks",
    }
    assert isinstance(payload["metadata"], dict)
    assert isinstance(payload["blocks"], list)
    assert payload["render_schema_version"] == "v1"
    assert payload["blocks"]
    assert [block["order"] for block in payload["blocks"]] == list(range(len(payload["blocks"])))
    assert {block["block_type"] for block in payload["blocks"]} <= {
        "text",
        "markdown",
        "surah_distribution",
    }


def test_search_job_result_endpoint_preserves_surahs_filter_when_ready(
    client,
    search_job_create_payload,
):
    search_job_create_payload = {
        **search_job_create_payload,
        "filters": {"surahs": [1, 2, 7]},
    }
    create_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    job_id = create_response.json()["job_id"]

    for _ in range(4):
        response = client.get(f"/v1/search/jobs/{job_id}")
        assert response.status_code == 200

    result_response = client.get(f"/v1/search/jobs/{job_id}/result")
    assert result_response.status_code == 200

    distribution_blocks = [
        block
        for block in result_response.json()["blocks"]
        if block["block_type"] == "surah_distribution"
    ]
    assert len(distribution_blocks) == 1
    distribution = distribution_blocks[0]["payload"]
    assert distribution["values"] == [
        {"surah": 1, "value": 3},
        {"surah": 2, "value": 17},
        {"surah": 7, "value": 5},
    ]


def test_search_job_result_endpoint_can_return_markdown_when_ready(
    client,
    search_job_create_payload,
):
    search_job_create_payload = {
        **search_job_create_payload,
        "query": "light",
        "filters": {},
    }
    create_response = client.post("/v1/search/jobs", json=search_job_create_payload)
    job_id = create_response.json()["job_id"]

    for _ in range(4):
        response = client.get(f"/v1/search/jobs/{job_id}")
        assert response.status_code == 200

    result_response = client.get(f"/v1/search/jobs/{job_id}/result")
    assert result_response.status_code == 200

    markdown_blocks = [
        block for block in result_response.json()["blocks"] if block["block_type"] == "markdown"
    ]
    assert len(markdown_blocks) == 1
    assert isinstance(markdown_blocks[0]["payload"], dict)
    assert isinstance(markdown_blocks[0]["payload"]["content"], str)
    assert "| Surah | Mock mentions | Note |" in markdown_blocks[0]["payload"]["content"]


def test_search_job_endpoints_return_404_for_unknown_job(client):
    status_response = client.get("/v1/search/jobs/job_missing")
    assert status_response.status_code == 404

    result_response = client.get("/v1/search/jobs/job_missing/result")
    assert result_response.status_code == 404
