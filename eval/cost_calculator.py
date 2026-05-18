"""
Logs every API call with timing, cost, and token info.
Appends to a single JSONL file for post-hoc analysis.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from functools import wraps

LOG_PATH = Path(__file__).parent.parent / "results" / "cost" / "api_call_log.jsonl"


def log_api_call(
    task: str,
    model: str,
    provider: str,
    sample_id: str,
    latency_ms: float,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cost_inr: float | None = None,
    extra: dict | None = None,
):
    """Append a single API call record to the log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "model": model,
        "provider": provider,
        "sample_id": sample_id,
        "latency_ms": round(latency_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_inr": cost_inr,
    }
    if extra:
        record.update(extra)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def timed_call(func):
    """Decorator that times a function and returns (result, latency_ms)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return result, round(elapsed_ms, 2)
    return wrapper


# ── Pricing constants (as of May 2026) ───────────────────────────

PRICING = {
    "sarvam": {
        "vision_per_page": 0.0,          # free during promo
        "stt_per_hour_inr": 30,
        "tts_per_10k_chars_inr": 30,
        "translate_per_10k_chars_inr": 20,
        "llm_30b_per_1m_input_inr": None,   # TBD — check dashboard
        "llm_105b_per_1m_input_inr": None,   # TBD — check dashboard
        "currency": "INR",
    },
    "google": {
        "docai_per_1k_pages_usd": 0.65,
        "stt_per_min_usd": 0.016,
        "tts_per_1m_chars_usd": 16.0,      # Wavenet
        "translate_per_1m_chars_usd": 20.0,
        "gemini_flash_per_1m_input_usd": 0.10,
        "gemini_pro_per_1m_input_usd": 1.25,
        "currency": "USD",
    },
    "openai": {
        "gpt4o_vision_per_1m_input_usd": 2.50,
        "whisper_per_min_usd": 0.006,
        "tts_per_1m_chars_usd": 15.0,
        "gpt4o_mini_per_1m_input_usd": 0.15,
        "gpt4o_per_1m_input_usd": 2.50,
        "currency": "USD",
    },
}

USD_TO_INR = 85  # approximate, update as needed


def estimate_cost_inr(provider: str, product: str, units: float) -> float:
    """
    Quick cost estimate in INR.
    units: pages for vision, minutes for STT, chars for TTS/translate, tokens for LLM.
    """
    p = PRICING.get(provider, {})
    # This is a placeholder — actual calculation depends on product
    # Fill in per task in the notebook
    return 0.0
