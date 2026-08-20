---
type: schema
okf_version: "0.1"
title: Offer Entry Schema
description: The field contract every VKB product entry satisfies — frontmatter structure, permitted values, and body conventions.
x-civic:
  profile: civic/0.5
  maintainer: TechSoup
  namespace: techsoup
  applies_to: products/**/*_README.md
---

# Offer Entry Schema

Every product in the Verbose Knowledge Base is one markdown file at
`products/<category>/<product>/<product>_README.md`, consisting of YAML
frontmatter followed by prose. This document defines what that frontmatter
contains.

The contract below was derived from all **159** entries currently in the bundle
(141 active, 18 archived), and validated against every one of them. Where entries
disagree with each other, that is noted rather than smoothed over.

**Scope.** This schema covers `*_README.md` offer entries only. The
`agent/*_skill.md` files that sit alongside them use a different frontmatter
shape (`type: skill`) and are not governed by this document.

## Shape

```yaml
---
type: offer
title: 1Password for Nonprofits
x-civic:
  profile: civic/0.5
  status: ACTIVE
  category: Security
  sub_category: Password Manager
  alias:                        # optional
    - 1Pass
  relations:                    # optional
    - target: bitwarden
      type: alternative
      note: comparable team password manager; pick one
  offer:
    type: Discount
    summary: 50% Discount
    standard_tier: null
    savings_estimate: null
    badges:
      - Discount
  eligibility:
    eligible_audiences:
      - nonprofit
    regions:
      - US
    pcs_subject:
      - ALL
    rules: null
    min_budget: 0
    max_budget: null
  provenance:
    last_audited: '2026-05-16'
    vendor_url: https://1password.com/for-good/
    source: TechSoup VKB
---
```

## Top level

| Field | Required | Type | Notes |
|---|---|---|---|
| `type` | yes | string | Always `offer` for product entries. Present in all 159. |
| `title` | yes | string | Human-readable product name as TechSoup presents it. |
| `x-civic` | yes | object | All structured data lives here. See below. |

`x-civic` is an extension namespace: the `x-` prefix marks it as a profile-specific
block layered on top of the base document format, so a generic markdown or OKF
reader can ignore it without error while TechSoup tooling relies on it.

## `x-civic`

| Field | Required | Type | Notes |
|---|---|---|---|
| `profile` | yes | string | Schema profile identifier. `civic/0.5` across all entries. |
| `status` | yes | enum | `ACTIVE` (141) or `ARCHIVED` (18). |
| `category` | yes | enum | One of the seven categories. Must agree with the entry's directory. |
| `sub_category` | yes | string | Free text. See *Sub-category* below. |
| `alias` | no | string[] | Alternative names the product is known by. Present in 13 entries; may be `[]`. |
| `relations` | no | object[] | Links to other entries. Present in 13 entries; may be `[]`. |
| `offer` | yes | object | What is being offered. |
| `eligibility` | yes | object | Who qualifies. |
| `provenance` | yes | object | Where the information came from and when. |
| `archived` | archived only | object | Required when `status: ARCHIVED`. |
| `reason` | archived only | string | Prose explanation of the archival. |

### `category`

Seven permitted values. Counts include archived entries.

| Value | Entries |
|---|---:|
| `Operations` | 54 |
| `Communications` | 36 |
| `Infrastructure` | 30 |
| `Fundraising` | 15 |
| `Security` | 11 |
| `AI` | 8 |
| `Programs` | 5 |

### `sub_category`

Currently **free text**, and the least disciplined field in the schema: 88
distinct values across 159 entries. `General` accounts for 41 of them; roughly
sixty values are used exactly once, and several are near-duplicates of each other
(`Accounting & Finance` / `Accounting and Finance` / `Accounting`;
`E-Signature` / `E-Signature & Documents`; `Hardware` / `Hardware / devices` /
`Computers & hardware`).

Treat `sub_category` as a label, not a key. Do not group, filter, or build
navigation on it without normalizing first. Promoting it to a controlled
vocabulary is the obvious next step for this schema.

### `relations`

Each element links this entry to another product entry.

| Field | Required | Type | Notes |
|---|---|---|---|
| `target` | yes | string | Directory slug of the related entry, e.g. `openai`. |
| `type` | yes | enum | Observed value: `alternative`. |
| `note` | no | string | Why the relation holds, and any guidance for choosing. |

## `x-civic.offer`

| Field | Required | Type | Notes |
|---|---|---|---|
| `type` | yes | enum | Nature of the offer. See below. |
| `summary` | yes | string | Short plain-language statement, e.g. `50% Discount`, `$8/user/month`. |
| `badges` | yes | enum[] | Display labels. `Discount` (119), `Donation` (40), `Built for Nonprofits` (6), `Open Source` (6), `Discovery` (2). |
| `standard_tier` | no | string \| null | Commercial tier the offer maps to. Present in 146 entries, frequently `null`. |
| `savings_estimate` | no | string \| null | Estimated value of the offer. Present in 146 entries, frequently `null`. |

`offer.type` values:

| Value | Entries | Meaning |
|---|---:|---|
| `Discount` | 115 | Reduced commercial pricing. |
| `Donation` | 32 | Provided at no cost. |
| `Discovery` | 5 | Listed for awareness; no TechSoup-negotiated terms. |
| `Open Source` | 4 | Freely available; listed as a recommendation. |
| `Built for Nonprofits` | 1 | Purpose-built for the sector. |
| `Commercially Built for Nonprofits` | 1 | Commercial product built for the sector. |
| `Nonprofit Built for Nonprofits` | 1 | Built by a nonprofit for nonprofits. |

