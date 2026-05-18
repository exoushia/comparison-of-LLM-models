"""
Unified provider wrappers for Sarvam, OpenAI, and Google.

Every function returns:
{
    "output":        str | bytes,
    "latency_ms":    float,
    "input_tokens":  int | None,
    "output_tokens": int | None,
    "model":         str,
    "provider":      str,
}
"""

import os
import sys
import time
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


def _encode_image_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _mime(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".")
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "pdf": "application/pdf", "webp": "image/webp"}.get(ext, "image/png")


# ═════════════════════════════════════════════════════════════════
#  VISION (T1, T2, T3)
# ═════════════════════════════════════════════════════════════════

def sarvam_vision(image_path: str, system_prompt: str, user_prompt: str) -> dict:
    """Sarvam: digitize → markdown, then Sarvam-30B for structured extraction."""
    from sarvamai import SarvamAI
    from openai import OpenAI

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    # Step 1: OCR / digitize
    t0 = time.perf_counter()
    resp = client.document_digitization.digitize(
        file_path=image_path, language="en-IN", output_format="md",
    )
    t1 = time.perf_counter()
    step1_ms = (t1 - t0) * 1000

    md = ""
    if hasattr(resp, "pages"):
        for page in resp.pages:
            for block in page.blocks:
                md += block.text + "\n"
    elif hasattr(resp, "text"):
        md = resp.text
    else:
        md = str(resp)

    # Step 2: LLM structuring
    llm = OpenAI(base_url="https://api.sarvam.ai/v1", api_key=SARVAM_API_KEY)
    t2 = time.perf_counter()
    chat = llm.chat.completions.create(
        model="sarvam-30b", temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Digitized content:\n\n{md}\n\n{user_prompt}"},
        ],
    )
    t3 = time.perf_counter()
    step2_ms = (t3 - t2) * 1000

    inp_tok = chat.usage.prompt_tokens if chat.usage else None
    out_tok = chat.usage.completion_tokens if chat.usage else None

    return {
        "output": chat.choices[0].message.content or "",
        "latency_ms": round(step1_ms + step2_ms, 2),
        "latency_step1_ms": round(step1_ms, 2),
        "latency_step2_ms": round(step2_ms, 2),
        "input_tokens": inp_tok,
        "output_tokens": out_tok,
        "model": "sarvam-vision + sarvam-30b",
        "provider": "sarvam",
    }


def openai_vision(image_path: str, system_prompt: str, user_prompt: str) -> dict:
    """OpenAI GPT-4o with image."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    b64 = _encode_image_b64(image_path)

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model="gpt-4o", temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:{_mime(image_path)};base64,{b64}", "detail": "high",
                }},
            ]},
        ],
    )
    latency = (time.perf_counter() - t0) * 1000

    return {
        "output": resp.choices[0].message.content or "",
        "latency_ms": round(latency, 2),
        "input_tokens": resp.usage.prompt_tokens if resp.usage else None,
        "output_tokens": resp.usage.completion_tokens if resp.usage else None,
        "model": "gpt-4o",
        "provider": "openai",
    }


def gemini_vision(image_path: str, system_prompt: str, user_prompt: str) -> dict:
    """Google Gemini 2.0 Flash with image."""
    import google.generativeai as genai
    from PIL import Image

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt,
    )
    img = Image.open(image_path)

    t0 = time.perf_counter()
    resp = model.generate_content(
        [user_prompt, img],
        generation_config=genai.types.GenerationConfig(temperature=0),
    )
    latency = (time.perf_counter() - t0) * 1000

    inp_tok = getattr(resp.usage_metadata, "prompt_token_count", None) if hasattr(resp, "usage_metadata") else None
    out_tok = getattr(resp.usage_metadata, "candidates_token_count", None) if hasattr(resp, "usage_metadata") else None

    return {
        "output": resp.text or "",
        "latency_ms": round(latency, 2),
        "input_tokens": inp_tok,
        "output_tokens": out_tok,
        "model": "gemini-2.0-flash",
        "provider": "google",
    }


VISION_PROVIDERS = {"sarvam": sarvam_vision, "openai": openai_vision, "google": gemini_vision}


# ═════════════════════════════════════════════════════════════════
#  TRANSLATION (T4)
# ═════════════════════════════════════════════════════════════════

def sarvam_translate(text: str, source_lang: str = "en-IN", target_lang: str = "hi-IN") -> dict:
    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    t0 = time.perf_counter()
    resp = client.text.translate(input=text, source_language_code=source_lang, target_language_code=target_lang)
    latency = (time.perf_counter() - t0) * 1000

    out = resp.translated_text if hasattr(resp, "translated_text") else str(resp)
    return {
        "output": out,
        "latency_ms": round(latency, 2),
        "input_tokens": len(text),
        "output_tokens": len(out),
        "model": "sarvam-translate",
        "provider": "sarvam",
    }


def google_translate(text: str, source_lang: str = "en", target_lang: str = "hi") -> dict:
    from deep_translator import GoogleTranslator

    t0 = time.perf_counter()
    out = GoogleTranslator(source=source_lang, target=target_lang).translate(text) or ""
    latency = (time.perf_counter() - t0) * 1000

    return {
        "output": out,
        "latency_ms": round(latency, 2),
        "input_tokens": len(text),
        "output_tokens": len(out),
        "model": "google-translate",
        "provider": "google",
    }


TRANSLATE_PROVIDERS = {"sarvam": sarvam_translate, "google": google_translate}


# ═════════════════════════════════════════════════════════════════
#  TTS (Phase 3)
# ═════════════════════════════════════════════════════════════════

def sarvam_tts(text: str, language: str = "hi-IN", speaker: str = "meera") -> dict:
    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    t0 = time.perf_counter()
    resp = client.text.speech(input=text, target_language_code=language, model="bulbul:v3", speaker=speaker)
    latency = (time.perf_counter() - t0) * 1000

    audio = resp.audio if hasattr(resp, "audio") else resp
    if isinstance(audio, str):
        audio = base64.b64decode(audio)

    return {
        "output": audio,
        "latency_ms": round(latency, 2),
        "input_tokens": len(text),
        "output_tokens": None,
        "model": "bulbul-v3",
        "provider": "sarvam",
    }


def openai_tts(text: str, voice: str = "nova") -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    t0 = time.perf_counter()
    resp = client.audio.speech.create(model="tts-1-hd", voice=voice, input=text)
    latency = (time.perf_counter() - t0) * 1000

    return {
        "output": resp.content,
        "latency_ms": round(latency, 2),
        "input_tokens": len(text),
        "output_tokens": None,
        "model": "tts-1-hd",
        "provider": "openai",
    }


TTS_PROVIDERS = {"sarvam": sarvam_tts, "openai": openai_tts}
