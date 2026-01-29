"""LLM provider protocol and implementations.

Provides a unified interface for different LLM providers (Anthropic, OpenAI)
and a MockProvider for testing without API calls.
"""

from __future__ import annotations

import json
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

if TYPE_CHECKING:
    pass


T = TypeVar("T", bound=BaseModel)


@dataclass
class CompletionResult:
    """Result from an LLM completion request."""

    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    raw_response: Any = None


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers.

    Providers must implement methods for text completion and structured output.
    """

    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None) -> CompletionResult:
        """Generate a text completion.

        Args:
            prompt: The user prompt to complete.
            system: Optional system prompt.

        Returns:
            CompletionResult with the generated text.
        """
        ...

    @abstractmethod
    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
    ) -> T:
        """Generate a structured completion matching a Pydantic schema.

        Args:
            prompt: The user prompt.
            schema: A Pydantic model class for the expected output.
            system: Optional system prompt.

        Returns:
            An instance of the schema class populated with LLM output.
        """
        ...


class AnthropicProvider:
    """LLM provider using Anthropic's Claude API.

    Requires the 'anthropic' package and ANTHROPIC_API_KEY environment variable.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ):
        """Initialize the Anthropic provider.

        Args:
            model: The Claude model to use.
            max_tokens: Maximum tokens in the response.
        """
        try:
            import anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            ) from e

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, prompt: str, *, system: str | None = None) -> CompletionResult:
        """Generate a text completion using Claude."""
        messages = [{"role": "user", "content": prompt}]

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)

        return CompletionResult(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            raw_response=response,
        )

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
    ) -> T:
        """Generate a structured completion matching a Pydantic schema."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_json}

Return ONLY the JSON object, no additional text."""

        result = self.complete(structured_prompt, system=system)
        data = json.loads(result.content)
        return schema.model_validate(data)


class OllamaProvider:
    """LLM provider using Ollama's OpenAI-compatible API.

    Works with Ollama and other OpenAI-compatible local LLM servers
    (LiteLLM, vLLM, LocalAI, etc.). No API key required for local models.
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str | None = None,
        max_tokens: int = 4096,
    ):
        """Initialize the Ollama provider.

        Args:
            model: The model to use (e.g., 'llama3.2', 'mistral', 'codellama').
            base_url: API endpoint URL. Defaults to OLLAMA_HOST env var or localhost.
            max_tokens: Maximum tokens in the response.
        """
        import os

        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "openai package required for Ollama provider. Install with: pip install openai"
            ) from e

        # Resolve base URL: parameter > env var > default
        if base_url is None:
            base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

        # Ensure /v1 suffix for OpenAI compatibility
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"

        self.client = openai.OpenAI(
            base_url=base_url,
            api_key="ollama",  # allow-secret: Ollama doesn't require a key but openai client needs one
        )
        self.model = model
        self.max_tokens = max_tokens
        self.base_url = base_url

    def complete(self, prompt: str, *, system: str | None = None) -> CompletionResult:
        """Generate a text completion using Ollama."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
        )

        content = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

        return CompletionResult(
            content=content,
            model=response.model,
            usage=usage,
            raw_response=response,
        )

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
    ) -> T:
        """Generate a structured completion matching a Pydantic schema."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_json}

Return ONLY the JSON object, no additional text or markdown code blocks."""

        result = self.complete(structured_prompt, system=system)

        # Handle potential markdown code block wrapping
        content = result.content.strip()
        if content.startswith("```"):
            # Remove markdown code block
            lines = content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)

        data = json.loads(content)
        return schema.model_validate(data)


class OpenAIProvider:
    """LLM provider using OpenAI's API.

    Requires the 'openai' package and OPENAI_API_KEY environment variable.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        base_url: str | None = None,
    ):
        """Initialize the OpenAI provider.

        Args:
            model: The OpenAI model to use.
            max_tokens: Maximum tokens in the response.
            base_url: Optional custom API endpoint for OpenAI-compatible services.
        """
        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            ) from e

        client_kwargs = {}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = openai.OpenAI(**client_kwargs)
        self.model = model
        self.max_tokens = max_tokens
        self.base_url = base_url

    def complete(self, prompt: str, *, system: str | None = None) -> CompletionResult:
        """Generate a text completion using OpenAI."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
        )

        content = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }

        return CompletionResult(
            content=content,
            model=response.model,
            usage=usage,
            raw_response=response,
        )

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
    ) -> T:
        """Generate a structured completion matching a Pydantic schema."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        structured_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{schema_json}

Return ONLY the JSON object, no additional text."""

        result = self.complete(structured_prompt, system=system)
        data = json.loads(result.content)
        return schema.model_validate(data)


