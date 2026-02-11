"""API routes for narratological studies."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from narratological.loader import load_compendium, load_study
from narratological.models.study import Category

router = APIRouter()

CATEGORY_FILTER = Query(None, description="Filter by category")
SEARCH_QUERY = Query(..., description="Search query")
SEARCH_LIMIT = Query(20, ge=1, le=100, description="Max results")


@router.get("/")
async def list_studies(
    category: Category | None = CATEGORY_FILTER,
) -> list[dict[str, Any]]:
    """List all available studies with optional category filter."""
    compendium = load_compendium()

    if category:
        studies = compendium.get_studies_by_category(category)
    else:
        studies = list(compendium.studies.values())

    return [
        {
            "id": s.id,
            "creator": s.creator,
            "work": s.work,
            "category": s.category.value,
            "axiom_count": len(s.axioms),
            "algorithm_count": len(s.core_algorithms),
            "question_count": len(s.diagnostic_questions),
        }
        for s in studies
    ]


@router.get("/categories")
async def list_categories() -> list[str]:
    """List all study categories."""
    return [c.value for c in Category]


@router.get("/pairs")
async def list_sequence_pairs() -> list[dict[str, Any]]:
    """List thematic sequence pairs."""
    compendium = load_compendium()
    pairs = compendium.get_sequence_pairs()

    return [
        {
            "id": p.id,
            "name": p.name,
            "studies": p.studies,
            "shared_principles": p.shared_principles,
            "contrasts": p.contrasts,
        }
        for p in pairs
    ]


@router.get("/search/axioms")
async def search_axioms(
    q: str = SEARCH_QUERY,
    limit: int = SEARCH_LIMIT,
) -> list[dict[str, Any]]:
    """Search axioms across all studies."""
    compendium = load_compendium()
    results = compendium.search_axioms(q)

    return [
        {
            "study_id": study_id,
            "axiom": axiom.model_dump(),
        }
        for study_id, axiom in results[:limit]
    ]


@router.get("/search/algorithms")
async def search_algorithms(
    q: str = SEARCH_QUERY,
    limit: int = SEARCH_LIMIT,
) -> list[dict[str, Any]]:
    """Search algorithms across all studies."""
    compendium = load_compendium()
    results = compendium.search_algorithms(q)

    return [
        {
            "study_id": study_id,
            "algorithm": algo.model_dump(),
        }
        for study_id, algo in results[:limit]
    ]


@router.get("/{study_id}")
async def get_study(study_id: str) -> dict[str, Any]:
    """Get a complete study by ID."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return study.model_dump()


@router.get("/{study_id}/axioms")
async def get_study_axioms(study_id: str) -> list[dict[str, Any]]:
    """Get all axioms for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return [a.model_dump() for a in study.axioms]


@router.get("/{study_id}/axioms/{axiom_id}")
async def get_axiom(study_id: str, axiom_id: str) -> dict[str, Any]:
    """Get a specific axiom by ID."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    axiom = study.get_axiom(axiom_id)
    if axiom is None:
        raise HTTPException(status_code=404, detail=f"Axiom {axiom_id} not found")

    return axiom.model_dump()


@router.get("/{study_id}/algorithms")
async def get_study_algorithms(study_id: str) -> list[dict[str, Any]]:
    """Get all algorithms for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return [a.model_dump() for a in study.core_algorithms]


@router.get("/{study_id}/algorithms/{algo_name}")
async def get_algorithm(study_id: str, algo_name: str) -> dict[str, Any]:
    """Get a specific algorithm by name."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    algo = study.get_algorithm(algo_name)
    if algo is None:
        raise HTTPException(status_code=404, detail=f"Algorithm '{algo_name}' not found")

    return algo.model_dump()


@router.get("/{study_id}/questions")
async def get_study_questions(study_id: str) -> list[dict[str, Any]]:
    """Get all diagnostic questions for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return [q.model_dump() for q in study.diagnostic_questions]


@router.get("/{study_id}/hierarchy")
async def get_study_hierarchy(study_id: str) -> dict[str, Any]:
    """Get the structural hierarchy for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return study.structural_hierarchy.model_dump()


@router.get("/{study_id}/quick-reference")
async def get_quick_reference(study_id: str) -> dict[str, Any]:
    """Get the quick reference card for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return study.quick_reference.model_dump()


@router.get("/{study_id}/correspondences")
async def get_correspondences(study_id: str) -> dict[str, Any]:
    """Get theoretical correspondences for a study."""
    try:
        study = load_study(study_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return study.theoretical_correspondences.model_dump()
