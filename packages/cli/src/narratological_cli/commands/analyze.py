"""CLI commands for analyzing scripts and stories."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from narratological_cli.llm_config import (
    BASE_URL_OPTION_HELP,
    MODEL_OPTION_HELP,
    PROVIDER_OPTION_HELP,
    get_provider,
)
from narratological_cli.parser import load_input, parse_script

app = typer.Typer(help="Analyze scripts and stories")
console = Console()


def _display_coverage_report(report) -> None:
    """Display a coverage report."""
    from narratological.models.report import RecommendationType

    # Recommendation color
    rec_colors = {
        RecommendationType.CONSIDER: "green",
        RecommendationType.PASS: "red",
        RecommendationType.DEVELOP: "yellow",
        RecommendationType.URGENT: "cyan",
    }
    rec_color = rec_colors.get(report.recommendation, "white")

    console.print(Panel(
        f"[bold]Recommendation:[/bold] [{rec_color}]{report.recommendation.value}[/{rec_color}]\n\n"
        f"[bold]Logline:[/bold] {report.logline}\n\n"
        f"[dim]{report.synopsis[:500]}{'...' if len(report.synopsis) > 500 else ''}[/dim]",
        title=f"Coverage: {report.title}",
    ))

    # Ratings table
    table = Table(title="Ratings")
    table.add_column("Category")
    table.add_column("Score", justify="center")
    table.add_column("Rating")

    ratings = [
        ("Premise", report.premise_rating),
        ("Structure", report.structure_rating),
        ("Character", report.character_rating),
        ("Dialogue", report.dialogue_rating),
        ("Originality", report.originality_rating),
        ("Marketability", report.marketability_rating),
    ]

    for name, score in ratings:
        color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
        rating_bar = "[green]" + "=" * score + "[/green]" + "[dim]" + "-" * (10 - score) + "[/dim]"
        table.add_row(name, f"[{color}]{score}/10[/{color}]", rating_bar)

    console.print(table)

    # Strengths and weaknesses
    if report.strengths:
        console.print("\n[bold green]Strengths[/bold green]")
        for s in report.strengths[:5]:
            console.print(f"  + {s}")

    if report.weaknesses:
        console.print("\n[bold red]Weaknesses[/bold red]")
        for w in report.weaknesses[:5]:
            console.print(f"  - {w}")

    if report.opportunities:
        console.print("\n[bold cyan]Opportunities[/bold cyan]")
        for o in report.opportunities[:3]:
            console.print(f"  * {o}")

    if report.comparables:
        console.print(f"\n[bold]Comparables:[/bold] {', '.join(report.comparables)}")


def _display_beat_map_report(report) -> None:
    """Display a beat map report."""
    avg_tension = f"{report.average_tension:.1f}/10" if report.average_tension is not None else "N/A"
    console.print(Panel(
        f"[bold]Total Scenes:[/bold] {report.total_scenes}\n"
        f"[bold]Average Tension:[/bold] {avg_tension}",
        title=f"Beat Map: {report.title}",
    ))

    # Function distribution
    if report.function_distribution:
        console.print("\n[bold]Function Distribution:[/bold]")
        for func, count in sorted(report.function_distribution.items(), key=lambda x: -x[1]):
            bar_len = min(count * 2, 20)
            console.print(f"  {func:12} {'=' * bar_len} {count}")

    # Connector distribution
    if report.connector_distribution:
        console.print("\n[bold]Connector Distribution:[/bold]")
        total = sum(report.connector_distribution.values())
        for conn, count in report.connector_distribution.items():
            pct = count / total * 100 if total else 0
            color = "green" if conn in ("BUT", "THEREFORE") else "red" if conn == "AND THEN" else "yellow"
            console.print(f"  [{color}]{conn:12}[/{color}] {count:3} ({pct:.0f}%)")

    # Beat entries (sample)
    if report.entries:
        console.print(f"\n[bold]Scenes ({len(report.entries)} total):[/bold]")
        table = Table()
        table.add_column("#", justify="right", width=4)
        table.add_column("Slug", width=25)
        table.add_column("Function", width=12)
        table.add_column("Connector", width=10)
        table.add_column("Tension", justify="center", width=8)

        for entry in report.entries[:10]:  # Show first 10
            tension_color = "green" if entry.tension >= 7 else "yellow" if entry.tension >= 4 else "dim"
            connector = entry.connector.value if entry.connector else "-"
            table.add_row(
                str(entry.scene_number),
                entry.slug[:25],
                entry.function.value,
                connector,
                f"[{tension_color}]{entry.tension}[/{tension_color}]",
            )

        console.print(table)
        if len(report.entries) > 10:
            console.print(f"  [dim]... and {len(report.entries) - 10} more scenes[/dim]")


@app.command("script")
def analyze_script(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file (txt, pdf, fdx)"),
    ],
    framework: Annotated[
        Optional[str],
        typer.Option("--framework", "-f", help="Primary framework/study to apply"),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory for reports"),
    ] = None,
    reports: Annotated[
        str,
        typer.Option("--reports", "-r", help="Reports to generate: all, coverage, beatmap, structural, character, diagnostic"),
    ] = "coverage",
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help=PROVIDER_OPTION_HELP),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help=MODEL_OPTION_HELP),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", help=BASE_URL_OPTION_HELP),
    ] = None,
) -> None:
    """Analyze a script using narratological algorithms.

    This command ingests a script and generates analysis reports
    based on the selected framework(s).
    """
    from narratological.generators.base import GeneratorConfig
    from narratological.generators.coverage import CoverageReportGenerator
    from narratological.generators.beat_map import BeatMapReportGenerator

    if not script_path.exists():
        console.print(f"[red]Script file not found: {script_path}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Analyzing:[/bold] {script_path.name}\n"
        f"[bold]Framework:[/bold] {framework or 'auto-detect'}\n"
        f"[bold]Reports:[/bold] {reports}",
        title="Script Analysis",
    ))

    # Parse the script
    try:
        script = parse_script(script_path)
        console.print(f"[dim]Parsed {len(script.scenes)} scenes, {len(script.characters)} characters[/dim]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Failed to parse script: {e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url, verbose=True)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Configure generators
    config = GeneratorConfig(
        primary_framework=framework,
        active_studies=[framework] if framework else [],
    )

    # Determine which reports to generate
    report_types = reports.lower().split(",")
    if "all" in report_types:
        report_types = ["coverage", "beatmap"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        results = {}

        for report_type in report_types:
            report_type = report_type.strip()

            if report_type == "coverage":
                task = progress.add_task("Generating coverage report...", total=None)
                try:
                    generator = CoverageReportGenerator(provider=llm, config=config)
                    report = generator.generate(script)
                    results["coverage"] = report
                    progress.update(task, description="[green]Coverage report complete[/green]")
                except Exception as e:
                    progress.update(task, description=f"[red]Coverage failed: {e}[/red]")

            elif report_type == "beatmap":
                task = progress.add_task("Generating beat map...", total=None)
                try:
                    generator = BeatMapReportGenerator(provider=llm, config=config)
                    report = generator.generate(script)
                    results["beatmap"] = report
                    progress.update(task, description="[green]Beat map complete[/green]")
                except Exception as e:
                    progress.update(task, description=f"[red]Beat map failed: {e}[/red]")

            else:
                console.print(f"[yellow]Unknown report type: {report_type}[/yellow]")

    # Display results
    if "coverage" in results:
        console.print()
        _display_coverage_report(results["coverage"])

    if "beatmap" in results:
        console.print()
        _display_beat_map_report(results["beatmap"])

    # Save outputs if requested
    if output:
        output.mkdir(parents=True, exist_ok=True)
        for name, report in results.items():
            report_path = output / f"{script_path.stem}_{name}.json"
            report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
            console.print(f"[dim]Saved: {report_path}[/dim]")


@app.command("scene")
def analyze_scene(
    scene_text: Annotated[
        str,
        typer.Argument(help="Scene text to analyze (or path to file)"),
    ],
    framework: Annotated[
        Optional[str],
        typer.Option("--framework", "-f", help="Framework to apply"),
    ] = None,
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help=PROVIDER_OPTION_HELP),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help=MODEL_OPTION_HELP),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", help=BASE_URL_OPTION_HELP),
    ] = None,
) -> None:
    """Analyze a single scene using narratological algorithms.

    Provides quick analysis of beat function, tension, and structure.
    """
    from pydantic import BaseModel, Field

    # Check if it's a file path
    scene_path = Path(scene_text)
    if scene_path.exists():
        text = scene_path.read_text(encoding="utf-8")
    else:
        text = scene_text

    console.print(Panel(
        f"[dim]{text[:500]}{'...' if len(text) > 500 else ''}[/dim]",
        title="Scene Text",
    ))

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Define response model for scene analysis
    class SceneAnalysis(BaseModel):
        """Scene analysis response."""
        function: str = Field(description="Primary beat function (SETUP, INCITE, ESCALATE, REVEAL, CRISIS, CLIMAX, RESOLVE, etc.)")
        secondary_function: str | None = Field(default=None, description="Secondary function if applicable")
        tension_level: int = Field(ge=1, le=10, description="Tension level 1-10")
        connector_to_next: str | None = Field(default=None, description="How this connects to next scene (BUT, THEREFORE, AND THEN, MEANWHILE)")
        key_characters: list[str] = Field(default_factory=list, description="Characters present/mentioned")
        summary: str = Field(description="One-sentence summary of what happens")
        notes: str | None = Field(default=None, description="Additional observations")

    # Analyze with LLM
    system_prompt = """You are a professional script analyst using narratological frameworks.
