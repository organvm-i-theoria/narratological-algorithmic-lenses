"""Tests for the study loader."""

from pathlib import Path

import pytest

from narratological.loader import (
    get_study_summary,
    list_available_studies,
    load_compendium,
    load_study,
    load_study_from_file,
)
from narratological.models.study import Category, Compendium, Study

# Path to the actual unified JSON for integration tests
# __file__ = packages/core/tests/test_loader.py -> go up 4 levels to repo root
SPECS_PATH = Path(__file__).parent.parent.parent.parent / "specs" / "03-structured-data"
UNIFIED_JSON = SPECS_PATH / "narratological-algorithms-unified.json"


@pytest.fixture
def compendium_path():
    """Get path to the unified JSON if it exists."""
    if UNIFIED_JSON.exists():
        return UNIFIED_JSON
    pytest.skip("Unified JSON not found - skipping integration tests")


class TestLoadCompendium:
    """Tests for load_compendium function."""

    def test_load_compendium_from_path(self, compendium_path):
        """Test loading the compendium from an explicit path."""
        compendium = load_compendium(compendium_path)
        assert isinstance(compendium, Compendium)
        assert compendium.meta.study_count == 14

    def test_load_compendium_default_outside_repo_cwd(self, monkeypatch, tmp_path):
        """Default loading should work from outside the repository directory."""
        monkeypatch.chdir(tmp_path)
        compendium = load_compendium()
        assert isinstance(compendium, Compendium)
        assert compendium.meta.study_count == 14

    def test_compendium_has_all_categories(self, compendium_path):
        """Test that the compendium has all expected categories."""
        compendium = load_compendium(compendium_path)
        expected = {"Classical", "Film", "Comics", "Literature", "Interactive", "Animation"}
        actual = set(compendium.meta.categories)
        assert actual == expected

    def test_compendium_studies_count(self, compendium_path):
        """Test that the compendium has the expected number of studies."""
        compendium = load_compendium(compendium_path)
        assert len(compendium.studies) == 14


class TestLoadStudy:
    """Tests for load_study function."""

    def test_load_study_bergman(self, compendium_path):
        """Test loading the Bergman study."""
        study = load_study("bergman", compendium_path)
        assert isinstance(study, Study)
        assert study.creator == "Ingmar Bergman"
        assert study.category == Category.FILM

    def test_load_study_zelda(self, compendium_path):
        """Test loading the Zelda study."""
        study = load_study("zelda", compendium_path)
        assert study.category == Category.INTERACTIVE
        assert "Nintendo" in study.creator

    def test_load_study_not_found(self, compendium_path):
        """Test that loading a non-existent study raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            load_study("nonexistent-study", compendium_path)

    def test_load_study_has_axioms(self, compendium_path):
        """Test that loaded studies have axioms."""
        study = load_study("bergman", compendium_path)
        assert len(study.axioms) > 0
        assert all(a.id.startswith("IB-") for a in study.axioms)

    def test_load_study_has_algorithms(self, compendium_path):
        """Test that loaded studies have algorithms."""
        study = load_study("bergman", compendium_path)
        assert len(study.core_algorithms) > 0

    def test_load_study_has_diagnostic_questions(self, compendium_path):
        """Test that loaded studies have diagnostic questions."""
        study = load_study("bergman", compendium_path)
        assert len(study.diagnostic_questions) > 0


class TestStudyFromFile:
    """Tests for load_study_from_file function."""

    @pytest.fixture
    def single_study_path(self, compendium_path):
        """Get path to a single study JSON file."""
        json_extracts = SPECS_PATH / "json-extracts"
        bergman_json = json_extracts / "bergman.json"
        if bergman_json.exists():
            return bergman_json
        pytest.skip("Individual study JSON not found")

    def test_load_study_from_file(self, single_study_path):
        """Test loading a study from an individual file."""
        study = load_study_from_file(single_study_path)
        assert isinstance(study, Study)
        assert study.id == "bergman"


class TestListStudies:
    """Tests for list_available_studies function."""

    def test_list_available_studies(self, compendium_path):
        """Test listing all available study IDs."""
        ids = list_available_studies(compendium_path)
        assert len(ids) == 14
        assert "bergman" in ids
        assert "zelda" in ids
        assert "pixar" in ids


class TestGetStudySummary:
    """Tests for get_study_summary function."""

    def test_get_study_summary(self, compendium_path):
        """Test getting study summaries."""
        summaries = get_study_summary(compendium_path)
        assert len(summaries) == 14

        # Check summary structure
        for summary in summaries:
            assert "id" in summary
            assert "creator" in summary
            assert "work" in summary
            assert "category" in summary
            assert "axiom_count" in summary
            assert "algorithm_count" in summary


class TestStudyDataIntegrity:
    """Tests for data integrity of loaded studies."""

    EXPECTED_STUDIES = [
        "bergman",
        "tarkovsky",
        "zelda",
        "pixar",
        "final-fantasy",
        "alan-moore",
        "morrison",
        "kirby-new-gods",
        "tolkien",
        "ovid-metamorphoses",
        "gaiman-sandman",
        "tarantino",
        "warren-ellis",
        "david-lynch",
    ]

    @pytest.mark.parametrize("study_id", EXPECTED_STUDIES)
    def test_study_loads_successfully(self, compendium_path, study_id):
        """Test that each expected study loads successfully."""
        study = load_study(study_id, compendium_path)
        assert study.id == study_id
        assert study.creator  # Non-empty creator
        assert study.work  # Non-empty work
        assert study.category in Category

    @pytest.mark.parametrize("study_id", EXPECTED_STUDIES)
    def test_study_has_content(self, compendium_path, study_id):
        """Test that each study has meaningful content."""
        study = load_study(study_id, compendium_path)
        assert len(study.axioms) >= 1, f"{study_id} should have axioms"
        assert len(study.core_algorithms) >= 1, f"{study_id} should have algorithms"


class TestCrossReferences:
    """Tests for cross-reference data."""

    def test_sequence_pairs_exist(self, compendium_path):
        """Test that sequence pairs are loaded."""
        compendium = load_compendium(compendium_path)
        pairs = compendium.get_sequence_pairs()
        assert len(pairs) >= 7  # Expected 7 sequence pairs

    def test_sequence_pairs_reference_valid_studies(self, compendium_path):
        """Test that sequence pairs reference existing studies."""
        compendium = load_compendium(compendium_path)
        pairs = compendium.get_sequence_pairs()
        all_study_ids = set(compendium.list_study_ids())

        for pair in pairs:
            for study_id in pair.studies:
                # Normalize study ID (some may have different formats)
                normalized = study_id.replace("-", "").lower()
                matching = [
                    s for s in all_study_ids
                    if s.replace("-", "").lower() == normalized or study_id in s or s in study_id
                ]
                assert matching or study_id in all_study_ids, (
                    f"Sequence pair {pair.id} references unknown study: {study_id}"
                )

    def test_bergman_tarkovsky_pairing(self, compendium_path):
        """Test the Bergman-Tarkovsky pairing (Sequence B)."""
        compendium = load_compendium(compendium_path)
        pairs = compendium.get_sequence_pairs()

        cinematic_pair = next((p for p in pairs if p.id == "B"), None)
        assert cinematic_pair is not None
        assert "Cinematic" in cinematic_pair.name or "interiority" in cinematic_pair.name.lower()
