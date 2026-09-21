#!/usr/bin/env python3
import os
import yaml
import glob

# Example script: Generates an HTML web component showcasing products
# suitable for a small, brand-new nonprofit (budget $0).

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))

def generate_html_embed():
    print("Parsing OKF data packages for $0 minimum budget tools...\n")
    md_files = glob.glob(os.path.join(BUNDLE_DIR, "**", "*_README.md"), recursive=True)
    products = []
    
    for filepath in md_files:
        with open(filepath, "r") as f:
            content = f.read()
            
        if content.startswith("---"):
            frontmatter_text = content.split("---")[1]
            try:
                metadata = yaml.safe_load(frontmatter_text)
                x_civic = metadata.get("x-civic", {})
                eligibility = x_civic.get("eligibility", {})
                
                # Filter logic
                min_budget = eligibility.get("min_budget")
                if min_budget == 0:
                    title = metadata.get("title", "Unknown Product")
                    category = x_civic.get("category", "Uncategorized")
                    summary = x_civic.get("offer", {}).get("summary", "View details")
                    url = x_civic.get("provenance", {}).get("vendor_url", "#")
                    
                    products.append({
                        "title": title,
                        "category": category,
                        "summary": summary,
                        "url": url
                    })
            except Exception as e:
                pass

    # Generate the web component HTML
    html = """<!-- TechSoup Small Nonprofit Tech Embed -->
<div style="font-family: system-ui, sans-serif; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 600px; padding: 20px; background: #ffffff;">
    <h3 style="margin-top: 0; color: #1e293b;">Recommended Tools for Small Nonprofits</h3>
    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
        A curated list of technology donations and discounts with a $0 minimum budget requirement, perfect for getting started.
    </p>
    <ul style="list-style: none; padding: 0; margin: 0;">
"""
    
    for p in sorted(products, key=lambda x: x["title"]):
        html += f"""        <li style="border-bottom: 1px solid #f1f5f9; padding: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #0f172a; display: block;">{p["title"]}</strong>
                    <span style="color: #64748b; font-size: 12px;">{p["category"]} &bull; {p["summary"]}</span>
                </div>
                <a href="{p["url"]}" target="_blank" style="background: #2563eb; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: 500;">View Offer</a>
            </div>
        </li>\n"""
        
    html += """    </ul>
    <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px;">
        Powered by the <a href="https://github.com/TechSoup/TechSoup-Product-Bundle" target="_blank" style="color: #2563eb; text-decoration: none;">TechSoup Product Bundle</a>
    </div>
</div>
<!-- End TechSoup Embed -->
"""
    
    output_file = os.path.join(os.path.dirname(__file__), "small_npo_embed.html")
    with open(output_file, "w") as f:
        f.write(html)
        
    print(f"Success! Generated HTML embed at: {output_file}")
    print("You can open this file in a browser to preview the widget, or copy the HTML into your own website.")

if __name__ == "__main__":
    generate_html_embed()
