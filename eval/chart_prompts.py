"""
Chart-to-CSV extraction prompts for Task T1.

Each entry defines:
  - task_description: what the chart shows (context)
  - output_schema: exact CSV column structure expected
  - instructions: specific guidance for the model
  - difficulty: relative difficulty rating for analysis

These prompts are used identically across all 3 providers
(Sarvam Vision, Google DocAI / Gemini, GPT-4o) to ensure fair comparison.
"""

SYSTEM_PROMPT = (
    "You are a data extraction assistant. You are given a chart image from "
    "an Indian power sector analysis. Your task is to extract the underlying "
    "data and return it as a CSV. Return ONLY the CSV with headers — no "
    "explanation, no markdown fences, no commentary. Use the exact column "
    "names specified. Round numeric values to 2 decimal places."
)

CHART_PROMPTS = {
    "plot1_atc_feeders": {
        "task_description": (
            "This is a grouped bar chart showing AT&C (Aggregate Technical & "
            "Commercial) loss percentages across 11 KV feeders for three "
            "half-year periods. Each feeder has up to 3 bars representing "
            "H-1 Apr'24-Sep'24, H-2 Oct'24-Mar'25, and H-1 Apr'25-Sep'25. "
            "Some feeders may have missing data (no bar shown). "
            "An 'overall' aggregate is also shown."
        ),
        "output_schema": (
            "c_feeder_name,"
            "H-1 - Apr'24 - Sep'24,"
            "H-2- Oct'24 - Mar'25,"
            "H-1- Apr'25 - Sept'25"
        ),
        "instructions": (
            "Extract the AT&C percentage for each feeder and each period. "
            "Read values from the bar heights against the y-axis. "
            "Note: values can be negative (see 035-DOMGAON). "
            "If a feeder has no bar for a period, leave the cell empty. "
            "Include the 'overall' row. "
            "Return as CSV with the exact column headers specified."
        ),
        "difficulty": "medium",
        "notes": "Tests: negative values, missing data handling, grouped bar reading",
    },

    "plot2_bill_days_before_after": {
        "task_description": (
            "This is a 100% stacked bar chart showing the distribution of "
            "billing days across feeders, comparing 'before' and 'after' "
            "periods. Categories are: <=30 days, 30-35 days, 35-40 days, "
            "40-60 days, >60 days. Each feeder has two stacked bars "
            "(before and after). Consumer counts (n=) are shown at the top. "
            "An 'overall' aggregate is included."
        ),
        "output_schema": (
            "feeder,category,before_share_percent,after_share_percent,"
            "consumer_count,bill_count_before,bill_count_after"
        ),
        "instructions": (
            "For each feeder, extract the share percentage for each billing "
            "day category for both 'before' and 'after' periods. "
            "The consumer count is the 'n=' value shown at the top of each bar group. "
            "bill_count_before and bill_count_after may not be directly visible in the "
            "chart — extract what is visible and leave unavailable fields empty. "
            "Include the 'overall' row. Return as CSV."
        ),
        "difficulty": "hard",
        "notes": "Tests: stacked bar decomposition, before/after paired extraction, many columns",
    },

    "plot3_bill_days_overall": {
        "task_description": (
            "This is a 100% stacked bar chart showing monthly billing day "
            "distribution over time (Jan-2024 to Sep-2025). Categories: "
            "<=30 days, 30-35 days, 35-40 days, 40-60 days, >60 days. "
            "Consumer counts (n=) are shown at the top of each month's bar. "
            "Percentage annotations are shown on some segments."
        ),
        "output_schema": (
            "month,category,share_percent,consumer_count,feeder"
        ),
        "instructions": (
            "For each month, extract the share percentage for each billing "
            "day category. Read percentages from annotations where visible; "
            "estimate from segment heights where annotations are absent. "
            "The consumer count is the 'n=' value at the top. "
            "The 'feeder' column should be 'overall' for all rows. "
            "Months with n=0 should have 0.0 for all categories. "
            "Return as CSV."
        ),
        "difficulty": "very_hard",
        "notes": "Tests: 21 months × 5 categories = 105 rows, time-series stacked bars, mixed annotated/unannotated",
    },

    "plot4_pending_arrears": {
        "task_description": (
            "This is a 100% stacked bar chart showing the share of consumers "
            "with 0% pending arrears vs >0% pending arrears, by month "
            "(Apr-2024 to Sep-2025). Consumer counts (n=) shown at top. "
            "Percentage annotations on each segment."
        ),
        "output_schema": (
            "month,category,share_percent,consumer_count,feeder"
        ),
        "instructions": (
            "For each month, extract the share percentage for '0% PA' and "
            "'>0% PA' categories. Read values from the percentage annotations "
            "on the bars. Consumer count from the 'n=' labels at top. "
            "The 'feeder' column is 'overall' for all rows. "
            "Return as CSV."
        ),
        "difficulty": "medium",
        "notes": "Tests: only 2 categories per bar, but 18 months. Annotations clearly visible.",
    },

    "plot5_acos_solarisation": {
        "task_description": (
            "This is a dual-line chart (Figure 6) showing projected Average "
            "Cost of Supply (ACoS) in INR/kWh for Haryana from 2025 to 2030. "
            "Two lines: 'ACoS with 100% solarisation' (blue) and 'ACoS "
            "without 100% solarisation' (grey). All data points are labeled "
            "with exact values. Source citation at bottom."
        ),
        "output_schema": (
            "year,"
            "acos_with_100pct_solarisation_inr_per_kwh,"
            "acos_without_100pct_solarisation_inr_per_kwh"
        ),
        "instructions": (
            "Extract the ACoS values for both scenarios (with and without "
            "100% solarisation) for each year from 2025 to 2030. "
            "All values are labeled directly on the data points — read them "
            "exactly as shown. Do not estimate from axis position. "
            "Return as CSV."
        ),
        "difficulty": "easy",
        "notes": "Tests: line chart reading, all values annotated — should be near-perfect for any model",
    },
}

# Ordered list for iteration
PLOT_ORDER = [
    "plot1_atc_feeders",
    "plot2_bill_days_before_after",
    "plot3_bill_days_overall",
    "plot4_pending_arrears",
    "plot5_acos_solarisation",
]


def get_full_prompt(plot_id: str) -> str:
    """
    Compose the full user prompt for a given chart.
    The system prompt is separate (SYSTEM_PROMPT).
    """
    p = CHART_PROMPTS[plot_id]
    return (
        f"Chart description: {p['task_description']}\n\n"
        f"Task: {p['instructions']}\n\n"
        f"Required CSV format (use these exact column headers):\n"
        f"{p['output_schema']}\n\n"
        f"Return ONLY the CSV. No explanation."
    )
