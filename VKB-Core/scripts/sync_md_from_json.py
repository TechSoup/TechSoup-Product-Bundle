#!/usr/bin/env python3
"""
sync_md_from_json.py — the REVERSE of the build pipeline.

The normal flow is one-way: markdown READMEs -> products.json (build_products.py),
and diff_json_vs_md.py / make_diff_docx.py only *report* where they disagree,
leaving edits to a human. This tool instead treats **products.json as the source
of truth** and rewrites the markdown to match it:

  1. MODIFY  — for products in both, overwrite the managed frontmatter fields of
               the README with the products.json values (only the fields the flat
               contract owns; body prose and unmanaged frontmatter are preserved).
  2. ARCHIVE — for products in markdown but NOT in products.json (md-only), retire
               the README using the standard archive convention (x-civic.status =
               ARCHIVED + `archived` block + banner, moved to <category>/_archive/).
  3. CREATE  — for products in products.json but with no README (json-only), scaffold
               products/<category>/<slug>/<slug>_README.md with x-civic frontmatter
               reconstructed from the record and a Level 1/2/3 body template that
               matches the existing schema.

This is LOSSY by nature (products.json is a flattened projection — it has no body
prose, no offer.type, no provenance.source, no authored relations), so CREATE fills
those non-contract fields with defaults/placeholders and MODIFY never touches them.

SAFE BY DEFAULT: a bare run is a DRY RUN — it prints exactly what it would do and
writes nothing. Pass --apply to actually modify/archive/create. After --apply, run
`python VKB-Core/scripts/build_products.py` to regenerate the feed and confirm.

Usage:
    python VKB-Core/scripts/sync_md_from_json.py            # dry run (preview)
    python VKB-Core/scripts/sync_md_from_json.py --apply    # write changes
    python VKB-Core/scripts/sync_md_from_json.py --json <path-to-products.json>
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

import diff_json_vs_md as differ   # read_markdown_records / FIELD_TO_FRONTMATTER / DERIVED_FIELDS
import archive                     # reuse the canonical archive convention

CORE = pathlib.Path(__file__).resolve().parent.parent          # VKB-Core
PRODUCTS = CORE / "products"
# products.json source of truth. The published feed lives under resources/data/;
# fall back to the build's emit path if that's absent.
JSON_CANDIDATES = [
    CORE.parent / "Offer-Center" / "resources" / "data" / "products.json",
    CORE.parent / "Offer-Center" / "products.json",
]

# Reason/disposition stamped on md-only records when archived in bulk.
ARCHIVE_REASON = "Absent from the products.json feed (reverse-sync from JSON)."
ARCHIVE_DISPOSITION = "discontinued"

_MISSING = object()


def norm(v):
    """Collapse the three ways a field says 'no value' — absent, null, empty string —
    so they don't register as substantive differences (products.json stores '' where
    the markdown/flatten uses null or omits the key)."""
    if v is _MISSING or v is None or v == "":
        return None
    return v


def clean(v):
    """Strip incidental whitespace introduced while hand-editing the JSON (e.g. a
    leading space after a comma in a list: ' public_library'). Applied to the JSON
    value before BOTH comparison and writing, so whitespace-only noise is neither
    flagged as a change nor propagated into the markdown — only meaningful edits are."""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, list):
        return [clean(x) for x in v]
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    return v


def slugify(name):
    """Convention-conforming slug: lowercase, non-word runs -> single underscore."""
    return re.sub(r"[^\w]+", "_", (name or "").strip().lower()).strip("_")


def num_or_null(v):
    """Coerce a budget field to what the schema allows (number | null). The JSON stores
    '' for 'no budget'; the schema rejects that, so empty/non-numeric becomes null.
    Booleans are treated as non-numeric (True/False are not valid budgets)."""
    if isinstance(v, bool):
        return None
    return v if isinstance(v, (int, float)) else None


def show(v):
    return "(absent)" if v is _MISSING else repr(v)


def managed_paths():
    """flat products.json key -> frontmatter key path (list), for the fields the
    flat contract OWNS. Derived from diff_json_vs_md's field map: only entries that
    resolve to a real frontmatter location (`type`, `title`, or an `x-civic.*` dotted
    path) are writable; identity/derived keys (id, slug, audience_tuples, …) are not.
    """
    paths = {}
    for key, loc in differ.FIELD_TO_FRONTMATTER.items():
        if loc in ("type", "title"):
            paths[key] = [loc]
        elif loc.startswith("x-civic."):
            paths[key] = loc.split(".")
    return paths


MANAGED = managed_paths()


def get_nested(root, path):
    d = root
    for key in path:
        if not isinstance(d, dict) or key not in d:
            return _MISSING
        d = d[key]
    return d


def set_nested(root, path, value):
    d = root
    for key in path[:-1]:
        nxt = d.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            d[key] = nxt
        d = nxt
    d[path[-1]] = value


def resolve_json(explicit):
    if explicit:
        p = pathlib.Path(explicit)
        if not p.exists():
            sys.exit(f"products.json not found: {p}")
        return p
    for cand in JSON_CANDIDATES:
        if cand.exists():
            return cand
    sys.exit("products.json not found in any known location:\n  " +
             "\n  ".join(str(c) for c in JSON_CANDIDATES))


def category_dirs():
    """Map lowercased category -> actual existing folder name under products/."""
    return {p.name.lower(): p.name for p in PRODUCTS.iterdir() if p.is_dir()}


def dump_frontmatter(data):
    """Serialize frontmatter the same way archive.py does, for a consistent style."""
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=1000)


# --- (1) MODIFY -----------------------------------------------------------------

def plan_modify(slug, expected_flat, path, record):
    """Return [(flat_key, frontmatter_path, md_value, json_value)] for managed fields
    whose README value differs from the products.json record. json is the truth."""
    changes = []
    for key, fpath in MANAGED.items():
        raw = record.get(key, _MISSING)
        # Field absent from the JSON record — nothing to sync.
        if raw is _MISSING:
            continue
        json_val = clean(raw)                       # sanitized value we'd actually write
        md_val = expected_flat.get(key, _MISSING)
        # Skip whitespace-only / empty-vs-null noise — only meaningful edits count.
        if norm(md_val) == norm(json_val):
            continue
        changes.append((key, fpath, md_val, json_val))
    return changes


def apply_modify(path, changes):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"    ! {path} has no frontmatter — skipped")
        return False
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data.get("x-civic"), dict):
        print(f"    ! {path} has no x-civic block — skipped")
        return False
    for _key, fpath, _md, json_val in changes:
        set_nested(data, fpath, json_val)
    path.write_text("---\n" + dump_frontmatter(data) + "---" + parts[2], encoding="utf-8")
    return True


# --- (3) CREATE -----------------------------------------------------------------

BODY_TEMPLATE = """
## Level 1 (Quick Glance)
{summary}

