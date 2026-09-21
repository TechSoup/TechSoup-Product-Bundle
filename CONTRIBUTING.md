# Contributing to the TechSoup Product Bundle

First off, thank you for considering contributing to the TechSoup Product Bundle! This repository acts as a single, portable source of truth for nonprofit technology donations and discounts.

## Structural Requirements (OKF Conformant)
To maintain our "Trust Infrastructure", **all product additions must adhere to the Open Knowledge Format directory structure.**
- Each product must reside in its own folder within its category (e.g., `products/security/new_product/`).
- The primary markdown file must be named `[product_name]_README.md` and contain the required YAML frontmatter.

## How Can I Contribute?

### 1. Clone & Build Your Own Apps
You are encouraged to clone this repository and use the OKF-conformant markdown files to power your own applications, portals, or LLM agents. 
- If you build a new tool or integration, **let us know!**
- Feel free to share custom scripts (like those in the `scripts/` directory) that help organizations parse the bundle in creative ways.

### 2. Add New Products
If you know of a technology donation or discount available to nonprofits that isn t listed here:
1. **Fork** the repository.
2. **Create a new product folder** in the appropriate category under the `products/` directory.
3. **Add your `_README.md` file**, ensuring it follows our OKF-conformant YAML frontmatter structure (refer to existing files as templates).
4. **Submit a Pull Request (PR)** with a brief description of the offering.

### 3. Update Existing Products
Product offers, eligibility rules, and vendor URLs change over time. If you spot an inaccuracy:
1. **Fork** the repository.
2. Edit the relevant markdown file.
3. **Submit a Pull Request (PR)** explaining the update.

### 4. Share Custom Scripts
If you ve written a Python, Node.js, or bash script that filters, parses, or transforms this data into something useful, please submit a PR to add it to the `scripts/` directory!

By contributing to this repository, you agree that your contributions will be licensed under its CC BY-SA 4.0 License.
