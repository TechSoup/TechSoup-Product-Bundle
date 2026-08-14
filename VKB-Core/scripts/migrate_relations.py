#!/usr/bin/env python3
"""Migrate prose link-title edges (OKF #101) into x-civic.relations (civic/0.5).

Why
---
build_products.py derives its relationship graph from two sources: markdown link
titles in the body, and `x-civic.relations` in the frontmatter. The prose form is
not durable — any editor that re-serialises markdown from a parsed AST discards
the link title attribute, so the typed edge disappears with no error and no
change to the row count. This was reproduced with Keystatic using both of its
content field types; the loss happens upstream of serialisation, so no editor
configuration avoids it.

Frontmatter, by contrast, round-trips intact. This script moves existing prose
edges into `x-civic.relations` and strips the now-redundant title from the prose
link, keeping the link itself for human readers. The frontmatter becomes the
single source of truth.

The build mirrors symmetric edges automatically (only `requires` is directional)
and de-duplicates, so authoring both ends — as this script does — is safe.

Notes
-----
Surgical text insertion is used rather than a YAML round-trip so that untouched
keys keep their exact original formatting and quoting.

Usage
-----
    python migrate_relations.py            # dry run, prints what would change
    python migrate_relations.py --apply    # write the changes
"""

import pathlib
import re
import sys

CORE = pathlib.Path(__file__).resolve().parent.parent      # VKB-Core
PRODUCTS = CORE / 'products'

# keep in step with build_products.py
EDGE_TYPES = {
    'complements', 'alternative', 'conflicts', 'requires', 'related', 'learn-with'
}
TITLED_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)\s+"([^"]*)"\)')

APPLY = '--apply' in sys.argv


def is_product_readme(p):
    """A product-root README is `<slug>/<slug>_README.md` — same rule as the build."""
    return p.name.endswith('_README.md') and p.parent.name + '_README.md' == p.name


def yaml_scalar(s):
    """Quote only when necessary, matching the corpus's existing style."""
    if s == '':
        return "''"
    if re.search(r'^[\s]|[:#]\s|^[-?*&!|>%@`\[\]{},]|[\s]$', s):
        return "'" + s.replace("'", "''") + "'"
    return s


def main():
    readmes = [p for p in PRODUCTS.rglob('*_README.md') if is_product_readme(p)]
    by_basename = {p.name: p.parent.name for p in readmes}

    changed = 0
    for p in sorted(readmes):
        raw = p.read_text(encoding='utf-8')
        nl = '\r\n' if '\r\n' in raw else '\n'
        text = raw.replace('\r\n', '\n')
        if not text.startswith('---\n'):
            continue
        end = text.index('\n---', 3)
        fm, body = text[4:end + 1], text[end + 4:]

        edges = []
        for href, title in TITLED_LINK_RE.findall(body):
            if ':' not in title:
                continue
            token, _, note = title.partition(':')
            token = token.strip()
            if token not in EDGE_TYPES:
                continue
            target = by_basename.get(href.rsplit('/', 1)[-1])
            if target is None:
                print(f'  ! unresolved edge in {p.name}: {token} -> {href}')
                continue
            edges.append((target, token, note.strip()))

        if not edges:
            continue

        if 'relations:' in fm:
            print(f'  = {p.relative_to(PRODUCTS).as_posix()}: already has relations, skipping')
            continue

        block = ['  relations:']
        for target, etype, note in edges:
            block.append(f'  - target: {yaml_scalar(target)}')
            block.append(f'    type: {yaml_scalar(etype)}')
            block.append(f'    note: {yaml_scalar(note)}')
        block_text = '\n'.join(block) + '\n'

        # insert inside x-civic, after sub_category; fall back to end of frontmatter
        m = re.search(r'^  sub_category:.*\n', fm, re.M)
        new_fm = fm[:m.end()] + block_text + fm[m.end():] if m else fm + block_text

        # drop the now-redundant title attribute from the prose link
        new_body = TITLED_LINK_RE.sub(
            lambda mo: mo.group(0).replace(f' "{mo.group(2)}"', ''), body
        )

        out = ('---\n' + new_fm + '---' + new_body).replace('\n', nl)
        rel = p.relative_to(PRODUCTS).as_posix()
        print(f'  {"WROTE" if APPLY else "would write"} {rel}')
        for target, etype, note in edges:
            print(f'      {etype} -> {target}  ({note})')
        if APPLY:
            p.write_text(out, encoding='utf-8', newline='')
        changed += 1

    print(f'\n{"applied to" if APPLY else "would change"} {changed} file(s)'
          f'{"" if APPLY else "  — rerun with --apply"}')


if __name__ == '__main__':
    main()
