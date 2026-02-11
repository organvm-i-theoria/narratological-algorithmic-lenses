"""Framework Diagnostic.

Runs diagnostic questions from specific narratological studies
to identify framework-specific issues.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from narratological.diagnostics.base import BaseDiagnostic
from narratological.diagnostics.models import DiagnosticContext, DiagnosticType
from narratological.models.report import DiagnosticIssue, DiagnosticSeverity

if TYPE_CHECKING:
    from narratological.llm.providers import LLMProvider
    from narratological.models.study import Compendium, DiagnosticQuestion


class LLMQuestionResponse(BaseModel):
    """LLM response for a single diagnostic question."""

    question_id: str
    is_valid: bool
    explanation: str
    severity: str = "info"
    recommendation: str | None = None


class LLMFrameworkResponse(BaseModel):
    """LLM response for framework diagnostics."""

    responses: list[LLMQuestionResponse] = Field(default_factory=list)
    overall_alignment: float = 0.0
    summary: str = ""


class FrameworkDiagnostic(BaseDiagnostic):
    """Diagnostic that applies study-specific diagnostic questions.

    Uses the diagnostic_questions from each study in the compendium
    to assess how well a script aligns with various narratological
    frameworks.
    """

    diagnostic_type = DiagnosticType.FRAMEWORK
    description = "Applies study-specific diagnostic questions"

    def __init__(
        self,
        provider: LLMProvider | None = None,
        compendium: Compendium | None = None,
        **kwargs: Any,
    ):
        """Initialize the framework diagnostic.

        Args:
            provider: LLM provider for analysis.
            compendium: The compendium with studies and diagnostic questions.
            **kwargs: Additional arguments for base class.
        """
        super().__init__(provider, **kwargs)
        self.compendium = compendium
        self._questions_cache: dict[str, list[DiagnosticQuestion]] = {}

    def run(
        self,
        context: DiagnosticContext,
        study_ids: list[str] | None = None,
    ) -> list[DiagnosticIssue]:
        """Run framework diagnostics.

        Args:
            context: The diagnostic context.
            study_ids: Specific studies to use. If None, uses context.active_studies
                      or all studies if none specified.

        Returns:
            List of diagnostic issues.
        """
        can_run, error = self.can_run(context)
        if not can_run:
            return [
                self.create_issue(
                    description=error or "Cannot run diagnostic",
                    severity=DiagnosticSeverity.INFO,
                    recommendation="Provide LLM provider for framework analysis",
                )
            ]

        if self.compendium is None:
            return [
                self.create_issue(
                    description="No compendium loaded for framework diagnostics",
                    severity=DiagnosticSeverity.INFO,
                    recommendation="Load the narratological compendium",
                )
            ]

        # Determine which studies to use
        studies_to_check = study_ids or context.active_studies
        if not studies_to_check:
            # Default to a few key studies
            studies_to_check = ["pixar", "bergman", "tarantino"]

        issues = []

        for study_id in studies_to_check:
            study_issues = self._run_study_diagnostics(context, study_id)
            issues.extend(study_issues)

        return issues

    def calculate_score(self, context: DiagnosticContext) -> float:
        """Calculate overall framework alignment score."""
        # Framework diagnostic doesn't have a single score
        # Return 1.0 as a placeholder
        return 1.0

    def _requires_llm(self) -> bool:
        """Framework diagnostic requires LLM."""
        return True

    def _run_study_diagnostics(
        self,
        context: DiagnosticContext,
        study_id: str,
    ) -> list[DiagnosticIssue]:
        """Run diagnostics for a specific study."""
        if self.compendium is None:
            return []

        study = self.compendium.get_study(study_id)
        if study is None:
            return [
                self.create_issue(
                    description=f"Study '{study_id}' not found in compendium",
                    severity=DiagnosticSeverity.INFO,
                    category="framework",
                )
            ]

        if not study.diagnostic_questions:
            return []

        # Cache questions
        if study_id not in self._questions_cache:
            self._questions_cache[study_id] = study.diagnostic_questions

        questions = self._questions_cache[study_id]

        if self.provider is None:
            # Return info about available questions
            return [
                self.create_issue(
                    description=f"Study '{study_id}' has {len(questions)} diagnostic questions (LLM required to evaluate)",
                    severity=DiagnosticSeverity.INFO,
                    category="framework",
                )
            ]

        # Use LLM to evaluate questions
        return self._evaluate_questions_with_llm(context, study_id, questions)

    def _evaluate_questions_with_llm(
        self,
        context: DiagnosticContext,
        study_id: str,
        questions: list[DiagnosticQuestion],
    ) -> list[DiagnosticIssue]:
        """Evaluate diagnostic questions using LLM."""
        if self.provider is None:
            return []

        prompt = self._build_evaluation_prompt(context, study_id, questions)

        try:
            response = self.provider.complete_structured(
                prompt,
                LLMFrameworkResponse,
                system=self._build_system_prompt(study_id),
            )

            issues = []
            for resp in response.responses:
                if not resp.is_valid:
                    severity_map = {
                        "critical": DiagnosticSeverity.CRITICAL,
                        "warning": DiagnosticSeverity.WARNING,
                        "info": DiagnosticSeverity.INFO,
                        "suggestion": DiagnosticSeverity.SUGGESTION,
                    }
                    severity = severity_map.get(resp.severity.lower(), DiagnosticSeverity.WARNING)

                    issues.append(
                        self.create_issue(
                            description=f"[{study_id}] {resp.explanation}",
                            severity=severity,
                            recommendation=resp.recommendation or "Review against framework guidelines",
                            category="framework",
                        )
                    )

            # Add summary if alignment is low
            if response.overall_alignment < 0.7:
                issues.append(
                    self.create_issue(
                        description=f"Low alignment with {study_id} framework: {response.overall_alignment:.0%}",
                        severity=DiagnosticSeverity.WARNING,
                        recommendation=response.summary,
                        category="framework",
                    )
                )

            return issues

        except Exception as e:
            return [
                self.create_issue(
                    description=f"Failed to evaluate {study_id} framework: {e}",
                    severity=DiagnosticSeverity.INFO,
                    category="framework",
                )
            ]

    def _build_system_prompt(self, study_id: str) -> str:
        """Build system prompt for framework evaluation."""
        return f"""You are evaluating a script against the diagnostic questions from the {study_id} narratological framework.

