"""Thin LLM client wrapper. Provider is picked via LLM_PROVIDER so you can
swap Gemini / OpenAI / OpenRouter without touching rag.py.

Kept intentionally simple (no streaming, no retries) - matches the MVP
scope. Add streaming later once the basic flow works end to end.
"""
import os
import requests

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")


def _call_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL}:generateContent?key={LLM_API_KEY}"
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai_compatible(prompt: str, base_url: str) -> str:
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        json={
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def generate_answer(prompt: str) -> str:
    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not set. Add a key for your chosen provider to ai_service/.env "
            "(see .env.example)."
        )

    if LLM_PROVIDER == "gemini":
        return _call_gemini(prompt)
    elif LLM_PROVIDER == "openai":
        return _call_openai_compatible(prompt, "https://api.openai.com/v1")
    elif LLM_PROVIDER == "openrouter":
        return _call_openai_compatible(prompt, "https://openrouter.ai/api/v1")
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
