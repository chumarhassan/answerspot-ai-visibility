from __future__ import annotations
import logging
import httpx
import gemini
from config import get_settings
logger = logging.getLogger("answerspot.llm")
settings = get_settings()
class LLMError(Exception): pass
async def query_llm(prompt: str, *, as_json: bool = False, temperature: float = 0.3) -> str:
    if settings.gemini_configured:
        try:
            return await gemini.query_gemini(prompt, as_json=as_json, temperature=temperature)
        except gemini.GeminiError as exc:
            logger.warning("Gemini failed, trying failover: %s", exc)
    if settings.openrouter_configured:
        try:
            return await _query_openrouter(prompt, as_json=as_json, temperature=temperature)
        except Exception as exc:
            logger.warning("OpenRouter failover failed: %s", exc)
    if settings.groq_configured:
        try:
            return await _query_groq(prompt, as_json=as_json, temperature=temperature)
        except Exception as exc:
            logger.warning("Groq failover failed: %s", exc)
    raise LLMError("No LLM providers available or all exhausted.")
async def _query_openrouter(prompt: str, *, as_json: bool = False, temperature: float = 0.3) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.frontend_url,
        "X-Title": "Answerspot AI",
    }
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if as_json:
        payload["response_format"] = {"type": "json_object"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise LLMError(f"OpenRouter failed: {resp.status_code} {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
async def _query_groq(prompt: str, *, as_json: bool = False, temperature: float = 0.3) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    payload = {
        "model": settings.groq_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if as_json:
        payload["response_format"] = {"type": "json_object"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise LLMError(f"Groq failed: {resp.status_code} {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()