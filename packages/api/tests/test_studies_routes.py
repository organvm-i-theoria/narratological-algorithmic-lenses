"""Regression tests for studies routes."""

from fastapi.testclient import TestClient


def test_search_axioms_route_is_reachable(client: TestClient) -> None:
    """Search axioms should not be shadowed by dynamic study routes."""
    response = client.get("/studies/search/axioms", params={"q": "narrative"})

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)

    if payload:
        first = payload[0]
        assert "study_id" in first
        assert "axiom" in first


def test_search_algorithms_route_is_reachable(client: TestClient) -> None:
    """Search algorithms should not be shadowed by dynamic study routes."""
    response = client.get("/studies/search/algorithms", params={"q": "sequence"})

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)

    if payload:
        first = payload[0]
        assert "study_id" in first
        assert "algorithm" in first

