#!/usr/bin/env python3
"""migrate_audiences.py — civic/0.4 eligibility model: org_types -> eligible_audiences.

A flat (org_types AND pcs_subject) record cannot express offers open to two
different audiences at once — e.g. the 49 offers tagged `[Nonprofit, Library]`
are available to nonprofits (any mission) OR to public libraries (a government
org whose subject is libraries). That is an OR of two (org_type AND subject)
tuples, which a single flat pair can't hold.

This pass replaces the per-offer `org_types:` list with an `eligible_audiences:`
list of audience KEYS (see registry/audiences.json). Each key resolves to an
(org_type AND subject) tuple; an offer is eligible to a user who matches ANY of
its audiences. `pcs_subject` is left untouched — it remains an independent,
offer-level mission restriction.

The mapping below is a best-effort starting point for the human QA pass; the
`Library -> public_library` assumption in particular is what QA confirms per
offer. Frontmatter-only, formatting-preserving, idempotent (no `org_types:`
block -> no-op).

Usage:  ./venv/bin/python VKB-Core/scripts/migrate_audiences.py [--dry-run]
"""
import pathlib
import re
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"

# legacy org_type string -> audience key (see registry/audiences.json)
AUDIENCE = {
    "Nonprofit": "nonprofit",
    "Library": "public_library",
    "Public Library": "public_library",
    "Social Enterprise": "social_enterprise",
    "Healthcare": "healthcare",
    "K-12": "k12",
    "Personal": "personal",
    "Team": "team",
    "ALL": "everyone",
}

VALID_KEYS = set(AUDIENCE.values())  # already-migrated values (idempotency)
ITEM = re.compile(r"^\s*-\s*(.+?)\s*$")  # a YAML list item: "<indent>- value"


def is_product_readme(p):
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def migrate_text(text, unmapped):
    """Replace the org_types block with eligible_audiences in frontmatter only.

    Handles either key name (org_types or an already-renamed eligible_audiences
    whose values are still legacy strings), so the pass is safe to re-run.
    """
    if not text.startswith("---"):
        return text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    _, fm, body = parts

    lines = fm.split("\n")
    out, in_block, key_indent = [], False, None
    for line in lines:
        stripped = line.strip()
        if re.match(r"^(org_types|eligible_audiences):\s*(\[.*\])?\s*$", stripped):
            in_block = True
            key_indent = len(line) - len(line.lstrip())
            indent = " " * key_indent
            out.append(f"{indent}eligible_audiences:")
            collected = []
            out.append(("__AUDIENCE_ITEMS__", indent, collected))
            continue
        if in_block:
            m = ITEM.match(line)
            if m:
                val = m.group(1).strip().strip("'\"")
                if val in AUDIENCE:
                    key = AUDIENCE[val]
                elif val in VALID_KEYS:
                    key = val  # already migrated
                else:
                    unmapped.add(val)
                    key = val  # leave unknown values visible rather than dropping
                if key not in collected:
                    collected.append(key)
                continue
            indent = len(line) - len(line.lstrip())
            if stripped == "" or indent <= key_indent:
                in_block = False
        out.append(line)

    # expand the placeholder into "- key" lines
    expanded = []
    for item in out:
        if isinstance(item, tuple) and item[0] == "__AUDIENCE_ITEMS__":
            _, indent, collected = item
            for key in collected:
                expanded.append(f"{indent}- {key}")
        else:
            expanded.append(item)

    return "---" + "\n".join(expanded) + "---" + body


def main():
    dry = "--dry-run" in sys.argv
    changed, unmapped = [], set()
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not is_product_readme(p):
            continue
        text = p.read_text(encoding="utf-8")
        new = migrate_text(text, unmapped)
        if new != text:
            changed.append(p.relative_to(CORE))
            if not dry:
                p.write_text(new, encoding="utf-8")
    verb = "Would migrate" if dry else "Migrated"
    print(f"{verb} {len(changed)} file(s) to eligible_audiences.")
    for c in changed:
        print(f"  - {c}")
    if unmapped:
        print(f"\n!! {len(unmapped)} org_type value(s) had no audience mapping "
              f"(left as-is): {sorted(unmapped)}")


if __name__ == "__main__":
    main()
