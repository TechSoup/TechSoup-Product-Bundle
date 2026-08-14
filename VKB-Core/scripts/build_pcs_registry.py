#!/usr/bin/env python3
"""Build the Candid PCS registry for civic/0.3 from the official 2024 workbook.

Pass 2 (Chunk 1) of the civic/0.3 migration. We only consume the **Subject**
(867 terms) and **OrgType** (93 terms) facets; Population / Strategy / Transaction
are out of scope for VKB eligibility.

The workbook's `All Terms` column is an Excel ``=CONCATENATE(C,D,E,F)`` formula, so
its cached value is unavailable via openpyxl when formulas are present. We instead
compute each term's label directly from the hierarchy level columns (exactly one
level column is populated per row). We also capture the `Former GCS/NTEE Code`
crosswalk, which is what lets us migrate the legacy NTEE-style codes.

Source : /Users/marniewebb/Developer/Related Assets/PCS_Taxonomy_Definitions_2024.xlsx
Output : VKB-Core/registry/pcs_registry.json   (Candid PCS, CC BY 4.0 — see NOTICE)
Run    : ./venv/bin/python VKB-Core/scripts/build_pcs_registry.py
"""
import json
import os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
XLSX = "/Users/marniewebb/Developer/Related Assets/PCS_Taxonomy_Definitions_2024.xlsx"
OUT = os.path.join(REPO, "VKB-Core", "registry", "pcs_registry.json")

# (sheet name, first level column index 1-based, last level column index 1-based)
FACETS = {
    "subject": ("Subject", 3, 6),   # cols C..F
    "org_type": ("OrgType", 3, 6),  # cols C..F
}


def build_facet(ws, first_col, last_col):
    """Return {pcs_code: {label, level, former_code, definition}} for one sheet."""
    terms = {}
    def_col = last_col + 2  # one blank col after the All Terms formula col
    for row in range(2, ws.max_row + 1):
        code = ws.cell(row, 1).value
        if not code:
            continue
        code = str(code).strip()
        former = ws.cell(row, 2).value
        # Exactly one level column is populated per row; level = its 1-based depth.
        label, level = None, None
        for depth, col in enumerate(range(first_col, last_col + 1), start=1):
            val = ws.cell(row, col).value
            if val not in (None, ""):
                label, level = str(val).strip(), depth
                break
        definition = ws.cell(row, def_col).value
        terms[code] = {
            "label": label,
            "level": level,
            "former_code": (str(former).strip() if former not in (None, "") else None),
            "definition": (str(definition).strip() if definition not in (None, "") else None),
        }
    return terms


def main():
    wb = openpyxl.load_workbook(XLSX, data_only=False)
    registry = {
        "meta": {
            "source": "Candid Philanthropy Classification System (PCS), 2024 edition",
            "source_file": os.path.basename(XLSX),
            "license": "CC BY 4.0",
            "attribution": "Philanthropy Classification System, Candid",
            "facets": {},
        }
    }
    for key, (sheet, first_col, last_col) in FACETS.items():
        ws = wb[sheet]
        terms = build_facet(ws, first_col, last_col)
        registry[key] = terms
        registry["meta"]["facets"][key] = len(terms)
        print(f"{key:9s} <- sheet {sheet!r}: {len(terms)} terms")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
