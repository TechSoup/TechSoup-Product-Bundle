# VKB v2 — Hand-off & Direction

*Branch: `v2-knowledge-engine`. This document is to support handoff: what changed, how it works, and what can be built next. Kept deliberately simple.*

## The progression (v1 → v2)

- **v1:** products were markdown files with a custom YAML schema, compiled straight to `products.json`. It worked, but it was a bespoke format, single-author, and the engine was just a flat file.
- **v2 (this branch):** the same files, now **conformant to the Open Knowledge Format (OKF)** — an emerging open standard — with a real **SQLite engine** underneath. Same human-readable simplicity; now on a standard, with a queryable engine for tools like the recommender. `products.json` stays the published contract, so nothing downstream breaks.

## What changed on this branch (done)

- **OKF conformance:** all 96 products declare `type: offer` (OKF's one required field). Minimal one-line additions — see `scripts/migrate_to_okf.py` (re-runnable, idempotent).
- **Bundle root:** added `VKB-Core/index.md` declaring `okf_version: "0.1"`.
- **Build engine:** new `scripts/build_products.py` — **OKF files → SQLite (`vkb.db`) → `products.json`**.
- **De-duplicated** the catalog: removed the stale `Offer-Center/data/products.json`; the app reads the root `Offer-Center/products.json` (confirmed in `app.js`).
- `vkb.db` is **gitignored** — it's disposable and rebuilt from the files every run.

## Architecture (intentionally legible)

```
  products/**/[slug]_README.md      ← source of truth (read in any editor; no DB needed)
            │   python3 scripts/build_products.py
            ▼
        SQLite  (vkb.db)            ← build/query engine; disposable, rebuilt each run
            │   emits
            ▼
   Offer-Center/products.json       ← the headless API (unchanged contract)
            │
            ▼
   Offer Center  +  other tools (recommender, etc.)
```

- The **files are the source of truth.** No database is needed to *read* the knowledge.
- **SQLite is the engine**, not the truth — always rebuildable from the files.
- **`products.json` is the contract** the Offer Center and external tools consume. It lives where it always has, so the Azure/VPN hosting (owned by engineering) needs no change.

## How to run it

```
pip install pyyaml            # once
python3 VKB-Core/scripts/build_products.py
```
That rebuilds `vkb.db` and regenerates `Offer-Center/products.json`.

**To add or edit a product:** edit/create `products/[category]/[slug]/[slug]_README.md`. The frontmatter must include `type: offer`. Then run `build_products.py`. That's the whole loop.

## For other tool builders — the contract you build against

You can consume the catalog two ways:

1. **`products.json`** — the simple feed (also served behind the Azure endpoint, VPN-gated). A JSON array; each item is a product's frontmatter:
   `type, product_name, category, sub_category, cost, min_budget, max_budget, eligible_countries[], eligible_org_types[], eligibility_ntee_codes[], badges[], last_audited, vendor_url, slug`.
2. **`vkb.db`** (SQLite) — for filtering/ranking. Table `products`; list fields are stored as JSON strings, and a `data` column holds the full record. Example:
   `SELECT product_name, cost FROM products WHERE category='Communications';`

**Crucial design point:** the *structured facts* (price, eligibility) are in the JSON/DB. The *verbose expert knowledge* — the "Level 1/2/3" guidance, gotchas, security posture — lives in each product's **markdown body**, not in `products.json`. The recommender should load those bodies (and the relevant skills files) as context when it reasons. That split is the whole point of a "Verbose" KB: structured data for filtering, prose for judgment.

## Intentionally NOT done yet (the next layers)

Lifecycle states (`PROPOSED/INITIALIZED/ACTIVE/ARCHIVED/REJECTED`), namespaced extensions, link validation, and the briefing/signals loop are the **v2.x layers** described in the product spec. Left for the team to adopt deliberately.

## References

- **Product spec** (strategic, the "why"): shared separately with this hand-off.
- **OKF spec:** https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- **This work:** branch `v2-knowledge-engine` — `scripts/migrate_to_okf.py`, `scripts/build_products.py`, `index.md`.
