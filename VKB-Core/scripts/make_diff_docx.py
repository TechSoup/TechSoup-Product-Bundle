#!/usr/bin/env python3
"""
make_diff_docx.py — build a Word (.docx) version of the products.json vs. markdown
difference report, with step-by-step directions for editing by hand.

Runs the same comparison as diff_json_vs_md.py (reusing build_products.py's flatten
logic), then writes a formatted Word document.

Usage:  python VKB-Core/scripts/make_diff_docx.py
Output: VKB-Core/scripts/products_diff_report.docx
"""
import json
import pathlib
import sys

import build_products as build
import diff_json_vs_md as differ
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

CORE = pathlib.Path(__file__).resolve().parent.parent
JSON_PATH = CORE.parent / "Offer-Center" / "resources" / "data" / "products.json"
OUT = pathlib.Path(__file__).resolve().parent / "products_diff_report.docx"

MONO = "Consolas"


def code(run):
    run.font.name = MONO
    run.font.size = Pt(9)
    return run


def val(cell, v):
    """Write a value into a table cell as monospace-ish text."""
    if isinstance(v, (list, dict)):
        s = json.dumps(v, default=str)
    elif v is None:
        s = "(null)"
    elif v == "":
        s = "(empty)"
    else:
        s = str(v)
    p = cell.paragraphs[0]
    r = p.add_run(s)
    r.font.name = MONO
    r.font.size = Pt(9)


def add_code_line(doc, text):
    p = doc.add_paragraph()
    code(p.add_run(text))
    return p


