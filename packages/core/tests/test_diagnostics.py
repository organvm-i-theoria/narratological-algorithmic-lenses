"""Tests for diagnostic runners.

Tests cover:
- Diagnostic context and models
- Causal binding diagnostic
- Reorderability diagnostic
- Necessity diagnostic
- Information economy diagnostic
- Diagnostic runner orchestration
"""

import pytest

from narratological.diagnostics import (
    CausalBindingDiagnostic,
    DiagnosticContext,
    DiagnosticMetrics,
    DiagnosticRunner,
    DiagnosticThresholds,
    DiagnosticType,
    FrameworkDiagnostic,
    InformationEconomyDiagnostic,
    NecessityDiagnostic,
    ReorderabilityDiagnostic,
    SceneTransition,
    create_diagnostic_runner,
)
from narratological.llm import MockProvider
from narratological.loader import load_compendium
from narratological.models.analysis import ConnectorType
from narratological.models.report import DiagnosticReport, DiagnosticSeverity

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    return MockProvider()


@pytest.fixture
def simple_context():
    """Create a simple diagnostic context."""
    return DiagnosticContext(
        title="Test Script",
        scenes=[
            {
                "number": 1,
                "slug": "INT. HOUSE",
                "summary": "Introduction",
                "function": "SETUP",
                "connector": "THEREFORE",
                "characters": ["JOHN"],
                "tension": 3,
            },
            {
                "number": 2,
                "slug": "EXT. STREET",
                "summary": "Inciting incident",
                "function": "INCITE",
                "connector": "BUT",
                "characters": ["JOHN"],
                "tension": 6,
            },
            {
                "number": 3,
                "slug": "INT. OFFICE",
                "summary": "Complications",
                "function": "COMPLICATE",
                "connector": "THEREFORE",
                "characters": ["JOHN", "BOSS"],
                "tension": 7,
            },
            {
                "number": 4,
                "slug": "INT. HOUSE",
                "summary": "Climax",
                "function": "CLIMAX",
                "connector": "THEREFORE",
                "characters": ["JOHN", "MARY"],
                "tension": 10,
            },
            {
                "number": 5,
                "slug": "EXT. PARK",
                "summary": "Resolution",
                "function": "RESOLVE",
                "connector": None,
                "characters": ["JOHN"],
                "tension": 4,
            },
        ],
        characters=["JOHN", "MARY", "BOSS"],
        beat_map_available=True,
    )


@pytest.fixture
def weak_causal_context():
    """Create a context with weak causal binding."""
    return DiagnosticContext(
        title="Weak Script",
        scenes=[
            {
                "number": 1,
                "slug": "Scene 1",
                "summary": "Something happens",
                "function": "SETUP",
                "connector": "AND_THEN",
                "characters": [],
                "tension": 5,
            },
            {
                "number": 2,
                "slug": "Scene 2",
                "summary": "Something else happens",
                "function": "COMPLICATE",
                "connector": "AND_THEN",
                "characters": [],
                "tension": 5,
            },
            {
                "number": 3,
                "slug": "Scene 3",
                "summary": "Another thing happens",
                "function": "RESOLVE",
                "connector": None,
                "characters": [],
                "tension": 5,
            },
        ],
        beat_map_available=True,
    )


# =============================================================================
# Test DiagnosticContext
# =============================================================================


class TestDiagnosticContext:
    """Tests for DiagnosticContext model."""

    def test_context_creation(self):
        """Test creating diagnostic context."""
        context = DiagnosticContext(
            title="Test",
            scenes=[{"number": 1, "summary": "Scene 1"}],
        )
        assert context.title == "Test"
        assert len(context.scenes) == 1

    def test_context_from_script(self):
        """Test creating context from Script model."""
        from narratological.models.analysis import BeatFunction, Scene, Script

        script = Script(
            title="Test Script",
            scenes=[
                Scene(
                    number=1,
                    slug="INT. ROOM",
                    summary="Test scene",
                    function=BeatFunction.SETUP,
                ),
            ],
        )

        context = DiagnosticContext.from_script(script)

        assert context.title == "Test Script"
        assert len(context.scenes) == 1
        assert context.scenes[0]["function"] == "SETUP"


# =============================================================================
# Test DiagnosticThresholds
# =============================================================================


