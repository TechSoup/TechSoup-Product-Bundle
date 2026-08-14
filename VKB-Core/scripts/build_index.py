#!/usr/bin/env python3
"""
build_index.py — generate the OKF index.md MOCs for the VKB bundle.

Sibling to build_products.py. Where build_products.py emits the flat
`products.json` feed, this emits the *progressive-disclosure* layer the OKF
spec calls index files (§6): a map of content for each directory.

It writes:
  - products/<category>/index.md   one per category — a listing of that
                                   category's live products + its orchestrator.
                                   NO frontmatter (OKF §6: index files carry none).
  - VKB-Core/index.md              the bundle-root MOC. Its frontmatter is
                                   PRESERVED verbatim (OKF §11 + civic/0.5
                                   identity: build_products.py reads
                                   x-civic.namespace/base_uri from it); only the
                                   markdown body is regenerated.

Indexes are a generated view, like products.json — run after editing products,
commit the result by hand. Source of truth is the product frontmatter; this
script reuses build_products.py's paths and predicates so the two never drift.

Usage:  python3 VKB-Core/scripts/build_index.py
"""
import importlib.util
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

SCRIPTS = pathlib.Path(__file__).resolve().parent

# Reuse build_products.py for paths/constants/predicates (single source of
# truth). Importing only runs module-level definitions; main() is guarded.
_spec = importlib.util.spec_from_file_location("vkb_build", SCRIPTS / "build_products.py")
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

CORE = bp.CORE
PRODUCTS = bp.PRODUCTS
INDEX_PATH = bp.INDEX_PATH
LIVE_STATUSES = bp.LIVE_STATUSES


def read_fm(path):
    """Return (frontmatter dict, body str) for a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        return (yaml.safe_load(parts[1]) or {}), parts[2]
    except yaml.YAMLError:
        return {}, text


def first_heading(path):
    """The file's first `# ` heading, else a title-cased filename."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").title()


def is_live(xc):
    status = xc.get("status") if isinstance(xc, dict) else None
    return status is None or status in LIVE_STATUSES


def collect_category(cat_dir):
    """Gather a category's live products and its orchestrator skill.

    Returns {name, products: [{title, sub, summary, link}], orchestrator}.
    """
    products = []
    display = None
    for sub in sorted(cat_dir.iterdir()):
        if not sub.is_dir():
            continue
        readme = sub / f"{sub.name}_README.md"
        if not readme.exists():
            continue
        fm, _ = read_fm(readme)
        xc = fm.get("x-civic") or {}
        if not is_live(xc):
            continue
        display = display or xc.get("category")
        off = xc.get("offer") or {}
        products.append({
            "title": fm.get("title") or sub.name,
            "sub": xc.get("sub_category"),
            "summary": off.get("summary"),
            "link": f"{sub.name}/{readme.name}",
        })
    products.sort(key=lambda p: p["title"].lower())

    orchestrator = None
    orch_files = sorted(cat_dir.glob("*_orchestrator_skill.md"))
    if orch_files:
        of = orch_files[0]
        orchestrator = {"title": first_heading(of), "link": of.name}

    return {
        "name": display or cat_dir.name.replace("_", " ").title(),
        "products": products,
        "orchestrator": orchestrator,
    }


def render_category_index(cat):
    """Render a category index.md body (no frontmatter, per OKF §6)."""
    n = len(cat["products"])
    plural = "product" if n == 1 else "products"
    lines = [
        f"# {cat['name']}",
        "",
        f"{n} live {plural} in this category. Part of the [VKB catalog](../../index.md).",
        "",
        "## Products",
        "",
    ]
    for p in cat["products"]:
        desc = " · ".join(x for x in (p["sub"], p["summary"]) if x)
        suffix = f" — {desc}" if desc else ""
        lines.append(f"* [{p['title']}]({p['link']}){suffix}")
    if cat["orchestrator"]:
        o = cat["orchestrator"]
        lines += ["", "## Maintenance", "",
                  f"* [{o['title']}]({o['link']}) — category maintenance agent"]
    return "\n".join(lines) + "\n"


def render_root_body(cats):
    """Render the bundle-root MOC body (frontmatter is preserved separately)."""
    lines = [
        "# VKB-Core",
        "",
        "The source-of-truth knowledge base for TechSoup nonprofit product "
        "intelligence: each product is a markdown file with YAML frontmatter, "
        "compiled by `scripts/build_products.py` into the `products.json` headless "
        "API that the Offer Center and other tools consume. Build and conformance "
        "details live in [documentation/](documentation/).",
        "",
        "## Categories",
        "",
    ]
    for c in cats:
        n = len(c["products"])
        plural = "product" if n == 1 else "products"
        lines.append(f"* [{c['name']}]({c['link']}) — {n} {plural}")
    lines += [
        "",
        "## Documentation & registries",
        "",
        "* [documentation/](documentation/) — architecture, schema, conformance, "
        "maintainer workflow",
        "* [registry/](registry/) — audiences, PCS vocabulary, peers, capabilities",
    ]
    return "\n".join(lines) + "\n"


def write_root_index(body):
    """Replace the root index.md body, preserving its frontmatter verbatim."""
    text = INDEX_PATH.read_text(encoding="utf-8")
    if not text.startswith("---"):
        sys.exit(f"root index.md has no frontmatter to preserve: {INDEX_PATH}")
    parts = text.split("---", 2)
    if len(parts) < 3:
        sys.exit(f"root index.md frontmatter is malformed: {INDEX_PATH}")
    new = "---" + parts[1] + "---\n\n" + body
    INDEX_PATH.write_text(new, encoding="utf-8")


def main():
    cat_dirs = sorted(d for d in PRODUCTS.iterdir() if d.is_dir())
    cats = []
    for d in cat_dirs:
        cat = collect_category(d)
        (d / "index.md").write_text(render_category_index(cat), encoding="utf-8")
        cat["link"] = f"products/{d.name}/index.md"
        cats.append(cat)

    write_root_index(render_root_body(cats))

    total = sum(len(c["products"]) for c in cats)
    print(f"Wrote {len(cats)} category index.md files + the root MOC "
          f"({total} live products listed).")


if __name__ == "__main__":
    main()
