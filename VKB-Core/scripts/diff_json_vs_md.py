#!/usr/bin/env python3
"""
diff_json_vs_md.py — show where Offer-Center/products.json disagrees with the
markdown source of truth, and exactly which frontmatter field to edit to fix it.

The build pipeline is one-way: markdown READMEs -> products.json (see
build_products.py). This tool does NOT change anything. It re-flattens each live
README the same way build_products.py would, compares the result against the
current products.json, and writes a human-readable report so edits can be made
by hand in a .md editor.

Usage:  python VKB-Core/scripts/diff_json_vs_md.py
Output: VKB-Core/scripts/products_diff_report.md
"""
import json
import pathlib
import sys

import build_products as build  # reuse the exact flatten/status logic that produces products.json

CORE = pathlib.Path(__file__).resolve().parent.parent      # VKB-Core
PRODUCTS = CORE / "products"
JSON_PATH = CORE.parent / "Offer-Center" / "products.json"
REPORT = pathlib.Path(__file__).resolve().parent / "products_diff_report.md"

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

# products.json flat key  ->  where it lives in the README frontmatter.
FIELD_TO_FRONTMATTER = {
    "id": "(namespace:slug — identity, not an editable field)",
    "type": "type",
    "product_name": "title",
    "category": "x-civic.category",
    "sub_category": "x-civic.sub_category",
    "cost": "x-civic.offer.summary",
    "capability": "x-civic.capability",
    "alias": "x-civic.alias",
    "standard_tier": "x-civic.offer.standard_tier",
    "savings_estimate": "x-civic.offer.savings_estimate",
    "badges": "x-civic.offer.badges",
    "eligible_audiences": "x-civic.eligibility.eligible_audiences",
    "audience_tuples": "(derived from registry/audiences.json — not directly editable)",
    "eligible_audience_labels": "(derived from registry/audiences.json — not directly editable)",
    "eligible_countries": "x-civic.eligibility.regions",
    "eligibility_pcs_subject": "x-civic.eligibility.pcs_subject",
    "rules": "x-civic.eligibility.rules",
    "min_budget": "x-civic.eligibility.min_budget",
    "max_budget": "x-civic.eligibility.max_budget",
    "eligibility_notes": "x-civic.eligibility.notes",
    "last_audited": "x-civic.provenance.last_audited",
    "vendor_url": "x-civic.provenance.vendor_url",
    "slug": "(folder name — identity, not an editable field)",
}

# Keys present in products.json but derived AFTER flatten() (e.g. graph edges from
# attach_relations). They have no frontmatter source, so comparing them is noise.
DERIVED_FIELDS = {"relations"}


def read_markdown_records():
    """Return {slug: (flat_record, file_path)} for every live product README."""
    audiences = build.load_audiences()
    namespace = build.load_bundle()["namespace"]
    out = {}
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not build.is_product_readme(p):
            continue
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            data = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as e:
            print(f"  ! YAML error in {p}: {e}")
            continue
        if data.get("type", "offer") != "offer":   # products.json is offers only
            continue
        status = build.status_of(data)
        if status is not None and status not in build.LIVE_STATUSES:
            continue
        slug = p.parent.name
        out[slug] = (build.flatten(data, slug, audiences, namespace), p)
    return out


def fmt(v):
    """Render a value compactly for the report."""
    if isinstance(v, (list, dict)):
        return "`" + json.dumps(v, default=str) + "`"
    if v is None:
        return "*(null)*"
    if v == "":
        return "*(empty)*"
    return f"`{v}`"


def main():
    md = read_markdown_records()
    feed = json.load(open(JSON_PATH, encoding="utf-8"))
    records = feed["products"] if isinstance(feed, dict) else feed  # civic/0.5 wraps records under "products"
    actual = {r["slug"]: r for r in records}

    md_slugs, json_slugs = set(md), set(actual)
    only_md = sorted(md_slugs - json_slugs)
    only_json = sorted(json_slugs - md_slugs)
    common = sorted(md_slugs & json_slugs)

    # Per-product field differences.
    diffs = {}  # slug -> (path, [ (field, frontmatter_path, md_val, json_val) ])
    for slug in common:
        expected, path = md[slug]
        got = actual[slug]
        rows = []
        for key in sorted((set(expected) | set(got)) - DERIVED_FIELDS):
            if expected.get(key) != got.get(key):
                fm = FIELD_TO_FRONTMATTER.get(key, "*(unknown / not in contract)*")
                rows.append((key, fm, expected.get(key), got.get(key)))
        if rows:
            diffs[slug] = (path, rows)

    lines = []
    lines.append("# products.json vs. markdown — difference report")
    lines.append("")
    lines.append("`products.json` is generated from the product README frontmatter by "
                 "`build_products.py`. This report shows where the two currently disagree "
                 "and which frontmatter field to edit in a `.md` editor to reconcile them. "
                 "**Editing `products.json` directly is overwritten on the next build — "
                 "edit the markdown instead, then run `python VKB-Core/scripts/build_products.py`.**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Live markdown products: **{len(md)}**")
    lines.append(f"- products.json records: **{len(actual)}**")
    lines.append(f"- Products with field differences: **{len(diffs)}**")
    lines.append(f"- In markdown but missing from products.json: **{len(only_md)}** "
                 f"(run `build_products.py` to add)")
    lines.append(f"- In products.json but no live markdown: **{len(only_json)}** "
                 f"(edit was made only in JSON, or the README is archived/missing)")
    lines.append("")

    if only_md:
        lines.append("## In markdown, missing from products.json")
        lines.append("")
        lines.append("These would appear after a rebuild:")
        lines.append("")
        for slug in only_md:
            lines.append(f"- `{slug}` — {md[slug][1].relative_to(CORE.parent)}")
        lines.append("")

    if only_json:
        lines.append("## In products.json, no matching live markdown")
        lines.append("")
        lines.append("A rebuild would DROP these. If they should stay, the edit must be "
                     "made in (or a README created for) the markdown:")
        lines.append("")
        for slug in only_json:
            lines.append(f"- `{slug}` — {actual[slug].get('product_name')}")
        lines.append("")

    lines.append("## Field-level differences")
    lines.append("")
    if not diffs:
        lines.append("*None — every shared product matches.*")
    for slug in sorted(diffs):
        path, rows = diffs[slug]
        lines.append(f"### `{slug}` — {actual[slug].get('product_name')}")
        lines.append("")
        lines.append(f"**Edit:** `{path.relative_to(CORE.parent)}`")
        lines.append("")
        lines.append("| Field | Edit this frontmatter key | Markdown value (source) | products.json value |")
        lines.append("|---|---|---|---|")
        for field, fm, mdv, jsonv in rows:
            lines.append(f"| `{field}` | `{fm}` | {fmt(mdv)} | {fmt(jsonv)} |")
        lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(CORE.parent)}")
    print(f"  {len(diffs)} product(s) differ, "
          f"{len(only_md)} md-only, {len(only_json)} json-only.")


if __name__ == "__main__":
    main()
