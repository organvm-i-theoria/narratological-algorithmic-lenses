"""Tests for the script parser module."""

from pathlib import Path

import pytest

from narratological_cli.parser import (
    load_input,
    parse_beat_map_json,
    parse_script,
    script_to_diagnostic_context,
)


class TestParseScript:
    """Tests for parse_script function."""

    def test_parse_script_basic(self, sample_script_path: Path):
        """Test basic script parsing."""
        script = parse_script(sample_script_path)

        assert script.title == "Sample Script"
        assert len(script.scenes) > 0
        assert len(script.characters) > 0

    def test_parse_script_detects_sluglines(self, sample_script_path: Path):
        """Test that slugline-based scene detection works."""
        script = parse_script(sample_script_path)

        # Should detect INT. and EXT. scenes
        assert len(script.scenes) == 4
        assert "INT. APARTMENT" in script.scenes[0].slug
        assert "EXT. STREET" in script.scenes[1].slug
        assert "INT. COFFEE SHOP" in script.scenes[2].slug
        assert "EXT. PARK" in script.scenes[3].slug

    def test_parse_script_extracts_characters(self, sample_script_path: Path):
        """Test that characters are extracted from dialogue cues."""
        script = parse_script(sample_script_path)

        character_names = [c.name for c in script.characters]
        assert "JOHN" in character_names
        assert "SARAH" in character_names

    def test_parse_script_with_custom_title(self, sample_script_path: Path):
        """Test parsing with a custom title."""
        script = parse_script(sample_script_path, title="My Custom Title")
        assert script.title == "My Custom Title"

    def test_parse_script_file_not_found(self, tmp_path: Path):
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_script(tmp_path / "nonexistent.txt")

    def test_parse_script_estimates_pages(self, sample_script_path: Path):
        """Test that page count is estimated."""
        script = parse_script(sample_script_path)
        assert script.page_count is not None
        assert script.page_count >= 1


class TestParseBeatMapJson:
    """Tests for parse_beat_map_json function."""

    def test_parse_beat_map_basic(self, sample_beat_map_path: Path):
        """Test basic beat map parsing."""
        context = parse_beat_map_json(sample_beat_map_path)

        assert context.title == "Sample Script"
        assert len(context.scenes) == 4
        assert len(context.characters) == 3

    def test_parse_beat_map_creates_transitions(self, sample_beat_map_path: Path):
        """Test that scene transitions are created from connectors."""
        context = parse_beat_map_json(sample_beat_map_path)

        # Should have 3 transitions (between 4 scenes)
        assert len(context.transitions) == 3

        # First transition should be THEREFORE (causal)
        assert context.transitions[0].from_scene == 1
        assert context.transitions[0].to_scene == 2
        assert context.transitions[0].is_causal is True

    def test_parse_beat_map_detects_availability(self, sample_beat_map_path: Path):
        """Test that beat map availability is detected."""
        context = parse_beat_map_json(sample_beat_map_path)
        assert context.beat_map_available is True

    def test_parse_beat_map_file_not_found(self, tmp_path: Path):
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_beat_map_json(tmp_path / "nonexistent.json")

    def test_parse_beat_map_invalid_json(self, tmp_path: Path):
        """Test error handling for invalid JSON."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("not valid json {{{")

        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_beat_map_json(bad_json)


class TestScriptToDiagnosticContext:
    """Tests for script_to_diagnostic_context function."""

    def test_converts_script_to_context(self, sample_script_path: Path):
        """Test conversion of Script to DiagnosticContext."""
        script = parse_script(sample_script_path)
        context = script_to_diagnostic_context(script)

        assert context.title == script.title
        assert len(context.scenes) == len(script.scenes)


class TestLoadInput:
    """Tests for load_input function."""

    def test_load_input_script(self, sample_script_path: Path):
        """Test loading a script file."""
        script, context = load_input(sample_script_path)

        assert script is not None
        assert context is not None
        assert script.title == context.title

    def test_load_input_beat_map(self, sample_beat_map_path: Path):
        """Test loading a beat map JSON file."""
        script, context = load_input(sample_beat_map_path)

        # Script should be None for JSON input
        assert script is None
        assert context is not None
        assert context.title == "Sample Script"

    def test_load_input_file_not_found(self, tmp_path: Path):
        """Test error handling for missing files."""
        with pytest.raises(FileNotFoundError):
            load_input(tmp_path / "nonexistent.txt")
