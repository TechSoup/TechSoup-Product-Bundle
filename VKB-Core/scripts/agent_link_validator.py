"""
agent_link_validator.py — the LINKS & REGISTRY linter (one of three).

Checks that every product's vendor link is reachable, and writes a markdown
audit report (documentation/link_audit_report.md). Frontmatter *schema*
conformance is NOT checked here — that's validate.py's job (against
civic_schema.json); this linter does one thing: find link rot.

civic/0.5: the vendor URL lives at `x-civic.provenance.vendor_url`
(with a legacy top-level `vendor_url` fallback).

Usage:
    python3 VKB-Core/scripts/agent_link_validator.py              # full network audit
    python3 VKB-Core/scripts/agent_link_validator.py --no-network # extraction only (fast, offline)
    python3 VKB-Core/scripts/agent_link_validator.py --limit 10   # only the first 10 products
"""
import argparse
import os
import pathlib

import requests
import yaml
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)

PRODUCTS_DIR = os.path.join(VKB_CORE_DIR, 'products')
REPORT_FILE = os.path.join(VKB_CORE_DIR, 'documentation', 'link_audit_report.md')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


def vendor_url_of(data):
    """civic/0.5 vendor URL (x-civic.provenance.vendor_url), legacy fallback."""
    xc = data.get('x-civic') if isinstance(data, dict) else None
    if isinstance(xc, dict):
        url = (xc.get('provenance') or {}).get('vendor_url')
        if url:
            return url
    return data.get('vendor_url')  # pre-civic flat records


def title_of(data, fallback):
    if isinstance(data, dict):
        return data.get('title') or data.get('product_name') or fallback
    return fallback


def category_of(data):
    xc = data.get('x-civic') if isinstance(data, dict) else None
    if isinstance(xc, dict) and xc.get('category'):
        return xc['category']
    return data.get('category') if isinstance(data, dict) else None


def check_url(url):
    if not url:
        return "Missing URL"
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=10, allow_redirects=True)
        return "OK" if r.status_code < 400 else f"Error {r.status_code}"
    except Exception:
        return "Failed"


def is_product_root(readme_file):
    """Only the package-root README: products/<category>/<slug>/<slug>_README.md."""
    return len(readme_file.relative_to(PRODUCTS_DIR).parts) == 3


def main():
    ap = argparse.ArgumentParser(description="Audit vendor links across the VKB.")
    ap.add_argument("--no-network", action="store_true",
                    help="skip URL fetches; only verify URLs can be extracted")
    ap.add_argument("--limit", type=int, default=None,
                    help="check only the first N products")
    args = ap.parse_args()

    results, parse_issues = [], []
    total_checked = 0

    for readme_file in sorted(pathlib.Path(PRODUCTS_DIR).rglob('*_README.md')):
        if not is_product_root(readme_file):
            continue
        if args.limit is not None and total_checked >= args.limit:
            break

        content = readme_file.read_text(encoding="utf-8")
        if not content.startswith('---'):
            parse_issues.append((readme_file.name, 'Missing YAML frontmatter'))
            continue
        parts = content.split('---', 2)
        if len(parts) < 3:
            parse_issues.append((readme_file.name, 'Malformed YAML frontmatter'))
            continue
        try:
            data = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as e:
            parse_issues.append((readme_file.name, f'Invalid YAML: {e}'))
            continue

        total_checked += 1
        url = vendor_url_of(data)
        name = title_of(data, readme_file.name)

        if not url:
            results.append({'name': name, 'cat': category_of(data), 'url': '', 'status': 'Missing URL'})
            continue
        if args.no_network:
            continue
        status = check_url(url)
        if status != "OK":
            results.append({'name': name, 'cat': category_of(data), 'url': url, 'status': status})

    mode = "extraction-only (no network)" if args.no_network else "full network audit"
    date_str = datetime.now().strftime('%Y-%m-%d')
    report = [
        f"# Link Audit Report: {date_str}",
        "",
        f"_Mode: {mode}. Schema conformance is checked separately by `validate.py`._",
        "",
        "## Summary",
        f"- **Products checked:** {total_checked}",
        f"- **Link issues found:** {len(results)}",
        f"- **Frontmatter parse issues:** {len(parse_issues)}",
        "",
        "## Link Issues",
        "| Product | Category | URL | Status |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for r in results:
        report.append(f"| {r['name']} | {r['cat']} | {r['url']} | {r['status']} |")
    if parse_issues:
        report += ["", "## Frontmatter Parse Issues", "| File | Issue |", "| :--- | :--- |"]
        report += [f"| {n} | {m} |" for n, m in parse_issues]
    report.append("")

    pathlib.Path(REPORT_FILE).write_text("\n".join(report), encoding="utf-8")
    print(f"Audit complete ({mode}). {total_checked} products checked, "
          f"{len(results)} link issue(s), {len(parse_issues)} parse issue(s).")


if __name__ == "__main__":
    main()
