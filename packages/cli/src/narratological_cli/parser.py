"""Script parser for CLI commands.

Provides utilities to parse raw text files into Script models
and pre-analyzed beat map JSON files into DiagnosticContext.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from narratological.diagnostics.models import DiagnosticContext, SceneTransition
from narratological.models.analysis import (
    BeatFunction,
    Character,
    ConnectorType,
    Scene,
    Script,
)


# Scene detection patterns
SLUGLINE_PATTERN = re.compile(
    r"^(INT\.|EXT\.|INT/EXT\.|I/E\.)[\s]+(.+?)(?:\s*[-–—]\s*(.+))?$",
    re.IGNORECASE | re.MULTILINE,
)
CHARACTER_CUE_PATTERN = re.compile(r"^([A-Z][A-Z\s\.\']+)(?:\s*\(.*\))?$")
PARENTHETICAL_PATTERN = re.compile(r"^\(.+\)$")


def parse_script(
    path: Path,
    title: str | None = None,
    format: str = "Feature",
) -> Script:
    """Parse a text file into a Script model with basic scene detection.

    Uses heuristics to detect scenes from sluglines (INT./EXT.) and
    falls back to paragraph breaks if no sluglines are found.

    Args:
        path: Path to the script text file.
        title: Optional title override. Defaults to filename without extension.
        format: Script format (Feature, Pilot, etc.).

    Returns:
        Script model with detected scenes and characters.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file cannot be parsed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Script file not found: {path}")

    text = path.read_text(encoding="utf-8")
    script_title = title or path.stem.replace("_", " ").replace("-", " ").title()

    # Try slugline-based scene detection first
    scenes = _detect_scenes_by_sluglines(text)

    # Fall back to paragraph-based detection if no sluglines found
    if not scenes:
        scenes = _detect_scenes_by_paragraphs(text)

    # Extract characters from scenes
    characters = _extract_characters(text)

    # Estimate page count (approx 55 lines per page for screenplay format)
    line_count = text.count("\n")
    page_count = max(1, line_count // 55)

    return Script(
        title=script_title,
        format=format,
        page_count=page_count,
        scene_count=len(scenes),
        scenes=scenes,
        characters=characters,
    )


def _detect_scenes_by_sluglines(text: str) -> list[Scene]:
    """Detect scenes using INT./EXT. slugline patterns."""
    scenes = []
    matches = list(SLUGLINE_PATTERN.finditer(text))

    if not matches:
        return []

    for i, match in enumerate(matches):
        # Determine scene boundaries
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        # Extract scene content
        scene_content = text[start_pos:end_pos].strip()

        # Build slug from match groups
        int_ext = match.group(1).upper()
        location = match.group(2).strip()
        time_of_day = match.group(3).strip() if match.group(3) else ""
        slug = f"{int_ext} {location}"
        if time_of_day:
            slug += f" - {time_of_day}"

        # Generate summary from first meaningful lines
        summary = _generate_scene_summary(scene_content)

        # Extract characters present in this scene
        characters_present = _extract_characters_in_scene(scene_content)

        scenes.append(Scene(
            number=i + 1,
            slug=slug,
            summary=summary,
            characters_present=characters_present,
        ))

    return scenes


def _detect_scenes_by_paragraphs(text: str) -> list[Scene]:
    """Detect scenes using paragraph breaks as scene boundaries.

    Fallback when no sluglines are present (prose, treatments, etc.).
    """
    # Split by double newlines (paragraph breaks)
    paragraphs = re.split(r"\n\s*\n", text.strip())

    # Filter out very short paragraphs
    paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]

    if not paragraphs:
        # Single scene for the whole text
        return [Scene(
            number=1,
            slug="SCENE 1",
            summary=text[:200].strip() + "..." if len(text) > 200 else text.strip(),
            characters_present=_extract_characters_in_scene(text),
        )]

    scenes = []
    for i, para in enumerate(paragraphs):
        summary = para[:200].strip()
        if len(para) > 200:
            summary += "..."

        scenes.append(Scene(
            number=i + 1,
            slug=f"SCENE {i + 1}",
            summary=summary,
            characters_present=_extract_characters_in_scene(para),
        ))

    return scenes


def _generate_scene_summary(content: str) -> str:
    """Generate a brief summary from scene content."""
    # Take first few lines, skipping character cues and parentheticals
    lines = content.split("\n")
    meaningful_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip character cues
        if CHARACTER_CUE_PATTERN.match(line):
            continue
        # Skip parentheticals
        if PARENTHETICAL_PATTERN.match(line):
            continue
        meaningful_lines.append(line)
        if len(meaningful_lines) >= 3:
            break

    summary = " ".join(meaningful_lines)
    if len(summary) > 200:
        summary = summary[:197] + "..."

    return summary or "Scene content"


