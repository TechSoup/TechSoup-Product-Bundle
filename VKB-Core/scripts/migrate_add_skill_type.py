#!/usr/bin/env python3
"""
migrate_add_skill_type.py — give the agent/skill markdown files OKF frontmatter.

Until now the only OKF concept documents in products/ were the product READMEs.
The category orchestrators (`<cat>/*_orchestrator_skill.md`) and per-product
entry agents (`<cat>/<slug>/agent/*_skill.md`) were plain markdown with no
frontmatter — strictly non-conformant under OKF §9 (every non-reserved .md needs
a parseable `type`).

This prepends minimal core-OKF frontmatter:
  - orchestrators -> type: orchestrator
  - agent skills  -> type: skill            (one undivided skill type for now;
                                             subtypes can come later)
plus a `title` (from the file's H1) and a one-line `description`. No x-civic block
— these are not offers; they stay out of the civic schema and out of
products.json (build_products.py / validate.py only read `*_README.md`).

Idempotent: files that already start with `---` are left untouched.

Usage:  python3 VKB-Core/scripts/migrate_add_skill_type.py [--dry-run]
"""
import pathlib
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"
RESERVED = {"index.md", "log.md"}  # OKF reserved filenames — not concepts


def first_heading(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def classify(p):
    """Return (type, description_suffix) for a skill file, or None to skip."""
    if p.name.endswith("_orchestrator_skill.md"):
        return "orchestrator", "maintains this category's VKB product entries."
    if p.parent.name == "agent" and p.name.endswith("_skill.md"):
        return "skill", "drafts and maintains this product's VKB record."
    return None


def main():
    dry = "--dry-run" in sys.argv
    targets = sorted(p for p in PRODUCTS.rglob("*.md")
                     if not p.name.endswith("_README.md") and p.name not in RESERVED)

    changed, skipped, unmatched = 0, 0, []
    for p in targets:
        kind = classify(p)
        if kind is None:
            unmatched.append(p.relative_to(CORE))
            continue
        ttype, suffix = kind
        text = p.read_text(encoding="utf-8")
        if text.startswith("---"):
            skipped += 1
            continue
        title = first_heading(text, p.stem.replace("_", " ").title())
        fm = (f"---\ntype: {ttype}\ntitle: {title}\n"
              f"description: {title} — {suffix}\n---\n\n")
        if dry:
            print(f"[would write] {p.relative_to(CORE)}  (type: {ttype})")
        else:
            p.write_text(fm + text, encoding="utf-8")
        changed += 1

    print()
    print(f"{'Would update' if dry else 'Updated'} {changed} file(s); "
          f"{skipped} already had frontmatter.")
    if unmatched:
        print(f"WARNING: {len(unmatched)} non-README .md did not match either "
              f"skill pattern (left untouched):")
        for u in unmatched:
            print(f"  - {u}")


if __name__ == "__main__":
    main()
