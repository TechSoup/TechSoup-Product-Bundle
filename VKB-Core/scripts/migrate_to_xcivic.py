#!/usr/bin/env python3
"""
migrate_to_xcivic.py — one-time migration of VKB product files to x-civic 0.2.

Rewrites the YAML frontmatter of every product-root README from the flat
"v3" schema into the nested `x-civic` profile (civic/0.2):

    flat keys                      ->  nested x-civic
    -------------------------------    ------------------------------------
    product_name                   ->  title (top-level, OKF core)
    category / sub_category        ->  x-civic.category / sub_category
    cost                           ->  x-civic.offer.summary
    badges                         ->  x-civic.offer.badges (+ offer.type)
    standard_tier / savings_estimate-> x-civic.offer.*
    eligible_org_types             ->  x-civic.eligibility.org_types
    eligible_countries             ->  x-civic.eligibility.regions
    eligibility_ntee_codes         ->  x-civic.eligibility.ntee_codes
    rules / min_budget / max_budget->  x-civic.eligibility.*
    eligibility_notes              ->  x-civic.eligibility.notes
    last_audited / vendor_url      ->  x-civic.provenance.*

Adds the three fields the flat schema lacked: x-civic.profile (civic/0.2),
x-civic.status (ACTIVE), x-civic.provenance.source (TechSoup VKB).

The document BODY is left untouched. Safe to re-run: a file that already has
an `x-civic` block is skipped. `capability` and `relations` are intentionally
NOT added here — those are Phase 2 curation.

Usage:  python3 VKB-Core/scripts/migrate_to_xcivic.py
"""
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"
PROFILE = "civic/0.2"


def to_xcivic(d):
    """Build the nested frontmatter dict from a flat one (order = YAML order)."""
    badges = d.get("badges") or []
    offer = {
        "type": badges[0] if badges else "Offer",
        "summary": d.get("cost"),
        "standard_tier": d.get("standard_tier"),
        "savings_estimate": d.get("savings_estimate"),
        "badges": badges,
    }
    eligibility = {
        "org_types": d.get("eligible_org_types"),
        "regions": d.get("eligible_countries"),
        "ntee_codes": d.get("eligibility_ntee_codes"),
        "rules": d.get("rules"),
        "min_budget": d.get("min_budget"),
    }
    if "max_budget" in d:
        eligibility["max_budget"] = d.get("max_budget")
    if "eligibility_notes" in d:
        eligibility["notes"] = d.get("eligibility_notes")

    la = d.get("last_audited")
    provenance = {
        "last_audited": str(la) if la is not None else None,
        "vendor_url": d.get("vendor_url"),
        "source": "TechSoup VKB",
    }

    return {
        "type": d.get("type", "offer"),
        "title": d.get("product_name"),
        "x-civic": {
            "profile": PROFILE,
            "status": "ACTIVE",
            "category": d.get("category"),
            "sub_category": d.get("sub_category"),
            "offer": offer,
            "eligibility": eligibility,
            "provenance": provenance,
        },
    }


def migrate_file(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return "skip (no frontmatter)"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "skip (malformed frontmatter)"
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return f"ERROR: {e}"
    if not isinstance(data, dict):
        return "skip (frontmatter not a mapping)"
    if "x-civic" in data:
        return "skip (already migrated)"

    new_fm = to_xcivic(data)
    dumped = yaml.safe_dump(new_fm, sort_keys=False, allow_unicode=True,
                            default_flow_style=False, width=1000)
    path.write_text("---\n" + dumped + "---" + parts[2], encoding="utf-8")
    return "migrated"


def main():
    files = [p for p in sorted(PRODUCTS.rglob("*_README.md"))
             if len(p.relative_to(PRODUCTS).parts) == 3]
    counts = {}
    for p in files:
        result = migrate_file(p)
        counts[result.split(":")[0]] = counts.get(result.split(":")[0], 0) + 1
        if result.startswith("ERROR"):
            print(f"  ! {p.relative_to(CORE)}: {result}")
    print(f"Processed {len(files)} product files.")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
