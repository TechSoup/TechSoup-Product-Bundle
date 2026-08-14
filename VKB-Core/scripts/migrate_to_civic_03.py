#!/usr/bin/env python3
"""migrate_to_civic_03.py — one-time VKB migration from civic/0.2 to civic/0.3.

Pass 1 (structure) of the graph migration. Per product-root README, it makes two
mechanical, formatting-preserving frontmatter edits:

  1. x-civic.profile:  civic/0.2  ->  civic/0.3
  2. eligibility key:  ntee_codes  ->  pcs_subject   (rename only; VALUES are
     unchanged here — the NTEE->PCS value crosswalk is Pass 2)

It does NOT touch the body or eligibility values, and does targeted text
replacement (not a YAML round-trip) so diffs stay minimal and comments survive.
Idempotent: running twice is a no-op.

Usage:  python3 VKB-Core/scripts/migrate_to_civic_03.py [--dry-run]
"""
import pathlib
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"


def is_product_readme(p):
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def migrate_text(text):
    """Apply the two renames inside the frontmatter block only. Returns new text."""
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    _, fm, body = parts
    fm = fm.replace("profile: civic/0.2", "profile: civic/0.3")
    fm = fm.replace("ntee_codes:", "pcs_subject:")
    return "---" + fm + "---" + body


def main():
    dry = "--dry-run" in sys.argv
    changed = []
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not is_product_readme(p):
            continue
        text = p.read_text(encoding="utf-8")
        new = migrate_text(text)
        if new != text:
            changed.append(p.relative_to(CORE))
            if not dry:
                p.write_text(new, encoding="utf-8")
    verb = "Would migrate" if dry else "Migrated"
    print(f"{verb} {len(changed)} file(s) to civic/0.3.")
    for c in changed:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