class TestDiagnosticThresholds:
    """Tests for DiagnosticThresholds model."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        thresholds = DiagnosticThresholds()

        assert thresholds.causal_binding_excellent == 0.90
        assert thresholds.causal_binding_good == 0.80
        assert thresholds.causal_binding_critical == 0.40

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        thresholds = DiagnosticThresholds(
            causal_binding_excellent=0.95,
            causal_binding_good=0.85,
        )

        assert thresholds.causal_binding_excellent == 0.95
        assert thresholds.causal_binding_good == 0.85


# =============================================================================
# Test DiagnosticMetrics
# =============================================================================


class TestDiagnosticMetrics:
    """Tests for DiagnosticMetrics model."""

    def test_compute_health_excellent(self):
        """Test health computation with excellent scores."""
        metrics = DiagnosticMetrics(
            causal_binding_ratio=0.95,
            reorderability_score=0.02,
            necessity_score=0.98,
            information_economy_score=0.95,
        )
        metrics.compute_health()

        assert metrics.causal_binding_health == "Excellent"
        assert metrics.overall_health == "Excellent"

    def test_compute_health_poor(self):
        """Test health computation with poor scores."""
        metrics = DiagnosticMetrics(
            causal_binding_ratio=0.30,
            reorderability_score=0.60,
            necessity_score=0.45,
            information_economy_score=0.35,
        )
        metrics.compute_health()

        assert metrics.causal_binding_health == "Critical"
        assert metrics.overall_health in ("Poor", "Critical")


# =============================================================================
# Test CausalBindingDiagnostic
# =============================================================================


class TestCausalBindingDiagnostic:
    """Tests for CausalBindingDiagnostic."""

    def test_diagnostic_type(self):
        """Test diagnostic type."""
        diagnostic = CausalBindingDiagnostic()
        assert diagnostic.diagnostic_type == DiagnosticType.CAUSAL_BINDING

    def test_calculate_score_strong_binding(self, simple_context):
        """Test score calculation with strong causal binding."""
        diagnostic = CausalBindingDiagnostic()
        score = diagnostic.calculate_score(simple_context)

        # 4 causal connectors (THEREFORE, BUT, THEREFORE, THEREFORE)
        # All causal, so score should be 1.0
        assert score == 1.0

    def test_calculate_score_weak_binding(self, weak_causal_context):
        """Test score calculation with weak causal binding."""
        diagnostic = CausalBindingDiagnostic()
        score = diagnostic.calculate_score(weak_causal_context)

        # 2 AND_THEN connectors, 0 causal
        # Score should be 0.0
        assert score == 0.0

    def test_run_diagnostic(self, simple_context):
        """Test running the diagnostic."""
        diagnostic = CausalBindingDiagnostic()
        issues = diagnostic.run(simple_context)

        assert isinstance(issues, list)
        # Should have at least the summary issue
        assert len(issues) >= 1

    def test_run_diagnostic_weak_binding(self, weak_causal_context):
        """Test running diagnostic with weak binding."""
        diagnostic = CausalBindingDiagnostic()
        issues = diagnostic.run(weak_causal_context)

        # Should have issues for AND_THEN transitions
        weak_issues = [
            i for i in issues
            if "AND THEN" in i.description or "weak" in i.description.lower()
        ]
        assert len(weak_issues) >= 1


# =============================================================================
# Test ReorderabilityDiagnostic
# =============================================================================


class TestReorderabilityDiagnostic:
    """Tests for ReorderabilityDiagnostic."""

    def test_diagnostic_type(self):
        """Test diagnostic type."""
        diagnostic = ReorderabilityDiagnostic()
        assert diagnostic.diagnostic_type == DiagnosticType.REORDERABILITY

    def test_calculate_score(self, simple_context):
        """Test score calculation."""
        diagnostic = ReorderabilityDiagnostic()
        score = diagnostic.calculate_score(simple_context)

        # Score is proportion of reorderable scenes
        assert 0.0 <= score <= 1.0

    def test_run_diagnostic(self, simple_context):
        """Test running the diagnostic."""
        diagnostic = ReorderabilityDiagnostic()
        issues = diagnostic.run(simple_context)

        assert isinstance(issues, list)


# =============================================================================
# Test NecessityDiagnostic
# =============================================================================


class TestNecessityDiagnostic:
    """Tests for NecessityDiagnostic."""

    def test_diagnostic_type(self):
        """Test diagnostic type."""
        diagnostic = NecessityDiagnostic()
        assert diagnostic.diagnostic_type == DiagnosticType.NECESSITY

    def test_calculate_score(self, simple_context):
        """Test score calculation."""
        diagnostic = NecessityDiagnostic()
        score = diagnostic.calculate_score(simple_context)

        # Score is proportion of necessary scenes
        assert 0.0 <= score <= 1.0

    def test_run_diagnostic(self, simple_context):
        """Test running the diagnostic."""
        diagnostic = NecessityDiagnostic()
        issues = diagnostic.run(simple_context)

        assert isinstance(issues, list)


# =============================================================================
# Test InformationEconomyDiagnostic
# =============================================================================


class TestInformationEconomyDiagnostic:
    """Tests for InformationEconomyDiagnostic."""

    def test_diagnostic_type(self):
        """Test diagnostic type."""
        diagnostic = InformationEconomyDiagnostic()
        assert diagnostic.diagnostic_type == DiagnosticType.INFORMATION_ECONOMY

    def test_requires_llm(self, simple_context):
        """Test that info economy requires LLM for meaningful analysis."""
        diagnostic = InformationEconomyDiagnostic()
        issues = diagnostic.run(simple_context)

        # Should return info message about needing LLM
        assert len(issues) >= 1

    def test_run_with_llm(self, simple_context, mock_provider):
        """Test running with LLM provider."""
        mock_provider.set_response(
            "",
            structured_data={
                "redundant_expositions": [],
                "missing_setups": [],
                "efficiency_score": 0.85,
                "recommendations": [],
            },
        )

        diagnostic = InformationEconomyDiagnostic(provider=mock_provider)
        issues = diagnostic.run(simple_context)

        assert isinstance(issues, list)


# =============================================================================
# Test FrameworkDiagnostic
# =============================================================================


class TestFrameworkDiagnostic:
    """Tests for framework-based diagnostics."""

    @pytest.fixture
    def framework_diagnostic(self):
        """Create a framework diagnostic with a loaded compendium."""
        return FrameworkDiagnostic(compendium=load_compendium())

    def test_unknown_study_without_provider_returns_info_issue(
        self,
        framework_diagnostic,
        simple_context,
    ):
        """Unknown study IDs should not crash when no provider is configured."""
        issues = framework_diagnostic.run(simple_context, study_ids=["does-not-exist"])

        assert len(issues) == 1
        assert issues[0].severity == DiagnosticSeverity.INFO
        assert "provider" in issues[0].description.lower()

    def test_unknown_study_with_provider_returns_info_issue(
        self,
        simple_context,
    ):
        """Unknown study IDs should be handled safely with a provider as well."""
        diagnostic = FrameworkDiagnostic(
            provider=MockProvider(),
            compendium=load_compendium(),
        )
        issues = diagnostic.run(simple_context, study_ids=["does-not-exist"])

        assert len(issues) == 1
        assert issues[0].severity == DiagnosticSeverity.INFO
        assert "not found" in issues[0].description.lower()

    def test_get_available_frameworks_returns_study_ids(self, framework_diagnostic):
        """Available frameworks should be returned as non-empty study ID strings."""
        frameworks = framework_diagnostic.get_available_frameworks()

        assert frameworks
        assert all(isinstance(study_id, str) for study_id in frameworks)

    def test_get_question_count_unknown_study_is_zero(self, framework_diagnostic):
        """Question count should be deterministic for unknown studies."""
        assert framework_diagnostic.get_question_count("does-not-exist") == 0


# =============================================================================
# Test DiagnosticRunner
# =============================================================================


class TestDiagnosticRunner:
    """Tests for DiagnosticRunner orchestration."""

    def test_runner_creation(self):
        """Test creating diagnostic runner."""
        runner = DiagnosticRunner()
        assert runner.provider is None
        assert runner.thresholds is not None

    def test_runner_with_provider(self, mock_provider):
        """Test creating runner with provider."""
        runner = DiagnosticRunner(provider=mock_provider)
        assert runner.provider == mock_provider

    def test_run_causal(self, simple_context):
        """Test running causal binding diagnostic."""
        runner = DiagnosticRunner()
        score, issues = runner.run_causal(simple_context)

        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_run_reorderability(self, simple_context):
        """Test running reorderability diagnostic."""
        runner = DiagnosticRunner()
        score, issues = runner.run_reorderability(simple_context)

        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_run_necessity(self, simple_context):
        """Test running necessity diagnostic."""
        runner = DiagnosticRunner()
        score, issues = runner.run_necessity(simple_context)

        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_run_all(self, simple_context):
        """Test running all diagnostics."""
        runner = DiagnosticRunner()
        report = runner.run_all(simple_context, include_framework=False)

        assert isinstance(report, DiagnosticReport)
        assert report.title == "Test Script"
        assert 0.0 <= report.causal_binding_ratio <= 1.0
        assert report.overall_health in (
            "Excellent", "Good", "Fair", "Poor", "Critical"
        )

    def test_run_single(self, simple_context):
        """Test running single diagnostic by type."""
        runner = DiagnosticRunner()
        score, issues = runner.run_single(
            DiagnosticType.CAUSAL_BINDING,
            simple_context,
        )

        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_run_single_by_string(self, simple_context):
        """Test running single diagnostic by string type."""
        runner = DiagnosticRunner()
        score, issues = runner.run_single("causal_binding", simple_context)

        assert 0.0 <= score <= 1.0

    def test_priority_fixes_generation(self, weak_causal_context):
        """Test that priority fixes are generated."""
        runner = DiagnosticRunner()
        report = runner.run_all(weak_causal_context, include_framework=False)

        # Should have priority fixes for weak script
        # (might be empty if all issues are just score summaries)
        assert isinstance(report.priority_fixes, list)


# =============================================================================
# Test create_diagnostic_runner Factory
# =============================================================================


class TestCreateDiagnosticRunner:
    """Tests for create_diagnostic_runner factory."""

    def test_create_runner(self):
        """Test creating runner via factory."""
        runner = create_diagnostic_runner()
        assert isinstance(runner, DiagnosticRunner)

    def test_create_runner_with_provider(self, mock_provider):
        """Test creating runner with provider."""
        runner = create_diagnostic_runner(provider=mock_provider)
        assert runner.provider == mock_provider

    def test_create_runner_with_thresholds(self):
        """Test creating runner with custom thresholds."""
        thresholds = DiagnosticThresholds(causal_binding_excellent=0.95)
        runner = create_diagnostic_runner(thresholds=thresholds)
        assert runner.thresholds.causal_binding_excellent == 0.95


# =============================================================================
# Test SceneTransition
# =============================================================================


class TestSceneTransition:
    """Tests for SceneTransition model."""

    def test_transition_creation(self):
        """Test creating scene transition."""
        transition = SceneTransition(
            from_scene=1,
            to_scene=2,
            connector=ConnectorType.THEREFORE,
            is_causal=True,
        )

        assert transition.from_scene == 1
        assert transition.to_scene == 2
        assert transition.connector == ConnectorType.THEREFORE
        assert transition.is_causal is True

    def test_transition_non_causal(self):
        """Test non-causal transition."""
        transition = SceneTransition(
            from_scene=1,
            to_scene=2,
            connector=ConnectorType.AND_THEN,
            is_causal=False,
        )

        assert transition.is_causal is False


# =============================================================================
# Test Issue Severity Classification
# =============================================================================


class TestIssueSeverity:
    """Tests for issue severity classification."""

    def test_causal_binding_severity_excellent(self):
        """Test severity for excellent causal binding."""
        diagnostic = CausalBindingDiagnostic()
        severity = diagnostic._get_severity_for_causal_binding(0.95)
        assert severity == DiagnosticSeverity.INFO

    def test_causal_binding_severity_good(self):
        """Test severity for good causal binding."""
        diagnostic = CausalBindingDiagnostic()
        severity = diagnostic._get_severity_for_causal_binding(0.85)
        assert severity == DiagnosticSeverity.SUGGESTION

    def test_causal_binding_severity_warning(self):
        """Test severity for adequate causal binding."""
        diagnostic = CausalBindingDiagnostic()
        severity = diagnostic._get_severity_for_causal_binding(0.65)
        assert severity == DiagnosticSeverity.WARNING

    def test_causal_binding_severity_critical(self):
        """Test severity for poor causal binding."""
        diagnostic = CausalBindingDiagnostic()
        severity = diagnostic._get_severity_for_causal_binding(0.30)
        assert severity == DiagnosticSeverity.CRITICAL