## Level 2 (Detailed Eligibility Matrix)
- <!-- TODO: eligibility details -->

## Level 3 (Implementation & Maintenance Requirements)
- **Technical Prerequisites:** <!-- TODO -->
- **IT Expertise Required:** <!-- TODO -->
- **Maintenance Overhead:** <!-- TODO -->
"""


def build_new_frontmatter(record):
    """Reconstruct x-civic frontmatter (civic/0.5) from a flat products.json record.

    Fields the flat contract can't carry (offer.type, provenance.source) get sane
    defaults/placeholders; everything else comes straight from the record.
    """
    record = clean(record)                          # strip hand-editing whitespace noise
    badges = record.get("badges") or []
    # offer.type is required to be a string by the schema but isn't in the flat
    # contract — infer it from the first badge (matches real files, e.g. "Discount"),
    # falling back to "Discount". Review by hand for accuracy.
    offer = {
        "type": badges[0] if badges else "Discount",
        "summary": clean(record.get("cost")) or "",
        "standard_tier": record.get("standard_tier") or None,
        "savings_estimate": record.get("savings_estimate") or None,
        "badges": badges,
    }
    eligibility = {
        "eligible_audiences": record.get("eligible_audiences") or [],
        "regions": record.get("eligible_countries") or [],
        "pcs_subject": record.get("eligibility_pcs_subject") or [],
        "rules": record.get("rules") or None,
        "min_budget": num_or_null(record.get("min_budget")),
        "max_budget": num_or_null(record.get("max_budget")),
    }
    if record.get("eligibility_notes"):
        eligibility["notes"] = record.get("eligibility_notes")

    xcivic = {
        "profile": "civic/0.5",
        "status": "ACTIVE",
        "category": record.get("category"),
        "sub_category": record.get("sub_category"),
    }
    if record.get("capability"):
        xcivic["capability"] = record.get("capability")
    if record.get("alias"):
        xcivic["alias"] = record.get("alias")
    xcivic["offer"] = offer
    xcivic["eligibility"] = eligibility
    xcivic["provenance"] = {
        "last_audited": record.get("last_audited"),
        "vendor_url": record.get("vendor_url"),
        "source": "products.json (reverse-sync)",
    }

    return {
        "type": record.get("type") or "offer",
        "title": record.get("product_name"),
        "x-civic": xcivic,
    }


def create_slug(record):
    """Convention-conforming slug for a json-only product. The JSON may carry a dirty
    slug (spaces/capitals, e.g. 'Brass Jacks') or none at all; fall back to the product
    name and slugify. Returns '' when there's no usable identity (record is skipped)."""
    return slugify(record.get("slug") or record.get("product_name") or "")


