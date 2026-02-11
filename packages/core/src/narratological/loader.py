"""Loader for narratological algorithm studies.

Provides functions to load studies from the unified JSON compendium
or individual study files.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

from narratological.models.study import Compendium, Study

if TYPE_CHECKING:
    from os import PathLike


def _get_default_compendium_path() -> Path:
    """Get the default path to the unified compendium.

    Looks for the compendium relative to this package, then falls back
    to looking in common locations.
    """
    # Try relative to package
    package_dir = Path(__file__).parent
    candidates = [
        package_dir / "../../../specs/03-structured-data/narratological-algorithms-unified.json",
        package_dir / "../../../../specs/03-structured-data/narratological-algorithms-unified.json",
        Path("specs/03-structured-data/narratological-algorithms-unified.json"),
        Path("03-structured-data/narratological-algorithms-unified.json"),
    ]

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists():
            return resolved

    raise FileNotFoundError(
        "Could not find narratological-algorithms-unified.json. "
        "Please provide an explicit path or ensure the specs directory is accessible."
    )


def _load_packaged_compendium() -> Compendium | None:
    """Load packaged compendium data from package resources if available."""
    resource = resources.files("narratological").joinpath(
        "data/narratological-algorithms-unified.json"
    )

    if not resource.is_file():
        return None

    with resource.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)

    return Compendium.model_validate(data)


def load_compendium(path: str | PathLike[str] | None = None) -> Compendium:
    """Load the complete narratological algorithm compendium.

    Args:
        path: Path to the unified JSON file. If None, uses default location.

    Returns:
        Compendium object containing all studies and cross-references.

    Raises:
        FileNotFoundError: If the compendium file cannot be found.
        ValidationError: If the JSON doesn't match the expected schema.
    """
    if path is None:
        packaged = _load_packaged_compendium()
        if packaged is not None:
            return packaged
        file_path = _get_default_compendium_path()
    else:
        file_path = Path(path)

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    return Compendium.model_validate(data)


def load_study(study_id: str, compendium_path: str | PathLike[str] | None = None) -> Study:
    """Load a single study by ID.

    Args:
        study_id: The study identifier (e.g., 'bergman', 'zelda').
        compendium_path: Path to unified JSON. If None, uses default.

    Returns:
        Study object for the requested study.

    Raises:
        KeyError: If the study ID is not found.
        FileNotFoundError: If the compendium cannot be found.
    """
    compendium = load_compendium(compendium_path)
    study = compendium.get_study(study_id)

    if study is None:
        available = ", ".join(compendium.list_study_ids())
        raise KeyError(
            f"Study '{study_id}' not found. Available studies: {available}"
        )

    return study


def load_study_from_file(path: str | PathLike[str]) -> Study:
    """Load a study from an individual JSON file.

    Args:
        path: Path to the study JSON file.

    Returns:
        Study object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValidationError: If the JSON doesn't match the expected schema.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return Study.model_validate(data)


def list_available_studies(compendium_path: str | PathLike[str] | None = None) -> list[str]:
    """List all available study IDs.

    Args:
        compendium_path: Path to unified JSON. If None, uses default.

    Returns:
        List of study IDs.
    """
    compendium = load_compendium(compendium_path)
    return compendium.list_study_ids()


def get_study_summary(compendium_path: str | PathLike[str] | None = None) -> list[dict[str, str]]:
    """Get a summary of all available studies.

    Returns:
        List of dicts with id, creator, work, category for each study.
    """
    compendium = load_compendium(compendium_path)
    return [
        {
            "id": study.id,
            "creator": study.creator,
            "work": study.work,
            "category": study.category.value,
            "axiom_count": str(len(study.axioms)),
            "algorithm_count": str(len(study.core_algorithms)),
        }
        for study in compendium.studies.values()
    ]
