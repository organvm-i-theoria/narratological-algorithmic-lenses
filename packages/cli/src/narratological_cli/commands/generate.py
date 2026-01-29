"""CLI commands for generating narrative structures."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from narratological_cli.llm_config import (
    BASE_URL_OPTION_HELP,
    MODEL_OPTION_HELP,
    PROVIDER_OPTION_HELP,
    get_provider,
)

app = typer.Typer(help="Generate narrative structures")
console = Console()


# Response models for LLM generation


class OutlineResponse(BaseModel):
    """Response model for story outline generation."""

    title: str = Field(description="Generated story title")
    logline: str = Field(description="One-sentence logline")
    theme: str = Field(description="Central theme/question")
    acts: list[dict] = Field(
        description="Act breakdown with name, summary, key_beats"
    )
    protagonist: dict = Field(
        description="Protagonist with name, want, need, lie, truth"
    )
    key_scenes: list[str] = Field(description="Key scene descriptions")


class BeatResponse(BaseModel):
    """Response model for beat generation."""

    beats: list[dict] = Field(
        description="List of beats with description, function, value_shift"
    )
    tension_arc: list[int] = Field(description="Tension levels for each beat (1-10)")
    notes: str | None = Field(default=None, description="Additional notes")


class CharacterResponse(BaseModel):
    """Response model for character generation."""

    name: str = Field(description="Character name")
    role: str = Field(description="Narrative role (protagonist, antagonist, etc.)")
    description: str = Field(description="Physical/personality description")
    want: str = Field(description="Conscious external goal")
    need: str = Field(description="Unconscious internal need")
    lie: str = Field(description="False belief character holds")
    truth: str = Field(description="Truth character must learn")
    arc: str = Field(description="Arc type: positive, negative, flat, corrupted, redeemed")
    key_moments: list[str] = Field(description="Key character moments/scenes")
    relationships: list[dict] = Field(description="Relationships with other characters")


class TransformationResponse(BaseModel):
    """Response model for Ovidian transformation generation."""

    pre_state: dict = Field(description="Subject's state before transformation")
    trigger: str = Field(description="What causes the transformation")
    process: list[str] = Field(description="Stages of transformation")
    post_state: dict = Field(description="Subject's state after transformation")
    mens_pristina: str = Field(description="What is preserved (original mind/identity)")
    thematic_meaning: str = Field(description="What the transformation symbolizes")


@app.command("outline")
def generate_outline(
    premise: Annotated[
        str,
        typer.Argument(help="Story premise or logline"),
    ],
    framework: Annotated[
        str,
        typer.Option("--framework", "-f", help="Framework/study to use"),
    ] = "pixar",
    acts: Annotated[
        int,
        typer.Option("--acts", "-a", help="Number of acts"),
    ] = 3,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file path"),
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
    """Generate a story outline from a premise.

    Uses the structural hierarchy and algorithms from the selected
    framework to generate a story outline.
    """
    from narratological.loader import load_study

    try:
        study = load_study(framework)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Premise:[/bold] {premise}\n"
        f"[bold]Framework:[/bold] {study.creator}\n"
        f"[bold]Acts:[/bold] {acts}",
        title="Outline Generation",
    ))

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url, verbose=True)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Build system prompt from study
    structural_hierarchy = "\n".join(
        f"Level {l.level}: {l.name} - {l.description}"
        for l in study.structural_hierarchy.levels
    )

    axioms = "\n".join(
        f"- {a.name}: {a.statement}"
        for a in study.axioms[:5]  # Top 5 axioms
    )

    system_prompt = f"""You are a story architect using the {study.creator} methodology.

STRUCTURAL HIERARCHY:
{structural_hierarchy}

KEY PRINCIPLES:
{axioms}

