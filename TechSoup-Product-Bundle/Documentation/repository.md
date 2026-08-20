---
type: documentation
okf_version: "0.1"
title: The VKB Repository — Home of TechSoup's Product Library
description: What the techsoup-product-bundle repository is, what it holds, and why TechSoup's product library lives in version control.
x-civic:
  profile: civic/0.5
  maintainer: TechSoup
  namespace: techsoup
---

# The VKB Repository

## What it is

TechSoup's product library has a single canonical home:

```
https://github.com/techsoup/techsoup-product-bundle.git
```

This repository holds the **Verbose Knowledge Base (VKB)** — the source-of-truth
record of every technology offer TechSoup makes available to nonprofits, libraries,
and social enterprises. When a staff member needs to know whether a product is
still active, who is eligible for it, what the discount actually is, or when the
offer was last verified, this repository is the answer. Everything else that
displays product information — the Offer Center, catalog pages, internal
tooling — is downstream of it.

The working folder is `TechSoup-Product-Bundle/`. The default branch is `main`,
tracking `origin/main`.

There is exactly one origin. This is the point: not a shared drive with several
near-identical spreadsheets, not a wiki page someone edited in 2023, not a
per-team export. One repository, one branch, one current answer.

## What lives in it

```
TechSoup-Product-Bundle/
├── index.md          Top-level entry point and category directory
├── products/         The knowledge base itself — one folder per product
├── Schema/           The contract every product entry must satisfy
└── Documentation/    Reference material about the bundle (this file)
```

The root `index.md` and the seven category `index.md` files are navigation, not
data. They point at product entries; they do not hold anything the entries
themselves don't.

### `products/`

The substance of the repository. Product entries are grouped into seven
categories, each a directory:

| Category | Active entries |
|---|---:|
| Operations | 50 |
| Communications | 32 |
| Infrastructure | 23 |
| Fundraising | 13 |
| Security | 11 |
| AI | 7 |
| Programs | 5 |
| **Total active** | **141** |

Each product is one directory. A fully populated one looks like this:

```
products/ai/anthropic/
├── anthropic_README.md          The offer entry — the authoritative record
├── agent/
│   └── anthropic_skill.md       Per-product agent persona and expert knowledge
└── content/
    ├── case_studies/            Reserved for real-world examples
    └── use_cases/               Reserved for scenario write-ups
```

**`<product>_README.md`** is the record that matters. It carries structured YAML
frontmatter describing the offer, eligibility, and provenance, followed by prose
written in escalating levels of detail. The `Schema/` folder defines that
structure formally. Every one of the 159 product directories has one.

**`agent/<product>_skill.md`** holds a per-product agent definition — a
consultant persona scoped to that product, with instructions calibrated to
small-and-mid-sized nonprofits, plus product-specific expert knowledge. 145 of
these exist, and each of the seven categories also has a
`<category>_orchestrator_skill.md` at its top level. These make the knowledge
base directly usable by AI tooling rather than only by people reading files: the
same audited record that answers a staff question can also ground an assistant's
answer. They are derived from the README, not a second source of truth — where
the two disagree, the README wins.

**`content/case_studies/` and `content/use_cases/`** are currently placeholders.
All 136 of them contain nothing but `.gitkeep` files. The structure is reserved
and committed so the intended shape is visible, but no case study or use case has
been written yet. Read them as scaffolding, not content.

Each category directory also carries an `index.md` listing its products.

### `_archive/` subfolders

Every category also has an `_archive/` directory holding offers that are no
longer available — **18 entries** at present. Archived offers are *retained, not
deleted*. Each keeps its full record plus the date it was archived and why
(`discontinued`, `acquired`). This matters more than it sounds: when someone asks
"didn't we used to offer that?", the archive answers it, and it prevents a
retired offer from being quietly re-added as though it were new.

Counting active and archived together, the repository holds **159 product
entries**.

### `Schema/`

The field contract. Documents which frontmatter fields every entry must carry,
which are optional, and what values are permitted. It exists so that a product
entry can be *checked* rather than merely eyeballed, and so that downstream
consumers can rely on a field being present and well-formed.

### `Documentation/`

Reference material about the bundle as an artifact — what it is, how it is
organized, what its conventions mean.

## Why it lives in version control

The VKB is reference data that a lot of people rely on and that changes
constantly — vendors alter their nonprofit terms, programs end, eligibility
rules shift. That combination is exactly what version control is for.

**One authoritative copy.** A product's current state is whatever is on `main`.
There is no question of which file is newest, because there is only one file.
Local copies are checkouts of a known point in history, not independent
documents that drift apart.

**Every change is attributable and reversible.** Git records who changed a
product entry, when, and what the previous value was. If a discount figure is
wrong, the history shows when it changed and to what — and it can be restored
exactly. For data that staff quote to nonprofits, being able to answer "where
did this number come from?" is not a nicety.

**Changes can be reviewed before they are published.** Because entries are plain
text, a change to an offer shows up as a readable diff — this eligibility rule
was added, this audit date moved, this offer became archived. Someone other than
the author can look at it before it reaches the people who depend on it.

**Structured text outlives its tools.** Entries are markdown with YAML
frontmatter: readable directly in a text editor, diffable, greppable, and
parseable by anything. Nothing here is locked inside a proprietary format or a
particular vendor's platform. A spreadsheet is legible to humans but hostile to
automation; a database is the reverse. Frontmatter-in-markdown is the format that
serves both, which is what a source of truth feeding both staff and software has
to do.

**Provenance is part of the record.** Each entry carries a `last_audited` date
and a `vendor_url`. The repository therefore tracks not just what is claimed
about an offer, but when someone last confirmed it and against what source. Stale
entries become visible instead of invisible.

## Known drift

Two discrepancies to be aware of when reading this repository, recorded here so
they are not mistaken for facts about the data:

- **The root `index.md` counts are stale.** It reports 135 products with
  per-category figures that no longer match the directory contents. The counts in
  this document were measured from the files themselves.
- **The tracked top-level folder is still named `VKB-Core`.** The working folder
  was renamed to `TechSoup-Product-Bundle` locally, and that rename has not been
  committed. Paths in this document use the intended name,
  `TechSoup-Product-Bundle`.
