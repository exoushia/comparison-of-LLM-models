"""
Headline translation prompts for Task T4.

Eval method: Human blind rating (CEEW colleagues).
Automated metric: chrF score (if reference translations are available).
Raters score Essence Captured (1-5) and Audience Appeal (1-5).

Models: Sarvam Mayura/Translate vs Google Translate
Outputs shuffled and labeled A/B before showing to raters.
"""

SYSTEM_PROMPT = (
    "You are a translator for an Indian energy and climate policy think tank "
    "(Council on Energy, Environment and Water — CEEW). Your task is to "
    "translate English blog headlines into Hindi. The Hindi headline must:\n"
    "1. Capture the same meaning AND tone as the English original\n"
    "2. Sound natural and compelling to a Hindi-speaking policy audience\n"
    "3. Be concise — a headline, not an explanation\n"
    "4. Keep proper nouns, acronyms, and technical terms that have no standard "
    "Hindi equivalent in English (e.g. DISCOM, CEEW, COP28)\n"
    "5. Use Hindi equivalents where they exist and are widely understood "
    "(e.g. बिजली for electricity, सौर ऊर्जा for solar energy, "
    "जलवायु परिवर्तन for climate change)\n\n"
    "Return ONLY the Hindi translation. No explanation, no romanisation."
)

# ── Headlines to translate ────────────────────────────────────────
# Fill these in with actual CEEW blog headlines

HEADLINES = {
    # "h01": {
    #     "english": "Why India's Power Distribution Companies Need Urgent Financial Reform",
    #     "notes": "Tests: DISCOM concept, financial terminology",
    # },
    # "h02": {
    #     "english": "Solar Rooftop Adoption in Gujarat: Lessons from the PM Surya Ghar Scheme",
    #     "notes": "Tests: scheme name preservation, state name, technical term",
    # },
}

HEADLINE_ORDER = list(HEADLINES.keys())


# ── Metadata for reporting ────────────────────────────────────────

TRANSLATION_METADATA = {
    "task": "t4_headline_translation",
    "direction": "English → Hindi",
    "domain": "Energy and climate policy (CEEW blog headlines)",
    "total_headlines": len(HEADLINES),
    "eval_automated": "chrF (if reference translations provided)",
    "eval_human": "Essence Captured (1-5), Audience Appeal (1-5)",
    "models": ["Sarvam Mayura", "Sarvam-Translate", "Google Translate"],
    "tests": [
        "Technical energy vocabulary (tariff, DISCOM, renewable)",
        "Policy tone preservation (urgency, analytical framing)",
        "Proper noun handling (scheme names, org names, place names)",
        "Conciseness (headline vs sentence)",
        "Hindi idiom vs literal translation",
    ],
}


def get_full_prompt(headline_id: str) -> str:
    """Compose the user prompt for a given headline."""
    h = HEADLINES[headline_id]
    return (
        f"Translate this English headline to Hindi:\n\n"
        f"\"{h['english']}\"\n\n"
        f"Return ONLY the Hindi translation."
    )


def get_all_prompts() -> list[dict]:
    """Return all headlines with their prompts for batch processing."""
    return [
        {
            "id": hid,
            "english": h["english"],
            "prompt": get_full_prompt(hid),
        }
        for hid, h in HEADLINES.items()
    ]
