#!/usr/bin/env python3
"""
validate.py — check VKB product files against the x-civic 0.5 schema.

Validates every product-root README against schemas/civic_schema.json:
frontmatter parses, core OKF `type` is present, and any x-civic block conforms
(profile civic/0.5, status enum, offer block, eligibility/provenance shapes).
Also checks that x-civic.capability, when present, is a registered key in
registry/capabilities.json (the controlled vocabulary).

Reserved filenames (index.md, log.md; OKF §3.1) are NOT concept records and are
exempt from the schema. Index files are checked separately for the §6/§11 rule
(no frontmatter except the bundle-root index), and the root index is checked for
its civic/0.5 federation identity (x-civic.namespace/base_uri/profile).

This is the FRONTMATTER/schema linter. Two sibling linters cover other concerns:
structure (lint_structure.py) and links (agent_link_validator.py).

Usage:  python3 VKB-Core/scripts/validate.py
"""
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")
try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("jsonschema required:  pip install -r requirements.txt")

CORE = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = CORE / "products"
SCHEMA_PATH = CORE / "schemas" / "civic_schema.json"
CAPABILITIES_PATH = CORE / "registry" / "capabilities.json"
PROFILE = "civic/0.5"


def load_capabilities():
    """Set of valid capability keys from the controlled vocabulary (empty if absent)."""
    try:
        reg = json.loads(CAPABILITIES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set()
    return set(reg.get("capabilities", {}).keys())


def capability_errors(data, capabilities):
    """Return errors for an x-civic.capability that isn't in the vocabulary."""
    xc = data.get("x-civic") if isinstance(data, dict) else None
    if not isinstance(xc, dict):
        return []
    cap = xc.get("capability")
    if cap and cap not in capabilities:
        return [f"x-civic/capability: {cap!r} is not in registry/capabilities.json"]
    return []


def is_product_readme(p):
    """A product-root README is `<slug>/<slug>_README.md` (active or archived)."""
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def records():
    """Concept records: product-root READMEs. Reserved files (index.md) excluded."""
    return [p for p in sorted(PRODUCTS.rglob("*_README.md")) if is_product_readme(p)]


def index_files():
    """Every index.md in the bundle (root + category dirs)."""
    paths = []
    root = CORE / "index.md"
    if root.exists():
        paths.append(root)
    paths += sorted(PRODUCTS.glob("*/index.md"))
    return paths


def check_root_identity(path):
    """The bundle-root index must declare its civic/0.5 federation identity —
    build_products.py reads x-civic.namespace/base_uri/profile from here."""
    data, err = frontmatter(path)
    if err:
        return [f"root index frontmatter: {err}"]
    xc = data.get("x-civic")
    if not isinstance(xc, dict):
        return ["root index is missing the x-civic identity block"]
    errs = []
    if not xc.get("namespace"):
        errs.append("root index missing x-civic.namespace (civic/0.5 identity)")
    if not xc.get("base_uri"):
        errs.append("root index missing x-civic.base_uri (civic/0.5 identity)")
    if xc.get("profile") != PROFILE:
        errs.append(f"root index x-civic.profile must be {PROFILE!r} (found {xc.get('profile')!r})")
    return errs


def check_index_files(paths):
    """OKF §6/§11: index files carry no frontmatter, except the bundle-root index
    (which may, to declare okf_version + the civic identity). Returns
    [(relative_path, [errors]), ...]."""
    root = (CORE / "index.md").resolve()
    results = []
    for p in paths:
        is_root = p.resolve() == root
        text = p.read_text(encoding="utf-8")
        has_fm = text.startswith("---") and len(text.split("---", 2)) >= 3
        errs = []
        if has_fm and not is_root:
            errs.append("index.md must not contain frontmatter (OKF §6/§11); "
                        "only the bundle-root index may")
        if is_root:
            errs += check_root_identity(p)
        results.append((p.relative_to(CORE), errs))
    return results


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, "no frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "malformed frontmatter"
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return None, f"unparseable frontmatter: {e}"
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, None


def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    capabilities = load_capabilities()

    results = []
    for p in records():
        data, err = frontmatter(p)
        errs = [err] if err else [
            f"{'/'.join(str(x) for x in e.path) or '(root)'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        ] + (capability_errors(data, capabilities) if not err else [])
        results.append((p.relative_to(CORE), errs))

    results += check_index_files(index_files())

    failed = sum(1 for _, errs in results if errs)
    for rel, errs in results:
        if errs:
            print(f"[FAIL] {rel}")
            for e in errs:
                print(f"       - {e}")
        else:
            print(f"[ok]   {rel}")
    print()
    print(f"{len(results) - failed}/{len(results)} records passed.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
