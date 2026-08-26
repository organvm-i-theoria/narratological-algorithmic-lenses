"""End-to-end tests for the public API user flow."""

from __future__ import annotations

import json
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from narratological_api.auth import quota_store


SCRIPT = """INT. WRITERS ROOM - DAY

A writer pins beat cards to a wall.

WRITER
The problem is not the ending. It is the engine.

EXT. STUDIO LOT - NIGHT

The writer crosses the lot with a new stack of pages.
"""


@pytest.fixture(autouse=True)
def api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure deterministic API keys for the end-to-end route flow."""
    monkeypatch.setenv(
        "NARRATOLOGICAL_API_KEYS",
        json.dumps(
            {
                "creator-key": {"tier": "creator", "account_id": "creator-acct"},
            }
        ),
    )
    quota_store.reset()


def test_api_main_user_flow_from_catalog_to_suite_analysis(client: TestClient) -> None:
    """A user can discover a framework, inspect an algorithm, diagnose, and run the suite."""
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}

    stats_response = client.get("/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["study_count"] >= 14
    assert stats["total_algorithms"] >= 92

    studies_response = client.get("/studies/")
    assert studies_response.status_code == 200
    studies = studies_response.json()
    assert len(studies) == stats["study_count"]

    pixar_summary = next(study for study in studies if study["id"] == "pixar")
    assert pixar_summary["algorithm_count"] > 0
    assert pixar_summary["question_count"] > 0

    study_response = client.get("/studies/pixar")
    assert study_response.status_code == 200
    study = study_response.json()
    assert study["id"] == "pixar"
    assert study["creator"] == "Pixar"
    assert len(study["core_algorithms"]) == pixar_summary["algorithm_count"]

    algorithm_name = "engineer_empathy"
    algorithm_response = client.get(
        f"/studies/pixar/algorithms/{quote(algorithm_name, safe='')}"
    )
    assert algorithm_response.status_code == 200
    algorithm = algorithm_response.json()
    assert algorithm["name"] == algorithm_name
    assert "empathy" in algorithm["purpose"].lower()

    diagnostic_response = client.post(
        "/diagnostics/causal-binding",
        params={"target": 0.75},
        json={
            "scenes": [
                {"number": 1, "connector": "THEREFORE"},
                {"number": 2, "connector": "BUT"},
                {"number": 3, "connector": "AND THEN"},
            ]
        },
    )
    assert diagnostic_response.status_code == 200
    diagnostic = diagnostic_response.json()
    assert diagnostic["causal_count"] == 2
    assert diagnostic["episodic_count"] == 1
    assert diagnostic["binding_ratio"] == pytest.approx(2 / 3)
    assert diagnostic["target_met"] is False
    assert diagnostic["weak_links"] == [3]

    suite_response = client.post(
        "/analysis/narrative-suite",
        headers={"X-API-Key": "creator-key"},
        json={
            "title": "Feature Draft",
            "format": "Feature",
            "content": SCRIPT,
            "include_algorithm_details": True,
        },
    )
    assert suite_response.status_code == 200
    suite = suite_response.json()
    assert suite["status"] == "ready"
    assert suite["tier"] == "creator"
    assert suite["input"]["title"] == "Feature Draft"
    assert suite["input"]["scene_count"] == 2
    assert suite["suite"]["suite_id"] == "narratological-92"
    assert suite["suite"]["selected_algorithm_count"] == 92
    assert suite["suite"]["full_suite"] is True
    assert len(suite["algorithms"]) == 92
    assert {study["study_id"] for study in suite["studies"]} >= {"bergman", "pixar"}
    assert suite["quota"]["used"] == 1
    assert suite_response.headers["X-Quota-Remaining"] == "49"
