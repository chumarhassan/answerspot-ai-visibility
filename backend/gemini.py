"""Gemini client — the ONLY tracked AI platform for the MVP (free tier, §4).

Design notes:
  * Uses the free Google AI Studio REST endpoint. Key is read server-side only.
  * The free tier is quota-limited (~15 req/min, ~1,500 req/day as of mid-2026) and
    those numbers change — so we never hardcode quota as fact; we react to HTTP 429
    with exponential backoff (honoring Retry-After) rather than failing hard (§4, §8).
  * The same key also powers internal copy generation (insights/fix wording), avoiding
    a second paid dependency (§10 decision).
  * Parsing helpers (`parse_business_list`, `match_target`) are PURE so they can be
    unit-tested without the network (tests/test_audit_parse.py).
"""
from __future__ import annotations

import asyncio
import json
import re

import httpx

from config import get_settings

settings = get_settings()

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
_MAX_RETRIES = 4
_BASE_BACKOFF_SECONDS = 2.0


class GeminiError(Exception):
    """Raised when a Gemini call cannot be completed (config, network, or quota)."""


class GeminiNotConfigured(GeminiError):
    pass


async def query_gemini(prompt: str, *, as_json: bool = False, temperature: float = 0.3) -> str:
    """Send a single prompt to Gemini and return the model's text.

    Retries with exponential backoff on 429 (rate limit) and 5xx. Raises GeminiError
    if the key is missing or all retries are exhausted — callers must treat this as a
    failed check and never substitute fake data (§8).
    """
    if not settings.gemini_configured:
        raise GeminiNotConfigured("GEMINI_API_KEY is not set on the server")

    url = f"{_BASE_URL}/{settings.gemini_model}:generateContent"
    body: dict = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if as_json:
        body["generationConfig"]["responseMimeType"] = "application/json"

    last_error: str = "unknown error"
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(_MAX_RETRIES):
            try:
                resp = await client.post(
                    url, params={"key": settings.gemini_api_key}, json=body
                )
            except httpx.RequestError as exc:
                last_error = f"network error: {exc}"
                await _sleep_backoff(attempt)
                continue

            if resp.status_code == 200:
                return _extract_text(resp.json())

            if resp.status_code == 429 or resp.status_code >= 500:
                # Rate-limited or transient server error — back off and retry.
                retry_after = _retry_after_seconds(resp)
                last_error = f"HTTP {resp.status_code} (rate-limited/transient)"
                await _sleep_backoff(attempt, retry_after)
                continue

            # 4xx other than 429 → not retryable (bad key, bad request).
            raise GeminiError(f"Gemini request failed: HTTP {resp.status_code} {resp.text[:200]}")

    raise GeminiError(f"Gemini unavailable after {_MAX_RETRIES} attempts: {last_error}")


async def _sleep_backoff(attempt: int, retry_after: float | None = None) -> None:
    delay = retry_after if retry_after is not None else _BASE_BACKOFF_SECONDS * (2**attempt)
    await asyncio.sleep(min(delay, 30.0))


def _retry_after_seconds(resp: httpx.Response) -> float | None:
    header = resp.headers.get("Retry-After")
    if header and header.isdigit():
        return float(header)
    return None


def _extract_text(payload: dict) -> str:
    """Pull the text out of a Gemini generateContent response."""
    try:
        candidates = payload["candidates"]
        if not candidates:
            return ""
        parts = candidates[0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, TypeError):
        return ""


# ── Pure parsing helpers (unit-tested) ────────────────────────────────────────
def build_audit_query(category: str, city: str) -> str:
    return f"best {category} in {city}"


def audit_prompt(category: str, city: str) -> str:
    """Prompt that asks Gemini who it would recommend, as a ranked JSON list."""
    query = build_audit_query(category, city)
    return (
        f'A customer asks an AI assistant: "{query}".\n'
        "List the specific local businesses you would actually recommend, in ranked "
        "order (best first). Use real business names only; do not invent names. If you "
        "cannot name specific local businesses, return an empty list.\n"
        'Respond with JSON of the exact form: {"businesses": ["Name 1", "Name 2", ...]}'
    )


def parse_business_list(raw: str) -> list[str]:
    """Parse a ranked business-name list out of Gemini's response.

    Tolerant of markdown code fences and stray prose around the JSON. Returns [] if
    nothing parseable is found (a valid "no businesses named" result).
    """
    if not raw:
        return []

    text = raw.strip()
    # Strip ```json ... ``` fences if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    # Try to locate a JSON object even if surrounded by prose.
    candidate = text
    brace = re.search(r"\{.*\}", text, re.DOTALL)
    if brace:
        candidate = brace.group(0)

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return []

    businesses = data.get("businesses") if isinstance(data, dict) else None
    if not isinstance(businesses, list):
        return []

    cleaned: list[str] = []
    seen: set[str] = set()
    for item in businesses:
        if not isinstance(item, str):
            continue
        name = " ".join(item.strip().split())
        if name and name.lower() not in seen:
            cleaned.append(name)
            seen.add(name.lower())
    return cleaned


def _norm(name: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", "", name.lower()).split())


def match_target(businesses: list[str], target_name: str) -> tuple[bool, int | None]:
    """Return (mentioned, 1-based position) for the target within the ranked list.

    Matching is fuzzy: case/punctuation-insensitive, and a hit if either name contains
    the other (so "Joe's Plumbing" matches "Joe's Plumbing LLC").
    """
    target = _norm(target_name)
    if not target:
        return False, None
    for idx, name in enumerate(businesses, start=1):
        n = _norm(name)
        if n == target or target in n or n in target:
            return True, idx
    return False, None