Generate story outlines that follow this framework's structural principles."""

    prompt = f"""Generate a {acts}-act story outline based on this premise:

"{premise}"

Include:
1. A compelling title
2. A clear logline
3. Central theme/question
4. Act breakdown with key beats
5. Protagonist with Want/Need/Lie/Truth
6. Key scene descriptions

Follow the {study.creator} methodology for structure and character."""

    try:
        console.print("\n[dim]Generating outline...[/dim]")
        result = llm.complete_structured(prompt, OutlineResponse, system=system_prompt)

        # Display results
        console.print(Panel(
            f"[bold]Title:[/bold] {result.title}\n\n"
            f"[bold]Logline:[/bold] {result.logline}\n\n"
            f"[bold]Theme:[/bold] {result.theme}",
            title="Generated Outline",
        ))

        # Protagonist
        console.print("\n[bold]Protagonist:[/bold]")
        p = result.protagonist
        console.print(f"  Name: {p.get('name', 'TBD')}")
        console.print(f"  [cyan]WANT:[/cyan] {p.get('want', 'TBD')}")
        console.print(f"  [cyan]NEED:[/cyan] {p.get('need', 'TBD')}")
        console.print(f"  [red]LIE:[/red] {p.get('lie', 'TBD')}")
        console.print(f"  [green]TRUTH:[/green] {p.get('truth', 'TBD')}")

        # Acts
        console.print("\n[bold]Structure:[/bold]")
        tree = Tree("[bold]Story Structure[/bold]")
        for i, act in enumerate(result.acts, 1):
            act_name = act.get("name", f"Act {i}")
            act_branch = tree.add(f"[cyan]Act {i}: {act_name}[/cyan]")
            if act.get("summary"):
                act_branch.add(f"[dim]{act['summary'][:100]}...[/dim]" if len(act.get("summary", "")) > 100 else f"[dim]{act.get('summary', '')}[/dim]")
            for beat in act.get("key_beats", [])[:3]:
                act_branch.add(f"- {beat}")
        console.print(tree)

        # Key scenes
        if result.key_scenes:
            console.print("\n[bold]Key Scenes:[/bold]")
            for i, scene in enumerate(result.key_scenes[:6], 1):
                console.print(f"  {i}. {scene}")

        # Save output
        if output:
            import json
            output.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
            console.print(f"\n[dim]Outline saved to: {output}[/dim]")

    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("beats")
def generate_beats(
    scene_description: Annotated[
        str,
        typer.Argument(help="Scene description or context"),
    ],
    function: Annotated[
        str,
        typer.Option("--function", "-f", help="Target beat function"),
    ] = "ESCALATE",
    count: Annotated[
        int,
        typer.Option("--count", "-c", help="Number of beats to generate"),
    ] = 5,
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
    """Generate beats for a scene.

    Creates micro-level beat structure for a scene based on
    the target function and dramatic context.
    """
    from narratological.models.analysis import BeatFunction

    try:
        beat_func = BeatFunction(function.upper())
    except ValueError:
        valid = ", ".join(f.value for f in BeatFunction)
        console.print(f"[red]Invalid function: {function}[/red]")
        console.print(f"Valid functions: {valid}")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Scene:[/bold] {scene_description[:100]}{'...' if len(scene_description) > 100 else ''}\n"
        f"[bold]Function:[/bold] {beat_func.value}\n"
        f"[bold]Beats:[/bold] {count}",
        title="Beat Generation",
    ))

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Beat function characteristics
    characteristics = {
        "SETUP": "Establishes information, world, characters",
        "INCITE": "Disrupts equilibrium, sets story in motion",
        "COMPLICATE": "Adds obstacles, complexity",
        "ESCALATE": "Raises stakes, increases tension",
        "REVEAL": "Discloses information, changes understanding",
        "CRISIS": "Forces difficult choice",
        "CLIMAX": "Peak of action/emotion",
        "RESOLVE": "Provides resolution",
        "BREATHE": "Pacing relief, emotional reset",
        "PLANT": "Sets up future payoff",
        "PAYOFF": "Delivers on earlier setup",
    }

    system_prompt = f"""You are a professional screenwriter generating scene beats.

Beat function {beat_func.value}: {characteristics.get(beat_func.value, 'N/A')}

A beat is the smallest unit of dramatic change - a shift in value, power, or information.
Generate beats that:
- Build tension progressively
- Create clear cause-and-effect chains
- Advance character and story
- Use visual/cinematic language"""

    prompt = f"""Generate {count} beats for this scene:

"{scene_description}"

Target function: {beat_func.value}

For each beat provide:
- Description (what happens)
- Function (beat type)
- Value shift (what changes, e.g., "hope -> despair")

Also provide a tension arc (1-10 scale) for each beat."""

    try:
        console.print("\n[dim]Generating beats...[/dim]")
        result = llm.complete_structured(prompt, BeatResponse, system=system_prompt)

        # Display results
        console.print("\n[bold]Generated Beats:[/bold]")
        for i, beat in enumerate(result.beats, 1):
            tension = result.tension_arc[i - 1] if i <= len(result.tension_arc) else 5
            tension_color = "green" if tension >= 7 else "yellow" if tension >= 4 else "dim"

            console.print(f"\n  [bold cyan]Beat {i}[/bold cyan] [{tension_color}]T:{tension}[/{tension_color}]")
            console.print(f"    {beat.get('description', 'N/A')}")
            if beat.get("function"):
                console.print(f"    [dim]Function: {beat['function']}[/dim]")
            if beat.get("value_shift"):
                console.print(f"    [dim]Value Shift: {beat['value_shift']}[/dim]")

        # Tension arc visualization
        console.print("\n[bold]Tension Arc:[/bold]")
        arc_str = ""
        for t in result.tension_arc:
            bar = "=" * t
            color = "green" if t >= 7 else "yellow" if t >= 4 else "dim"
            arc_str += f"  [{color}]{bar:10}[/{color}] {t}\n"
        console.print(arc_str)

        if result.notes:
            console.print(f"\n[dim]Notes: {result.notes}[/dim]")

    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("character")
