"""Thin OpenAI client with retry logic and prompt caching support."""
from __future__ import annotations
import json
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import AsyncOpenAI, APIError, RateLimitError
from app.config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
)
async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.1,
    response_format: str | None = None,
    max_tokens: int = 4096,
) -> str:
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": model or settings.OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}
    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


async def classify_accounts_batch(accounts: list[dict]) -> list[dict]:
    """Classify a batch of up to 50 accounts into IFRS categories."""
    from app.services.ifrs_taxonomy import MAPPING_HINTS
    categories = list(MAPPING_HINTS.keys())

    system_prompt = """You are an expert IFRS accountant. Classify each account into exactly one IFRS category.

Categories available:
""" + "\n".join(f"- {c}" for c in categories) + """

Rules:
1. Return a JSON array with one object per account.
2. Each object: {"id": <original_id>, "category": "<CATEGORY>", "subcategory": "<optional detail>", "normal_balance": "DR or CR", "confidence": 0.0-1.0, "explanation": "<1 sentence>"}
3. Be precise. If unsure, return the closest category with lower confidence.
4. Account codes starting with 1xxx = assets, 2xxx = liabilities, 3xxx = equity, 4xxx = revenue, 5xxx/6xxx/7xxx = expenses (common pattern)."""

    user_content = "Classify these accounts:\n" + json.dumps([
        {"id": a["id"], "code": a.get("code"), "name": a["name"]}
        for a in accounts
    ])

    response = await chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format="json",
        temperature=0.05,
        max_tokens=2048,
    )

    try:
        result = json.loads(response)
        if isinstance(result, dict) and "accounts" in result:
            result = result["accounts"]
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []
