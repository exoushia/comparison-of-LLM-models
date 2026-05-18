"""
T2: Tariff order document extraction. Automated eval.
Run: python -m runners.run_t2_docs
"""
import json, sys
import pandas as pd
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
# doc3 prompt file has all 3 docs
from eval.doc3_dvvnl_handwritten_hindi_prompts import SYSTEM_PROMPT, DOC_PROMPTS, get_full_prompt
from eval.cost_calculator import log_api_call, USD_TO_INR
from eval.metrics import cell_accuracy, compute_cer
from providers import VISION_PROVIDERS

BASE = Path(__file__).parent.parent
INPUTS = BASE / "test_inputs" / "t2_tariff_pages"
GT = BASE / "ground_truth" / "t2_tariff_pages"
OUT = BASE / "results" / "t2_tariff_pages"
OUT.mkdir(parents=True, exist_ok=True)

# Map doc_id → input filename
DOC_FILES = {
    "doc1_dgvcl_power_purchase": "doc1_dgvcl_power_purchase.pdf",
    "doc2_bescom_tariff_schedule": "doc2_bescom_tariff_schedule.pdf",
    "doc3_dvvnl_handwritten_hindi": "doc3_dvvnl_handwritten_hindi.png",
}


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

    for doc_id, input_file in DOC_FILES.items():
        input_path = INPUTS / input_file
        gt_path = GT / f"{doc_id}.csv"

        if not input_path.exists():
            print(f"SKIP {doc_id}: not found at {input_path}"); continue
        if doc_id not in DOC_PROMPTS:
            print(f"SKIP {doc_id}: no prompt defined"); continue

        gt_df = pd.read_csv(gt_path) if gt_path.exists() else None
        gt_text = gt_df.to_csv(index=False) if gt_df is not None else ""
        prompt = get_full_prompt(doc_id)

        print(f"\n{'='*50}\n{doc_id}\n{'='*50}")

        for name, fn in VISION_PROVIDERS.items():
            print(f"  {name}...", end=" ", flush=True)
            try:
                r = fn(str(input_path), SYSTEM_PROMPT, prompt)
            except Exception as e:
                print(f"ERROR: {e}")
                results.append({"doc_id": doc_id, "provider": name, "error": str(e)})
                continue

            pred = _parse_csv(r["output"])
            acc = cell_accuracy(pred, gt_df) if pred is not None and gt_df is not None else {"accuracy_pct": None}
            cer = round(compute_cer(r["output"], gt_text) * 100, 2) if gt_text else None
            cost = _cost_inr(name, r)
            print(f"{r['latency_ms']:.0f}ms | acc={acc['accuracy_pct']}% | CER={cer}% | ₹{cost}")

            log_api_call("t2_doc", r["model"], name, doc_id, r["latency_ms"],
                         r.get("input_tokens"), r.get("output_tokens"), cost,
                         {"cell_accuracy_pct": acc["accuracy_pct"], "cer_pct": cer})

            (OUT / f"{doc_id}_{name}_raw.txt").write_text(r["output"])
            rec = {"doc_id": doc_id, "provider": name, "model": r["model"],
                   "latency_ms": r["latency_ms"], "input_tokens": r.get("input_tokens"),
                   "output_tokens": r.get("output_tokens"), "cost_inr": cost,
                   "cell_accuracy_pct": acc["accuracy_pct"], "cer_pct": cer}
            if "latency_step1_ms" in r:
                rec["latency_step1_ms"] = r["latency_step1_ms"]
                rec["latency_step2_ms"] = r["latency_step2_ms"]
            results.append(rec)

    with open(OUT / "t2_summary.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → {OUT / 't2_summary.json'}")


if __name__ == "__main__":
    run()
