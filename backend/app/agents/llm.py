"""Gemini wrapper using the current google-genai SDK."""
import asyncio
import json
import re

from google import genai

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)

_MAX_RETRIES = 3
_RETRY_DELAY = 2.0


def _extract_json(text: str) -> dict:
    """Extract first JSON object from a string (handles markdown code fences)."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON found in response: {text[:200]}")


async def call_gemini(system_prompt: str, user_content: str) -> dict:
    """Send a prompt to Gemini and parse the JSON response. Retries on 503."""
    full_prompt = f"{system_prompt}\n\n---\n\n{user_content}"
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = await _client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=full_prompt,
            )
            return _extract_json(response.text)
        except Exception as e:
            last_exc = e
            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_RETRY_DELAY)
    raise last_exc


async def call_gemini_text(system_prompt: str, user_content: str) -> str:
    """Send a prompt to Gemini and return raw text. Retries on 503."""
    full_prompt = f"{system_prompt}\n\n---\n\n{user_content}"
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = await _client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as e:
            last_exc = e
            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(_RETRY_DELAY)
    raise last_exc