def generate_character(
    role: Annotated[
        str,
        typer.Argument(help="Character role (protagonist, antagonist, mentor, etc.)"),
    ],
    genre: Annotated[
        Optional[str],
        typer.Option("--genre", "-g", help="Genre context"),
    ] = None,
    framework: Annotated[
        str,
        typer.Option("--framework", "-f", help="Framework for character design"),
    ] = "pixar",
    context: Annotated[
        Optional[str],
        typer.Option("--context", "-c", help="Story context or premise"),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file path"),
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
    """Generate a character structure.

    Creates Want/Need/Lie/Truth structure and arc based on
    the selected framework's character principles.
    """
    from narratological.loader import load_study

    try:
        study = load_study(framework)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]Role:[/bold] {role}\n"
        f"[bold]Genre:[/bold] {genre or 'not specified'}\n"
        f"[bold]Framework:[/bold] {study.creator}",
        title="Character Generation",
    ))

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Build system prompt
    axioms = "\n".join(
        f"- {a.name}: {a.statement}"
        for a in study.axioms[:3]
    )

    system_prompt = f"""You are a character designer using the {study.creator} methodology.

KEY PRINCIPLES:
{axioms}

CHARACTER STRUCTURE:
- WANT: Conscious external goal (what they think they need)
- NEED: Unconscious internal need (what they actually need)
- LIE: False belief they hold about themselves or the world
- TRUTH: The truth they must learn/accept

ARC TYPES:
- Positive: Growth toward better state (learns truth, overcomes lie)
- Negative: Decline toward worse state (rejects truth, embraces lie)
- Flat: Tests existing beliefs (already knows truth, tests others)
- Corrupted: Twisted positive to negative
- Redeemed: Recovered from negative to positive"""

    genre_context = f"\nGenre: {genre}" if genre else ""
    story_context = f"\nStory context: {context}" if context else ""

    prompt = f"""Generate a detailed {role} character for a story.{genre_context}{story_context}

Include:
1. A memorable name
2. Role in the narrative
3. Physical/personality description
4. WANT (conscious external goal)
5. NEED (unconscious internal need)
6. LIE (false belief)
7. TRUTH (what they must learn)
8. Arc type and trajectory
9. Key moments in their arc
10. Relationships with other characters"""

    try:
        console.print("\n[dim]Generating character...[/dim]")
        result = llm.complete_structured(prompt, CharacterResponse, system=system_prompt)

        # Display results
        console.print(Panel(
            f"[bold]{result.name}[/bold] - {result.role}\n\n"
            f"{result.description}",
            title="Generated Character",
        ))

        console.print("\n[bold]Character Structure:[/bold]")
        console.print(f"  [cyan]WANT:[/cyan] {result.want}")
        console.print(f"  [cyan]NEED:[/cyan] {result.need}")
        console.print(f"  [red]LIE:[/red] {result.lie}")
        console.print(f"  [green]TRUTH:[/green] {result.truth}")

        arc_colors = {
            "positive": "green",
            "negative": "red",
            "flat": "yellow",
            "corrupted": "red",
            "redeemed": "green",
        }
        arc_color = arc_colors.get(result.arc.lower(), "white")
        console.print(f"\n[bold]Arc:[/bold] [{arc_color}]{result.arc}[/{arc_color}]")

        if result.key_moments:
            console.print("\n[bold]Key Moments:[/bold]")
            for i, moment in enumerate(result.key_moments, 1):
                console.print(f"  {i}. {moment}")

        if result.relationships:
            console.print("\n[bold]Relationships:[/bold]")
            for rel in result.relationships:
                console.print(f"  - {rel.get('character', 'Unknown')}: {rel.get('relationship', 'N/A')}")

        # Save output
        if output:
            import json
            output.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
            console.print(f"\n[dim]Character saved to: {output}[/dim]")

    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("transformation")
