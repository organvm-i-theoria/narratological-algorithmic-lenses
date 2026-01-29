"""CLI commands for running diagnostic tests."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from narratological_cli.llm_config import (
    BASE_URL_OPTION_HELP,
    MODEL_OPTION_HELP,
    PROVIDER_OPTION_HELP,
    get_provider,
)
from narratological_cli.parser import load_input

app = typer.Typer(help="Run diagnostic tests on narratives")
console = Console()


def _format_score(score: float, name: str, higher_is_better: bool = True) -> str:
    """Format a score with color based on thresholds."""
    if higher_is_better:
        if score >= 0.80:
            color = "green"
        elif score >= 0.60:
            color = "yellow"
        else:
            color = "red"
    else:
        # Lower is better (e.g., reorderability)
        if score <= 0.15:
            color = "green"
        elif score <= 0.30:
            color = "yellow"
        else:
            color = "red"

    return f"[{color}]{score:.1%}[/{color}]"


def _display_diagnostic_result(
    title: str,
    score: float,
    issues: list,
    higher_is_better: bool = True,
) -> None:
    """Display a single diagnostic result."""
    score_str = _format_score(score, title, higher_is_better)
    console.print(f"\n[bold]{title}:[/bold] {score_str}")

    if issues:
        for issue in issues[:5]:  # Show top 5 issues
            severity_color = {
                "CRITICAL": "red",
                "WARNING": "yellow",
                "SUGGESTION": "cyan",
                "INFO": "dim",
            }.get(issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity), "white")

            console.print(f"  [{severity_color}]{issue.severity.value if hasattr(issue.severity, 'value') else issue.severity}[/{severity_color}]: {issue.description}")
            if issue.recommendation:
                console.print(f"    [dim]Recommendation: {issue.recommendation}[/dim]")


@app.command("causal")
def diagnose_causal_binding(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file or beat map JSON"),
    ],
    target: Annotated[
        float,
        typer.Option("--target", "-t", help="Target causal binding ratio"),
    ] = 0.80,
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
    """Test causal binding (BUT/THEREFORE vs AND THEN).

    Strong narratives have >80% causal connectors (BUT/THEREFORE).
    Weak episodic structures rely on AND THEN connections.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner
    from narratological.diagnostics.models import DiagnosticThresholds

    console.print(Panel(
        f"[bold]Target:[/bold] {target:.0%} causal binding\n"
        "[bold]Method:[/bold] BUT/THEREFORE vs AND THEN analysis",
        title="Causal Binding Diagnostic",
    ))

    # Load input
    try:
        script, context = load_input(script_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Configure thresholds
    thresholds = DiagnosticThresholds(causal_binding_good=target)

    # Run diagnostic
    runner = create_diagnostic_runner(provider=llm, thresholds=thresholds)
    score, issues = runner.run_causal(context)

    _display_diagnostic_result("Causal Binding", score, issues, higher_is_better=True)

    console.print("\n[bold]Interpretation:[/bold]")
    console.print("  - [green]BUT[/green] - Contradiction/obstacle that changes direction")
    console.print("  - [green]THEREFORE[/green] - Direct consequence of previous action")
    console.print("  - [red]AND THEN[/red] - Sequential but not causally connected")
    console.print("  - [yellow]MEANWHILE[/yellow] - Parallel action (valid for subplots)")


@app.command("reorder")
def diagnose_reorderability(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file or beat map JSON"),
    ],
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
    """Test scene reorderability.

    Identifies scenes that could be reordered without affecting
    the narrative - a sign of weak causal structure.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner

    console.print(Panel(
        "[bold]Test:[/bold] Can scenes be reordered without breaking the narrative?",
        title="Reorderability Diagnostic",
    ))

    # Load input
    try:
        script, context = load_input(script_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Run diagnostic
    runner = create_diagnostic_runner(provider=llm)
    score, issues = runner.run_reorderability(context)

    _display_diagnostic_result("Reorderability", score, issues, higher_is_better=False)

    console.print("\n[bold]Interpretation:[/bold]")
    console.print("Strong narratives have scenes that MUST be in order.")
    console.print("If scenes can be shuffled, causal binding is weak.")
    console.print("  - [green]<15%[/green] - Excellent structure")
    console.print("  - [yellow]15-30%[/yellow] - Some reorderable scenes")
    console.print("  - [red]>30%[/red] - Weak causal structure")


@app.command("necessity")
def diagnose_necessity(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file or beat map JSON"),
    ],
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
    """Test scene necessity.

    Identifies scenes that could be removed without affecting
    the narrative - violates information economy.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner

    console.print(Panel(
        "[bold]Test:[/bold] Can any scene be removed without loss?",
        title="Necessity Diagnostic",
    ))

    # Load input
    try:
        script, context = load_input(script_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Run diagnostic
    runner = create_diagnostic_runner(provider=llm)
    score, issues = runner.run_necessity(context)

    _display_diagnostic_result("Necessity", score, issues, higher_is_better=True)

    console.print("\n[bold]Interpretation:[/bold]")
    console.print("Every scene should advance plot, character, or theme.")
    console.print("Scenes serving only one function should serve it irreplaceably.")
    console.print("  - [green]>85%[/green] - Excellent (all scenes necessary)")
    console.print("  - [yellow]70-85%[/yellow] - Some scenes could be cut")
    console.print("  - [red]<70%[/red] - Significant redundancy")


@app.command("framework")
def diagnose_with_framework(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file or beat map JSON"),
    ],
    study_id: Annotated[
        str,
        typer.Argument(help="Study/framework to use for diagnosis"),
    ],
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
    """Run diagnostic questions from a specific study.

    Uses the diagnostic questions defined in a narratological study
    to evaluate the script.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner
    from narratological.loader import load_compendium, load_study

    try:
        study = load_study(study_id)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Framework:[/bold] {study.creator} - {study.work}\n"
        f"[bold]Diagnostic Questions:[/bold] {len(study.diagnostic_questions)}",
        title=f"Framework Diagnostic: {study_id}",
    ))

    # Display available diagnostic questions
    if study.diagnostic_questions:
        table = Table(title="Diagnostic Questions")
        table.add_column("ID", style="cyan")
        table.add_column("Question")
        table.add_column("Valid If")

        for q in study.diagnostic_questions[:10]:  # Show first 10
            table.add_row(
                q.id,
                q.question[:60] + "..." if len(q.question) > 60 else q.question,
                q.valid_if[:50] + "..." if len(q.valid_if) > 50 else q.valid_if,
            )

        console.print(table)

    # Load input
    try:
        script, context = load_input(script_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Set active study for the context
    context.active_studies = [study_id]

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Run framework diagnostic
    compendium = load_compendium()
    runner = create_diagnostic_runner(provider=llm, compendium=compendium)
    issues = runner.run_framework(context, study_ids=[study_id])

    console.print(f"\n[bold]Framework Analysis Results:[/bold]")
    if issues:
        for issue in issues:
            severity_color = {
                "CRITICAL": "red",
                "WARNING": "yellow",
                "SUGGESTION": "cyan",
                "INFO": "dim",
            }.get(issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity), "white")

            console.print(f"  [{severity_color}]{issue.severity.value if hasattr(issue.severity, 'value') else issue.severity}[/{severity_color}]: {issue.description}")
            if issue.recommendation:
                console.print(f"    [dim]Recommendation: {issue.recommendation}[/dim]")
    else:
        console.print("  [green]No issues found.[/green]")


@app.command("all")
def diagnose_all(
    script_path: Annotated[
        Path,
        typer.Argument(help="Path to script file or beat map JSON"),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output path for diagnostic report JSON"),
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
    include_framework: Annotated[
        bool,
        typer.Option("--include-framework/--no-framework", help="Include framework diagnostics"),
    ] = True,
) -> None:
    """Run full diagnostic battery.

    Runs all diagnostic tests and generates a comprehensive
    diagnostic report with prioritized recommendations.
    """
    from narratological.diagnostics.runner import create_diagnostic_runner
    from narratological.loader import load_compendium

    console.print(Panel(
        "[bold]Tests:[/bold] Causal Binding, Reorderability, Necessity, Information Economy",
        title="Full Diagnostic Battery",
    ))

    # Load input
    try:
        script, context = load_input(script_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Run full diagnostic battery
    compendium = load_compendium() if include_framework else None
    runner = create_diagnostic_runner(provider=llm, compendium=compendium)

    console.print("\n[bold]Running diagnostics...[/bold]")
    report = runner.run_all(context, include_framework=include_framework)

    # Display results
    console.print(f"\n[bold]Script:[/bold] {report.title}")
    console.print(f"[bold]Overall Health:[/bold] {report.overall_health}")

    # Metrics table
    table = Table(title="Diagnostic Metrics")
    table.add_column("Metric")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    metrics = [
        ("Causal Binding", report.causal_binding_ratio, True),
        ("Reorderability", report.reorderability_score, False),
        ("Necessity", report.necessity_score, True),
        ("Information Economy", report.information_economy_score, True),
    ]

    for name, score, higher_is_better in metrics:
        score_str = _format_score(score, name, higher_is_better)
        if higher_is_better:
            status = "Good" if score >= 0.80 else "Warning" if score >= 0.60 else "Critical"
        else:
            status = "Good" if score <= 0.15 else "Warning" if score <= 0.30 else "Critical"
        table.add_row(name, score_str, status)

    console.print(table)

    # Issue summary
    console.print(f"\n[bold]Issues Found:[/bold]")
    console.print(f"  [red]Critical:[/red] {report.critical_count}")
    console.print(f"  [yellow]Warning:[/yellow] {report.warning_count}")

    # Priority fixes
    if report.priority_fixes:
        console.print(f"\n[bold]Priority Fixes:[/bold]")
        for i, fix in enumerate(report.priority_fixes[:5], 1):
            console.print(f"  {i}. {fix}")

    # Save to file if requested
    if output:
        output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"\n[dim]Report saved to: {output}[/dim]")
