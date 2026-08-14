#!/usr/bin/env python3
"""lint_structure.py — lint VKB product packages against the STRUCTURE standard.

This is its own linter, separate from the other two single-purpose tools:
  - validate.py            -> frontmatter/schema conformance (civic_schema.json)
  - agent_link_validator.py-> links & registry integrity
  - lint_structure.py      -> the on-disk PACKAGE SHAPE (this file)

The required shape lives in `schemas/structure_spec.json` (data, not code) so it
is portable across federated VKBs and can grow by `type` without touching this
linter. Findings are IMPACT-SCOPED: each names the consumer it affects and
whether its absence is *blocking* for that consumer. A missing `case_studies/`
folder is reported but does not break the Offer Center build — so by default the
linter exits non-zero ONLY on blocking findings. `--strict` treats every
deviation as blocking.

REPORT (default): one line per package plus each finding's stable ID
(`<slug>:<element>`), grouped impact summary, and an `N/M` tally.

FIX (opt-in, never destructive — only ever CREATES missing scaffolding):
  --fix <id> [<id> …]   fix exactly these findings
  --fix-from <file>     re-feed an edited copy of the report; every finding ID
                        still present in the file is fixed (delete the lines you
                        don't want fixed) — the "go through the report" flow
  --fix-all             fix every fixable finding

SCOPE: the active tree by default; `--all` includes `_archive/` (relaxed: only
blocking elements are required there). `--products <dir>` / `--spec <file>` let
you point the linter at another VKB or a test fixture.

Usage:
  ./venv/bin/python VKB-Core/scripts/lint_structure.py
  ./venv/bin/python VKB-Core/scripts/lint_structure.py --strict
  ./venv/bin/python VKB-Core/scripts/lint_structure.py --fix-all
  ./venv/bin/python VKB-Core/scripts/lint_structure.py --fix tableau:use_cases
"""
import argparse
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None  # only needed to read a product title when scaffolding a skill

CORE = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_PRODUCTS = CORE / "products"
DEFAULT_SPEC = CORE / "schemas" / "structure_spec.json"
TEMPLATE_DIR = CORE / "documentation" / "templates"

ID_RE = re.compile(r"[A-Za-z0-9._]+:[A-Za-z0-9_]+")


# ---------------------------------------------------------------- model

class Finding:
    def __init__(self, slug, element, impact, blocking, fixable, message, fix=None):
        self.id = f"{slug}:{element}"
        self.slug = slug
        self.element = element
        self.impact = impact
        self.blocking = blocking
        self.fixable = fixable
        self.message = message
        self.fix = fix          # callable() -> str (description) or None

    def line(self):
        tier = "BLOCKING" if self.blocking else "advisory"
        fixtag = " [fixable]" if self.fixable else ""
        return f"    - {self.id}  ({tier}; impact={self.impact}){fixtag}  {self.message}"


# ---------------------------------------------------------------- helpers

def load_json(path):
    import json
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def is_product_dir(d):
    """A product package is a dir containing `<dirname>_README.md`."""
    return (d / f"{d.name}_README.md").is_file()


def product_title(d):
    """Best-effort product title from README frontmatter (for skill scaffolding)."""
    readme = d / f"{d.name}_README.md"
    try:
        text = readme.read_text(encoding="utf-8")
        if yaml and text.startswith("---"):
            fm = yaml.safe_load(text.split("---", 2)[1]) or {}
            if fm.get("title"):
                return str(fm["title"])
    except Exception:
        pass
    return d.name.replace("_", " ").title()


def find_products(products_dir, include_archive):
    """All product package dirs under products_dir."""
    out = []
    for readme in products_dir.rglob("*_README.md"):
        d = readme.parent
        if d.name + "_README.md" != readme.name:
            continue
        if not include_archive and "_archive" in d.parts:
            continue
        out.append(d)
    return sorted(set(out))


# ---------------------------------------------------------------- fix actions