def generate_transformation(
    subject: Annotated[
        str,
        typer.Argument(help="Subject to transform"),
    ],
    cause: Annotated[
        str,
        typer.Option("--cause", "-c", help="Cause of transformation"),
    ] = "divine intervention",
    preserve: Annotated[
        str,
        typer.Option("--preserve", "-p", help="What to preserve (mens pristina)"),
    ] = "consciousness",
    target_form: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target form of transformation"),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file path"),
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
    """Generate an Ovidian transformation sequence.

    Uses the Metamorphoses algorithm to create a transformation
    narrative with proper mens_pristina preservation.
    """
    from narratological.loader import load_study

    study = load_study("ovid-metamorphoses")

    console.print(Panel(
        f"[bold]Subject:[/bold] {subject}\n"
        f"[bold]Cause:[/bold] {cause}\n"
        f"[bold]Preserve:[/bold] {preserve}\n"
        f"[bold]Target:[/bold] {target_form or 'determined by cause'}",
        title="Transformation Generation (Ovid)",
    ))

    # Get LLM provider
    try:
        llm = get_provider(provider, model=model, base_url=base_url)
    except (ValueError, EnvironmentError, ImportError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Build system prompt from Ovid study
    axioms = "\n".join(
        f"- {a.name}: {a.statement}"
        for a in study.axioms[:5]
    )

    # Find transformation algorithm
    transformation_algo = None
    for algo in study.core_algorithms:
        if "transformation" in algo.name.lower() or "metamorphosis" in algo.name.lower():
            transformation_algo = algo
            break

    algo_context = ""
    if transformation_algo:
        algo_context = f"\nALGORITHM: {transformation_algo.name}\n{transformation_algo.pseudocode}"

    system_prompt = f"""You are a mythological storyteller using Ovidian transformation principles.

PRINCIPLES:
{axioms}
{algo_context}

KEY CONCEPTS:
- Mens Pristina: The original mind/consciousness that survives transformation
- Corporeal Flux: The physical body is mutable, identity persists
- Divine Causation: Transformations have cosmic/mythological causes
- Symbolic Meaning: Every transformation carries thematic weight"""

    target_context = f" into {target_form}" if target_form else ""

    prompt = f"""Generate an Ovidian transformation sequence for:

Subject: {subject}
Cause: {cause}
What to Preserve: {preserve}
Target Form: {target_form or 'appropriate to the cause and subject'}

Describe:
1. Pre-transformation state (physical, emotional, social position)
2. The trigger/cause of transformation
3. Stages of transformation (gradual, specific physical changes)
4. Post-transformation state (new form, preserved elements)
5. Mens pristina (what of the original consciousness remains)
6. Thematic meaning (what the transformation symbolizes)

Follow Ovid's style: specific physical details, emotional resonance, cosmic significance."""

    try:
        console.print("\n[dim]Generating transformation...[/dim]")
        result = llm.complete_structured(prompt, TransformationResponse, system=system_prompt)

        # Display results
        console.print("\n[bold cyan]PRE-TRANSFORMATION[/bold cyan]")
        for key, value in result.pre_state.items():
            console.print(f"  {key}: {value}")

        console.print(f"\n[bold yellow]TRIGGER[/bold yellow]")
        console.print(f"  {result.trigger}")

        console.print(f"\n[bold]TRANSFORMATION PROCESS[/bold]")
        for i, stage in enumerate(result.process, 1):
            console.print(f"  {i}. {stage}")

        console.print("\n[bold green]POST-TRANSFORMATION[/bold green]")
        for key, value in result.post_state.items():
            console.print(f"  {key}: {value}")

        console.print(f"\n[bold magenta]MENS PRISTINA[/bold magenta]")
        console.print(f"  {result.mens_pristina}")

        console.print(f"\n[bold]THEMATIC MEANING[/bold]")
        console.print(f"  {result.thematic_meaning}")

        # Save output
        if output:
            import json
            output.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
            console.print(f"\n[dim]Transformation saved to: {output}[/dim]")

    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)
