"""API routes for script/narrative analysis."""

from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class SceneAnalysisRequest(BaseModel):
    """Request model for scene analysis."""

    text: str = Field(..., description="Scene text to analyze")
    framework: str | None = Field(None, description="Framework/study to apply")


class SceneAnalysisResponse(BaseModel):
    """Response model for scene analysis."""

    function: str = Field(..., description="Primary beat function")
    secondary_function: str | None = Field(None, description="Secondary function")
    tension_level: int = Field(..., ge=1, le=10, description="Tension level")
    connector_suggested: str = Field(..., description="Suggested connector to next scene")
    notes: str = Field(..., description="Analysis notes")


class ScriptUploadRequest(BaseModel):
    """Request model for script upload."""

    title: str = Field(..., description="Script title")
    content: str = Field(..., description="Script content")
    format: str = Field("Feature", description="Script format")


class AnalysisStatusResponse(BaseModel):
    """Response model for analysis status."""

    status: str = Field(..., description="Analysis status")
    progress: float = Field(..., ge=0, le=1, description="Progress (0-1)")
    message: str | None = Field(None, description="Status message")


class NotImplementedResponse(BaseModel):
    """Structured response payload for unimplemented endpoints."""

    status: str = Field("not_implemented", description="Endpoint implementation status")
    code: str = Field("ANALYSIS_NOT_IMPLEMENTED", description="Machine-readable error code")
    message: str = Field(..., description="User-facing explanation")
    planned: str = Field(..., description="Planned implementation area")


def _raise_not_implemented(message: str, planned: str) -> NoReturn:
    """Raise a standardized 501 error payload."""
    raise HTTPException(
        status_code=501,
        detail=NotImplementedResponse(
            status="not_implemented",
            code="ANALYSIS_NOT_IMPLEMENTED",
            message=message,
            planned=planned,
        ).model_dump(),
    )


NOT_IMPLEMENTED_RESPONSES: dict[int | str, dict[str, Any]] = {
    501: {
        "model": NotImplementedResponse,
        "description": "Endpoint exists but implementation is not available yet.",
    }
}


@router.post("/scene", responses=NOT_IMPLEMENTED_RESPONSES)
async def analyze_scene(request: SceneAnalysisRequest) -> dict[str, Any]:
    """Analyze a single scene.

    Note: Full analysis requires LLM integration. This endpoint
    returns a placeholder response showing the expected structure.
    """
    _ = request
    _raise_not_implemented(
        message="Full scene analysis requires LLM orchestration and script context.",
        planned="scene-analysis-pipeline",
    )


@router.post("/script", responses=NOT_IMPLEMENTED_RESPONSES)
async def upload_script(request: ScriptUploadRequest) -> dict[str, Any]:
    """Upload a script for analysis.

    Returns an analysis ID that can be used to track progress
    and retrieve results.
    """
    # In a full implementation, this would:
    # 1. Parse and validate the script
    # 2. Queue it for analysis
    # 3. Return an analysis ID

    _ = request
    _raise_not_implemented(
        message="Script upload and analysis queueing are not implemented yet.",
        planned="script-ingestion-and-job-queue",
    )


@router.get("/script/{analysis_id}/status", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_analysis_status(analysis_id: str) -> AnalysisStatusResponse:
    """Get the status of a script analysis."""
    _ = analysis_id
    _raise_not_implemented(
        message="Analysis status tracking is not implemented yet.",
        planned="analysis-status-tracking",
    )


@router.get("/script/{analysis_id}/reports", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_analysis_reports(analysis_id: str) -> dict[str, Any]:
    """Get all available reports for a completed analysis."""
    _ = analysis_id
    _raise_not_implemented(
        message="Analysis reports are not available until the analysis pipeline is implemented.",
        planned="report-generation-pipeline",
    )


@router.get("/script/{analysis_id}/reports/coverage", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_coverage_report(analysis_id: str) -> dict[str, Any]:
    """Get the coverage report for a completed analysis."""
    _ = analysis_id
    _raise_not_implemented(
        message="Coverage report generation is not implemented yet.",
        planned="coverage-report-generator",
    )


@router.get("/script/{analysis_id}/reports/beat-map", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_beat_map(analysis_id: str) -> dict[str, Any]:
    """Get the beat map for a completed analysis."""
    _ = analysis_id
    _raise_not_implemented(
        message="Beat map generation is not implemented yet.",
        planned="beat-map-generator",
    )


@router.get("/script/{analysis_id}/reports/structural", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_structural_report(analysis_id: str) -> dict[str, Any]:
    """Get the structural analysis report."""
    _ = analysis_id
    _raise_not_implemented(
        message="Structural analysis reporting is not implemented yet.",
        planned="structural-report-generator",
    )


@router.get("/script/{analysis_id}/reports/character-atlas", responses=NOT_IMPLEMENTED_RESPONSES)
async def get_character_atlas(analysis_id: str) -> dict[str, Any]:
    """Get the character atlas for a completed analysis."""
    _ = analysis_id
    _raise_not_implemented(
        message="Character atlas generation is not implemented yet.",
        planned="character-atlas-generator",
    )


@router.get("/frameworks")
async def list_analysis_frameworks() -> list[dict[str, Any]]:
    """List available frameworks for analysis."""
    from narratological.loader import load_compendium

    compendium = load_compendium()

    return [
        {
            "id": s.id,
            "creator": s.creator,
            "category": s.category.value,
            "algorithm_count": len(s.core_algorithms),
            "question_count": len(s.diagnostic_questions),
        }
        for s in compendium.studies.values()
    ]
