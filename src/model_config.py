"""Central model-provider configuration for the workshop.

The MCP server does not care which model sits on the other end of the
conversation — that is the whole point of the protocol. To make that concrete,
every client in this workshop picks its model here, and you switch providers by
editing one line in `.env`:

    MCP_WORKSHOP_PROVIDER=ollama   # ollama | google | grok | foundry

Two entry points are exposed, because the workshop connects to models two ways:

* `get_openai_client()`  — used by the hand-written loop in module 3.
  Every supported provider speaks the OpenAI Chat Completions API, so the same
  loop works for all four.
* `get_pydantic_model()` — used by Pydantic AI in modules 4 and 5.
  Imported lazily so that this module still works in the server virtualenv,
  which deliberately does not have Pydantic AI installed.

See `docs/models.md` for signup instructions and current model names.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

PROVIDERS = ("ollama", "google", "grok", "foundry")

# Sensible defaults, all known to support tool calling at time of writing.
# Model names move fast — override with MCP_WORKSHOP_MODEL in your .env.
DEFAULT_MODELS = {
    "ollama": "qwen3:4b",
    "google": "gemini-flash-latest",
    "grok": "grok-4-fast",
    "foundry": "gpt-4o-mini",
}

OPENAI_COMPATIBLE_BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "grok": "https://api.x.ai/v1",
    # foundry is per-deployment, so it comes from AZURE_OPENAI_ENDPOINT
}

API_KEY_VARS = {
    "ollama": None,  # local, no key needed
    "google": "GOOGLE_API_KEY",
    "grok": "XAI_API_KEY",
    "foundry": "AZURE_OPENAI_API_KEY",
}


class ConfigError(RuntimeError):
    """Raised when the selected provider is missing something it needs."""


@dataclass(frozen=True)
class ModelChoice:
    """The resolved provider and model name."""

    provider: str
    model: str


def get_choice() -> ModelChoice:
    """Read the configured provider and model from the environment."""
    provider = os.getenv("MCP_WORKSHOP_PROVIDER", "ollama").strip().lower()
    if provider not in PROVIDERS:
        raise ConfigError(
            f"Unknown MCP_WORKSHOP_PROVIDER={provider!r}. "
            f"Choose one of: {', '.join(PROVIDERS)}."
        )
    model = os.getenv("MCP_WORKSHOP_MODEL", "").strip() or DEFAULT_MODELS[provider]
    return ModelChoice(provider=provider, model=model)


def _require_key(provider: str) -> str:
    var = API_KEY_VARS[provider]
    if var is None:
        return "not-needed"
    key = os.getenv(var, "").strip()
    if not key:
        raise ConfigError(
            f"Provider {provider!r} needs {var} to be set. "
            f"Copy .env.example to .env and fill it in — see docs/models.md."
        )
    return key


def get_openai_client(choice: ModelChoice | None = None):
    """Return an OpenAI-compatible client for the configured provider.

    Used by the hand-written agent loop in module 3. Returns the client and the
    model name, because the caller needs both.
    """
    from openai import AsyncOpenAI

    choice = choice or get_choice()
    provider = choice.provider

    if provider == "foundry":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        if not endpoint:
            raise ConfigError(
                "Provider 'foundry' needs AZURE_OPENAI_ENDPOINT, e.g. "
                "https://<your-resource>.openai.azure.com/openai/v1/"
            )
        base_url = endpoint
    else:
        base_url = OPENAI_COMPATIBLE_BASE_URLS[provider]

    # Ollama requires the api_key argument to be present but never checks it.
    api_key = _require_key(provider) if provider != "ollama" else "ollama"

    return AsyncOpenAI(base_url=base_url, api_key=api_key), choice.model


def get_pydantic_model(choice: ModelChoice | None = None):
    """Return a Pydantic AI `Model` for the configured provider.

    Used by modules 4 and 5. Pydantic AI is imported inside the function so this
    module can also be imported from the server virtualenv, where Pydantic AI is
    intentionally absent.
    """
    choice = choice or get_choice()
    provider = choice.provider

    if provider == "ollama":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.ollama import OllamaProvider

        base_url = os.getenv("OLLAMA_BASE_URL", OPENAI_COMPATIBLE_BASE_URLS["ollama"])
        return OpenAIChatModel(choice.model, provider=OllamaProvider(base_url=base_url))

    if provider == "google":
        from pydantic_ai.models.google import GoogleModel
        from pydantic_ai.providers.google import GoogleProvider

        return GoogleModel(choice.model, provider=GoogleProvider(api_key=_require_key(provider)))

    if provider == "grok":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider

        # xAI is OpenAI-compatible, so we avoid pulling in the extra xai-sdk
        # dependency that the native XaiProvider requires.
        return OpenAIChatModel(
            choice.model,
            provider=OpenAIProvider(
                base_url=OPENAI_COMPATIBLE_BASE_URLS["grok"],
                api_key=_require_key(provider),
            ),
        )

    if provider == "foundry":
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.azure import AzureProvider

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        if not endpoint:
            raise ConfigError("Provider 'foundry' needs AZURE_OPENAI_ENDPOINT.")
        return OpenAIChatModel(
            choice.model,
            provider=AzureProvider(
                azure_endpoint=endpoint,
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                api_key=_require_key(provider),
            ),
        )

    raise ConfigError(f"Unhandled provider {provider!r}")


def describe() -> str:
    """One-line summary of the active configuration, handy for printing."""
    choice = get_choice()
    return f"provider={choice.provider} model={choice.model}"
