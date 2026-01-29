"""CLI commands for exploring and executing algorithms."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

app = typer.Typer(help="Explore and execute narratological algorithms")
console = Console()


@app.command("list")
def list_algorithms(
    study: Annotated[
        Optional[str],
        typer.Option("--study", "-s", help="Filter by study ID"),
    ] = None,
    search: Annotated[
        Optional[str],
        typer.Option("--search", "-q", help="Search algorithms by name or purpose"),
    ] = None,
) -> None:
    """List all available algorithms.

    Shows algorithms across all 14 studies with their names, purposes,
    and input/output counts.
    """
    from narratological.algorithms import AlgorithmRegistry

    registry = AlgorithmRegistry()

    if search:
        algorithms = registry.search(search)
        if not algorithms:
            console.print(f"[yellow]No algorithms found matching '{search}'[/yellow]")
            return
    elif study:
        algorithms = registry.list_by_study(study)
        if not algorithms:
            console.print(f"[yellow]No algorithms found for study '{study}'[/yellow]")
            console.print(f"Available studies: {', '.join(registry.list_studies())}")
            return
    else:
        algorithms = registry.all()

    # Group by study for better display
    by_study: dict[str, list] = {}
    for algo in algorithms:
        by_study.setdefault(algo.study_id, []).append(algo)

    total = len(algorithms)
    table = Table(
        title=f"Narratological Algorithms ({total} total)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Study", style="cyan", width=15)
    table.add_column("Algorithm", style="green")
    table.add_column("Purpose", width=50)
    table.add_column("In/Out", justify="center")

    for study_id in sorted(by_study.keys()):
        for i, algo in enumerate(by_study[study_id]):
            # Only show study name on first row
            study_display = study_id if i == 0 else ""

            # Truncate purpose
            purpose = algo.purpose
            if len(purpose) > 50:
                purpose = purpose[:47] + "..."

            io_count = f"{len(algo.inputs)}/{len(algo.outputs)}"

            table.add_row(study_display, algo.name, purpose, io_count)

        # Add separator between studies
        if study_id != sorted(by_study.keys())[-1]:
            table.add_row("", "", "", "")

    console.print(table)
    console.print(f"\n[dim]Use 'narratological algorithm show <study>.<name>' for details[/dim]")


@app.command("show")
def show_algorithm(
    algorithm: Annotated[
        str,
        typer.Argument(help="Algorithm in format 'study.name' (e.g., 'pixar.engineer_empathy')"),
    ],
) -> None:
    """Show detailed information about an algorithm.

    Displays the algorithm's purpose, pseudocode, inputs, and outputs.
    """
    from narratological.algorithms import AlgorithmRegistry

    registry = AlgorithmRegistry()

    # Parse algorithm reference
    if "." in algorithm:
        parts = algorithm.split(".", 1)
        study_id, algo_name = parts[0], parts[1]
    else:
        console.print("[red]Algorithm must be in format 'study.name' (e.g., 'pixar.engineer_empathy')[/red]")
        raise typer.Exit(1)

    try:
        algo = registry.get(study_id, algo_name)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Display algorithm details
    console.print()
    console.print(Panel(
        f"[bold]{algo.name}[/bold]\n"
        f"[dim]From: {algo.study_creator} ({algo.study_id})[/dim]",
        title="Algorithm",
        border_style="cyan",
    ))

    console.print("\n[bold]Purpose[/bold]")
    console.print(algo.purpose)

    console.print("\n[bold]Pseudocode[/bold]")
    # Format pseudocode for better readability
    pseudocode = algo.pseudocode.replace("; ", ";\n")
    syntax = Syntax(pseudocode, "sql", theme="monokai", word_wrap=True)
    console.print(syntax)

    if algo.inputs:
        console.print("\n[bold]Inputs[/bold]")
        for inp in algo.inputs:
            console.print(f"  - {inp}")

    if algo.outputs:
        console.print("\n[bold]Outputs[/bold]")
        for out in algo.outputs:
            console.print(f"  - {out}")

    console.print()


@app.command("run")
def run_algorithm(
    algorithm: Annotated[
        str,
        typer.Argument(help="Algorithm in format 'study.name'"),
    ],
    input_file: Annotated[
        Path,
        typer.Option("--input", "-i", help="Input file to analyze"),
    ],
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Execution mode: analyze, generate, validate"),
    ] = "analyze",
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="LLM provider: ollama, anthropic, openai, mock"),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option("--model", help="Model name override"),
    ] = None,
    base_url: Annotated[
        Optional[str],
        typer.Option("--base-url", help="Custom API endpoint for OpenAI-compatible providers"),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file for results (JSON)"),
    ] = None,
) -> None:
    """Execute an algorithm on input text.

    Requires an LLM provider API key to be set (ANTHROPIC_API_KEY or OPENAI_API_KEY).

    Example:
        narratological algorithm run pixar.engineer_empathy --input story.txt
    """
    from narratological.algorithms import AlgorithmRegistry, create_executor

    # Read input file
    if not input_file.exists():
        console.print(f"[red]Input file not found: {input_file}[/red]")
        raise typer.Exit(1)

    text = input_file.read_text(encoding="utf-8")

    # Parse algorithm reference
    if "." not in algorithm:
        console.print("[red]Algorithm must be in format 'study.name'[/red]")
        raise typer.Exit(1)

    study_id, algo_name = algorithm.split(".", 1)

    # Get algorithm
    registry = AlgorithmRegistry()
    try:
        algo = registry.get(study_id, algo_name)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Create executor with provider options
    console.print(f"[dim]Using provider: {provider}[/dim]")
    if model:
        console.print(f"[dim]Model: {model}[/dim]")
    if base_url:
        console.print(f"[dim]Base URL: {base_url}[/dim]")

    # Build provider kwargs
    provider_kwargs = {}
    if model:
        provider_kwargs["model"] = model
    if base_url:
        provider_kwargs["base_url"] = base_url

    try:
        executor = create_executor(provider, **provider_kwargs)
    except ImportError as e:
        console.print(f"[red]Provider not available: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Failed to create executor: {e}[/red]")
        raise typer.Exit(1)

    # Execute
    console.print(f"[bold]Running {algo.name}[/bold] in {mode} mode...")
    console.print()

    try:
        if mode == "analyze":
            result = executor.analyze(algo, text)

            # Display analysis results
            console.print(Panel(
                f"[bold]Input Summary:[/bold] {result.input_summary}",
                title="Analysis Result",
                border_style="green",
            ))

            if result.findings:
                console.print("\n[bold]Findings[/bold]")
                for finding in result.findings:
                    console.print(f"  - {finding}")

            if result.elements_identified:
                console.print("\n[bold]Elements Identified[/bold]")
                for key, value in result.elements_identified.items():
                    console.print(f"  [cyan]{key}:[/cyan] {value}")

            if result.recommendations:
                console.print("\n[bold]Recommendations[/bold]")
                for rec in result.recommendations:
                    console.print(f"  - {rec}")

            if result.score is not None:
                score_color = "green" if result.score >= 0.7 else "yellow" if result.score >= 0.4 else "red"
                console.print(f"\n[bold]Score:[/bold] [{score_color}]{result.score:.2f}[/{score_color}]")

        elif mode == "validate":
            result = executor.validate(algo, text)

            status = "[green]VALID[/green]" if result.is_valid else "[red]INVALID[/red]"
            console.print(Panel(
                f"Status: {status}\nConfidence: {result.confidence:.2f}",
                title="Validation Result",
                border_style="green" if result.is_valid else "red",
            ))

            if result.criteria_met:
                console.print("\n[bold green]Criteria Met[/bold green]")
                for criteria in result.criteria_met:
                    console.print(f"  [green]\u2713[/green] {criteria}")

            if result.criteria_failed:
                console.print("\n[bold red]Criteria Failed[/bold red]")
                for criteria in result.criteria_failed:
                    console.print(f"  [red]\u2717[/red] {criteria}")

            if result.suggestions:
                console.print("\n[bold]Suggestions[/bold]")
                for sug in result.suggestions:
                    console.print(f"  - {sug}")

        elif mode == "generate":
            # For generate mode, parse input as parameters (simple key=value format)
            params = {}
            for line in text.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    params[key.strip()] = value.strip()

            result = executor.generate(algo, params)

            console.print(Panel(
                result.generated_content,
                title="Generated Content",
                border_style="blue",
            ))

            if result.notes:
                console.print("\n[bold]Notes[/bold]")
                for note in result.notes:
                    console.print(f"  - {note}")

        else:
            console.print(f"[red]Invalid mode: {mode}. Use analyze, generate, or validate.[/red]")
            raise typer.Exit(1)

        # Save output if requested
        if output:
            import json
            output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            console.print(f"\n[dim]Results saved to: {output}[/dim]")

    except Exception as e:
        console.print(f"[red]Execution failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("stats")
def algorithm_stats() -> None:
    """Show statistics about the algorithm collection."""
    from narratological.algorithms import AlgorithmRegistry

    registry = AlgorithmRegistry()

    console.print(Panel(
        f"[bold]{registry.count()}[/bold] algorithms across [bold]{len(registry.list_studies())}[/bold] studies",
        title="Algorithm Statistics",
        border_style="cyan",
    ))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Study")
    table.add_column("Creator")
    table.add_column("Algorithms", justify="right")

    counts = registry.count_by_study()
    from narratological.loader import load_compendium
    compendium = load_compendium()

    for study_id, count in sorted(counts.items()):
        study = compendium.get_study(study_id)
        creator = study.creator if study else "Unknown"
        table.add_row(study_id, creator, str(count))

    console.print(table)
