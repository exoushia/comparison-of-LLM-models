"""
T4: English → Hindi headline translation. Human blind rating.
Logs latency, char count (input + output), cost.
Run: python -m runners.run_t4_translations
"""
import json, sys, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.translation_prompts import HEADLINES
from eval.cost_calculator import log_api_call, PRICING, USD_TO_INR
from providers import TRANSLATE_PROVIDERS

BASE = Path(__file__).parent.parent
OUT = BASE / "results" / "t4_translation"
OUT.mkdir(parents=True, exist_ok=True)

# Headlines hardcoded from screenshot images in test_inputs/t4_translation/
# (Translation APIs need text, not images)
FALLBACK_HEADLINES = {
    "h01": {
        "english": "An Inclusive Transition Must Recognise Coal Miners in India's Green Future",
        "notes": "Tests: energy transition vocabulary, proper noun handling",
    },
    "h02": {
        "english": "Harnessing the Wind for India's Ambitious Energy Transition",
        "notes": "Tests: metaphor preservation, conciseness",
    },
    "h03": {
        "english": "Why AQI alone cannot guide effective air quality enforcement in India",
        "notes": "Tests: acronym (AQI), technical policy phrasing",
    },
}


def _cost_inr(provider: str, chars: int) -> float:
    if provider == "sarvam":
        return round(chars / 10_000 * PRICING["sarvam"]["translate_per_10k_chars_inr"], 4)
    if provider == "google":
        return round(chars / 1e6 * PRICING["google"]["translate_per_1m_chars_usd"] * USD_TO_INR, 4)
    return 0.0


def run():
    headlines = HEADLINES if HEADLINES else FALLBACK_HEADLINES
    if not headlines:
        print("No headlines defined."); return

    results = []
    blind = {}

    for hid, h in headlines.items():
        english = h["english"]
        if not english.strip():
            continue

        print(f"\n{'='*50}\n{hid}: {english[:60]}...\n{'='*50}")
        blind[hid] = {"english": english}

        for name, fn in TRANSLATE_PROVIDERS.items():
            print(f"  {name}...", end=" ", flush=True)
            try:
                if name == "sarvam":
                    r = fn(english, source_lang="en-IN", target_lang="hi-IN")
                else:
                    r = fn(english, source_lang="en", target_lang="hi")
            except Exception as e:
                print(f"ERROR: {e}"); continue

            cost = _cost_inr(name, len(english))
            print(f"{r['latency_ms']:.0f}ms | ₹{cost}")
            print(f"    → {r['output']}")

            blind[hid][name] = r["output"]
            log_api_call("t4_translation", r["model"], name, hid, r["latency_ms"],
                         r.get("input_tokens"), r.get("output_tokens"), cost)

            results.append({"headline_id": hid, "english": english, "provider": name,
                            "model": r["model"], "translation": r["output"],
                            "latency_ms": r["latency_ms"],
                            "input_chars": len(english), "output_chars": len(r["output"]),
                            "cost_inr": cost})

    with open(OUT / "t4_summary.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Blind rating sheet
    providers = list(TRANSLATE_PROVIDERS.keys())
    label_map = dict(zip(["A", "B"], random.sample(providers, len(providers))))
    rev = {v: k for k, v in label_map.items()}

    lines = ["# T4 Blind Rating — Headline Translation (EN→HI)\n",
             "Rate Essence Captured (1-5) and Audience Appeal (1-5).\n\n"]
    for hid, data in blind.items():
        lines.append(f"## {hid}\n**English:** {data['english']}\n")
        for prov in providers:
            t = data.get(prov, "(no output)")
            lines.append(f"**{rev[prov]}:** {t}\n\nEssence: ___ / 5 | Appeal: ___ / 5\n\n")
    lines.append("---\n## KEY\n")
    for label, prov in label_map.items():
        lines.append(f"- {label} = {prov}\n")
    (OUT / "t4_blind_rating.md").write_text("\n".join(lines))

    print(f"\nSaved → {OUT / 't4_summary.json'} + {OUT / 't4_blind_rating.md'}")


if __name__ == "__main__":
    run()
