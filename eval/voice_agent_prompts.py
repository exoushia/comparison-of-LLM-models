"""
Voice agent scenarios for Phase 3 — TTS Gradio demo.

DISCOM: KRDCL (Krishnapur Rajya Distribution Company Limited) — fictional
Models: Sarvam Bulbul v3 (agent) + one competitor TTS (customer), or vice versa
Total duration per scenario: ≤20 seconds HARD LIMIT

Real-world context baked into prompts (sourced May 2026):
- UP scrapped smart prepaid meters on May 8, 2026 due to mass complaints
  (Business Standard, May 2026)
- 1912 helpline received 95 lakh+ complaints across UP DISCOMs in FY 2025-26,
  of which 2.3 lakh were smart meter/prepaid specific (Millennium Post, Apr 2026)
- Digital payment via UPI (Paytm/PhonePe/Google Pay) is standard across all DISCOMs
- Check meter installation is a standard resolution for billing disputes
- Several DISCOMs offer 1-2% rebate on digital/online payment
"""

# ── Shared context for agent ─────────────────────────────────────

AGENT_CONTEXT = (
    "You are a Hindi-speaking customer service agent for KRDCL "
    "(Krishnapur Rajya Distribution Company Limited), a state electricity "
    "distribution company. Key facts about KRDCL:\n"
    "- Helpline number: 1912\n"
    "- Consumer app: KRDCL Mitra (available on Play Store / App Store)\n"
    "- Online payment: via KRDCL website, Paytm, PhonePe, Google Pay using consumer number\n"
    "- Digital payment discount: 1% rebate on bills paid online before due date\n"
    "- Smart meter programme: KRDCL is installing smart prepaid meters under RDSS scheme\n"
    "- Smart prepaid benefits: real-time usage tracking, no estimated billing, "
    "recharge anytime like mobile, no security deposit, automatic disconnection "
    "warnings before balance runs out\n"
    "- Check meter: can be installed within 48 hours on complaint to verify billing accuracy\n"
    "- Billing cycle: monthly, due date is 15th of following month\n\n"
    "Tone: Empathetic, patient, professional. Use simple Hindi. "
    "Address consumer as 'ji'. Keep responses SHORT — max 2 sentences per turn."
)

CUSTOMER_CONTEXT = (
    "You are a Hindi-speaking electricity consumer of KRDCL. "
    "You speak in simple, colloquial Hindi. You may mix in some English words "
    "naturally (bill, meter, payment, online, app). "
    "Keep responses SHORT — max 1-2 sentences per turn."
)


# ── Scenario 1: Smart meter billing complaint ────────────────────

SCENARIO_1 = {
    "id": "s1_billing_complaint",
    "title": "Smart Meter Billing Complaint",
    "description": (
        "Consumer is frustrated that electricity bill has been higher since "
        "smart meter installation. Agent empathises, offers to check bills "
        "and install a check meter within 48 hours."
    ),
    "real_world_context": (
        "In May 2026, UP govt scrapped smart prepaid meters statewide after "
        "mass protests over alleged overbilling. 2.3 lakh smart meter "
        "complaints were filed on 1912 helpline in FY 2025-26. "
        "This scenario reflects a very real and current consumer pain point."
    ),
    "target_duration_sec": 18,
    "max_duration_sec": 20,
    "turns": [
        {
            "speaker": "customer",
            "emotion": "frustrated",
            "hindi": "हेलो, मेरा बिल पिछले दो महीने से बहुत ज़्यादा आ रहा है जब से ये नया smart meter लगा है!",
            "english_gloss": "Hello, my bill has been very high for the last two months since this new smart meter was installed!",
            "approx_duration_sec": 5,
        },
        {
            "speaker": "agent",
            "emotion": "empathetic",
            "hindi": "जी, मैं समझ सकता हूँ आपकी परेशानी। आप अपना consumer number बताइए, मैं अभी आपके पिछले bills चेक करता हूँ।",
            "english_gloss": "Ji, I understand your concern. Please share your consumer number, I'll check your previous bills right now.",
            "approx_duration_sec": 5,
        },
        {
            "speaker": "customer",
            "emotion": "anxious",
            "hindi": "मेरा number है 4012-3389। पहले दो हज़ार आता था, अब साढ़े तीन हज़ार आ रहा है।",
            "english_gloss": "My number is 4012-3389. Earlier it was two thousand, now it's coming three and a half thousand.",
            "approx_duration_sec": 4,
        },
        {
            "speaker": "agent",
            "emotion": "reassuring",
            "hindi": "जी, मैंने complaint register कर दी है। कल तक check meter लग जाएगा, सही reading आने पर bill revise हो जाएगा।",
            "english_gloss": "Ji, I've registered your complaint. A check meter will be installed by tomorrow, and the bill will be revised once correct reading comes.",
            "approx_duration_sec": 5,
        },
    ],
    "total_approx_duration_sec": 19,
    "guardrails": {
        "max_words_per_turn": 30,
        "max_turns": 4,
        "hard_cutoff_sec": 20,
        "fallback_if_exceeds": "Audio is trimmed at 20s. If a turn is cut off, that itself becomes an eval data point — which model handles timing better?",
    },
}


