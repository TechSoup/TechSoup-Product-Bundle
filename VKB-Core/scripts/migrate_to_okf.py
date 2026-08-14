#!/usr/bin/env python3
"""
Migrate VKB product files to Open Knowledge Format (OKF) conformance.

OKF's one hard rule: every concept document declares a `type`. This script adds
`type: offer` to each product's frontmatter if it's missing — and nothing else.
It edits textually (inserts a single line after the opening `---`) so diffs stay
minimal and reviewable. Re-runnable and idempotent: products that already declare
a `type` are skipped.

Usage:  python3 VKB-Core/scripts/migrate_to_okf.py
"""
import pathlib
import re

PRODUCTS = pathlib.Path(__file__).resolve().parent.parent / "products"


def main():
    changed, skipped = 0, 0
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        # Only product-root READMEs: products/[category]/[slug]/[slug]_README.md
        if len(p.relative_to(PRODUCTS).parts) != 3:
            continue
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            print(f"  ! no frontmatter, skipped: {p}")
            skipped += 1
            continue
        end = text.find("\n---", 4)
        frontmatter = text[4:end] if end != -1 else ""
        if re.search(r"(?m)^type:\s*\S", frontmatter):
            skipped += 1
            continue
        # Insert `type: offer` as the first frontmatter field
        p.write_text("---\ntype: offer\n" + text[4:], encoding="utf-8")
        changed += 1
    print(f"\nDone. type added: {changed}  |  already had type / skipped: {skipped}")


if __name__ == "__main__":
    main()
