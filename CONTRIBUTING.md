# Contributing to the TechSoup Product Bundle

Thank you for considering contributing to the TechSoup Product Bundle! This
repository is a portable, open copy of the dataset TechSoup uses to describe
technology donations and discounts for nonprofits.

There are three ways to help, and each one takes a different route.

| You want to… | Do this |
|---|---|
| Add a product, or fix a product entry | [Open an issue](#1-suggest-a-product-or-report-an-inaccuracy) — please **don't** send a pull request to `products/` |
| Share something you built with the bundle | [Tell us about it](#2-share-what-you-built), or add it to `examples/` in a pull request |
| Improve the docs, schema, or examples | [Send a pull request](#3-improve-the-docs-schema-or-examples) |

## Why product changes go through issues

Everything in `products/` is mirrored automatically from TechSoup's internal
Verbose Knowledge Base (VKB), where entries are researched and audited before
they are published. Every sync replaces the whole `products/` directory, so a
pull request that edits a product file here would be overwritten the next time
the mirror runs.

Opening an issue gets your change into the VKB instead. Once it is reviewed
there, it flows back into this repository with the next sync, and into every
tool built on top of it.

## 1. Suggest a product or report an inaccuracy

Offers, eligibility rules, and vendor URLs change often, and we want to hear
when an entry is wrong or when something is missing.

- **New product:** open a [Suggest a product](https://github.com/TechSoup/TechSoup-Product-Bundle/issues/new?template=suggest-product.yml)
  issue. Include the vendor's nonprofit program page, what the offer is, and who
  qualifies.
- **Correction:** open a [Report an inaccuracy](https://github.com/TechSoup/TechSoup-Product-Bundle/issues/new?template=report-inaccuracy.yml)
  issue. Name the entry (for example `products/security/1password/`), say what's
  wrong, and link a source that shows the current terms.

A link to the vendor's own page is the most useful thing you can include: every
entry records the page its terms were read from (`x-civic.provenance.vendor_url`),
and a reviewer will check your change against it.

## 2. Share what you built

If you've built something on top of the bundle — a website widget, a filtered
feed, a chatbot, a spreadsheet import, a script — **we'd love to see it**, and
we'd like to share it with others in the sector. Either:

- **Tell us about it:** open a [Share what you built](https://github.com/TechSoup/TechSoup-Product-Bundle/issues/new?template=share-what-you-built.yml)
  issue with a link and a sentence or two about what it does. We'll add it to
  the *Built with the bundle* list in the [README](README.md); or
- **Add it to `examples/`:** if it's small and self-contained, send a pull
  request that adds a folder under `examples/`. Follow the pattern of the
  existing examples: one folder with its own `README.md` explaining what it does
  and how to run it, reading from `../../products/` rather than a copy of the
  data.

## 3. Improve the docs, schema, or examples

Pull requests are welcome for everything outside `products/`: the README, this
guide, the files in `Schema/`, and the code in `examples/`.

1. **Fork** the repository and create a branch.
2. Make your change. If you're editing an example, regenerate its feed with its
   `build_feed.py` and check the demo still loads.
3. **Open a pull request** describing what you changed and why.

If a schema change would make existing entries fail validation, open an issue
first. The schema is calibrated against the data that's already published, so
tightening it means cleaning up the data first.

## Licensing

By contributing, you agree that your contributions are licensed the same way as
the part of the repository they belong to:

- **Data and documentation** (everything except `examples/`) — [CC BY-SA 4.0](LICENSE).
- **Example code** in `examples/` — [MIT](examples/LICENSE), so it can be dropped
  into any project. The JSON feeds generated from the bundle are still data and
  stay under CC BY-SA 4.0.
