import os
import re

import requests

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
DEFAULT_HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def _load_env():
    try:
        from dotenv import load_dotenv

        env_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(env_path)
    except ImportError:
        pass


_load_env()


def _parse_suggestions(text, max_items=4):
    """Turn model output into a clean list of suggestion strings."""
    if not text:
        return []

    lines = []
    for raw_line in text.replace("\r", "").split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        line = re.sub(r"^[-*•]\s*", "", line)
        line = re.sub(r"^\d+[\).\:-]\s*", "", line)
        line = line.strip('"').strip("'").strip()

        if len(line) >= 15:
            lines.append(line)

    if not lines and text.strip():
        parts = [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", text.strip())
            if len(part.strip()) >= 15
        ]
        lines = parts

    return lines[:max_items]


def _call_groq(system_prompt, user_prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "Groq API key not configured"

    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.7,
            "max_tokens": 900,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=45,
    )

    if response.status_code != 200:
        return None, f"Groq API error {response.status_code}: {response.text[:200]}"

    content = response.json()["choices"][0]["message"]["content"]
    return content, None


def _call_huggingface(system_prompt, user_prompt):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None, "Hugging Face API key not configured"

    model = os.getenv("HUGGINGFACE_MODEL", DEFAULT_HF_MODEL)
    prompt = f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]"
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 900,
                "temperature": 0.7,
                "return_full_text": False,
            },
        },
        timeout=60,
    )

    if response.status_code != 200:
        return None, f"Hugging Face API error {response.status_code}: {response.text[:200]}"

    payload = response.json()
    if isinstance(payload, list) and payload:
        content = payload[0].get("generated_text", "")
    elif isinstance(payload, dict):
        content = payload.get("generated_text") or payload.get("answer") or ""
    else:
        content = str(payload)

    return content, None


def _call_openai(system_prompt, user_prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "OpenAI API key not configured"

    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.7,
            "max_tokens": 900,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=45,
    )

    if response.status_code != 200:
        return None, f"OpenAI API error {response.status_code}: {response.text[:200]}"

    content = response.json()["choices"][0]["message"]["content"]
    return content, None


def generate_ai_suggestions(system_prompt, user_prompt, max_items=4):
    """Generate suggestions using the configured AI provider only."""
    _load_env()

    provider = os.getenv("AI_PROVIDER", "auto").lower()
    providers = []

    if provider == "auto":
        if os.getenv("GROQ_API_KEY"):
            providers.append("groq")
        if os.getenv("HUGGINGFACE_API_KEY"):
            providers.append("huggingface")
        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")
    else:
        providers = [provider]

    callers = {
        "groq": _call_groq,
        "huggingface": _call_huggingface,
        "hf": _call_huggingface,
        "openai": _call_openai,
    }

    errors = []
    for name in providers:
        caller = callers.get(name)
        if not caller:
            continue

        print(f"🤖 Requesting real AI suggestions via {name}...")
        content, error = caller(system_prompt, user_prompt)
        if error:
            errors.append(f"{name}: {error}")
            continue

        suggestions = _parse_suggestions(content, max_items=max_items)
        if suggestions:
            print(f"✅ AI suggestions generated via {name}: {len(suggestions)} items")
            return format_ai_response(suggestions, source=name, status="success")

        errors.append(f"{name}: empty response")

    if not providers:
        return format_ai_response(
            [],
            source="none",
            status="no_api_key",
            message=(
                "No AI API key configured. Set GROQ_API_KEY, HUGGINGFACE_API_KEY, "
                "or OPENAI_API_KEY in backend/.env"
            ),
            errors=errors,
        )

    return format_ai_response(
        [],
        source="none",
        status="error",
        message="AI suggestion request failed. Check backend logs and API key.",
        errors=errors,
    )


def format_ai_response(suggestions, source, status="success", message=None, errors=None):
    """Return a consistent AI suggestions payload for all APIs."""
    return {
        "status": status,
        "source": source,
        "model_used": source if source not in ("none", "rule_based") else None,
        "message": message,
        "suggestions": suggestions,
        "errors": errors or [],
    }
