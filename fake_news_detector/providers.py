"""
providers.py — Thin wrappers around OpenAI and Gemini LLM APIs.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    """Common interface for all LLM backends."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send the prompts and return the raw text response."""


class OpenAIProvider(LLMProvider):
    """Uses the OpenAI Chat Completions API (gpt-4o-mini by default)."""

    MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install openai: pip install openai") from exc

        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY in .env or pass --api-key."
            )
        self._client = OpenAI(api_key=key)
        self._model = model or self.MODEL

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class GeminiProvider(LLMProvider):
    """Uses the Google Gemini API via the new google-genai SDK (gemini-flash-latest by default)."""

    MODEL = "gemini-flash-lite-latest"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        try:
            from google import genai  # new SDK: pip install google-genai
        except ImportError as exc:
            raise ImportError(
                "Install google-genai: pip install google-genai"
            ) from exc

        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY in .env or pass --api-key."
            )
        self._client = genai.Client(api_key=key)
        self._model_name = model or self.MODEL

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        import warnings
        from google import genai
        from google.genai import types

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                ),
            )
        return response.text or ""


def get_provider(name: str, api_key: str | None = None, model: str | None = None) -> LLMProvider:
    """Factory: return the correct provider by name ('openai' | 'gemini')."""
    name = name.lower().strip()
    if name == "openai":
        return OpenAIProvider(api_key=api_key, model=model)
    if name in ("gemini", "google"):
        return GeminiProvider(api_key=api_key, model=model)
    raise ValueError(f"Unknown provider '{name}'. Choose 'openai' or 'gemini'.")
