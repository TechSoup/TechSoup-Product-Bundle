#!/usr/bin/env python3
"""
archive.py — retire an offer from the VKB (a deliberate state transition).

Archiving is an authoring action, NOT part of the build. This does all of it
atomically so the signals can't drift:

  1. Frontmatter: set x-civic.status = ARCHIVED, add `reason` and the structured
     `archived` block (date, disposition, optional successor).
  2. Body: prepend a generated "ARCHIVED" banner (regenerated from the
     frontmatter, between markers) above the preserved original content.
  3. Move the product folder to  products/<category>/_archive/<slug>/
     so humans (Obsidian) and bots surfing the active tree don't see it.
  4. Flip the discovery registry row's Status to ARCHIVED — the row STAYS so the
     offer is never re-discovered/re-added.
  5. Rebuild products.json (the offer drops out, excluded by status).

The record is retained, not deleted — that is the whole point.

Usage:
    python3 VKB-Core/scripts/archive.py <slug> \
        --reason "Acquired by GoFundMe; no longer a standalone offer." \
        --disposition acquired [--successor <slug>] [--date YYYY-MM-DD]
"""
import argparse
import csv
import datetime
import pathlib
import re
import shutil
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

import build_products as build   # same directory; reused to regenerate products.json

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"
REGISTRY = CORE / "registry" / "offers_registry.csv"

DISPOSITIONS = ["acquired", "discontinued", "merged", "superseded",
                "eligibility-changed", "duplicate"]
BANNER_START = "<!-- archived-banner -->"
BANNER_END = "<!-- /archived-banner -->"


def find_readme(slug):
    """Locate <slug>/<slug>_README.md anywhere under products/ (active or archived)."""
    matches = [p for p in PRODUCTS.rglob(f"{slug}_README.md") if p.parent.name == slug]
    return matches[0] if matches else None


def make_banner(reason, archived):
    lines = [
        BANNER_START,
        "# 🗄️ ARCHIVED — not an active offer",
        "",
        f"**Disposition:** {archived['disposition']} · **Archived:** {archived['date']}",
        f"**Reason:** {reason}",
    ]
    if archived.get("successor"):
        lines.append(f"**Successor:** {archived['successor']}")
    lines += ["", BANNER_END, "", ""]
    return "\n".join(lines)


def rewrite_frontmatter_and_body(path, reason, archived):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        sys.exit(f"  ! {path} has no frontmatter")
    data = yaml.safe_load(parts[1]) or {}
    xc = data.get("x-civic")
    if not isinstance(xc, dict):
        sys.exit(f"  ! {path} has no x-civic block")

    # status + reason + archived, inserted right after status, in order
    xc["status"] = "ARCHIVED"
    xc.pop("reason", None)
    xc.pop("archived", None)
    ordered = {}
    for k, v in xc.items():
        ordered[k] = v
        if k == "status":
            ordered["reason"] = reason
            ordered["archived"] = archived
    data["x-civic"] = ordered

    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True,
                            default_flow_style=False, width=1000)

    # strip any prior banner, then prepend a fresh one
    body = re.sub(re.escape(BANNER_START) + r".*?" + re.escape(BANNER_END) + r"\n*",
                  "", parts[2], flags=re.S).lstrip("\n")
    new_body = "\n\n" + make_banner(reason, archived) + body
    path.write_text("---\n" + dumped + "---" + new_body, encoding="utf-8")


def move_to_archive(readme):
    src = readme.parent                      # <category>/<slug>
    archive_dir = src.parent / "_archive"
    dest = archive_dir / src.name
    archive_dir.mkdir(exist_ok=True)
    shutil.move(str(src), str(dest))
    return dest / readme.name


def update_registry(vendor_url, title, reason, disposition, date):
    if not REGISTRY.exists():
        print(f"  ! registry not found at {REGISTRY} — skipped")
        return
    norm = lambda u: (u or "").strip().lower().rstrip("/")
    with open(REGISTRY, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    matched = 0
    for row in rows:
        if norm(row.get("Vendor URL")) == norm(vendor_url) or \
           row.get("Product Name", "").strip().lower() == title.strip().lower():
            row["Status"] = "ARCHIVED"
            row["Last Audited"] = date
            note = f"ARCHIVED {date} ({disposition}): {reason}"
            row["Notes"] = (row.get("Notes", "") + " | " + note) if row.get("Notes") else note
            matched += 1
    if not matched:
        print("  ! no matching registry row (offer will not be blocked from re-discovery!)")
        return
    with open(REGISTRY, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  registry: flipped {matched} row(s) to ARCHIVED")


def main():
    ap = argparse.ArgumentParser(description="Archive (retire) a VKB offer.")
    ap.add_argument("slug")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--disposition", required=True, choices=DISPOSITIONS)
    ap.add_argument("--successor", default=None)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    readme = find_readme(args.slug)
    if readme is None:
        sys.exit(f"No product found for slug '{args.slug}'.")
    if readme.parent.parent.name == "_archive":
        sys.exit(f"'{args.slug}' is already archived ({readme.relative_to(CORE)}).")

    data = yaml.safe_load(readme.read_text(encoding="utf-8").split("---", 2)[1]) or {}
    vendor_url = (data.get("x-civic", {}).get("provenance", {}) or {}).get("vendor_url", "")
    title = data.get("title", args.slug)

    archived = {"date": args.date, "disposition": args.disposition}
    if args.successor:
        archived["successor"] = args.successor

    print(f"Archiving '{args.slug}' ({title})…")
    rewrite_frontmatter_and_body(readme, args.reason, archived)
    dest = move_to_archive(readme)
    print(f"  moved → {dest.parent.relative_to(CORE)}")
    update_registry(vendor_url, title, args.reason, args.disposition, args.date)
    print("  rebuilding products.json…")
    build.main()
    print("Done.")


if __name__ == "__main__":
    main()