The last three are singletons and overlap conceptually with the `Built for
Nonprofits` badge. They are candidates for consolidation.

## `x-civic.eligibility`

| Field | Required | Type | Notes |
|---|---|---|---|
| `eligible_audiences` | yes | enum[] | Organization types that qualify. |
| `regions` | yes | enum[] | Where the offer is available. |
| `pcs_subject` | yes | string[] | Philanthropy Classification System subject codes. |
| `min_budget` | yes | number | Lower budget bound. `0` in effectively all entries. |
| `max_budget` | no | number \| null | Upper bound. Present in 104 entries, usually `null`. |
| `rules` | no | string \| null | Free-text qualifications not captured by the fields above. Present in 148 entries, usually `null`. |
| `notes` | deprecated | string \| null | Duplicates `rules`. One entry only (`programs/safe_shelter_collaborative`). Merge into `rules`; do not add new uses. |

`eligible_audiences` values: `nonprofit` (155), `public_library` (59),
`everyone` (4), `social_enterprise` (3), `healthcare` (1), `k12` (1), `team` (1),
`personal` (1). Multiple values per entry are normal.

`regions` values: `ALL` (108), `US` (51), `CA` (5), `UK` (1), `AU` (1). `ALL`
means unrestricted, not "every listed region".

`pcs_subject` is `ALL` in 157 entries; the remainder carry PCS codes
(`SS000000`, `SJ000000`, `SK000000`, `SN000000`, `SR000000`). `ALL` means the
offer is not restricted by subject area.

## `x-civic.provenance`

Required on every entry. This block is what makes an entry citable.

| Field | Required | Type | Notes |
|---|---|---|---|
| `last_audited` | yes | date (`YYYY-MM-DD`, quoted) | When a human last verified the entry against the vendor. |
| `vendor_url` | yes | url | The vendor page the offer terms were read from. |
| `source` | yes | enum | How the record originated. See below. |

Quote the date so YAML parses it as a string rather than coercing it to a
native date type, matching existing entries.

`source` has two values, and the distinction matters when judging how much to
trust an entry:

| Value | Entries | Meaning |
|---|---:|---|
| `TechSoup VKB` | 136 | Authored and audited here. Authoritative. |
| `products.json (reverse-sync)` | 23 | Reconstructed from the downstream feed rather than written first-hand. Structurally valid but thinner; these entries are the best candidates for a genuine audit. |

Three entries wrap a long `vendor_url` using a YAML folded scalar (`>-`). That is
valid YAML and parses to an ordinary string — no special handling needed by
consumers.

## `x-civic.archived`

Required when `status: ARCHIVED`, absent otherwise. All 18 archived entries carry
it.

| Field | Required | Type | Notes |
|---|---|---|---|
| `date` | yes | date (`YYYY-MM-DD`, quoted) | When the offer was archived. |
| `disposition` | yes | enum | `discontinued` (17) or `acquired` (1). |

The sibling `x-civic.reason` field carries the prose explanation.

Archived entries additionally open their body with a banner block, delimited by
`<!-- archived-banner -->` and `<!-- /archived-banner -->`, restating the
disposition, date, and reason so the archival is unmissable when the file is read
directly.

## Body structure

The canonical body is three sections of escalating detail — the "verbose" in
Verbose Knowledge Base. Each answers a different reader's question:

```markdown
## Level 1 (Quick Glance)
What the product is and what the offer is, in a short paragraph.

## Level 2 (Detailed Eligibility Matrix)
Who actually qualifies, what documentation is required, how long it lasts.

## Level 3 (Implementation & Maintenance Requirements)
What adopting it costs in effort: prerequisites, expertise required,
ongoing overhead.

### Embedded Parameters
Cross-cutting assessments — security posture, AI functionality,
long-term sustainability.
```

The levels exist so one entry serves several audiences without being rewritten.
Someone triaging a question reads Level 1; someone confirming a nonprofit's
eligibility reads Level 2; someone deciding whether the organization can actually
support the product reads Level 3.

**Conformance is partial.** 111 of 159 entries use this structure; **48 do not**,
instead using `## Overview` (43) and `## Details` (28) headings inherited from an
earlier convention. `### Embedded Parameters` appears in 88. Bringing the
remaining 48 entries onto the Level 1–3 structure is outstanding work — treat the
three-level form as the target for anything new or edited.

## Validating an entry

`offer.schema.json` in this folder expresses the frontmatter contract above as a
JSON Schema (draft 2020-12), for use against parsed frontmatter rather than the
raw file. **All 159 entries currently validate against it with zero errors.**

The schema is deliberately calibrated to pass on today's data. The normalization
gaps called out above — `sub_category` as free text, the three singleton
`offer.type` values, the deprecated `eligibility.notes` field — are permitted
rather than enforced, so that a validation failure means something actually broke
instead of restating drift already known. Tightening any of them is a data
cleanup first and a schema change second, in that order; reversing the order just
makes the schema fail on committed files.

`additionalProperties` is `false` throughout. An unrecognized field is treated as
an error rather than ignored, so a typo like `vendor_urls` or `elligibility`
surfaces at validation time instead of silently disappearing from every consumer
that reads the field by name.
