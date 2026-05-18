"""
Document extraction prompts for Task T2.

Each entry defines the task, expected CSV schema, and specific instructions.
Used identically across all 3 providers (Sarvam Vision, Google DocAI, GPT-4o).
"""

SYSTEM_PROMPT = (
    "You are a document extraction assistant specialising in Indian power "
    "sector regulatory documents. You are given scanned or digital pages "
    "from electricity regulatory commission tariff orders or DISCOM forms. "
    "Your task is to extract data and return it as a CSV. "
    "Return ONLY the CSV with headers — no explanation, no markdown fences. "
    "Use the exact column names specified. Preserve original values exactly "
    "as printed or handwritten. Use empty cells for dashes or missing data."
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

    "doc2_bescom_tariff_schedule": {
        "task_description": (
            "This is a scanned single-page BESCOM tariff schedule (Format D-20) "
            "showing existing tariff for 2023-24 and proposed tariff for 2024-25 "
            "side by side. The page has a watermark stamp partially obscuring some "
            "data. Tariff categories range from LT-1 to HT-6 plus SEZ. "
            "Each category may have multiple slab rows (e.g. different rates "
            "for different sanctioned load levels). Some categories have a "
            "'Demand Based' sub-type variant."
        ),
        "output_schema": (
            "sl_no,tariff_category,sub_type,slab_condition,"
            "fixed_charge_unit,fixed_charge_existing_rs,fixed_charge_proposed_rs,"
            "energy_slab,energy_charge_existing_paise_per_kwh,"
            "energy_charge_proposed_paise_per_kwh"
        ),
        "instructions": (
            "Extract every tariff line from the table. Each slab within a tariff "
            "category becomes its own row. "
            "The 'sub_type' column captures variants like 'Demand Based' or "
            "'under HI' — leave empty if none. "
            "The 'slab_condition' captures conditions like 'With SL upto 50 KW' "
            "or 'With SL < 100HP' — use a dash (–) if no condition. "
            "Both existing (2023-24) and proposed (2024-25) rates go in the same row. "
            "Fixed charge units include: Per KW / Month, Per HP / Month, "
            "Per KVA / Month, Min.Per Inst. / Month. "
            "Note: the page has a watermark/stamp — read through it. "
            "Return as CSV."
        ),
        "difficulty": "very_hard",
        "notes": "Tests: scanned with watermark, side-by-side existing vs proposed, multi-slab categories, mixed units",
    },

    "doc3_dvvnl_handwritten_hindi": {
        "task_description": (
            "This is a cropped section of a DVVNL (Dakshin Vidyut Vitran Nigam "
            "Limited) consumer details form. The table has printed Hindi and "
            "English column headers (क्र0सं0/S.no, शीर्षक/Title, विवरण/Details) "
            "with handwritten responses in the Details column. "
            "The handwriting is in English cursive script. "
            "4 rows are visible: Name, Father/Husband Name, Address, "
            "Organization Name."
        ),
        "output_schema": (
            "sr_no,title_hindi,title_english,details"
        ),
        "instructions": (
            "Extract all rows from the form. "
            "The 'title_hindi' column should contain the Hindi label exactly "
            "as printed (in Devanagari script). "
            "The 'title_english' column should contain the English label. "
            "The 'details' column should contain the handwritten response — "
            "read the cursive handwriting as accurately as possible. "
            "If a field is empty (no handwriting), leave the cell empty. "
            "Return as CSV."
        ),
        "difficulty": "medium",
        "notes": "Tests: handwriting recognition, bilingual labels, cursive English, empty field",
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
