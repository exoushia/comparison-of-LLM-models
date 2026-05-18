"""
T1: Chart → CSV extraction. Automated eval.
Run: python -m runners.run_t1_charts
"""
import json, sys
import pandas as pd
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.chart_prompts import SYSTEM_PROMPT, PLOT_ORDER, get_full_prompt
from eval.cost_calculator import log_api_call, USD_TO_INR
from eval.metrics import cell_accuracy
from providers import VISION_PROVIDERS

BASE = Path(__file__).parent.parent
CHARTS = BASE / "test_inputs" / "t1_charts"
GT = BASE / "ground_truth" / "t1_charts"
OUT = BASE / "results" / "t1_charts"
OUT.mkdir(parents=True, exist_ok=True)


def _parse_csv(text: str) -> pd.DataFrame | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(l for l in cleaned.split("\n") if not l.startswith("```")).strip()
    try:
        return pd.read_csv(StringIO(cleaned))
    except Exception:
        return None


def _cost_inr(provider: str, r: dict) -> float:
    inp = r.get("input_tokens") or 0
    out = r.get("output_tokens") or 0
    if provider == "sarvam": return 0.0
    if provider == "openai": return round((inp * 2.50 + out * 10.0) / 1e6 * USD_TO_INR, 4)
    if provider == "google": return round((inp * 0.10 + out * 0.40) / 1e6 * USD_TO_INR, 4)
    return 0.0


def run():
    results = []
    for plot_id in PLOT_ORDER:
        img = CHARTS / f"{plot_id}.png"
        gt_path = GT / f"{plot_id}.csv"
        if not img.exists():
            print(f"SKIP {plot_id}: no image"); continue

        gt_df = pd.read_csv(gt_path) if gt_path.exists() else None
        prompt = get_full_prompt(plot_id)
        print(f"\n{'='*50}\n{plot_id}\n{'='*50}")

        for name, fn in VISION_PROVIDERS.items():
            print(f"  {name}...", end=" ", flush=True)
            try:
                r = fn(str(img), SYSTEM_PROMPT, prompt)
            except Exception as e:
                print(f"ERROR: {e}")
                results.append({"plot_id": plot_id, "provider": name, "error": str(e)})
                continue

            pred = _parse_csv(r["output"])
            acc = cell_accuracy(pred, gt_df) if pred is not None and gt_df is not None else {"accuracy_pct": None}
            cost = _cost_inr(name, r)
            print(f"{r['latency_ms']:.0f}ms | acc={acc['accuracy_pct']}% | ₹{cost}")

            log_api_call("t1_chart", r["model"], name, plot_id, r["latency_ms"],
                         r.get("input_tokens"), r.get("output_tokens"), cost,
                         {"cell_accuracy_pct": acc["accuracy_pct"]})

            (OUT / f"{plot_id}_{name}_raw.csv").write_text(r["output"])
            rec = {"plot_id": plot_id, "provider": name, "model": r["model"],
                   "latency_ms": r["latency_ms"], "input_tokens": r.get("input_tokens"),
                   "output_tokens": r.get("output_tokens"), "cost_inr": cost,
                   "cell_accuracy_pct": acc["accuracy_pct"]}
            if "latency_step1_ms" in r:
                rec["latency_step1_ms"] = r["latency_step1_ms"]
                rec["latency_step2_ms"] = r["latency_step2_ms"]
            results.append(rec)

    with open(OUT / "t1_summary.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → {OUT / 't1_summary.json'}")


if __name__ == "__main__":
    run()
