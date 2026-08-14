# VKB Schema — OKF core + `x-civic` 0.5

This schema defines the data contract for VKB product records. Source files use the **nested `x-civic` profile (version `civic/0.5`)**; the build pipeline flattens them into `products.json` for downstream tools.

> **New in civic/0.5: federation.** A bundle now declares a `namespace` (and `base_uri`) in `index.md`, every record gets a global `id` of `namespace:slug`, and `relations` edges can point into *other* VKBs by CURIE (`namespace:slug`). `capability` is now a controlled vocabulary and the cross-VKB join key. See **Federation (civic/0.5)** below.

> **Two layers, on purpose.**
> - **Source of truth** = the markdown frontmatter, in the nested `x-civic` shape below. This is the OKF/`x-civic` artifact.
> - **`products.json`** = a generated *flat* view that the Offer Center and Cost Optimizer consume. Its keys are unchanged from before the migration, so tools that read it need no changes. The flat keys are derived by `build_products.py` (see "Flat projection" below).

## Source frontmatter (`x-civic` 0.4)

Top-level keys are core OKF; everything civic-specific lives under `x-civic`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `type` | String | **Required (OKF).** `offer` for products. The one field OKF requires. |
| `title` | String | Display name of the product (was `product_name`). Identity is still the folder/slug path. |
| `x-civic.profile` | String | **Required.** Profile version — `civic/0.5`. |
| `x-civic.status` | Enum | Record lifecycle: `PROPOSED` · `INITIALIZED` · `ACTIVE` · `ARCHIVED` · `REJECTED`. Only `ACTIVE`/`INITIALIZED` are live; anything else is **excluded from `products.json`** by `build_products.py`. `reason` is required for `ARCHIVED`/`REJECTED`. |
| `x-civic.category` | String | High-level grouping (AI, Communications, Infrastructure…). |
| `x-civic.sub_category` | String | Specific tool type for deep filtering (Marketing, Video…). |
| `x-civic.capability` | String | *Optional.* The shared function a product provides; two products with the same capability are substitutes. When set, it **must** be a key in `registry/capabilities.json` (validated). This is the cross-VKB join axis — see Federation. |
| `x-civic.offer.type` | String | `Discount` · `Donation` · `Free / Open Source` · `Discovery`. |
| `x-civic.offer.summary` | String | Human-readable cost/discount (was `cost`), e.g. "50% Discount". |
| `x-civic.offer.standard_tier` | String/Null | The specific tier being discounted. |
| `x-civic.offer.savings_estimate` | String/Null | ROI / annual-savings statement. |
| `x-civic.offer.badges` | Array | UI tags (e.g. `["Discount"]`). |
| `x-civic.eligibility.eligible_audiences` | Array | **OR-list of audience keys** (see `registry/audiences.json`); replaced `org_types` in civic/0.4. Each key resolves to an (org_type **AND** subject) PCS tuple; the offer is eligible to a user who matches **any** one audience. e.g. `[nonprofit, public_library]` = "open to nonprofits OR public libraries". |
| `x-civic.eligibility.regions` | Array | ISO country codes or `["ALL"]` (was `eligible_countries`). |
| `x-civic.eligibility.pcs_subject` | Array | **Independent, offer-level mission restriction** (Candid PCS Subject codes, or `["ALL"]`). ANDed on top of audience eligibility; was `ntee_codes` (NTEE) before the civic/0.3 crosswalk. Note: an audience's *own* subject (e.g. libraries for `public_library`) lives in the audience definition, not here. |
| `x-civic.eligibility.rules` | String/Null | Specific constraints/limits. |
| `x-civic.eligibility.min_budget` | Number | Minimum org budget to qualify (default 0). |
| `x-civic.eligibility.max_budget` | Number/Null | Maximum org budget to qualify (omit if unbounded). |
| `x-civic.provenance.last_audited` | String/Null | Date of last manual verification (YYYY-MM-DD). `null` = not yet audited. |
| `x-civic.provenance.vendor_url` | String | **Required.** Link to the official offer/landing page. |
| `x-civic.provenance.source` | String | Where the record came from (e.g. `TechSoup VKB`). |
| `x-civic.relations` | Array | *Optional.* Typed edges `{target, type, note}`. `type` ∈ `complements`/`alternative`/`conflicts`/`requires`/`related`/`learn-with`. `target` is a local slug or a CURIE `namespace:slug` (a federated edge into another VKB). Edges may also be authored as prose link-titles in the body (local only). See Federation. |
| `x-civic.reason` | String | Required when `status` is `ARCHIVED`/`REJECTED` — why the record was retired. |
| `x-civic.archived` | Object | Required when `status` is `ARCHIVED`: `{date, disposition, successor?}`. `disposition` ∈ `acquired`/`discontinued`/`merged`/`superseded`/`eligibility-changed`/`duplicate`; `successor` is the slug of a replacement, if any. |