Analyze the given scene text and provide structured analysis including:
- Beat function (what narrative purpose it serves)
- Tension level (1-10 scale)
- Connection type (how it would connect to the next scene)
- Key characters and a brief summary"""

    prompt = f"""Analyze this scene:

{text}

Provide analysis as a JSON object."""

    try:
        result = llm.complete_structured(prompt, SceneAnalysis, system=system_prompt)

        # Display results
        console.print("\n[bold]Scene Analysis[/bold]")

        func_color = {
            "SETUP": "cyan",
            "INCITE": "yellow",
            "ESCALATE": "orange3",
            "REVEAL": "blue",
            "CRISIS": "red",
            "CLIMAX": "bold red",
            "RESOLVE": "green",
        }.get(result.function.upper(), "white")

        console.print(f"  [bold]Function:[/bold] [{func_color}]{result.function}[/{func_color}]")
        if result.secondary_function:
            console.print(f"  [bold]Secondary:[/bold] {result.secondary_function}")

        tension_color = "green" if result.tension_level >= 7 else "yellow" if result.tension_level >= 4 else "dim"
        console.print(f"  [bold]Tension:[/bold] [{tension_color}]{result.tension_level}/10[/{tension_color}]")

        if result.connector_to_next:
            conn_color = "green" if result.connector_to_next.upper() in ("BUT", "THEREFORE") else "red"
            console.print(f"  [bold]Connector:[/bold] [{conn_color}]{result.connector_to_next}[/{conn_color}]")

        if result.key_characters:
            console.print(f"  [bold]Characters:[/bold] {', '.join(result.key_characters)}")

        console.print(f"\n  [bold]Summary:[/bold] {result.summary}")

        if result.notes:
            console.print(f"\n  [dim]Notes: {result.notes}[/dim]")

    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("compare")
def compare_scripts(
    script_a: Annotated[Path, typer.Argument(help="First script")],
    script_b: Annotated[Path, typer.Argument(help="Second script")],
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help=PROVIDER_OPTION_HELP),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help=MODEL_OPTION_HELP),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", help=BASE_URL_OPTION_HELP),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output path for comparison report"),
    ] = None,
) -> None:
    """Compare two scripts structurally.

    Analyzes structural similarities and differences between scripts.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner

    if not script_a.exists() or not script_b.exists():
        console.print("[red]One or both script files not found[/red]")
        raise typer.Exit(1)

    console.print(f"Comparing: [cyan]{script_a.name}[/cyan] vs [cyan]{script_b.name}[/cyan]")

    # Parse both scripts
    try:
        script_1 = parse_script(script_a)
        script_2 = parse_script(script_b)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Failed to parse scripts: {e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Run diagnostics on both
    runner = create_diagnostic_runner(provider=llm)

    console.print("\n[bold]Analyzing scripts...[/bold]")

    _, context_a = load_input(script_a)
    _, context_b = load_input(script_b)

    report_a = runner.run_all(context_a, include_framework=False)
    report_b = runner.run_all(context_b, include_framework=False)

    # Comparison table
    table = Table(title="Structural Comparison")
    table.add_column("Metric")
    table.add_column(script_a.stem, justify="right")
    table.add_column(script_b.stem, justify="right")
    table.add_column("Difference", justify="right")

    comparisons = [
        ("Scenes", len(script_1.scenes), len(script_2.scenes)),
        ("Characters", len(script_1.characters), len(script_2.characters)),
        ("Causal Binding", report_a.causal_binding_ratio, report_b.causal_binding_ratio),
        ("Reorderability", report_a.reorderability_score, report_b.reorderability_score),
        ("Necessity", report_a.necessity_score, report_b.necessity_score),
    ]

    for name, val_a, val_b in comparisons:
        if isinstance(val_a, float):
            diff = val_b - val_a
            diff_str = f"{diff:+.1%}" if abs(diff) > 0.01 else "~"
            table.add_row(name, f"{val_a:.1%}", f"{val_b:.1%}", diff_str)
        else:
            diff = val_b - val_a
            diff_str = f"{diff:+d}" if diff != 0 else "="
            table.add_row(name, str(val_a), str(val_b), diff_str)

    console.print(table)

    # Health comparison
    console.print(f"\n[bold]Overall Health:[/bold]")
    console.print(f"  {script_a.stem}: {report_a.overall_health}")
    console.print(f"  {script_b.stem}: {report_b.overall_health}")

    # Save output if requested
    if output:
        comparison = {
            "script_a": {"title": script_1.title, "metrics": report_a.model_dump()},
            "script_b": {"title": script_2.title, "metrics": report_b.model_dump()},
        }
        output.write_text(json.dumps(comparison, indent=2, default=str), encoding="utf-8")
        console.print(f"\n[dim]Comparison saved to: {output}[/dim]")


@app.command("batch")
def batch_analyze(
    directory: Annotated[
        Path,
        typer.Argument(help="Directory containing scripts"),
    ],
    pattern: Annotated[
        str,
        typer.Option("--pattern", "-p", help="File pattern to match"),
    ] = "*.txt",
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory"),
    ] = None,
    provider: Annotated[
        str,
        typer.Option("--provider", help=PROVIDER_OPTION_HELP),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help=MODEL_OPTION_HELP),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", help=BASE_URL_OPTION_HELP),
    ] = None,
) -> None:
    """Batch analyze multiple scripts.

    Process all matching scripts in a directory.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner

    if not directory.exists():
        console.print(f"[red]Directory not found: {directory}[/red]")
        raise typer.Exit(1)

    scripts = list(directory.glob(pattern))
    console.print(f"Found [cyan]{len(scripts)}[/cyan] scripts matching '{pattern}'")

    if not scripts:
        console.print("[yellow]No scripts to process[/yellow]")
        return

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    runner = create_diagnostic_runner(provider=llm)

    # Process each script
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for script_path in scripts:
            task = progress.add_task(f"Analyzing {script_path.name}...", total=None)

            try:
                _, context = load_input(script_path)
                report = runner.run_all(context, include_framework=False)
                results.append({
                    "script": script_path.name,
                    "health": report.overall_health,
                    "causal_binding": report.causal_binding_ratio,
                    "issues": report.critical_count + report.warning_count,
                })
                progress.update(task, description=f"[green]{script_path.name}: {report.overall_health}[/green]")
            except Exception as e:
                results.append({
                    "script": script_path.name,
                    "health": "Error",
                    "causal_binding": 0,
                    "issues": -1,
                    "error": str(e),
                })
                progress.update(task, description=f"[red]{script_path.name}: Error[/red]")

    # Summary table
    console.print()
    table = Table(title=f"Batch Analysis Results ({len(results)} scripts)")
    table.add_column("Script")
    table.add_column("Health")
    table.add_column("Causal Binding", justify="right")
    table.add_column("Issues", justify="right")

    for r in results:
        health_color = {"Excellent": "green", "Good": "green", "Fair": "yellow", "Poor": "red", "Critical": "red", "Error": "red"}.get(r["health"], "white")
        cb = f"{r['causal_binding']:.0%}" if r["causal_binding"] else "-"
        issues = str(r["issues"]) if r["issues"] >= 0 else "N/A"
        table.add_row(r["script"], f"[{health_color}]{r['health']}[/{health_color}]", cb, issues)

    console.print(table)

    # Save output if requested
    if output:
        output.mkdir(parents=True, exist_ok=True)
        summary_path = output / "batch_summary.json"
        summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        console.print(f"\n[dim]Summary saved to: {summary_path}[/dim]")