# ── Scenario 2: Digital payment help + smart prepaid nudge ───────

SCENARIO_2 = {
    "id": "s2_digital_payment",
    "title": "Digital Payment Help + Smart Prepaid Nudge",
    "description": (
        "Consumer wants to pay bill but doesn't know how to pay digitally. "
        "Agent guides through UPI payment, mentions 1% digital discount. "
        "On learning consumer has a smart meter, gently explains prepaid benefits."
    ),
    "real_world_context": (
        "Digital payment adoption in Indian DISCOMs is growing but many "
        "rural/semi-urban consumers still pay at counters. DISCOMs offer "
        "1-2% rebate on online payments to incentivise digital adoption. "
        "Smart prepaid meters allow recharge-based billing like mobile phones."
    ),
    "target_duration_sec": 18,
    "max_duration_sec": 20,
    "turns": [
        {
            "speaker": "customer",
            "emotion": "confused",
            "hindi": "भाई, बिल जमा करना है लेकिन office बंद है। online कैसे भरें, कुछ समझ नहीं आता।",
            "english_gloss": "Brother, I need to pay the bill but the office is closed. How to pay online, I don't understand.",
            "approx_duration_sec": 4,
        },
        {
            "speaker": "agent",
            "emotion": "helpful",
            "hindi": "जी, बहुत आसान है। Paytm या PhonePe खोलिए, Electricity पर जाइए, KRDCL चुनिए और consumer number डालिए। और हाँ, online भरने पर एक percent की छूट भी मिलेगी!",
            "english_gloss": "Ji, it's very easy. Open Paytm or PhonePe, go to Electricity, select KRDCL and enter your consumer number. And yes, you'll get 1% discount on paying online!",
            "approx_duration_sec": 6,
        },
        {
            "speaker": "customer",
            "emotion": "curious",
            "hindi": "अच्छा? छूट भी मिलेगी? और हाँ, मेरे यहाँ smart meter लगा है, उसमें कोई फ़ायदा है क्या?",
            "english_gloss": "Really? Discount too? And yes, I have a smart meter installed, is there any benefit in that?",
            "approx_duration_sec": 4,
        },
        {
            "speaker": "agent",
            "emotion": "encouraging",
            "hindi": "बिल्कुल जी! Smart prepaid में mobile जैसा recharge होता है, जितना चाहें उतना डालिए। कोई estimated bill नहीं, कोई security deposit नहीं।",
            "english_gloss": "Absolutely ji! Smart prepaid works like mobile recharge — top up as much as you want. No estimated bills, no security deposit.",
            "approx_duration_sec": 5,
        },
    ],
    "total_approx_duration_sec": 19,
    "guardrails": {
        "max_words_per_turn": 35,
        "max_turns": 4,
        "hard_cutoff_sec": 20,
        "fallback_if_exceeds": "Audio is trimmed at 20s.",
    },
}


# ── TTS model configuration ──────────────────────────────────────

TTS_MODELS = {
    "sarvam_bulbul": {
        "provider": "sarvam",
        "model": "bulbul:v3",
        "language": "hi-IN",
        "customer_voice": "meera",       # female voice for customer
        "agent_voice": "shubh",          # male voice for agent
        "api": "sarvamai SDK — client.text.speech()",
    },
    "competitor": {
        "provider": "openai",            # or google
        "model": "tts-1-hd",
        "language": "hi",
        "customer_voice": "nova",         # OpenAI female
        "agent_voice": "onyx",            # OpenAI male
        "api": "openai SDK — client.audio.speech.create()",
    },
}


# ── Eval criteria for TTS demo ───────────────────────────────────

TTS_EVAL = {
    "automated": {
        "total_duration_sec": "Must be ≤20s. Measured from combined audio.",
        "latency_per_turn_ms": "Time from API call to audio returned.",
    },
    "human_rating": {
        "naturalness": "1-5: Does it sound like a real Hindi speaker?",
        "emotion_match": "1-5: Does frustrated sound frustrated? Does empathetic sound empathetic?",
        "number_handling": "Did it correctly pronounce 4012-3389, साढ़े तीन हज़ार, एक percent?",
        "code_mixing": "Did it handle Hindi-English switches naturally (smart meter, consumer number, online)?",
    },
}


# ── Helper to get all turns as flat list ─────────────────────────

def get_scenario_texts(scenario: dict) -> list[dict]:
    """Return list of {speaker, hindi, emotion} for TTS generation."""
    return [
        {
            "speaker": t["speaker"],
            "hindi": t["hindi"],
            "emotion": t["emotion"],
            "approx_sec": t["approx_duration_sec"],
        }
        for t in scenario["turns"]
    ]


SCENARIOS = {
    "s1_billing_complaint": SCENARIO_1,
    "s2_digital_payment": SCENARIO_2,
}
