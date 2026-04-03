def test_segmentation_generate_endpoint_returns_required_provenance_fields(
    client,
    segmentation_generate_payload,
):
    response = client.post("/v1/segmentation/generate", json=segmentation_generate_payload)
    assert response.status_code == 200

    payload = response.json()
    assert set(payload) == {
        "external_id",
        "model_name",
        "model_version",
        "params",
        "produced_at",
        "segments",
    }
    assert isinstance(payload["params"], dict)
    assert isinstance(payload["segments"], list)


def test_segmentation_generate_segment_shape_is_valid(client, segmentation_generate_payload):
    response = client.post("/v1/segmentation/generate", json=segmentation_generate_payload)
    assert response.status_code == 200

    payload = response.json()
    assert payload["segments"]
    segment = payload["segments"][0]
    assert {"start_ayah", "end_ayah", "title", "summary", "tags"} <= set(segment)
    assert segment["start_ayah"] <= segment["end_ayah"]
    assert isinstance(segment["tags"], list)
