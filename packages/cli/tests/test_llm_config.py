"""Tests for the LLM configuration module."""

import os
from unittest.mock import patch

import pytest

from narratological_cli.llm_config import (
    DEFAULT_MODELS,
    ProviderType,
    get_provider,
)


class TestProviderType:
    """Tests for ProviderType enum."""

    def test_provider_types_exist(self):
        """Test that all expected provider types exist."""
        assert ProviderType.OLLAMA == "ollama"
        assert ProviderType.ANTHROPIC == "anthropic"
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.MOCK == "mock"


class TestDefaultModels:
    """Tests for default model configuration."""

    def test_default_models_defined(self):
        """Test that default models are defined for each provider."""
        assert ProviderType.OLLAMA in DEFAULT_MODELS
        assert ProviderType.ANTHROPIC in DEFAULT_MODELS
        assert ProviderType.OPENAI in DEFAULT_MODELS
        assert ProviderType.MOCK in DEFAULT_MODELS

    def test_default_model_values(self):
        """Test specific default model values."""
        assert DEFAULT_MODELS[ProviderType.OLLAMA] == "llama3.2"
        assert "claude" in DEFAULT_MODELS[ProviderType.ANTHROPIC]
        assert "gpt" in DEFAULT_MODELS[ProviderType.OPENAI]


class TestGetProvider:
    """Tests for get_provider function."""

    def test_get_mock_provider(self):
        """Test getting a mock provider."""
        provider = get_provider("mock")
        assert provider is not None

        # Verify it's a MockProvider
        result = provider.complete("test prompt")
        assert result is not None

    def test_get_provider_invalid_name(self):
        """Test error handling for invalid provider name."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("invalid_provider")

    def test_get_provider_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        provider1 = get_provider("mock")
        provider2 = get_provider("MOCK")
        provider3 = get_provider("Mock")

        assert provider1 is not None
        assert provider2 is not None
        assert provider3 is not None

    def test_get_provider_with_model_override(self):
        """Test getting a provider with model override."""
        provider = get_provider("mock", model="custom-model")
        assert provider is not None

    def test_get_provider_anthropic_without_key(self):
        """Test that Anthropic provider requires API key."""
        # Ensure no API key is set
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(EnvironmentError, match="ANTHROPIC_API_KEY"):
                get_provider("anthropic")

    def test_get_provider_openai_without_key(self):
        """Test that OpenAI provider requires API key."""
        # Ensure no API key is set
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
                get_provider("openai")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_provider_anthropic_with_key(self):
        """Test that Anthropic provider works with API key."""
        # This test may still fail if the anthropic package isn't installed
        # or if the client validates the key, but it shouldn't raise EnvironmentError
        try:
            provider = get_provider("anthropic")
            assert provider is not None
        except ImportError:
            pytest.skip("anthropic package not installed")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_get_provider_openai_with_key(self):
        """Test that OpenAI provider works with API key."""
        try:
            provider = get_provider("openai")
            assert provider is not None
        except ImportError:
            pytest.skip("openai package not installed")
