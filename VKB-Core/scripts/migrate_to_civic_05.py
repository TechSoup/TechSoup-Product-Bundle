#!/usr/bin/env python3
"""
migrate_to_civic_05.py — one-time profile bump civic/0.4 -> civic/0.5.

civic/0.5 adds federation (bundle `namespace`/`base_uri` + global `id`, federated
`relations` edges) and a controlled `capability` vocabulary. None of that is
mandatory on an existing record, so the only per-record change is the profile
stamp: `x-civic.profile: civic/0.4` -> `civic/0.5`.

This is a targeted line replacement (not a YAML re-dump) so frontmatter
formatting, ordering, and comments are preserved. Idempotent. Touches every
product README (active and archived); index.md is bumped separately.

Usage:  python3 VKB-Core/scripts/migrate_to_civic_05.py
"""
import pathlib
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"

OLD = "profile: civic/0.4"
NEW = "profile: civic/0.5"


def is_product_readme(p):
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def main():
    changed = 0
    scanned = 0
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not is_product_readme(p):
            continue
        scanned += 1
        text = p.read_text(encoding="utf-8")
        if OLD in text:
            p.write_text(text.replace(OLD, NEW), encoding="utf-8")
            changed += 1
    print(f"Bumped {changed}/{scanned} product records to civic/0.5 "
          f"({scanned - changed} already current).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