@dataclass
class MockResponse:
    """A mock response for testing."""

    content: str
    structured_data: dict[str, Any] | None = None


class MockProvider:
    """Mock LLM provider for testing.

    Allows setting up expected responses and validating prompts
    without making actual API calls.
    """

    def __init__(self, default_response: str = "Mock response"):
        """Initialize the mock provider.

        Args:
            default_response: Default text response when no specific response is set.
        """
        self.default_response = default_response
        self.responses: list[MockResponse] = []
        self.calls: list[dict[str, Any]] = []
        self._response_index = 0

    def set_response(self, content: str, structured_data: dict[str, Any] | None = None) -> None:
        """Set a response to return on the next call.

        Args:
            content: Text content to return.
            structured_data: Optional structured data for structured completions.
        """
        self.responses.append(MockResponse(content, structured_data))

    def set_responses(self, responses: list[MockResponse]) -> None:
        """Set multiple responses to return in sequence.

        Args:
            responses: List of MockResponse objects.
        """
        self.responses = responses

    def get_calls(self) -> list[dict[str, Any]]:
        """Get all calls made to this provider."""
        return self.calls

    def get_last_call(self) -> dict[str, Any] | None:
        """Get the most recent call made to this provider."""
        return self.calls[-1] if self.calls else None

    def reset(self) -> None:
        """Reset call history and response queue."""
        self.calls = []
        self.responses = []
        self._response_index = 0

    def _get_next_response(self) -> MockResponse:
        """Get the next response from the queue."""
        if self._response_index < len(self.responses):
            response = self.responses[self._response_index]
            self._response_index += 1
            return response
        return MockResponse(self.default_response)

    def complete(self, prompt: str, *, system: str | None = None) -> CompletionResult:
        """Return a mock completion."""
        self.calls.append({
            "method": "complete",
            "prompt": prompt,
            "system": system,
        })

        response = self._get_next_response()
        return CompletionResult(
            content=response.content,
            model="mock-model",
            usage={"input_tokens": len(prompt.split()), "output_tokens": 10},
        )

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system: str | None = None,
    ) -> T:
        """Return a mock structured completion."""
        self.calls.append({
            "method": "complete_structured",
            "prompt": prompt,
            "schema": schema,
            "system": system,
        })

        response = self._get_next_response()
        if response.structured_data:
            return schema.model_validate(response.structured_data)

        # Generate minimal valid data from schema
        schema_info = schema.model_json_schema()
        minimal_data = self._generate_minimal_data(schema_info)
        return schema.model_validate(minimal_data)

    def _generate_minimal_data(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate minimal valid data from a JSON schema."""
        result: dict[str, Any] = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            if prop_name in required:
                prop_type = prop_schema.get("type", "string")
                if prop_type == "string":
                    result[prop_name] = f"mock_{prop_name}"
                elif prop_type == "integer":
                    result[prop_name] = 0
                elif prop_type == "number":
                    result[prop_name] = 0.0
                elif prop_type == "boolean":
                    result[prop_name] = False
                elif prop_type == "array":
                    result[prop_name] = []
                elif prop_type == "object":
                    result[prop_name] = {}
                else:
                    result[prop_name] = None

        return result


def get_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    """Factory function to get an LLM provider by name.

    Args:
        provider_name: One of 'ollama', 'anthropic', 'openai', or 'mock'.
        **kwargs: Additional arguments to pass to the provider constructor.

    Returns:
        An LLMProvider instance.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    providers = {
        "ollama": OllamaProvider,
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "mock": MockProvider,
    }

    if provider_name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")

    return providers[provider_name](**kwargs)
