"""
T3: Hindi image captioning. Human blind rating.
Logs latency, tokens, cost. Generates blind rating sheet.
Run: python -m runners.run_t3_captions
"""
import json, sys, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.caption_prompts import SYSTEM_PROMPT, CAPTION_PROMPTS
from eval.cost_calculator import log_api_call, USD_TO_INR
from providers import VISION_PROVIDERS

BASE = Path(__file__).parent.parent
IMG_DIR = BASE / "test_inputs" / "t3_captioning"
OUT = BASE / "results" / "t3_captioning"
OUT.mkdir(parents=True, exist_ok=True)

DEFAULT_INSTRUCTION = "इस छवि में आप क्या देख रहे हैं, 2-3 वाक्यों में हिंदी में बताइए।"


def _discover_images() -> dict:
    """Auto-discover images if CAPTION_PROMPTS is empty."""
    images = {}
    if IMG_DIR.exists():
        for f in sorted(IMG_DIR.glob("*")):
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                images[f.stem] = {
                    "image_path": str(f),
                    "context": "",
                    "instruction": DEFAULT_INSTRUCTION,
                }
    return images


def _cost_inr(provider: str, r: dict) -> float:
    inp = r.get("input_tokens") or 0
    out = r.get("output_tokens") or 0
    if provider == "sarvam": return 0.0
    if provider == "openai": return round((inp * 2.50 + out * 10.0) / 1e6 * USD_TO_INR, 4)
    if provider == "google": return round((inp * 0.10 + out * 0.40) / 1e6 * USD_TO_INR, 4)
    return 0.0


def run():
    prompts = CAPTION_PROMPTS if CAPTION_PROMPTS else _discover_images()
    if not prompts:
        print("No images found in test_inputs/t3_captioning/"); return

    results = []
    blind = {}  # {img_id: {provider: caption}}

    for img_id, p in prompts.items():
        img_path = p.get("image_path") or str(IMG_DIR / f"{img_id}.png")
        if not Path(img_path).exists():
            print(f"SKIP {img_id}"); continue

        user_prompt = f"{p.get('context', '')}\n\n{p['instruction']}\n\nRespond ONLY in Hindi (Devanagari script)."
        print(f"\n{'='*50}\n{img_id}\n{'='*50}")
        blind[img_id] = {}

        for name, fn in VISION_PROVIDERS.items():
            print(f"  {name}...", end=" ", flush=True)
            try:
                r = fn(img_path, SYSTEM_PROMPT, user_prompt)
            except Exception as e:
                print(f"ERROR: {e}"); continue

            cost = _cost_inr(name, r)
            caption = r["output"]
            print(f"{r['latency_ms']:.0f}ms | {len(caption)} chars | ₹{cost}")

            blind[img_id][name] = caption
            log_api_call("t3_caption", r["model"], name, img_id, r["latency_ms"],
                         r.get("input_tokens"), r.get("output_tokens"), cost)

            results.append({"image_id": img_id, "provider": name, "model": r["model"],
                            "latency_ms": r["latency_ms"], "input_tokens": r.get("input_tokens"),
                            "output_tokens": r.get("output_tokens"), "cost_inr": cost,
                            "caption": caption})

    with open(OUT / "t3_summary.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Generate blind rating sheet
    providers = list(VISION_PROVIDERS.keys())
    label_map = dict(zip(["A", "B", "C"], random.sample(providers, len(providers))))
    rev = {v: k for k, v in label_map.items()}

    lines = ["# T3 Blind Rating — Hindi Image Captioning\n",
             "Rate Accuracy (1-5) and Naturalness (1-5) for each.\n\n"]
    for img_id, caps in blind.items():
        lines.append(f"## {img_id}\n")
        for prov, cap in caps.items():
            lines.append(f"**{rev.get(prov, '?')}:** {cap}\n\nAccuracy: ___ / 5 | Naturalness: ___ / 5\n\n")
    lines.append("---\n## KEY (fill after rating)\n")
    for label, prov in label_map.items():
        lines.append(f"- {label} = {prov}\n")
    (OUT / "t3_blind_rating.md").write_text("\n".join(lines))

    print(f"\nSaved → {OUT / 't3_summary.json'} + {OUT / 't3_blind_rating.md'}")


if __name__ == "__main__":
    run()
