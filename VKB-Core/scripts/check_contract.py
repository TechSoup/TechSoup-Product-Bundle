#!/usr/bin/env python3
"""Contract guard for the published products.json.

The Offer Center (and any other tool) consumes `Offer-Center/products.json` as a
frozen "headless API". This guard pins that contract so the federation /
standardization work (civic/0.5 and beyond) can proceed underneath it without
ever silently breaking a consumer.

What it does
------------
1. Rebuilds the catalog into a TEMP file (it imports build_products.py and redirects its
   output paths), so the live, possibly-deployed products.json is never touched.
2. Compares that fresh build against the frozen golden snapshot
   (tests/golden_products.json).

Contract rules
--------------
A change is a VIOLATION (exit 1) if it would break a consumer reading the
existing shape:
  * a product present in golden is missing from the build      (dropped offer)
  * a key present in a golden product is gone from the build    (removed field)
  * a key's value changed                                       (changed field)
  * a stable meta key changed or disappeared

A change is ALLOWED (reported, exit 0) when it is purely additive or expected:
  * new products                                               (catalog grew)
  * new keys on a product (e.g. `id`, an external `relations` edge)
  * new meta keys (e.g. `namespace`)
  * a change to a meta key in MUTABLE_META (currently just `profile`, which the
    civic/0.5 bump is expected to change)

Usage
-----
  python3 VKB-Core/scripts/check_contract.py            # verify (CI gate)
  python3 VKB-Core/scripts/check_contract.py --update   # re-freeze golden
                                                         # (deliberately bless an
                                                         #  additive/version change)
"""

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
CORE = SCRIPTS.parent
GOLDEN = CORE / "tests" / "golden_products.json"

# meta keys allowed to change without re-blessing the golden.
MUTABLE_META = {"profile"}


def build_to_temp():
    """Run build_products.py with its outputs redirected to a temp dir and return the
    parsed feed, without touching the live Offer-Center/products.json."""
    spec = importlib.util.spec_from_file_location("vkb_build", SCRIPTS / "build_products.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)

    # build.main() prints JSON_OUT.relative_to(PROJECT), so the temp output must
    # live inside the repo. Use a temp dir under the project root, cleaned up after.
    with tempfile.TemporaryDirectory(dir=build.PROJECT, prefix=".contract_tmp_") as td:
        build.JSON_OUT = Path(td) / "products.json"
        build.DB_PATH = Path(td) / "vkb.db"
        build.main()
        return json.loads(build.JSON_OUT.read_text(encoding="utf-8"))


def compare(golden, current):
    """Return (violations, additions) comparing a golden feed to a current one."""
    violations, additions = [], []

    g_prods = {p["slug"]: p for p in golden["products"]}
    c_prods = {p["slug"]: p for p in current["products"]}

    for slug, gp in g_prods.items():
        cp = c_prods.get(slug)
        if cp is None:
            violations.append(f"DROPPED PRODUCT: '{slug}' is in golden but not in the build")
            continue
        for k, gv in gp.items():
            if k not in cp:
                violations.append(f"REMOVED KEY:  {slug}.{k}")
            elif cp[k] != gv:
                violations.append(
                    f"CHANGED VALUE: {slug}.{k}\n"
                    f"      golden : {json.dumps(gv)}\n"
                    f"      build  : {json.dumps(cp[k])}"
                )
        for k in cp.keys() - gp.keys():
            additions.append(f"new key:     {slug}.{k}")

    for slug in c_prods.keys() - g_prods.keys():
        additions.append(f"new product: {slug}")

    g_meta, c_meta = golden.get("meta", {}), current.get("meta", {})
    for k, gv in g_meta.items():
        if k in MUTABLE_META:
            if c_meta.get(k) != gv:
                additions.append(f"meta.{k}: {json.dumps(gv)} -> {json.dumps(c_meta.get(k))} (mutable)")
            continue
        if k not in c_meta:
            violations.append(f"REMOVED META: meta.{k}")
        elif c_meta[k] != gv:
            violations.append(f"CHANGED META: meta.{k}")
    for k in c_meta.keys() - g_meta.keys():
        additions.append(f"new meta key: {k}")

    return violations, additions


def main():
    ap = argparse.ArgumentParser(description="Guard the products.json contract.")
    ap.add_argument("--update", action="store_true",
                    help="re-freeze the golden snapshot from a fresh build")
    args = ap.parse_args()

    current = build_to_temp()

    if args.update:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(json.dumps(current, indent=4) + "\n", encoding="utf-8")
        print(f"Froze golden snapshot: {GOLDEN.relative_to(CORE)} "
              f"({len(current['products'])} products).")
        return

    if not GOLDEN.exists():
        sys.exit(f"No golden snapshot at {GOLDEN}. Run with --update to create one.")

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    violations, additions = compare(golden, current)

    for a in additions:
        print(f"  + {a}")
    if additions:
        print(f"({len(additions)} additive/allowed change(s) — contract preserved.)\n")

    if violations:
        print("CONTRACT VIOLATIONS — these would break a consumer:\n")
        for v in violations:
            print(f"  ✗ {v}")
        print(f"\n{len(violations)} violation(s). If intentional, re-run with --update to bless.")
        sys.exit(1)

    print(f"OK — products.json contract preserved "
          f"({len(golden['products'])} products, all keys/values stable).")


if __name__ == "__main__":
    main()
