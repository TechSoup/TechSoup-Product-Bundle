# TechSoup Product Bundle

![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)
![bundle](https://img.shields.io/badge/bundle-v0.7-orange.svg)
![maintained by](https://img.shields.io/badge/maintained_by-TechSoup_Global_Network-blueviolet.svg)

The TechSoup Product Bundle is a collection of Open Knowledge Format (OKF) conformant Markdown documents (Data Packages). These documents describe technology donations and discounts available for nonprofits, regardless of where those discounts are found or who publishes them. 

This repository is a public version of the exact dataset TechSoup uses to power our own tooling, such as the [Offer Center](https://offercenter.techsoup.org/).

## Architecture
This repository is structured as a flexible, open information architecture. By treating knowledge as content (file-first), the **same set of files** can be used to construct many different tools, interfaces, and agents. It acts as a single, portable source of truth that anyone in the sector can build upon without needing to host a complex backend database.

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
   Because these are structured markdown files, they can be directly imported into an LLM context. For example, our `ask-techsoup` skills file allows a user to map this dataset into an LLM, enabling users to query and receive customized tech recommendations.
3. **Create Custom Website Embeds**
   You can parse the data locally to generate targeted HTML widgets for your own website. We have provided reference examples of this in the `examples/` directory.

### Example: Embed Curated Tools on Your Website

We ve provided a reference builder in the `examples/` directory that demonstrates how to filter this dataset and generate deployable HTML web components. 

**How it works:**
1. Navigate to the `examples/` folder in this repository. 
2. You will see a visual preview of what the generated web components look like.
3. Right below the preview, you can copy the raw HTML and paste it directly into your website s CMS (e.g., WordPress Custom HTML).
4. If you want to regenerate the embeds with updated data, simply run `python3 examples/build_examples_readme.py`.

## Contributing
We welcome community involvement! Whether you want to clone this repository to power your own applications, submit a pull request to add new products, or share scripts you ve written, please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide.

## License
This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Public License](LICENSE).
