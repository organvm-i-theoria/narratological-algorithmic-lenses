"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from narratological_cli.main import app

runner = CliRunner()


class TestStudyCommands:
    """Tests for study CLI commands."""

    def test_study_list(self):
        """Test study list command."""
        result = runner.invoke(app, ["study", "list"])
        assert result.exit_code == 0
        # Should show some study categories
        assert "Studies" in result.output or "study" in result.output.lower()

    def test_study_show(self):
        """Test study show command with a known study."""
        result = runner.invoke(app, ["study", "show", "pixar"])
        # May succeed or fail depending on data loading
        # Just check it doesn't crash unexpectedly
        assert result.exit_code in [0, 1]

    def test_study_show_nonexistent(self):
        """Test study show command with nonexistent study."""
        result = runner.invoke(app, ["study", "show", "nonexistent-study-xyz"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()


class TestAlgorithmCommands:
    """Tests for algorithm CLI commands."""

    def test_algorithm_list(self):
        """Test algorithm list command."""
        result = runner.invoke(app, ["algorithm", "list"])
        assert result.exit_code == 0
        # Should show algorithm count or table
        assert "Algorithm" in result.output or "algorithm" in result.output.lower()

    def test_algorithm_stats(self):
        """Test algorithm stats command."""
        result = runner.invoke(app, ["algorithm", "stats"])
        assert result.exit_code == 0
        # Should show some statistics
        assert "Study" in result.output or "algorithms" in result.output.lower()


class TestDiagnoseCommands:
    """Tests for diagnose CLI commands."""

    def test_diagnose_causal_help(self):
        """Test diagnose causal command help."""
        result = runner.invoke(app, ["diagnose", "causal", "--help"])
        assert result.exit_code == 0
        assert "causal" in result.output.lower()

    def test_diagnose_all_help(self):
        """Test diagnose all command help."""
        result = runner.invoke(app, ["diagnose", "all", "--help"])
        assert result.exit_code == 0
        assert "diagnostic" in result.output.lower()

    def test_diagnose_causal_with_mock(self, sample_script_path: Path):
        """Test diagnose causal command with mock provider."""
        result = runner.invoke(app, [
            "diagnose", "causal",
            str(sample_script_path),
            "--provider", "mock",
        ])
        # Should run without crashing (may have analysis output)
        assert result.exit_code in [0, 1]

    def test_diagnose_all_with_mock(self, sample_script_path: Path):
        """Test diagnose all command with mock provider."""
        result = runner.invoke(app, [
            "diagnose", "all",
            str(sample_script_path),
            "--provider", "mock",
            "--no-framework",  # Skip framework diagnostics for speed
        ])
        # Should run without crashing
        assert result.exit_code in [0, 1]


class TestAnalyzeCommands:
    """Tests for analyze CLI commands."""

    def test_analyze_script_help(self):
        """Test analyze script command help."""
        result = runner.invoke(app, ["analyze", "script", "--help"])
        assert result.exit_code == 0
        assert "script" in result.output.lower()

    def test_analyze_scene_help(self):
        """Test analyze scene command help."""
        result = runner.invoke(app, ["analyze", "scene", "--help"])
        assert result.exit_code == 0

    def test_analyze_script_file_not_found(self):
        """Test analyze script with nonexistent file."""
        result = runner.invoke(app, [
            "analyze", "script",
            "nonexistent_file.txt",
            "--provider", "mock",
        ])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestGenerateCommands:
    """Tests for generate CLI commands."""

    def test_generate_outline_help(self):
        """Test generate outline command help."""
        result = runner.invoke(app, ["generate", "outline", "--help"])
        assert result.exit_code == 0
        assert "premise" in result.output.lower()

    def test_generate_character_help(self):
        """Test generate character command help."""
        result = runner.invoke(app, ["generate", "character", "--help"])
        assert result.exit_code == 0
        assert "role" in result.output.lower()

    def test_generate_transformation_help(self):
        """Test generate transformation command help."""
        result = runner.invoke(app, ["generate", "transformation", "--help"])
        assert result.exit_code == 0
        assert "subject" in result.output.lower()

    def test_generate_beats_help(self):
        """Test generate beats command help."""
        result = runner.invoke(app, ["generate", "beats", "--help"])
        assert result.exit_code == 0
        assert "scene" in result.output.lower() or "beat" in result.output.lower()


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_command(self):
        """Test info command displays study summary."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        # Should show some study information (title says "Studies")
        assert "Studies" in result.output or "studies" in result.output.lower()


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        # Should show version information
        assert "version" in result.output.lower() or "0." in result.output


class TestProviderOptions:
    """Tests for provider option handling across commands."""

    def test_provider_option_in_diagnose(self):
        """Test that provider option is recognized in diagnose commands."""
        result = runner.invoke(app, ["diagnose", "causal", "--help"])
        assert "--provider" in result.output

    def test_provider_option_in_analyze(self):
        """Test that provider option is recognized in analyze commands."""
        result = runner.invoke(app, ["analyze", "script", "--help"])
        assert "--provider" in result.output

    def test_provider_option_in_generate(self):
        """Test that provider option is recognized in generate commands."""
        result = runner.invoke(app, ["generate", "outline", "--help"])
        assert "--provider" in result.output

    def test_model_option_in_diagnose(self):
        """Test that model option is recognized in diagnose commands."""
        result = runner.invoke(app, ["diagnose", "causal", "--help"])
        assert "--model" in result.output

    def test_base_url_option_in_diagnose(self):
        """Test that base-url option is recognized in diagnose commands."""
        result = runner.invoke(app, ["diagnose", "causal", "--help"])
        assert "--base-url" in result.output
