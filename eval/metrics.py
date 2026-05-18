"""
Evaluation metrics for each task type.
"""

import pandas as pd
import editdistance


# ── T1 & T2: Cell-level accuracy for table extraction ────────────

def cell_accuracy(predicted_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> dict:
    """
    Compare two DataFrames cell by cell.
    Returns accuracy percentage and list of mismatches.

    Both DataFrames are converted to string for comparison,
    with whitespace stripped and case normalized.
    """
    pred = predicted_df.reset_index(drop=True).copy()
    gt = ground_truth_df.reset_index(drop=True).copy()

    # Normalize: string, strip, lowercase
    pred = pred.astype(str).apply(lambda x: x.str.strip().str.lower())
    gt = gt.astype(str).apply(lambda x: x.str.strip().str.lower())

    # Reset column names to integers so both DFs align
    pred.columns = range(len(pred.columns))
    gt.columns = range(len(gt.columns))

    # Pad to same shape
    max_rows = max(len(pred), len(gt))
    max_cols = max(len(pred.columns), len(gt.columns))

    pred = pred.reindex(index=range(max_rows), columns=range(max_cols), fill_value="")
    gt = gt.reindex(index=range(max_rows), columns=range(max_cols), fill_value="")

    total_cells = max_rows * max_cols
    matches = 0
    mismatches = []

    for r in range(max_rows):
        for c in range(max_cols):
            p = pred.iloc[r, c]
            g = gt.iloc[r, c]
            if p == g:
                matches += 1
            else:
                mismatches.append({
                    "row": r,
                    "col": c,
                    "predicted": p,
                    "ground_truth": g,
                })

    return {
        "accuracy_pct": round(matches / total_cells * 100, 2) if total_cells > 0 else 0,
        "total_cells": total_cells,
        "correct_cells": matches,
        "mismatches": mismatches,
    }


# ── T2: Character Error Rate for text extraction ──────────────────

def compute_cer(prediction: str, ground_truth: str) -> float:
    """
    Character Error Rate = edit_distance(pred, gt) / len(gt)
    Standard OCR metric. Lower is better.
    """
    if len(ground_truth) == 0:
        return 0.0 if len(prediction) == 0 else 1.0
    return editdistance.eval(prediction, ground_truth) / len(ground_truth)


def compute_wer(prediction: str, ground_truth: str) -> float:
    """
    Word Error Rate = edit_distance(pred_words, gt_words) / len(gt_words)
    """
    pred_words = prediction.split()
    gt_words = ground_truth.split()
    if len(gt_words) == 0:
        return 0.0 if len(pred_words) == 0 else 1.0
    return editdistance.eval(pred_words, gt_words) / len(gt_words)


# ── T4: chrF for translation ─────────────────────────────────────

def compute_chrf(prediction: str, reference: str) -> float:
    """
    Character F-score. Better than BLEU for morphologically rich languages (Hindi).
    Returns score between 0-100.
    """
    try:
        from sacrebleu import sentence_chrf
        result = sentence_chrf(prediction, [reference])
        return round(result.score, 2)
    except ImportError:
        # Fallback: simple character n-gram overlap
        return _simple_chrf(prediction, reference)


def _simple_chrf(pred: str, ref: str, n: int = 6) -> float:
    """Simplified chrF fallback without sacrebleu."""
    def char_ngrams(text, order):
        return [text[i:i+order] for i in range(len(text) - order + 1)]

    scores = []
    for order in range(1, n + 1):
        pred_ngrams = char_ngrams(pred, order)
        ref_ngrams = char_ngrams(ref, order)
        if not pred_ngrams or not ref_ngrams:
            continue
        ref_set = set(ref_ngrams)
        matches = sum(1 for ng in pred_ngrams if ng in ref_set)
        precision = matches / len(pred_ngrams) if pred_ngrams else 0
        recall = matches / len(ref_ngrams) if ref_ngrams else 0
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
            scores.append(f1)

    return round(sum(scores) / len(scores) * 100, 2) if scores else 0.0


# ── Shared: Technical term preservation ───────────────────────────

def term_preservation(prediction: str, terms: list[str]) -> dict:
    """
    Check which technical terms survived in the output.
    Case-insensitive check.

    terms: list of strings like ["PGVCL", "MW", "Rs/kWh", "FY 2026-27"]
    """
    pred_lower = prediction.lower()
    preserved = []
    lost = []

    for term in terms:
        if term.lower() in pred_lower:
            preserved.append(term)
        else:
            lost.append(term)

    return {
        "total_terms": len(terms),
        "preserved": len(preserved),
        "preserved_list": preserved,
        "lost_list": lost,
        "preservation_pct": round(len(preserved) / len(terms) * 100, 2) if terms else 100,
    }
