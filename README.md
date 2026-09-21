# TechSoup Product Bundle

![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)
![bundle](https://img.shields.io/badge/bundle-v0.7-orange.svg)
![maintained by](https://img.shields.io/badge/maintained_by-TechSoup_Global_Network-blueviolet.svg)

The TechSoup Product Bundle is a collection of Open Knowledge Format (OKF) conformant Markdown documents (Data Packages). These documents describe technology donations and discounts available for nonprofits, regardless of where those discounts are found or who publishes them. 

This repository is a public version of the exact dataset TechSoup uses to power our own tooling, such as the [Offer Center](https://offercenter.techsoup.org/).

## Architecture
This repository is structured as a flexible, open information architecture. By treating configuration and knowledge as content (file-first), the **same set of files** can be used to construct many different tools, interfaces, and AI agents. It acts as a single, portable source of truth that anyone in the sector can build upon without needing to host a complex backend database.

## Future Roadmap
We are actively building out this product bundle to contain deeper, richer metadata about each product, including:
- **Technical Expertise Required:** How much IT experience you need to implement the solution.
- **Target Audience:** Who the product is best suited for.
- **Community Support:** Where to find communities and peers to help you with implementation.

## Ways You Can Use These Files

This repository is designed to be highly portable so you can weave this data into your own applications. Here are a few examples:

1. **Build a Web Application**
   Like the Offer Center, you can parse these files into a single JSON object to drive an entire interactive portal.
2. **Train AI & LLM Agents**
   Because these are structured markdown files, they can be directly imported into an LLM context (like our `ask-techsoup` agent) to allow users to query and receive customized tech recommendations.
3. **Create Custom Website Embeds**
   You can parse the data to generate targeted widgets for your own website. We have provided an example of this below.

### Example: Embed Tools for Small Nonprofits on Your Website

We ve provided a reference script in the `scripts/` directory that demonstrates how you can filter this data to generate a deployable HTML web component. 

- `scripts/generate_small_npo_embed.py`: This script parses the bundle for products suitable for brand-new, small nonprofits (minimum budget of $0) and outputs a ready-to-use HTML snippet you can drop onto any webpage, complete with TechSoup credits.

## Contributing
We welcome community involvement! Whether you want to clone this repository to power your own applications, submit a pull request to add new products, or share scripts you ve written, please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide.

## License
This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Public License](LICENSE).
