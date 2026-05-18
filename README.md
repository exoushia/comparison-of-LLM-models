# Sarvam AI Evaluation for CEEW Power Markets Team

**Internal evaluation of Sarvam AI products for potential adoption in CEEW's utilities research workflow.**

## What This Evaluates

| Task | Sarvam Product | vs Google | vs OpenAI | Eval Method |
|------|---------------|-----------|-----------|-------------|
| T1: Chart → CSV extraction | Sarvam Vision | Google Document AI | GPT-4o vision | Automated: cell accuracy |
| T2: Tariff order extraction | Sarvam Vision | Google Document AI | GPT-4o vision | Automated: cell accuracy, CER. Manual: structure |
| T3: Hindi image captioning | Sarvam Vision | Gemini Flash | GPT-4o | Human blind rating (CEEW colleagues) |
| T4: Blog headline translation | Mayura / Sarvam-Translate | Google Translate | — | Human blind rating (CEEW colleagues) |

## Directory Structure

```
sarvam-ceew-eval/
├── test_inputs/
│   ├── t1_charts/              # Chart images
│   ├── t2_tariff_pages/        # Tariff order page scans
│   ├── t3_captioning/          # Images for Hindi captioning
│   └── t4_translation/         # English headlines (JSON)
├── ground_truth/
│   ├── t1_charts/              # Expected CSVs per chart
│   └── t2_tariff_pages/        # Manually verified text/tables
├── results/
│   ├── t1_charts/              # Model outputs per provider
│   ├── t2_tariff_pages/        # Model outputs per provider
│   ├── t3_captioning/          # Captions per provider (for blind rating)
│   ├── t4_translation/         # Translations per provider (for blind rating)
│   └── cost/                   # Latency + cost logs
├── eval/
│   ├── metrics.py              # CER, cell accuracy, chrF
│   ├── compare.py              # Side-by-side result generation
│   └── cost_calculator.py      # Pricing comparison
├── human_rating_sheets/        # Sheets for CEEW colleagues to rate T3/T4
├── notebook.ipynb              # Main notebook: all API calls
└── README.md
```

## Setup

```bash
pip install sarvamai openai google-cloud-documentai google-cloud-translate \
            google-cloud-texttospeech pandas jiwer sacrebleu editdistance \
            Pillow openpyxl
```

## Eval Metrics Summary

| Task | Automated Metric | Manual Metric |
|------|-----------------|---------------|
| T1: Chart → CSV | Cell accuracy (%) | — |
| T2: Tariff extraction | Cell accuracy (%), CER | Structure preserved (Y/N), term handling |
| T3: Image captioning | — | Human rating 1-5 (blind) |
| T4: Translation | chrF | Human rating 1-5 (blind) |
| All tasks | Latency (seconds) | — |
