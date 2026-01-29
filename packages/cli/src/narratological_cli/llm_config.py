"""LLM configuration and provider utilities for CLI commands.

Provides a unified interface for configuring LLM providers across
all CLI commands with consistent flag handling and environment variables.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any

from rich.console import Console

console = Console()


class ProviderType(str, Enum):
    """Available LLM provider types."""

    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    MOCK = "mock"


# Default models for each provider
DEFAULT_MODELS = {
    ProviderType.OLLAMA: "llama3.2",
    ProviderType.ANTHROPIC: "claude-sonnet-4-20250514",
    ProviderType.OPENAI: "gpt-4o",
    ProviderType.MOCK: "mock-model",
}


def get_provider(
    provider: str = "ollama",
    model: str | None = None,
    base_url: str | None = None,
    verbose: bool = False,
) -> Any:
    """Get an LLM provider with the specified configuration.

    Provider priority (OSS-first):
    1. Ollama (default) - Local models, no API key needed
    2. OpenAI-compatible - Works with LiteLLM, vLLM, LocalAI
    3. Anthropic - Claude models
    4. Mock - Testing without any LLM

    Environment variables checked:
    - OLLAMA_HOST: Ollama server URL (default: http://localhost:11434)
    - ANTHROPIC_API_KEY: Required for Anthropic provider
    - OPENAI_API_KEY: Required for OpenAI provider

    Args:
        provider: Provider name ('ollama', 'anthropic', 'openai', 'mock').
        model: Model name override. If None, uses provider default.
        base_url: Custom API endpoint for OpenAI-compatible providers.
        verbose: Whether to print provider configuration details.

    Returns:
        An LLMProvider instance.

    Raises:
        ValueError: If the provider is not recognized.
        ImportError: If required packages are not installed.
        EnvironmentError: If required API keys are not set.
    """
    from narratological.llm.providers import get_provider as core_get_provider

    # Normalize provider name
    try:
        provider_type = ProviderType(provider.lower())
    except ValueError:
        valid = ", ".join(p.value for p in ProviderType)
        raise ValueError(f"Unknown provider '{provider}'. Available: {valid}")

    # Determine model
    if model is None:
        model = DEFAULT_MODELS[provider_type]

    # Check for required API keys
    _check_api_key(provider_type)

    # Build provider kwargs
    kwargs: dict[str, Any] = {"model": model}

    if provider_type == ProviderType.OLLAMA:
        if base_url:
            kwargs["base_url"] = base_url
        # OLLAMA_HOST is handled by the provider itself

    elif provider_type == ProviderType.OPENAI:
        if base_url:
            kwargs["base_url"] = base_url

    elif provider_type == ProviderType.ANTHROPIC:
        # Anthropic doesn't support base_url override
        pass

    elif provider_type == ProviderType.MOCK:
        # Mock provider uses default_response
        kwargs = {"default_response": "Mock response from CLI"}

    if verbose:
        _print_provider_info(provider_type, model, base_url)

    return core_get_provider(provider_type.value, **kwargs)


def _check_api_key(provider_type: ProviderType) -> None:
    """Check if required API keys are set for the provider.

    Args:
        provider_type: The provider type to check.

    Raises:
        EnvironmentError: If required API key is not set.
    """
    if provider_type == ProviderType.ANTHROPIC:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Set it with: export ANTHROPIC_API_KEY=your-key-here"
            )

    elif provider_type == ProviderType.OPENAI:
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it with: export OPENAI_API_KEY=your-key-here"
            )

    # Ollama and Mock don't require API keys


def _print_provider_info(
    provider_type: ProviderType,
    model: str,
    base_url: str | None,
) -> None:
    """Print provider configuration details."""
    console.print(f"[dim]Provider: {provider_type.value}[/dim]")
    console.print(f"[dim]Model: {model}[/dim]")
    if base_url:
        console.print(f"[dim]Base URL: {base_url}[/dim]")


def provider_help_text() -> str:
    """Generate help text for provider options."""
    return (
        "LLM provider to use. Options:\n"
        "  - ollama: Local models via Ollama (default, no API key needed)\n"
        "  - anthropic: Claude models (requires ANTHROPIC_API_KEY)\n"
        "  - openai: OpenAI models (requires OPENAI_API_KEY)\n"
        "  - mock: Mock responses for testing"
    )


def model_help_text() -> str:
    """Generate help text for model option."""
    defaults = ", ".join(f"{p.value}={m}" for p, m in DEFAULT_MODELS.items() if p != ProviderType.MOCK)
    return f"Model name override. Defaults: {defaults}"


def base_url_help_text() -> str:
    """Generate help text for base-url option."""
    return (
        "Custom API endpoint for OpenAI-compatible providers. "
        "Works with Ollama, LiteLLM, vLLM, LocalAI, etc."
    )


# Common CLI options as a convenient re-export
# These can be used with typer.Option in command definitions
PROVIDER_OPTION_HELP = provider_help_text()
MODEL_OPTION_HELP = model_help_text()
BASE_URL_OPTION_HELP = base_url_help_text()
