#!/usr/bin/env python3
"""crosswalk_civic_03.py — Pass 2 (Chunk 2) of the civic/0.3 migration.

Pass 1 renamed the eligibility key (ntee_codes -> pcs_subject) but left the
VALUES as legacy NTEE codes. This pass rewrites those values to Candid PCS
Subject codes, using the registry built in Chunk 1 (registry/pcs_registry.json).

Only six non-`ALL` NTEE codes are actually in use across the product set, and
all six are NTEE *common codes* (the X01 Alliance/Advocacy and X02
Management/Technical-Assistance series). PCS expresses advocacy/management via
the Strategy facet — out of scope here — so there is no leaf-level Subject
equivalent. Per decision (2026-06-27), each is mapped to its NTEE major-group
root's PCS Subject term; the two roots with no crosswalk entry (I00 Crime &
Legal-Related, J00 Employment) are hand-assigned to their level-1 PCS homes.

`ALL` is left untouched. The map is exhaustive for current values; any value
not in CROSSWALK is left in place and reported, so new codes never silently pass
through. Edits are confined to the frontmatter `pcs_subject:` list and preserve
formatting. Idempotent: PCS codes are not in CROSSWALK, so a second run is a no-op.

Usage:  ./venv/bin/python VKB-Core/scripts/crosswalk_civic_03.py [--dry-run]
"""
import pathlib
import re
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"

# legacy NTEE value -> PCS Subject code.  See module docstring for rationale.
CROSSWALK = {
    "P01": "SS000000",  # Human services            (P00 crosswalk)
    "R01": "SR000000",  # International human rights (R00 crosswalk; civil/human rights home)
    "W01": "SK000000",  # Public affairs            (W00 crosswalk)
    "W02": "SK000000",  # Public affairs            (W00 crosswalk)
    "I01": "SJ000000",  # Public safety and disaster management (Crime & Legal; hand-assigned)
    "J01": "SN000000",  # Community and economic development    (Employment; hand-assigned)
}

# A pcs_subject list item: "    - <value>" with optional inline comment/quotes.
ITEM = re.compile(r"^(\s*-\s*)([A-Za-z0-9]+)(\s*(?:#.*)?)$")
# A migrated value: `ALL` or a PCS Subject code (S + letter + 6 digits).
SETTLED = re.compile(r"^(ALL|S[A-Z]\d{6})$")


def is_product_readme(p):
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def crosswalk_text(text, unmapped):
    """Rewrite pcs_subject list values in the frontmatter only. Returns new text."""
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    _, fm, body = parts

    lines = fm.split("\n")
    out, in_block, key_indent, seen = [], False, None, set()
    for line in lines:
        stripped = line.strip()
        if re.match(r"^pcs_subject:\s*(\[.*\])?\s*$", stripped):
            in_block, key_indent, seen = True, len(line) - len(line.lstrip()), set()
            out.append(line)
            continue
        if in_block:
            m = ITEM.match(line)
            if m:
                prefix, val, suffix = m.groups()
                new_val = CROSSWALK.get(val, val)
                if new_val == val and not SETTLED.match(val):
                    unmapped.add(val)  # neither ALL, a PCS code, nor in the crosswalk
                if new_val in seen:
                    continue  # collapse duplicates (e.g. W01 & W02 both -> SK000000)
                seen.add(new_val)
                out.append(f"{prefix}{new_val}{suffix}")
                continue
            # A line that isn't a list item ends the block (next key, blank, etc.)
            indent = len(line) - len(line.lstrip())
            if stripped == "" or indent <= key_indent:
                in_block = False
        out.append(line)

    return "---" + "\n".join(out) + "---" + body


def main():
    dry = "--dry-run" in sys.argv
    changed, unmapped = [], set()
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not is_product_readme(p):
            continue
        text = p.read_text(encoding="utf-8")
        new = crosswalk_text(text, unmapped)
        if new != text:
            changed.append(p.relative_to(CORE))
            if not dry:
                p.write_text(new, encoding="utf-8")
    verb = "Would crosswalk" if dry else "Crosswalked"
    print(f"{verb} {len(changed)} file(s) to PCS Subject codes.")
    for c in changed:
        print(f"  - {c}")
    if unmapped:
        print(f"\n!! {len(unmapped)} value(s) had no crosswalk entry (left in place): "
              f"{sorted(unmapped)}")


if __name__ == "__main__":
    main()