def _extract_characters_in_scene(content: str) -> list[str]:
    """Extract character names from scene content."""
    characters = set()

    for line in content.split("\n"):
        line = line.strip()
        match = CHARACTER_CUE_PATTERN.match(line)
        if match:
            name = match.group(1).strip()
            # Filter out common non-character cues
            if name not in {"CONTINUED", "FADE IN", "FADE OUT", "CUT TO", "DISSOLVE TO", "THE END"}:
                characters.add(name)

    return sorted(characters)


def _extract_characters(text: str) -> list[Character]:
    """Extract all characters from the full script."""
    all_characters = set()

    for line in text.split("\n"):
        line = line.strip()
        match = CHARACTER_CUE_PATTERN.match(line)
        if match:
            name = match.group(1).strip()
            if name not in {"CONTINUED", "FADE IN", "FADE OUT", "CUT TO", "DISSOLVE TO", "THE END"}:
                all_characters.add(name)

    # Create Character models
    characters = []
    for name in sorted(all_characters):
        characters.append(Character(
            name=name,
            role="character",  # Generic role, can be refined by analysis
            description=f"Character appearing in script",
        ))

    return characters


def parse_beat_map_json(path: Path) -> DiagnosticContext:
    """Parse a beat map JSON file into DiagnosticContext for diagnostics.

    Expected JSON format:
    {
        "title": "Script Title",
        "scenes": [
            {
                "number": 1,
                "slug": "INT. LOCATION - DAY",
                "summary": "Scene summary",
                "function": "SETUP",
                "connector": "THEREFORE",
                "characters": ["JOHN", "MARY"],
                "tension": 5
            }
        ],
        "characters": ["JOHN", "MARY", "BOB"]
    }

    Args:
        path: Path to the beat map JSON file.

    Returns:
        DiagnosticContext ready for diagnostic analysis.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the JSON is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Beat map file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in beat map file: {e}") from e

    title = data.get("title", path.stem)
    scenes = data.get("scenes", [])
    characters = data.get("characters", [])

    # Extract character names if they're Character objects
    if characters and isinstance(characters[0], dict):
        characters = [c.get("name", "") for c in characters]

    # Build scene transitions from connector data
    transitions = []
    for i, scene in enumerate(scenes[:-1]):
        connector_str = scene.get("connector")
        connector = None
        is_causal = False

        if connector_str:
            connector_map = {
                "BUT": ConnectorType.BUT,
                "THEREFORE": ConnectorType.THEREFORE,
                "AND_THEN": ConnectorType.AND_THEN,
                "AND THEN": ConnectorType.AND_THEN,
                "MEANWHILE": ConnectorType.MEANWHILE,
            }
            connector = connector_map.get(connector_str.upper())
            is_causal = connector in (ConnectorType.BUT, ConnectorType.THEREFORE)

        transitions.append(SceneTransition(
            from_scene=scene.get("number", i + 1),
            to_scene=scenes[i + 1].get("number", i + 2),
            connector=connector,
            is_causal=is_causal,
        ))

    # Determine if beat map data is available
    beat_map_available = any(scene.get("function") for scene in scenes)

    return DiagnosticContext(
        title=title,
        scenes=scenes,
        characters=characters,
        transitions=transitions,
        beat_map_available=beat_map_available,
    )


def script_to_diagnostic_context(script: Script) -> DiagnosticContext:
    """Convert a Script model to DiagnosticContext.

    Args:
        script: The script to convert.

    Returns:
        DiagnosticContext for diagnostic analysis.
    """
    return DiagnosticContext.from_script(script)


def load_input(
    path: Path,
    title: str | None = None,
) -> tuple[Script | None, DiagnosticContext]:
    """Load input from a file, handling both raw scripts and beat maps.

    Args:
        path: Path to the input file.
        title: Optional title override.

    Returns:
        Tuple of (Script or None, DiagnosticContext).
        Script is None if input was a beat map JSON.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file cannot be parsed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    # Check if it's a JSON file (likely a beat map)
    if path.suffix.lower() == ".json":
        context = parse_beat_map_json(path)
        return None, context

    # Otherwise parse as a script
    script = parse_script(path, title=title)
    context = script_to_diagnostic_context(script)
    return script, context
