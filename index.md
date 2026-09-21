---
type: index
okf_version: "0.1"
title: VKB-Core — TechSoup Product Intelligence
description: The Verbose Knowledge Base core — nonprofit technology product intelligence as an Open Knowledge Format (OKF) bundle.
x-civic:
  profile: civic/0.5
  maintainer: TechSoup
  namespace: techsoup
  base_uri: https://vkb.techsoup.org/
---

# VKB-Core

exp: each product is a markdown file with YAML frontmatter, compiled by `scripts/build_products.py` into the `products.json` headless API that the Offer Center and other tools consume. Build and conformance details live in [documentation/](documentation/).

## Categories

* [AI](products/ai/index.md) — 5 products
* [Communications](products/communications/index.md) — 34 products
* [Fundraising](products/fundraising/index.md) — 12 products
* [Infrastructure](products/infrastructure/index.md) — 26 products
* [Operations](products/operations/index.md) — 44 products
* [Programs](products/programs/index.md) — 5 products
* [Security](products/security/index.md) — 9 products

## Documentation & registries

* [documentation/](documentation/) — architecture, schema, conformance, maintainer workflow
* [registry/](registry/) — audiences, PCS vocabulary, peers, capabilities
