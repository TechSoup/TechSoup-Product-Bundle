#!/usr/bin/env python3
import os
import yaml
import glob

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "README.md")

def build_widget_html(title, description, products):
    """Generates the raw HTML string for the widget"""
    html = f"""<!-- TechSoup Embed: {title} -->
<div style="font-family: system-ui, -apple-system, sans-serif; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 100%; padding: 24px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <h3 style="margin-top: 0; color: #0f172a; font-size: 18px;">{title}</h3>
    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.5;">
        {description}
    </p>
    <ul style="list-style: none; padding: 0; margin: 0;">
"""
    for p in sorted(products, key=lambda x: x["title"]):
        html += f"""        <li style="border-bottom: 1px solid #f1f5f9; padding: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <strong style="color: #0f172a; display: block; font-size: 15px;">{p["title"]}</strong>
                    <span style="color: #64748b; font-size: 13px;">{p["category"]} &bull; {p["summary"]}</span>
                </div>
                <a href="{p["url"]}" target="_blank" style="background: #2563eb; color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; white-space: nowrap; transition: background 0.2s;">View Tool</a>
            </div>
        </li>\n"""
        
    html += f"""    </ul>
    <div style="margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        Powered by the <a href="https://github.com/TechSoup/TechSoup-Product-Bundle" target="_blank" style="color: #2563eb; text-decoration: none;">TechSoup Product Bundle</a>
    </div>
</div>
<!-- End TechSoup Embed -->"""
    return html

def build_markdown_mockup(title, description, products):
    """Generates the Markdown visual preview of the widget"""
    md = f"### {title}\n"
    md += f"_{description}_\n\n"
    md += "---\n\n"
    for p in sorted(products, key=lambda x: x["title"]):
        md += f"**{p[title]}**<br>\n"
        md += f"<sub>{p[category]} &bull; {p[summary]}</sub>\n"
        md += f"<div align=\"right\"><a href=\"{p[url]}\">View Tool</a></div>\n\n"
        md += "---\n\n"
    md += "<div align=\"center\"><sub>Powered by the TechSoup Product Bundle</sub></div>\n\n"
    return md

def generate_examples():
    print("Parsing OKF data packages...")
    md_files = glob.glob(os.path.join(BUNDLE_DIR, "**", "*_README.md"), recursive=True)
    
    os_products = []
    sec_products = []
    
    for filepath in md_files:
        with open(filepath, "r") as f:
            content = f.read()
            
        if content.startswith("---"):
            frontmatter_text = content.split("---")[1]
            try:
                metadata = yaml.safe_load(frontmatter_text)
                x_civic = metadata.get("x-civic", {})
                
                title = metadata.get("title", "Unknown Product")
                category = x_civic.get("category", "Uncategorized")
                summary = x_civic.get("offer", {}).get("summary", "View details")
                url = x_civic.get("provenance", {}).get("vendor_url", "#")
                
                prod_data = {
                    "title": title,
                    "category": category,
                    "summary": summary,
                    "url": url
                }
                
                if "Open Source" in frontmatter_text:
                    os_products.append(prod_data)
                    
                if category == "Security":
                    sec_products.append(prod_data)
                    
            except Exception as e:
                pass
                
    # Compile the final README.md
    final_md = "# Web Component Examples\n\n"
    final_md += "This directory contains reference implementations showing how you can easily parse the TechSoup Product Bundle into targeted web components for your own website.\n\n"
    
    # 1. Open Source Section
    final_md += "## Example 1: Open Source Tools Widget\n\n"
    final_md += "### Visual Preview\n"
    final_md += "> This is a markdown simulation of what the widget looks like on your site:\n\n"
    final_md += build_markdown_mockup("Recommended Open Source Tools", "A curated list of free and open-source technology solutions available to nonprofits.", os_products)
    final_md += "### Embed Code\n"
    final_md += "Copy this HTML snippet into your CMS (e.g., WordPress Custom HTML block):\n"
    final_md += "```html\n"
    final_md += build_widget_html("Recommended Open Source Tools", "A curated list of free and open-source technology solutions available to nonprofits.", os_products)
    final_md += "\n```\n\n"
    
    # 2. Security Section
    final_md += "## Example 2: Security Tools Widget\n\n"
    final_md += "### Visual Preview\n"
    final_md += "> This is a markdown simulation of what the widget looks like on your site:\n\n"
    final_md += build_markdown_mockup("Recommended Security Tools", "A curated list of technology donations and discounts to help secure your nonprofit organization.", sec_products)
    final_md += "### Embed Code\n"
    final_md += "Copy this HTML snippet into your CMS (e.g., WordPress Custom HTML block):\n"
    final_md += "```html\n"
    final_md += build_widget_html("Recommended Security Tools", "A curated list of technology donations and discounts to help secure your nonprofit organization.", sec_products)
    final_md += "\n```\n"

    with open(OUTPUT_FILE, "w") as f:
        f.write(final_md)
        
    print(f"Success! Built interactive markdown preview at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_examples()