**Example source YAML:**
```yaml
type: offer
title: "OpenAI for Nonprofits"
x-civic:
  profile: civic/0.4
  status: ACTIVE
  category: "AI"
  sub_category: "General"
  offer:
    type: "Discount"
    summary: "Discounted ChatGPT Team & Enterprise"
    standard_tier: "Team / Enterprise"
    savings_estimate: "Significant discount off standard rates"
    badges: ["Discount"]
  eligibility:
    eligible_audiences: ["nonprofit"]
    regions: ["ALL"]
    pcs_subject: ["ALL"]
    rules: "Requires 501(c)(3) verification"
    min_budget: 0
    max_budget: null
  provenance:
    last_audited: "2026-05-16"
    vendor_url: "https://help.openai.com/..."
    source: "TechSoup VKB"
```

## Flat projection (`products.json`)

`build_products.py` flattens each record to the keys the frontend already reads, so the published contract is unchanged:

| `products.json` key | from |
| :--- | :--- |
| `id` | **derived** — `namespace:slug` (global identity; civic/0.5) |
| `capability` | `x-civic.capability` (emitted only when set) |
| `product_name` | `title` |
| `category`, `sub_category` | `x-civic.category`, `x-civic.sub_category` |
| `cost` | `x-civic.offer.summary` |
| `standard_tier`, `savings_estimate`, `badges` | `x-civic.offer.*` |
| `eligible_audiences` | `x-civic.eligibility.eligible_audiences` (the audience keys, verbatim) |
| `audience_tuples` | **derived** — each audience key expanded via `registry/audiences.json` into `{org_types, pcs_subject}` PCS-code tuples; this is what the frontend matches against (OR across tuples, AND within) |
| `eligible_audience_labels` | **derived** — human labels for the audience keys, for card display |
| `eligible_countries` | `x-civic.eligibility.regions` |
| `eligibility_pcs_subject` | `x-civic.eligibility.pcs_subject` (offer-level mission restriction) |
| `rules`, `min_budget`, `max_budget` | `x-civic.eligibility.*` |
| `last_audited`, `vendor_url` | `x-civic.provenance.*` |
| `slug` | folder name |

The feed is wrapped — `{ meta, products }` — and `meta` carries `profile`, `namespace`, `base_uri`, `license`, and the full `audiences` registry so consumers can resolve keys to codes and know which bundle they're reading. Per record, `id` and (when set) `capability` are now projected, as is `relations` (typed graph edges, local and federated). The remaining x-civic fields (`status`, `provenance.source`) stay source-only.

> **Contract stability.** All of the civic/0.5 additions are *additive* — `id`, `capability`, `meta.namespace`, `meta.base_uri` — plus the `meta.profile` bump. No existing `products.json` key changed value, so the Offer Center is unaffected. This is enforced by `scripts/check_contract.py` against `tests/golden_products.json`.

## Federation (civic/0.5)

A VKB is one bundle of files. civic/0.5 lets independently-maintained bundles form a single navigable graph, the way Data Commons federates over shared entity IDs.

**1. Global identity.** The bundle declares its prefix in `index.md`:

```yaml
x-civic:
  namespace: techsoup
  base_uri: https://vkb.techsoup.org/
```

Locally a record's identity is still its folder/slug. Globally it's `namespace:slug` (e.g. `techsoup:openai`), emitted as each record's `id` and echoed in `meta.namespace`/`meta.base_uri`. The namespace must match `^[a-z][a-z0-9_-]*$`.

**2. Federated edges.** A `relations` entry whose `target` is a CURIE for a *different* namespace is a federated edge:

```yaml
x-civic:
  relations:
    - target: "sociotechno:disaster-mapping"   # another VKB
      type: complements
      note: "Pairs with our GIS offers"
    - target: "salesforce"                       # local slug — unchanged behavior
      type: alternative
```

The build keeps the CURIE verbatim and tags the edge `external: true` + `namespace`. External edges are **not** mirrored (we can't write into a peer's files); local edges still are (except directional `requires`). The peer namespace is checked against `registry/peers.json` — an unregistered peer is a warning, not a failure, so the build stays **offline by default**. A future opt-in step can fetch a peer's `products.json` to confirm the target and pull its title.

**3. Capability as the join key.** `x-civic.capability` (validated against `registry/capabilities.json`) names the shared function an offer provides. Two offers with the same capability — in the same VKB or across federated ones — are substitutes. This is what lets an agent answer "my VKB has nothing for *fundraising* — does a peer?": group by capability across the federated graph.

**Registries:** `registry/peers.json` (namespace → bundle location) and `registry/capabilities.json` (the capability vocabulary).

## Lifecycle & archiving

An offer that is no longer valid is **archived, not deleted** — the record is retained so we don't re-add it, and so we can later query *why* offers were retired and what became of them. Archiving (via `scripts/archive.py`) does four things atomically:

1. Sets `x-civic.status: ARCHIVED` and writes `reason` + the `archived` block.
2. Prepends a generated **ARCHIVED banner** above the preserved original content.
3. Moves the product folder into a per-category **`_archive/`** directory: `products/<category>/_archive/<slug>/`.
4. Flips the offer's row in `registry/offers_registry.csv` to `Status: ARCHIVED` — the row **stays** so discovery never re-adds the offer.

`build_products.py` then excludes it from `products.json` **by status** (not by location — status is the source of truth).

> **`_archive/` is excluded from surfacing.** By convention, anything that surfaces the active knowledge base — the Offer Center build, an Obsidian Gardener browsing, or a bot doing retrieval over the products tree — **must scope to the active tree and skip `_archive/`**. That keeps archived records out of human and AI attention (frugal by default) while preserving them on disk for audit and "don't re-add" checks.

## Tooling

- **Validate (frontmatter):** `python3 VKB-Core/scripts/validate.py` — checks every record (active *and* archived) against `schemas/civic_schema.json`.
- **Lint (structure):** `python3 VKB-Core/scripts/lint_structure.py` — checks each product *package's* on-disk shape (skill + content folders + `.gitkeep`) against `schemas/structure_spec.json`. Report-only; `--fix-all`/`--fix <id>`/`--fix-from <file>` scaffold missing pieces (never destructive); `--strict` to fail on any deviation. See its `--help`.
- **Build:** `python3 VKB-Core/scripts/build_products.py` — regenerates `products.json` (live statuses only).
- **Guard the contract:** `python3 VKB-Core/scripts/check_contract.py` — rebuilds in a temp dir and verifies the published `products.json` still matches the frozen snapshot (`tests/golden_products.json`). New keys and a `meta.profile` bump are allowed; a removed/changed field fails. `--update` re-freezes the snapshot to bless an intentional change. Runs in CI on every push/PR.
- **Archive:** `python3 VKB-Core/scripts/archive.py <slug> --reason "…" --disposition <kind> [--successor <slug>]` — retires an offer (see Lifecycle above).
- **Migrations (one-time, already run):**
  - `migrate_to_xcivic.py` — legacy flat frontmatter → `x-civic` 0.2.
  - `migrate_to_civic_03.py` — profile 0.2 → 0.3; `ntee_codes` key → `pcs_subject` (rename only).
  - `build_pcs_registry.py` — builds `registry/pcs_registry.json` (Candid PCS Subject + OrgType) from the 2024 workbook.
  - `crosswalk_civic_03.py` — rewrites legacy NTEE `pcs_subject` values → PCS Subject codes.
  - `migrate_audiences.py` — profile 0.3 → 0.4; `org_types` list → `eligible_audiences` keys (see `registry/audiences.json`).
  - `migrate_to_civic_05.py` — profile 0.4 → 0.5 (federation: identity, federated edges, capability vocab; profile bump only, idempotent).
