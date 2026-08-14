#!/usr/bin/env python3
"""
build_products.py — the VKB v2 build pipeline (civic/0.5).

    OKF product files (x-civic 0.5)  ->  SQLite (vkb.db)  ->  products.json

The markdown files are the source of truth. Product frontmatter is the nested
`x-civic` profile (civic/0.5). This loads the files into a SQLite engine
(queryable by tools like the recommender), resolves the typed relationship edges,
then emits products.json — the headless API the Offer Center and other tools
consume.

IDENTITY (civic/0.5). The bundle declares a `namespace` in index.md
(`x-civic.namespace`, e.g. `techsoup`). Every record gets a global `id` of
`namespace:slug`, and the feed's `meta` carries `namespace` + `base_uri`. This is
what lets edges cross between independently-maintained, federated VKBs.

GRAPH EDGES (civic/0.5). Relationships come from two sources. (1) Prose link-title
edges in the body (OKF #101) — always local:

    [Anthropic Claude](anthropic_README.md "complements: shared workspace AI")

(2) Frontmatter `x-civic.relations` entries, whose `target` is a local slug, a
CURIE `namespace:slug` for this bundle (local), or a CURIE for ANOTHER namespace
— a federated (external) edge, kept verbatim and tagged `external` + `namespace`,
validated against registry/peers.json. Edge type is one of complements,
alternative, conflicts, requires, related, learn-with. Symmetric local edges are
mirrored onto the target; `requires` is directional; external edges are never
mirrored (we can't write into a peer's files). Resolved edges are emitted as each
record's `relations` list.

FEED SHAPE (civic/0.5). products.json is a wrapped object:

    { "meta": { profile, namespace, base_uri, license, audiences }, "products": [ ... ] }

so the feed is self-describing and carries its own layered license (TechSoup
CC BY-SA 4.0 over the offer data; Candid CC BY 4.0 over the PCS vocabulary). The
per-product records keep the SAME FLAT CONTRACT (product_name, cost, eligible_*,
badges, …); only the eligibility key `eligibility_ntee_codes` was renamed to
`eligibility_pcs_subject` in this version.

The database is disposable — rebuilt from the files every run, and gitignored.
The files, and the emitted products.json, are what's committed.

Usage:  python3 VKB-Core/scripts/build_products.py
"""
import json
import pathlib
import re
import sqlite3
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install -r requirements.txt")

CORE = pathlib.Path(__file__).resolve().parent.parent      # VKB-Core
PRODUCTS = CORE / "products"
PROJECT = CORE.parent                                       # repo root
DB_PATH = CORE / "vkb.db"
# The feed is written to BOTH known locations. resources/data/ is the published
# path the Offer Center front end actually fetches (app.js) and the one
# sync_md_from_json.py treats as the source of truth; the Offer-Center root copy
# is the build's historical emit path, kept so nothing depending on it breaks.
# Writing both removes the manual copy step that previously stood between a
# rebuild and the site reflecting it.
JSON_OUTPUTS = [
    PROJECT / "Offer-Center" / "resources" / "data" / "products.json",
    PROJECT / "Offer-Center" / "products.json",
]
JSON_OUT = JSON_OUTPUTS[0]        # primary/published path, for messages
AUDIENCES_PATH = CORE / "registry" / "audiences.json"
INDEX_PATH = CORE / "index.md"
PEERS_PATH = CORE / "registry" / "peers.json"
CAPABILITIES_PATH = CORE / "registry" / "capabilities.json"

PROFILE = "civic/0.5"

# Only these statuses are "live" and appear in the published catalog. Status is
# the single source of truth for build inclusion — archived/rejected records are
# excluded by status, regardless of where their files live (e.g. _archive/).
LIVE_STATUSES = {"ACTIVE", "INITIALIZED"}

# Typed relationship edges (OKF #101 link-title convention). Symmetric edges are
# mirrored onto their target; directional edges are one-way.
EDGE_TYPES = {"complements", "alternative", "conflicts", "requires", "related", "learn-with"}
DIRECTIONAL_EDGE_TYPES = {"requires"}

# A markdown link carrying a title: [text](href "title")
TITLED_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\s+\"([^\"]*)\"\)")

# Self-describing feed license (civic/0.4). The two layers are licensed
# separately: TechSoup's contributed data is CC BY-SA 4.0; the Candid PCS
# vocabulary embedded in eligibility codes remains CC BY 4.0.
FEED_LICENSE = {
    "data": {
        "holder": "TechSoup Global Network",
        "spdx": "CC-BY-SA-4.0",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "applies_to": "VKB offer data, eligibility curation, and the relationship graph",
        "attribution_url": "https://about.techsoup.org",
    },
    "taxonomy": {
        "holder": "Candid",
        "work": "Philanthropy Classification System (PCS)",
        "spdx": "CC-BY-4.0",
        "url": "https://creativecommons.org/licenses/by/4.0/",
        "source": "https://taxonomy.candid.org",
        "modified": True,
        "applies_to": "PCS subject and organization-type codes in eligibility",
    },
}