For each question, determine:
1. Whether the script satisfies the criterion
2. If not, what's missing and how to address it
3. The severity of any issues found

Be specific and actionable in your recommendations."""

    def _build_evaluation_prompt(
        self,
        context: DiagnosticContext,
        study_id: str,
        questions: list[DiagnosticQuestion],
    ) -> str:
        """Build the evaluation prompt."""
        scenes_text = "\n".join(
            f"Scene {s.get('number')}: {s.get('summary', 'No summary')}"
            for s in context.scenes[:25]
        )

        questions_text = "\n".join(
            f"{q.id}. {q.question}\n   Valid if: {q.valid_if}"
            for q in questions[:10]  # Limit questions
        )

        return f"""Evaluate this script against the {study_id} framework diagnostic questions.

SCRIPT: {context.title}

SCENES:
{scenes_text}

DIAGNOSTIC QUESTIONS:
{questions_text}

For each question, respond with:
- question_id: The question ID
- is_valid: Whether the script passes this test
- explanation: Why it passes or fails
- severity: If failing, how serious (critical, warning, info, suggestion)
- recommendation: If failing, how to fix it

Also provide:
- overall_alignment: Float 0-1 for overall framework alignment
- summary: Brief summary of framework fit

Respond as JSON."""

    def get_available_frameworks(self) -> list[str]:
        """Get list of available framework study IDs."""
        if self.compendium is None:
            return []
        return [
            study.id
            for study in self.compendium.studies.values()
            if study.diagnostic_questions
        ]

    def get_question_count(self, study_id: str) -> int:
        """Get number of diagnostic questions for a study."""
        if self.compendium is None:
            return 0
        study = self.compendium.get_study(study_id)
        if study is None:
            return 0
        return len(study.diagnostic_questions)