def make_dir_fix(folder, gitkeep):
    def _fix():
        folder.mkdir(parents=True, exist_ok=True)
        created = "folder"
        if gitkeep:
            gk = folder / ".gitkeep"
            if not gk.exists():
                gk.write_text("")
            created = "folder + .gitkeep"
        return f"created {created}: {folder}"
    return _fix


def make_skill_fix(d, dest, title):
    def _fix():
        tpl = (TEMPLATE_DIR / "agent_skill_template.md").read_text(encoding="utf-8")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(tpl.replace("[Product Name]", title), encoding="utf-8")
        return f"scaffolded skill from template: {dest}"
    return _fix


# ---------------------------------------------------------------- checks

def check_product(d, products_dir, spec, relaxed):
    """Return (typ, [Finding, ...]) for one product package."""
    slug = d.name
    findings = []

    # naming
    pat = spec.get("naming", {}).get("slug_pattern")
    if pat and not re.match(pat, slug):
        findings.append(Finding(slug, "slug", "standard-drift", False, False,
                                 f"slug {slug!r} violates naming pattern {pat}"))

    # type -> rules (default offer; unknown types fall back to offer for now)
    typ = "offer"
    readme = d / f"{slug}_README.md"
    if yaml:
        try:
            text = readme.read_text(encoding="utf-8")
            if text.startswith("---"):
                fm = yaml.safe_load(text.split("---", 2)[1]) or {}
                typ = fm.get("type", "offer")
        except Exception:
            pass
    rules = spec["types"].get(typ) or spec["types"]["offer"]

    for el in rules.get("elements", []):
        # in a relaxed (archive) pass, only blocking elements are required
        if relaxed and not el.get("blocking"):
            continue
        rel = el["path"].replace("{slug}", slug)
        target = d / rel
        present = target.is_file() if el["kind"] == "file" else target.is_dir()
        gitkeep_ok = True
        if present and el["kind"] == "dir" and el.get("gitkeep"):
            gitkeep_ok = (target / ".gitkeep").is_file()

        if not present:
            fix = None
            if el.get("fixable"):
                fix = (make_dir_fix(target, el.get("gitkeep")) if el["kind"] == "dir"
                       else make_skill_fix(d, target, product_title(d)))
            findings.append(Finding(slug, el["id"], el["impact"], el.get("blocking", False),
                                    bool(el.get("fixable")), f"missing {rel} — {el['message']}", fix))
        elif not gitkeep_ok:
            findings.append(Finding(slug, el["id"], el["impact"], el.get("blocking", False),
                                    True, f"{rel}/ exists but has no .gitkeep — empty dir will vanish on clone",
                                    make_dir_fix(target, True)))

    for d_el in rules.get("deny", []):
        if (d / d_el["path"]).exists():
            findings.append(Finding(slug, d_el["id"], d_el["impact"], d_el.get("blocking", False),
                                    False, f"present but forbidden: {d_el['path']} — {d_el['message']}"))

    return typ, findings


# ---------------------------------------------------------------- report / run

def find_orphans(products_dir, include_archive, product_dirs):
    """Dirs that look like a product (have agent/ or content/) but lack a README.

    This is the only way a `readme` (blocking) finding can fire — a dir without
    its README is invisible to the build, so it must be surfaced explicitly.
    """
    known = set(product_dirs)
    out = []
    for sub in ("agent", "content"):
        for marker in products_dir.rglob(sub):
            if not marker.is_dir():
                continue
            d = marker.parent
            if d in known or d in out:
                continue
            if not include_archive and "_archive" in d.parts:
                continue
            if not is_product_dir(d):
                out.append(d)
    return sorted(set(out))


