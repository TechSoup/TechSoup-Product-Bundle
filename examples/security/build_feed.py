#!/usr/bin/env python3
"""
Example: compile a JSON feed from the TechSoup Product Bundle, filtered to
the Security category, for a small web component to render.

This is one way to build on the bundle -- any language that can parse YAML
frontmatter could produce the same feed. Swap the filter below and you have a
different widget over the same source data (see ../open-source/build_feed.py).
"""
import glob
import json
import os

import yaml

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "products"))
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "products.json")


def load_frontmatter(filepath):
    with open(filepath) as f:
        content = f.read()
    if not content.startswith("---"):
        return None
    frontmatter = content.split("---", 2)[1]
    return yaml.safe_load(frontmatter)


def build_feed():
    products = []
    for filepath in glob.glob(os.path.join(BUNDLE_DIR, "**", "*_README.md"), recursive=True):
        metadata = load_frontmatter(filepath)
        if not metadata:
            continue

        civic = metadata.get("x-civic", {})
        if civic.get("status") != "ACTIVE":
            continue

        if civic.get("category") != "Security":
            continue

        products.append({
            "title": metadata.get("title", "Unknown Product"),
            "category": civic.get("category", "Uncategorized"),
            "summary": civic.get("offer", {}).get("summary", "View details"),
            "url": civic.get("provenance", {}).get("vendor_url", "#"),
        })

    products.sort(key=lambda p: p["title"])

    with open(OUTPUT_FILE, "w") as f:
        json.dump(products, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(products)} products to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_feed()
