"""
Document extraction prompts for Task T2.

Each entry defines the task, expected CSV schema, and specific instructions.
Used identically across all 3 providers (Sarvam Vision, Google DocAI, GPT-4o).
"""

SYSTEM_PROMPT = (
    "You are a document extraction assistant specialising in Indian power "
    "sector regulatory documents. You are given scanned or digital pages "
    "from GERC (Gujarat Electricity Regulatory Commission) tariff orders. "
    "Your task is to extract tabular data and return it as a CSV. "
    "Return ONLY the CSV with headers — no explanation, no markdown fences. "
    "Use the exact column names specified. Preserve original values exactly "
    "as printed. Use empty cells (not 'NA' or '0') for dashes or missing data."
)

DOC_PROMPTS = {
    "doc1_dgvcl_power_purchase": {
        "task_description": (
            "This is a 2-page table from a DGVCL (Dakshin Gujarat Vij Company) "
            "tariff order showing source-wise power purchase details for FY 2026-27. "
            "The table has sections: IPP/Others (rows 1-11), Central Sector "
            "(rows 1-36), Others (Captive Power), and Renewable (rows 1-15). "
            "Each section ends with a Sub Total row. A grand TOTAL row is at the end. "
            "Some cells contain dashes (-) meaning no data."
        ),
        "output_schema": (
            "section,sr_no,name_of_station,available_mu,dispatch_mu,"
            "fixed_cost_rs_crore,variable_cost_rs_per_kwh,"
            "variable_cost_rs_crore,total_cost_rs_crore"
        ),
        "instructions": (
            "Extract every row from the power purchase table across both pages. "
            "Add a 'section' column indicating which section each row belongs to: "
            "'IPP/Others', 'Central Sector', 'Others', or 'Renewable'. "
            "Include Sub Total and TOTAL rows. "
            "For cells with a dash (-), leave the CSV cell empty. "
            "Preserve station names exactly as printed. "
            "Numbers should not have commas (e.g. 13440 not 13,440). "
            "Return as CSV."
        ),
        "difficulty": "hard",
        "notes": "Tests: multi-page continuity, section classification, 67 rows × 9 cols",
    },
}

DOC_ORDER = list(DOC_PROMPTS.keys())


def get_full_prompt(doc_id: str) -> str:
    """Compose the full user prompt for a given document."""
    p = DOC_PROMPTS[doc_id]
    return (
        f"Document description: {p['task_description']}\n\n"
        f"Task: {p['instructions']}\n\n"
        f"Required CSV format (use these exact column headers):\n"
        f"{p['output_schema']}\n\n"
        f"Return ONLY the CSV. No explanation."
    )
