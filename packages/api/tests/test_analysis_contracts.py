"""Contract tests for analysis endpoints."""

from fastapi.testclient import TestClient

NOT_IMPLEMENTED_KEYS = {"status", "code", "message", "planned"}


def test_scene_analysis_stub_returns_standard_501(client: TestClient) -> None:
    """Scene analysis endpoint should expose a structured 501 payload."""
    response = client.post(
        "/analysis/scene",
        json={"text": "INT. ROOM - DAY", "framework": "pixar"},
    )

    assert response.status_code == 501
    detail = response.json()["detail"]
    assert set(detail.keys()) == NOT_IMPLEMENTED_KEYS
    assert detail["status"] == "not_implemented"
    assert detail["code"] == "ANALYSIS_NOT_IMPLEMENTED"


def test_script_status_stub_returns_standard_501(client: TestClient) -> None:
    """Script status endpoint should expose a structured 501 payload."""
    response = client.get("/analysis/script/test-id/status")

    assert response.status_code == 501
    detail = response.json()["detail"]
    assert set(detail.keys()) == NOT_IMPLEMENTED_KEYS


def test_openapi_documents_501_for_selected_analysis_routes(client: TestClient) -> None:
    """OpenAPI should explicitly document 501 responses for unimplemented routes."""
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]

    checked_routes = [
        ("/analysis/scene", "post"),
        ("/analysis/script", "post"),
        ("/analysis/script/{analysis_id}/status", "get"),
        ("/analysis/script/{analysis_id}/reports", "get"),
    ]

    for route, method in checked_routes:
        responses = paths[route][method]["responses"]
        assert "501" in responses
        schema = responses["501"]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("NotImplementedResponse")