def main():
    md = differ.read_markdown_records()
    feed = json.load(open(JSON_PATH, encoding="utf-8"))
    records = feed["products"] if isinstance(feed, dict) else feed  # civic/0.5 wraps records under "products"
    actual = {r["slug"]: r for r in records}

    md_slugs, json_slugs = set(md), set(actual)
    only_md = sorted(md_slugs - json_slugs)
    only_json = sorted(json_slugs - md_slugs)
    common = sorted(md_slugs & json_slugs)

    diffs = {}
    for slug in common:
        expected, path = md[slug]
        got = actual[slug]
        rows = []
        for key in sorted((set(expected) | set(got)) - differ.DERIVED_FIELDS):
            if expected.get(key) != got.get(key):
                fm = differ.FIELD_TO_FRONTMATTER.get(key, "(unknown / not in contract)")
                rows.append((key, fm, expected.get(key), got.get(key)))
        if rows:
            diffs[slug] = (path, rows)

    doc = Document()

    doc.add_heading("products.json vs. Markdown — Difference Report & Editing Guide", 0)

    intro = doc.add_paragraph()
    intro.add_run(
        "products.json is generated from the product README frontmatter by build.py. "
        "This document shows where the two currently disagree and gives step-by-step "
        "directions for reconciling them by hand in a Markdown editor."
    )

    # --- Directions -------------------------------------------------------
    doc.add_heading("How the pipeline works", 1)
    p = doc.add_paragraph()
    p.add_run("The build runs in one direction only:").bold = False
    add_code_line(doc, "markdown READMEs  ->  SQLite  ->  Offer-Center/products.json")
    p = doc.add_paragraph()
    p.add_run(
        "The markdown files are the source of truth. products.json is a generated "
        "artifact. Any edit made directly to products.json is overwritten the next "
        "time build_products.py runs, so corrections must be made in the markdown."
    )

    doc.add_heading("Directions: how to make an edit", 1)

    steps = [
        ("Find the product below.", "Each product with a difference is listed in the "
         "\"Field-level differences\" section with its exact file path."),
        ("Open the README in a Markdown editor.", "The file is "
         "VKB-Core/products/<category>/<slug>/<slug>_README.md. Edit only the YAML "
         "frontmatter at the top (between the two --- lines)."),
        ("Edit the frontmatter key shown in the table.", "The \"Edit this frontmatter "
         "key\" column gives the dotted path, e.g. x-civic.offer.summary means the "
         "'summary:' line nested under 'offer:' under 'x-civic:'. Set it to the value "
         "you want. Keep the YAML indentation exactly as-is."),
        ("Save the file.", "Do not edit products.json directly — your change belongs in "
         "the markdown."),
        ("Rebuild products.json.", "Run: python VKB-Core/scripts/build_products.py"),
        ("Verify.", "Re-run the diff to confirm the difference is gone: "
         "python VKB-Core/scripts/diff_json_vs_md.py"),
    ]
    for i, (title, body) in enumerate(steps, 1):
        pp = doc.add_paragraph(style="List Number")
        pp.add_run(title).bold = True
        pp.add_run(" " + body)

    doc.add_heading("Field-to-frontmatter map", 1)
    doc.add_paragraph(
        "Each flat key in products.json maps to a location in the README frontmatter:"
    )
    mt = doc.add_table(rows=1, cols=2)
    mt.style = "Light Grid Accent 1"
    mt.rows[0].cells[0].paragraphs[0].add_run("products.json key").bold = True
    mt.rows[0].cells[1].paragraphs[0].add_run("Frontmatter location").bold = True
    for k, v in differ.FIELD_TO_FRONTMATTER.items():
        row = mt.add_row().cells
        val(row[0], k)
        val(row[1], v)

    # --- Summary ----------------------------------------------------------
    doc.add_heading("Summary of current differences", 1)
    for label, num in [
        ("Live markdown products", len(md)),
        ("products.json records", len(actual)),
        ("Products with field differences", len(diffs)),
        ("In markdown but missing from products.json (run build.py to add)", len(only_md)),
        ("In products.json but no live markdown", len(only_json)),
    ]:
        pp = doc.add_paragraph(style="List Bullet")
        pp.add_run(f"{label}: ")
        pp.add_run(str(num)).bold = True

    if only_md:
        doc.add_heading("In markdown, missing from products.json", 2)
        for slug in only_md:
            doc.add_paragraph(
                f"{slug} — {md[slug][1].relative_to(CORE.parent)}", style="List Bullet"
            )

    if only_json:
        doc.add_heading("In products.json, no matching live markdown", 2)
        doc.add_paragraph(
            "A rebuild would drop these unless a README exists for them:"
        )
        for slug in only_json:
            doc.add_paragraph(
                f"{slug} — {actual[slug].get('product_name')}", style="List Bullet"
            )

    # --- Field-level differences -----------------------------------------
    doc.add_heading("Field-level differences", 1)
    if not diffs:
        p = doc.add_paragraph()
        r = p.add_run("None — every shared product currently matches. "
                      "products.json is fully in sync with the markdown.")
        r.italic = True
    else:
        for slug in sorted(diffs):
            path, rows = diffs[slug]
            doc.add_heading(f"{slug} — {actual[slug].get('product_name')}", 2)
            pp = doc.add_paragraph()
            pp.add_run("Edit: ").bold = True
            code(pp.add_run(str(path.relative_to(CORE.parent))))

            t = doc.add_table(rows=1, cols=4)
            t.style = "Light Grid Accent 1"
            hdr = t.rows[0].cells
            for c, txt in zip(hdr, ["Field", "Edit this frontmatter key",
                                    "Markdown value (source)", "products.json value"]):
                c.paragraphs[0].add_run(txt).bold = True
            for field, fm, mdv, jsonv in rows:
                cells = t.add_row().cells
                val(cells[0], field)
                val(cells[1], fm)
                val(cells[2], mdv)
                val(cells[3], jsonv)

    doc.save(OUT)
    print(f"Wrote {OUT.relative_to(CORE.parent)}")
    print(f"  {len(diffs)} product(s) differ, "
          f"{len(only_md)} md-only, {len(only_json)} json-only.")


if __name__ == "__main__":
    main()
