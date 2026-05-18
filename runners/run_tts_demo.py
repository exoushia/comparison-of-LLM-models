"""
TTS: Voice agent demo — Sarvam Bulbul vs OpenAI TTS.
Generates audio for both scenarios, logs latency + cost.
Run: python -m runners.run_tts_demo
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.voice_agent_prompts import SCENARIOS, TTS_MODELS, get_scenario_texts
from eval.cost_calculator import log_api_call, PRICING, USD_TO_INR
from providers import sarvam_tts, openai_tts

BASE = Path(__file__).parent.parent
OUT = BASE / "results" / "tts_demo"
OUT.mkdir(parents=True, exist_ok=True)


def _cost_inr(provider: str, chars: int) -> float:
    if provider == "sarvam":
        return round(chars / 10_000 * PRICING["sarvam"]["tts_per_10k_chars_inr"], 4)
    if provider == "openai":
        return round(chars / 1e6 * PRICING["openai"]["tts_per_1m_chars_usd"] * USD_TO_INR, 4)
    return 0.0


def _get_voice(config: dict, speaker: str) -> str:
    return config.get("customer_voice" if speaker == "customer" else "agent_voice", "meera")


def run():
    results = []

    for sid, scenario in SCENARIOS.items():
        turns = get_scenario_texts(scenario)
        print(f"\n{'='*50}\n{scenario['title']} (target ≤{scenario['max_duration_sec']}s)\n{'='*50}")

        for tts_name, config in TTS_MODELS.items():
            provider = config["provider"]
            model = config["model"]
            print(f"\n  {tts_name} ({model})")

            chunks = []
            total_lat = 0
            total_chars = 0
            total_cost = 0

            for i, turn in enumerate(turns):
                voice = _get_voice(config, turn["speaker"])
                text = turn["hindi"]
                print(f"    turn {i+1} ({turn['speaker']})...", end=" ", flush=True)

                try:
                    if provider == "sarvam":
                        r = sarvam_tts(text, config.get("language", "hi-IN"), voice)
                    elif provider == "openai":
                        r = openai_tts(text, voice)
                    else:
                        print("SKIP"); continue
                except Exception as e:
                    print(f"ERROR: {e}"); continue

                audio = r["output"]
                cost = _cost_inr(provider, len(text))
                print(f"{r['latency_ms']:.0f}ms | {len(audio)} bytes | ₹{cost}")

                fname = f"{sid}_{tts_name}_turn{i+1}_{turn['speaker']}.wav"
                with open(OUT / fname, "wb") as f:
                    f.write(audio)

                chunks.append(audio)
                total_lat += r["latency_ms"]
                total_chars += len(text)
                total_cost += cost

                log_api_call("tts", model, provider, f"{sid}_turn{i+1}",
                             r["latency_ms"], len(text), None, cost,
                             {"speaker": turn["speaker"], "emotion": turn["emotion"]})

            # Concatenate
            concat = OUT / f"{sid}_{tts_name}_full.wav"
            with open(concat, "wb") as f:
                for c in chunks:
                    f.write(c)

            results.append({
                "scenario": sid, "tts": tts_name, "model": model,
                "total_latency_ms": round(total_lat, 2),
                "total_chars": total_chars,
                "total_cost_inr": round(total_cost, 4),
                "turns": len(turns),
            })
            print(f"  TOTAL: {total_lat:.0f}ms | {total_chars} chars | ₹{total_cost:.4f}")

    with open(OUT / "tts_summary.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}\nTTS COMPARISON\n{'='*50}")
    for r in results:
        print(f"  {r['scenario']:25} | {r['tts']:10} | {r['total_latency_ms']:>8.0f}ms | ₹{r['total_cost_inr']:.4f}")
    print(f"\nSaved → {OUT / 'tts_summary.json'}")


if __name__ == "__main__":
    run()
