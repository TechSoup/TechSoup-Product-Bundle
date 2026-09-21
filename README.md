# TechSoup Product Bundle

![TechSoup Open Source](https://img.shields.io/badge/TechSoup-Open%20Source-blue)
![License](https://img.shields.io/badge/License-MIT-green)

The TechSoup Product Bundle is a collection of OKF (Open Knowledge Foundation) conformant Markdown documents (Data Packages). These documents describe technology donations and discounts available for nonprofits, regardless of where those discounts are found or who publishes them. 

This repository acts as a single, portable source of truth. The structured data within these Markdown files can easily be parsed into JSON or other formats to feed downstream applications, HTML interfaces, and LLM integrations.

## Architecture
This repository maintains 1:1 structural parity with the TechSoup VKB (Verbose Knowledge Base). Each product is wrapped in its own folder to securely bundle its schemas, metadata, and skill files together in accordance with Open Knowledge Format principles.

## Future Roadmap
We are actively building out this product bundle to contain deeper, richer metadata about each product, including:
- **Technical Expertise Required:** How much IT experience you need to implement the solution.
- **Target Audience:** Who the product is best suited for.
- **Community Support:** Where to find communities and peers to help you with implementation.

## Examples of Usage

This repository is designed to be highly portable and meshed with other tools. Here are two examples of how this data is currently being used:

1. **[Offer Center](https://offercenter.techsoup.org/)**
   A centralized HTML window/application powered by a JSON file built dynamically from a subset of this product bundle.
2. **`ask-techsoup` (LLM Integration)**
   An LLM skills file and agent that imports the JSON representation of this bundle into an AI context, allowing users to query and receive customized recommendations based on their needs.

## Exploring the Data

Weve provided simple Python scripts in the `scripts/` directory to demonstrate how you can parse and filter this data locally without needing a heavy backend.

- `scripts/filter_small_nonprofit.py`: Extracts products best suited for a brand-new, small nonprofit organization.
- `scripts/filter_fundraising.py`: Pulls out specifically categorized fundraising tools.

## Contributing

We welcome community involvement! Whether you want to clone this repository to power your own applications, submit a pull request to add new products, or share scripts youve written, please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