def new_readme_path(record, cat_dirs):
    cat = (record.get("category") or "misc").strip()
    folder = cat_dirs.get(cat.lower(), cat.lower())
    slug = create_slug(record)
    return PRODUCTS / folder / slug / f"{slug}_README.md"


def apply_create(path, record):
    front = build_new_frontmatter(record)
    body = BODY_TEMPLATE.format(
        summary=(clean(record.get("cost")) or "<!-- TODO: one-line summary -->"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + dump_frontmatter(front) + "---\n" + body, encoding="utf-8")


# --- driver ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Reverse-sync: rewrite the product markdown to match products.json.")
    ap.add_argument("--apply", action="store_true",
                    help="actually write changes (default is a dry-run preview)")
    ap.add_argument("--json", default=None,
                    help="path to products.json (defaults to the published feed)")
    ap.add_argument("--skip-modify", action="store_true",
                    help="do not modify existing READMEs (e.g. archive/create only)")
    ap.add_argument("--skip-archive", action="store_true",
                    help="do not archive md-only products (sync content edits only)")
    ap.add_argument("--skip-create", action="store_true",
                    help="do not create READMEs for json-only products")
    args = ap.parse_args()

    json_path = resolve_json(args.json)
    feed = json.loads(json_path.read_text(encoding="utf-8"))
    records = feed["products"] if isinstance(feed, dict) else feed
    # Key by NORMALIZED slug so dirty JSON slugs ('Acrisure', 'Brass Jacks') match the
    # markdown slugs we already generated ('acrisure', 'brass_jacks') — otherwise every
    # re-run would archive-then-recreate the same products forever.
    actual = {}
    for r in records:
        s = create_slug(r)
        if not s:
            print(f"  ! JSON record with no usable slug/name — skipped: {r.get('product_name')!r}")
            continue
        if s in actual:
            print(f"  ! duplicate normalized slug {s!r} in JSON — keeping first occurrence")
            continue
        actual[s] = r

    md = differ.read_markdown_records()          # {folder_slug: (flat_record, path)}
    # Normalize the markdown side too: an existing folder may carry a non-conforming
    # slug (e.g. 'make.com_for_ngos' with a dot) that slugifies to the same key as the
    # JSON record ('make_com_for_ngos'). Match on the normalized key but keep the
    # ORIGINAL folder slug/path for any file operations (no folder renames).
    md_by_norm = {}                              # norm_slug -> (orig_slug, flat, path)
    for orig_slug, (flat, path) in md.items():
        n = slugify(orig_slug)
        if n in md_by_norm:
            print(f"  ! duplicate normalized markdown slug {n!r} — keeping first occurrence")
            continue
        md_by_norm[n] = (orig_slug, flat, path)

    md_slugs, json_slugs = set(md_by_norm), set(actual)

    common = sorted(md_slugs & json_slugs)
    only_md = sorted(md_slugs - json_slugs)      # -> archive
    only_json = sorted(json_slugs - md_slugs)    # -> create

    # (1) modifications
    modifications = {}
    for slug in common:
        orig_slug, expected_flat, path = md_by_norm[slug]
        changes = plan_modify(orig_slug, expected_flat, path, actual[slug])
        if changes:
            modifications[slug] = (path, changes)

    cat_dirs = category_dirs()
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"Reverse-sync ({mode}) — source of truth: {json_path.relative_to(CORE.parent)}")
    print(f"  markdown products: {len(md)}   json products: {len(actual)}")
    print(f"  to modify: {len(modifications)}   to archive (md-only): {len(only_md)}"
          f"   to create (json-only): {len(only_json)}")
    print()

    # --- MODIFY ---
    if modifications and args.skip_modify:
        print(f"== MODIFY skipped (--skip-modify): {len(modifications)} README(s) left as-is ==\n")
    elif modifications:
        print(f"== MODIFY {len(modifications)} README(s) to match products.json ==")
        for slug in sorted(modifications):
            path, changes = modifications[slug]
            print(f"  {slug}  ({path.relative_to(CORE.parent)})")
            for key, fpath, md_val, json_val in changes:
                print(f"      {'.'.join(fpath)}: {show(md_val)} -> {show(json_val)}")
            if args.apply:
                apply_modify(path, changes)
        print()

    # --- ARCHIVE ---
    if only_md and args.skip_archive:
        print(f"== ARCHIVE skipped (--skip-archive): {len(only_md)} md-only product(s) left as-is ==\n")
    elif only_md:
        print(f"== ARCHIVE {len(only_md)} md-only README(s) (status ARCHIVED) ==")
        archived = {"date": datetime.date.today().isoformat(),
                    "disposition": ARCHIVE_DISPOSITION}
        for slug in only_md:
            orig_slug, _flat, path = md_by_norm[slug]
            print(f"  {orig_slug}  ({path.relative_to(CORE.parent)})  ->  _archive/")
            if args.apply:
                archive.rewrite_frontmatter_and_body(path, ARCHIVE_REASON, archived)
                dest = archive.move_to_archive(path)
                print(f"      moved -> {dest.parent.relative_to(CORE)}")
        print()

    # --- CREATE ---
    if only_json and args.skip_create:
        print(f"== CREATE skipped (--skip-create): {len(only_json)} json-only product(s) not scaffolded ==\n")
    elif only_json:
        print(f"== CREATE {len(only_json)} README(s) for json-only products ==")
        for slug in only_json:
            record = actual[slug]
            new_slug = create_slug(record)
            if not new_slug:
                print(f"      ! {slug!r}: no usable slug or product name — skipped")
                continue
            path = new_readme_path(record, cat_dirs)
            label = f"(renamed {slug!r} -> {new_slug!r}) " if slugify(slug) != new_slug else ""
            print(f"  {new_slug}  {label}->  {path.relative_to(CORE.parent)}"
                  f"   [{clean(record.get('category'))} / {clean(record.get('sub_category'))}]")
            if args.apply:
                if path.exists():
                    print(f"      ! already exists — skipped")
                    continue
                apply_create(path, record)
        print()

    if args.apply:
        print("Done. Now rebuild the feed:")
        print("  python VKB-Core/scripts/build_products.py")
    else:
        print("Dry run only — no files changed. Re-run with --apply to write.")


if __name__ == "__main__":
    main()
