"""Pytest configuration and fixtures for CLI tests."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_script_text() -> str:
    """Sample screenplay text for testing."""
    return """FADE IN:

INT. APARTMENT - MORNING

JOHN, 30s, disheveled, stares at his phone. The screen shows a text message: "It's over."

JOHN
(whispering)
No... no, no, no.

He throws the phone against the wall. It shatters.

EXT. STREET - DAY

John walks aimlessly through the city. People pass by, oblivious to his pain.

SARAH, 20s, bright and energetic, approaches from across the street.

SARAH
John? John! Is that you?

John looks up, confused.

JOHN
Sarah? What are you doing here?

SARAH
I moved back last month. Are you okay? You look terrible.

INT. COFFEE SHOP - LATER

John and Sarah sit across from each other. Coffee cups between them.

SARAH
So what happened with Maria?

JOHN
(sighing)
She left. Said I wasn't present enough. That I was always somewhere else.

SARAH
Were you?

John doesn't answer. He stares out the window.

EXT. PARK - SUNSET

John sits on a bench, alone. Sarah approaches and sits beside him.

SARAH
You know, running away from your feelings doesn't make them disappear.

JOHN
Who says I'm running?

SARAH
Your eyes. They've been running since the day I met you.

John finally looks at her. Really looks.

JOHN
How do I stop?

SARAH
You start by staying. Just... stay.

FADE OUT.

THE END
"""


@pytest.fixture
def sample_script_path(tmp_path: Path, sample_script_text: str) -> Path:
    """Create a temporary script file."""
    script_path = tmp_path / "sample_script.txt"
    script_path.write_text(sample_script_text)
    return script_path


@pytest.fixture
def sample_beat_map_json() -> dict:
    """Sample beat map JSON data."""
    return {
        "title": "Sample Script",
        "scenes": [
            {
                "number": 1,
                "slug": "INT. APARTMENT - MORNING",
                "summary": "John receives devastating news",
                "function": "INCITE",
                "connector": "THEREFORE",
                "characters": ["JOHN"],
                "tension": 8,
            },
            {
                "number": 2,
                "slug": "EXT. STREET - DAY",
                "summary": "John wanders aimlessly, meets Sarah",
                "function": "COMPLICATE",
                "connector": "BUT",
                "characters": ["JOHN", "SARAH"],
                "tension": 4,
            },
            {
                "number": 3,
                "slug": "INT. COFFEE SHOP - LATER",
                "summary": "John opens up to Sarah about Maria",
                "function": "REVEAL",
                "connector": "THEREFORE",
                "characters": ["JOHN", "SARAH"],
                "tension": 6,
            },
            {
                "number": 4,
                "slug": "EXT. PARK - SUNSET",
                "summary": "Sarah helps John confront his feelings",
                "function": "RESOLVE",
                "connector": None,
                "characters": ["JOHN", "SARAH"],
                "tension": 5,
            },
        ],
        "characters": ["JOHN", "SARAH", "MARIA"],
    }


@pytest.fixture
def sample_beat_map_path(tmp_path: Path, sample_beat_map_json: dict) -> Path:
    """Create a temporary beat map JSON file."""
    import json

    beat_map_path = tmp_path / "sample_beatmap.json"
    beat_map_path.write_text(json.dumps(sample_beat_map_json, indent=2))
    return beat_map_path


@pytest.fixture
def mock_provider():
    """Get a mock LLM provider for testing."""
    from narratological.llm.providers import MockProvider

    return MockProvider()
