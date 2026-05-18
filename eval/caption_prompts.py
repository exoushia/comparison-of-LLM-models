"""
Image captioning prompts for Task T3.

Eval method: Human blind rating (CEEW colleagues).
No automated GT — raters score Accuracy (1-5) and Naturalness (1-5).

Models: Sarvam Vision, Gemini Flash, GPT-4o
All get the same image + same prompt. Outputs are shuffled
and labeled A/B/C before showing to raters.
"""

SYSTEM_PROMPT = (
    "You are a visual analyst working for an Indian energy policy research "
    "organisation. You will be shown an image. Describe what you see in Hindi "
    "(Devanagari script). Your description should be factual, precise, and "
    "written in natural Hindi that a policy researcher would use. "
    "Do not transliterate English words unnecessarily — use Hindi equivalents "
    "where they exist (e.g. बिजली not electricity, ऊर्जा not energy). "
    "Keep technical terms in English only if no standard Hindi equivalent "
    "exists (e.g. DISCOM, MW, kWh)."
)

CAPTION_PROMPTS = {
    # Add entries as images are uploaded. Example:
    # "img1_solar_panel_field": {
    #     "image_path": "test_inputs/t3_captioning/img1_solar_panel_field.png",
    #     "context": "Photo of a solar installation in rural India",
    #     "instruction": "Describe this image in Hindi in 2-3 sentences.",
    # },
}

IMAGE_ORDER = list(CAPTION_PROMPTS.keys())

# ── Metadata for reporting ────────────────────────────────────────

CAPTION_METADATA = {
    # "img1_solar_panel_field": {
    #     "short_name": "img1",
    #     "description": "Solar panel installation in rural setting",
    #     "difficulty": "Easy",
    #     "tests": "Technical vocabulary (solar, MW), rural Indian context",
    # },
}

TOTAL_IMAGES = len(CAPTION_METADATA)


def get_full_prompt(image_id: str) -> str:
    """Compose the user prompt for a given image."""
    p = CAPTION_PROMPTS[image_id]
    context = f"Context: {p['context']}\n\n" if p.get("context") else ""
    return (
        f"{context}"
        f"{p['instruction']}\n\n"
        f"Respond ONLY in Hindi (Devanagari script). No English translation."
    )
