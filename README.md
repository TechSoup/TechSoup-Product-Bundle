# TechSoup Product Bundle

![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)
![bundle](https://img.shields.io/badge/bundle-v0.7-orange.svg)
![maintained by](https://img.shields.io/badge/maintained_by-TechSoup_Global_Network-blueviolet.svg)

The TechSoup Product Bundle is a collection of Open Knowledge Format (OKF) conformant Markdown documents (Data Packages). These documents describe technology donations and discounts available for nonprofits, regardless of where those discounts are found or who publishes them.

This repository is a public version of the exact dataset TechSoup uses to power our own tooling, such as the [Offer Center](https://offercenter.techsoup.org/). The entries are researched and audited in TechSoup's internal Verbose Knowledge Base (VKB) and mirrored into `products/` automatically, so this copy stays current as offers change.

## Architecture
This repository is structured as a flexible, open information architecture. By treating knowledge as content (file-first), the **same set of files** can be used to construct many different tools, interfaces, and agents. It acts as a single, portable source of truth that anyone in the sector can build upon without needing to host a complex backend database.

### What's in the repository

| Path | Contents |
|---|---|
| [`products/`](products/) | One folder per product, grouped by category. Each holds a `<product>_README.md` entry: YAML frontmatter with the structured data, followed by prose in three levels of detail. |
| [`Schema/`](Schema/) | The [offer entry schema](Schema/offer-entry.md) describing every field, and a [JSON Schema](Schema/offer.schema.json) for validating parsed frontmatter. |
| [`examples/`](examples/) | Reference implementations that compile the bundle into a JSON feed and render it on a web page. |

Some product folders also contain empty `content/case_studies/` and `content/use_cases/` directories. These are intentional placeholders for material planned in the roadmap below; they have no content yet.

## Future Roadmap
We are actively building out this product bundle to contain deeper, richer metadata about each product, including:
- **Technical Expertise Required:** How much IT experience you need to implement the solution.
- **Target Audience:** Who the product is best suited for.
- **Community Support:** Where to find communities and peers to help you with implementation.

## Ways You Can Use These Files

This repository is designed to be highly portable so you can weave this data into your own applications. Here are a few examples:

1. **Build a Web Application**
   Like the Offer Center, you can parse these files into a single JSON object to drive an entire interactive portal.
2. **Import into LLMs**
   Because these are structured markdown files, they can be directly imported into an LLM context. For example, our [`ask-techsoup`](https://github.com/TechSoup/ask-techsoup) skill lets an AI assistant answer questions about this bundle, so users can query it and receive customized tech recommendations.
3. **Create Custom Website Embeds**
   You can parse the data locally to generate targeted HTML widgets for your own website. We have provided reference examples of this in the [`examples/`](examples/) directory.

### Example: Build a Widget From the Bundle

The `examples/` directory contains reference implementations of the
"filter this dataset, drive your own UI" pattern: a Python script compiles a
filtered slice of the bundle into a JSON feed, and a small web component
renders that feed wherever you drop it.

**How it works:**
1. Navigate to [`examples/open-source/`](examples/open-source/) or [`examples/security/`](examples/security/) in this repository.
2. Each folder is self-contained: a build script, its generated `products.json`, a `<ts-offer-list>` web component, and a demo `index.html`. Run the folder's own `README.md` instructions to see it live.
3. To regenerate a feed with updated data, run that folder's `build_feed.py`.
4. To adapt the pattern for your own site, host `products.json` and `ts-offer-list.js` anywhere reachable over http(s) and point the component's `src` attribute at it.

## Built with the bundle

- **[Offer Center](https://offercenter.techsoup.org/)** — TechSoup's interactive catalog of nonprofit technology offers.
- **[ask-techsoup](https://github.com/TechSoup/ask-techsoup)** — a skill that lets an AI assistant answer questions about the catalog.

Built something too? [Tell us about it](https://github.com/TechSoup/TechSoup-Product-Bundle/issues/new?template=share-what-you-built.yml) and we'll add it here.

## Contributing
We welcome community involvement! Whether you want to report an out-of-date offer, suggest a product we're missing, or share something you've built on top of the bundle, please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide. Because `products/` is mirrored automatically, changes to product entries go through issues rather than pull requests.

## License
The data and documentation in this repository are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Public License](LICENSE). The example code in [`examples/`](examples/) is licensed under the [MIT License](examples/LICENSE); the JSON feeds it generates are derived from the bundle and remain under CC BY-SA 4.0.