def load_audiences():
    """Load the audience registry (key -> {label, org_types, pcs_subject, ...})."""
    try:
        reg = json.loads(AUDIENCES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"audiences registry not found: {AUDIENCES_PATH}")
    return reg.get("audiences", {})


def load_bundle():
    """Read the bundle's federation identity from index.md frontmatter.

    Returns {namespace, base_uri}. The namespace is this VKB's globally-unique
    prefix; a record's global id is `namespace:slug`. Edges whose CURIE target
    carries a *different* namespace are federated (external) edges.
    """
    text = INDEX_PATH.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    xc = (fm or {}).get("x-civic", {}) or {}
    ns = xc.get("namespace")
    if not ns:
        sys.exit(f"index.md is missing x-civic.namespace (required for civic/0.5 identity): {INDEX_PATH}")
    return {"namespace": ns, "base_uri": xc.get("base_uri")}


def load_peers():
    """Load the federated-peer registry (namespace -> {base_uri, ...})."""
    try:
        reg = json.loads(PEERS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    return reg.get("peers", {})


def is_product_readme(p):
    """A product-root README is `<slug>/<slug>_README.md` (active or archived)."""
    return p.name.endswith("_README.md") and p.parent.name + "_README.md" == p.name


def status_of(data):
    xc = data.get("x-civic")
    return xc.get("status") if isinstance(xc, dict) else None


def flatten(d, slug, audiences, namespace):
    """Flatten an x-civic record into the flat products.json contract.

    Pre-migration flat records are passed through unchanged.

    max_budget and eligibility_notes were previously presence-gated with
    `if "..." in el`, which made the feed depend on whether the YAML key existed
    at all. The source cannot carry that distinction reliably: editors that
    serialise from a schema (Keystatic) drop keys whose value is null or empty,
    so `max_budget: null` silently became a missing key and the field vanished
    from the feed for that product.

    Both are now insensitive to key presence:
      - max_budget       emitted always (null when unset) — null already means
                         "unlimited" to Offer-Center/app.js, and this keeps the
                         key on every row rather than 98 of 141.
      - eligibility_notes emitted only when it has a value — absent and empty
                         both mean "no notes", so gating on the value rather
                         than the key is equally robust and leaves the feed
                         unchanged for the 140 rows that have none.

    Offer-Center/app.js tests truthiness, not presence
    (`max_budget && max_budget !== "null"`), so null and undefined already took
    the same branch. No rendered behaviour changes.

    Eligibility (civic/0.4) is an OR-list of audience keys (`eligible_audiences`).
    Each key is expanded via the audience registry into an (org_types AND
    pcs_subject) tuple; the offer is eligible to a user who matches ANY tuple.
    `eligibility_pcs_subject` remains an independent, offer-level mission filter.
    """
    if "x-civic" not in d:                       # legacy flat record
        flat = dict(d)
        flat["slug"] = slug
        flat["id"] = f"{namespace}:{slug}"
        return flat

    xc = d.get("x-civic") or {}
    off = xc.get("offer") or {}
    el = xc.get("eligibility") or {}
    pr = xc.get("provenance") or {}
    la = pr.get("last_audited")

    flat = {
        "id": f"{namespace}:{slug}",          # global identity (civic/0.5)
        "type": d.get("type"),
        "product_name": d.get("title"),
        "category": xc.get("category"),
        "sub_category": xc.get("sub_category"),
        "cost": off.get("summary"),
    }
    if xc.get("capability"):                  # cross-VKB join key; emitted only when set
        flat["capability"] = xc.get("capability")
    # Alternate / legacy / marketing names. Value-gated, not presence-gated: an
    # absent key and an empty list both mean "no aliases", so an editor that
    # writes `alias: []` produces the same feed as one that omits the key.
    if xc.get("alias"):
        flat["alias"] = xc.get("alias")
    flat["max_budget"] = el.get("max_budget")
    flat["eligible_countries"] = el.get("regions")

    # Expand eligible_audiences -> resolved (org_types AND pcs_subject) tuples.
    aud_keys = el.get("eligible_audiences") or []
    tuples, labels = [], []
    for k in aud_keys:
        a = audiences.get(k)
        if a is None:
            print(f"  ! {slug}: unknown audience key {k!r} (not in audiences.json)")
            continue
        tuples.append({"org_types": a.get("org_types", ["ALL"]),
                       "pcs_subject": a.get("pcs_subject", ["ALL"])})
        labels.append(a.get("label", k))
    flat["eligible_audiences"] = aud_keys
    flat["audience_tuples"] = tuples
    flat["eligible_audience_labels"] = labels

    flat["eligibility_pcs_subject"] = el.get("pcs_subject")
    flat["last_audited"] = str(la) if la is not None else None
    flat["vendor_url"] = pr.get("vendor_url")
    flat["badges"] = off.get("badges")
    flat["standard_tier"] = off.get("standard_tier")
    flat["savings_estimate"] = off.get("savings_estimate")
    flat["rules"] = el.get("rules")
    flat["min_budget"] = el.get("min_budget")
    # value-gated, not presence-gated: an absent key and an empty/null value both
    # mean "no notes", so this is immune to a schema editor dropping the key —
    # and unlike an unconditional emit it doesn't add a null to all 141 rows
    if el.get("notes"):
        flat["eligibility_notes"] = el.get("notes")
    flat["slug"] = slug
    return flat


def parse_edges(body):
    """Typed edges from prose link titles. Returns [{href, type, note}, ...].

    Only links whose title begins with a recognized edge token count; incidental
    links (no title, or an unrecognized token) are ignored.
    """
    edges = []
    for href, title in TITLED_LINK_RE.findall(body):
        if ":" not in title:
            continue
        token, _, note = title.partition(":")
        token = token.strip()
        if token not in EDGE_TYPES:
            continue
        edges.append({"href": href, "type": token, "note": note.strip()})
    return edges


def read_products(audiences, namespace):
    """Parse every live product-root README. Returns [{slug, flat, body}, ...].

    products.json is the Offer Center feed, so it carries OFFERS only. The OKF
    `type` field is the entry-kind discriminator (offer | course | service |
    resource …); non-offer kinds live in the same tree but are emitted to their
    own feeds, not here. Legacy records with no `type` are treated as offers.
    """
    records = []
    skipped = 0
    skipped_kind = 0
    for p in sorted(PRODUCTS.rglob("*_README.md")):
        if not is_product_readme(p):
            continue
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            data = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as e:
            print(f"  ! YAML error in {p}: {e}")
            continue
        if data.get("type", "offer") != "offer":          # courses/services → their own feeds
            skipped_kind += 1
            continue
        status = status_of(data)
        if status is not None and status not in LIVE_STATUSES:
            skipped += 1                                  # archived/rejected → not in catalog
            continue
        slug = p.parent.name                              # path/slug = identity (OKF)
        xc = data.get("x-civic") or {}
        records.append({
            "slug": slug,
            "flat": flatten(data, slug, audiences, namespace),
            "body": parts[2],
            "xrel": xc.get("relations") or [],            # authored frontmatter edges (civic/0.5)
        })
    if skipped:
        print(f"  ({skipped} non-live record(s) excluded by status)")
    if skipped_kind:
        print(f"  ({skipped_kind} non-offer record(s) excluded by type)")
    return records


def attach_relations(records, namespace, peers):
    """Attach a `relations` list to each product, from two authoring sources:

      1. Prose link-title edges in the body (OKF #101) — always LOCAL.
      2. Frontmatter `x-civic.relations` entries (civic/0.5) — each `target` is
         either a local slug, a CURIE `namespace:slug` for THIS bundle (local),
         or a CURIE for a DIFFERENT namespace (a federated / external edge).

    Local edges resolve to a sibling slug; symmetric ones are mirrored onto the
    target so the graph is navigable both ways (`requires` is directional and not
    mirrored). External edges keep their CURIE target, are tagged `external` with
    the peer `namespace`, and are NOT mirrored — we can't write into a peer's
    files. The peer namespace is validated against registry/peers.json (a warning,
    not a hard failure, so the build stays offline and resilient).
    Unresolved local targets are reported and dropped.
    """
    by_basename = {f"{r['slug']}_README.md": r["slug"] for r in records}
    local_slugs = set(by_basename.values())
    rel_map = {r["slug"]: [] for r in records}
    unresolved = 0
    external = 0

    def add(slug, rel):
        if rel not in rel_map[slug]:
            rel_map[slug].append(rel)

    def add_local(src, target, etype, note):
        add(src, {"target": target, "type": etype, "note": note})
        if etype not in DIRECTIONAL_EDGE_TYPES:                 # mirror symmetric edges
            add(target, {"target": src, "type": etype, "note": note})

    for r in records:
        src = r["slug"]

        # (1) prose link-title edges — resolved locally by README basename
        for e in parse_edges(r["body"]):
            target = by_basename.get(e["href"].rsplit("/", 1)[-1])
            if target is None:
                print(f"  ! unresolved prose edge in {src}: {e['type']} -> {e['href']}")
                unresolved += 1
                continue
            add_local(src, target, e["type"], e["note"])

        # (2) frontmatter relations — local slug, local CURIE, or federated CURIE
        for rel in r["xrel"]:
            target_raw = (rel.get("target") or "").strip()
            etype = rel.get("type")
            note = rel.get("note", "")
            if not target_raw or etype not in EDGE_TYPES:
                print(f"  ! invalid relation in {src}: {rel!r}")
                unresolved += 1
                continue

            if ":" in target_raw:                              # CURIE: namespace:slug
                ns, _, rest = target_raw.partition(":")
                if ns == namespace:                            # our own namespace => local
                    if rest in local_slugs:
                        add_local(src, rest, etype, note)
                    else:
                        print(f"  ! unresolved local edge in {src}: {etype} -> {target_raw}")
                        unresolved += 1
                    continue
                # different namespace => federated (external) edge
                if ns not in peers:
                    print(f"  ! {src}: edge to unregistered peer namespace '{ns}' "
                          f"(add it to registry/peers.json) -> {target_raw}")
                add(src, {"target": target_raw, "type": etype, "note": note,
                          "external": True, "namespace": ns})
                external += 1
            else:                                              # bare local slug
                if target_raw in local_slugs:
                    add_local(src, target_raw, etype, note)
                else:
                    print(f"  ! unresolved local edge in {src}: {etype} -> {target_raw}")
                    unresolved += 1

    edge_count = 0
    for r in records:
        r["flat"]["relations"] = sorted(
            rel_map[r["slug"]], key=lambda x: (x["type"], x["target"]))
        edge_count += len(r["flat"]["relations"])
    return edge_count, unresolved, external


def build_db(items):
    """Load products into a fresh SQLite engine and return the connection."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """CREATE TABLE products(
            slug TEXT PRIMARY KEY, id TEXT, type TEXT, product_name TEXT, category TEXT,
            sub_category TEXT, capability TEXT, alias TEXT, cost TEXT, min_budget, max_budget,
            eligible_countries TEXT, eligible_audiences TEXT,
            eligibility_pcs_subject TEXT, badges TEXT, relations TEXT,
            last_audited TEXT, vendor_url TEXT, data TEXT)"""
    )
    for d in items:
        con.execute(
            "INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                d.get("slug"), d.get("id"), d.get("type"), d.get("product_name"), d.get("category"),
                d.get("sub_category"), d.get("capability"),
                json.dumps(d.get("alias")),  # list -> JSON text, as for badges
                d.get("cost"),
                d.get("min_budget"), d.get("max_budget"),
                json.dumps(d.get("eligible_countries")), json.dumps(d.get("eligible_audiences")),
                json.dumps(d.get("eligibility_pcs_subject")), json.dumps(d.get("badges")),
                json.dumps(d.get("relations")),
                str(d.get("last_audited") or ""), d.get("vendor_url"),
                json.dumps(d, default=str),
            ),
        )
    con.commit()
    return con


def emit_json(con, audiences, bundle):
    """Emit the wrapped, self-describing products.json from the database."""
    rows = con.execute("SELECT data FROM products ORDER BY product_name").fetchall()
    products = [json.loads(r[0]) for r in rows]
    feed = {
        "meta": {
            "profile": PROFILE,
            "namespace": bundle["namespace"],
            "base_uri": bundle["base_uri"],
            "license": FEED_LICENSE,
            "audiences": audiences,
        },
        "products": products,
    }
    payload = json.dumps(feed, indent=4)
    for out in JSON_OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return len(products)


def main():
    bundle = load_bundle()
    peers = load_peers()
    audiences = load_audiences()
    records = read_products(audiences, bundle["namespace"])
    edges, unresolved, external = attach_relations(records, bundle["namespace"], peers)
    items = [r["flat"] for r in records]
    con = build_db(items)
    n = emit_json(con, audiences, bundle)
    con.close()
    note = f" ({unresolved} unresolved)" if unresolved else ""
    ext = f", {external} federated" if external else ""
    written = " + ".join(str(o.relative_to(PROJECT)).replace("\\", "/") for o in JSON_OUTPUTS)
    print(f"Built {DB_PATH.name} and {written} "
          f"from {len(items)} OKF product files as '{bundle['namespace']}' "
          f"({n} rows, {edges} graph edges{ext}{note}).")


if __name__ == "__main__":
    main()
