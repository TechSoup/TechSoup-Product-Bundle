---
type: index
okf_version: "0.1"
title: TechSoup Product Bundle
description: Nonprofit technology product intelligence as an Open Knowledge Format (OKF) bundle, published by TechSoup.
x-civic:
  profile: civic/0.5
  maintainer: TechSoup
  namespace: techsoup
  base_uri: https://techsoup.github.io/TechSoup-Product-Bundle/products/
---

# TechSoup Product Bundle

Each product is a markdown file with YAML frontmatter in a category directory
below, following the contract in [../Schema/offer-entry.md](../Schema/offer-entry.md).
See [../README.md](../README.md) for the full picture, and [../examples/](../examples/)
for reference implementations that compile this bundle into a JSON feed and
render it.

## Categories

* [AI](ai/) — 8 products
* [Communications](communications/) — 36 products
* [Fundraising](fundraising/) — 15 products
* [Infrastructure](infrastructure/) — 30 products
* [Operations](operations/) — 54 products
* [Programs](programs/) — 5 products
* [Security](security/) — 11 products

Counts include archived entries; see `x-civic.status` in each entry's
frontmatter.

## Documentation

* [../Schema/](../Schema/) — the offer entry schema and its JSON Schema validator
* [../examples/](../examples/) — reference builds on top of the bundle
* [../CONTRIBUTING.md](../CONTRIBUTING.md) — how to add or update a product entry
