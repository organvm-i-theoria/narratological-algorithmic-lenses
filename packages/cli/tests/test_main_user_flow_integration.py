"""Integration tests for the CLI's primary user flow."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from narratological_cli.main import app

runner = CliRunner()


def test_cli_main_user_flow_explores_and_analyzes_script(
    sample_script_path: Path,
    tmp_path: Path,
) -> None:
    """A user can explore lenses, inspect an algorithm, and generate analysis output."""
    studies = runner.invoke(app, ["study", "list"])
    assert studies.exit_code == 0
    assert "pixar" in studies.output
    assert "Narratological Studies" in studies.output

    study_detail = runner.invoke(app, ["study", "show", "pixar", "--section", "algorithms"])
    assert study_detail.exit_code == 0
    assert "Pixar" in study_detail.output
    assert "engineer_empathy" in study_detail.output

    algorithm_detail = runner.invoke(app, ["algorithm", "show", "pixar.engineer_empathy"])
    assert algorithm_detail.exit_code == 0
    assert "engineer_empathy" in algorithm_detail.output
    assert "empathy" in algorithm_detail.output.lower()

    diagnostic_output = tmp_path / "diagnostic-report.json"
    diagnostics = runner.invoke(
        app,
        [
            "diagnose",
            "all",
            str(sample_script_path),
            "--provider",
            "mock",
            "--no-framework",
            "--output",
            str(diagnostic_output),
        ],
    )
    assert diagnostics.exit_code == 0
    assert "Full Diagnostic Battery" in diagnostics.output
    assert diagnostic_output.exists()

    diagnostic_payload = json.loads(diagnostic_output.read_text(encoding="utf-8"))
    assert diagnostic_payload["title"] == "Sample Script"
    assert diagnostic_payload["frameworks_applied"] == [
        "causal_binding",
        "reorderability",
        "necessity",
        "information_economy",
    ]
    assert 0 <= diagnostic_payload["causal_binding_ratio"] <= 1

    analysis_dir = tmp_path / "analysis"
    analysis = runner.invoke(
        app,
        [
            "analyze",
            "script",
            str(sample_script_path),
            "--framework",
            "pixar",
            "--reports",
            "coverage",
            "--provider",
            "mock",
            "--output",
            str(analysis_dir),
        ],
    )
    assert analysis.exit_code == 0
    assert "Script Analysis" in analysis.output

    coverage_output = analysis_dir / f"{sample_script_path.stem}_coverage.json"
    assert coverage_output.exists()
    coverage_payload = json.loads(coverage_output.read_text(encoding="utf-8"))
    assert coverage_payload["title"] == "Sample Script"
    assert coverage_payload["recommendation"] == "DEVELOP"
    assert 1 <= coverage_payload["premise_rating"] <= 10
