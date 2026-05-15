"""
groq_client.py
--------------
Thin async wrapper around the Groq Python SDK.
Raises explicitly on API errors — no silent fallbacks.
"""
from __future__ import annotations

from groq import AsyncGroq, APIStatusError, APIConnectionError, RateLimitError
from app.core.config import settings


_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    """Returns the module-level Groq async client (lazy init)."""
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Set it in your .env file before starting the server."
            )
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    return _client


async def chat_completion(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    """
    Sends a chat completion request to Groq and returns the content string.

    Raises
    ------
    RuntimeError
        On connection errors, rate limits, or API errors — with clear messages.
    """
    client = get_groq_client()

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except APIConnectionError as exc:
        raise RuntimeError(
            f"Cannot reach Groq API. Check your network connection. Error: {exc}"
        ) from exc
    except RateLimitError as exc:
        raise RuntimeError(
            f"Groq rate limit exceeded. Slow down requests or upgrade your plan. Error: {exc}"
        ) from exc
    except APIStatusError as exc:
        raise RuntimeError(
            f"Groq API returned HTTP {exc.status_code}: {exc.message}"
        ) from exc

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError(
            f"Groq returned an empty response for model '{settings.GROQ_MODEL}'. "
            "This may indicate a content policy block or a malformed request."
        )
    return content.strip()