def gather(products_dir, spec, include_archive):
    results = []
    product_dirs = find_products(products_dir, include_archive)
    for d in product_dirs:
        relaxed = "_archive" in d.parts
        typ, findings = check_product(d, products_dir, spec, relaxed)
        results.append((d, typ, findings))
    for d in find_orphans(products_dir, include_archive, product_dirs):
        f = Finding(d.name, "readme", "offer-center", True, False,
                    f"missing {d.name}_README.md — folder has agent/ or content/ but no product README "
                    "(invisible to the build; rename the folder/README to match, or add the README)")
        results.append((d, "offer", [f]))
    return results


def run_report(results, products_dir, strict):
    all_findings = []
    failed = 0
    for d, typ, findings in results:
        rel = d.relative_to(products_dir)
        blocking = [f for f in findings if f.blocking or strict]
        if not findings:
            print(f"[ok]   {rel}")
            continue
        tag = "FAIL" if blocking else "warn"
        if blocking:
            failed += 1
        print(f"[{tag}] {rel}")
        for f in findings:
            print(f.line())
        all_findings.extend(findings)

    total = len(results)
    print(f"\n{total - failed}/{total} packages pass (blocking{' + strict' if strict else ''}).")
    if all_findings:
        from collections import Counter
        by_impact = Counter(f"{f.impact}{'*' if f.blocking else ''}" for f in all_findings)
        print("findings by impact (* = blocking):")
        for k, v in sorted(by_impact.items()):
            print(f"  {v:3d}  {k}")
        fixable = [f for f in all_findings if f.fixable]
        if fixable:
            print(f"\n{len(fixable)} fixable. Apply with: --fix-all, "
                  f"--fix <id>…, or --fix-from <edited-report>. e.g. --fix {fixable[0].id}")
    return failed


def run_fix(results, selector):
    """selector: 'all', set of ids, or ('from', path)."""
    ids = None
    if selector == "all":
        ids = None
    elif isinstance(selector, tuple) and selector[0] == "from":
        text = pathlib.Path(selector[1]).read_text(encoding="utf-8")
        ids = set(ID_RE.findall(text))
    else:
        ids = set(selector)

    fixed, skipped_unfixable = [], []
    for _, _, findings in results:
        for f in findings:
            if ids is not None and f.id not in ids:
                continue
            if not f.fixable or not f.fix:
                if ids is not None:
                    skipped_unfixable.append(f.id)
                continue
            fixed.append((f.id, f.fix()))

    for fid, desc in fixed:
        print(f"[fixed] {fid}: {desc}")
    if skipped_unfixable:
        print(f"\n! not fixable (reported only, never auto-changed): {sorted(set(skipped_unfixable))}")
    print(f"\n{len(fixed)} finding(s) fixed.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Lint VKB product packages against the structure standard.")
    ap.add_argument("--products", default=str(DEFAULT_PRODUCTS), help="products dir to lint (default: VKB-Core/products)")
    ap.add_argument("--spec", default=str(DEFAULT_SPEC), help="structure spec JSON (default: schemas/structure_spec.json)")
    ap.add_argument("--all", action="store_true", help="include _archive/ (relaxed: only blocking elements required)")
    ap.add_argument("--strict", action="store_true", help="treat every deviation as blocking (exit non-zero on any)")
    ap.add_argument("--fix", nargs="+", metavar="ID", help="fix exactly these finding IDs")
    ap.add_argument("--fix-from", metavar="FILE", help="fix every finding ID found in this file (an edited report)")
    ap.add_argument("--fix-all", action="store_true", help="fix every fixable finding")
    args = ap.parse_args()

    products_dir = pathlib.Path(args.products).resolve()
    if not products_dir.is_dir():
        sys.exit(f"products dir not found: {products_dir}")
    spec = load_json(args.spec)

    results = gather(products_dir, spec, include_archive=args.all)

    if args.fix or args.fix_from or args.fix_all:
        if args.fix_all:
            return run_fix(results, "all")
        if args.fix_from:
            return run_fix(results, ("from", args.fix_from))
        return run_fix(results, args.fix)

    failed = run_report(results, products_dir, strict=args.strict)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
