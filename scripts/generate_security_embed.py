#!/usr/bin/env python3
import os
import yaml
import glob

# Example script: Generates an HTML web component showcasing
# tools specifically in the Security category.

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))

def generate_html_embed():
    print("Parsing OKF data packages for Security tools...\n")
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
                
                # Filter logic: Check if category is Security
                category = x_civic.get("category", "")
                if category != "Security":
                    continue
                    
                title = metadata.get("title", "Unknown Product")
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

    # Generate the web component HTML (styled inline for easy embedding)
    html = """<!-- TechSoup Security Tech Embed -->
<div style="font-family: system-ui, sans-serif; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 600px; padding: 20px; background: #ffffff;">
    <h3 style="margin-top: 0; color: #1e293b;">Recommended Security Tools</h3>
    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">
        A curated list of technology donations and discounts to help secure your nonprofit organization.
    </p>
    <ul style="list-style: none; padding: 0; margin: 0;">
"""
    
    for p in sorted(products, key=lambda x: x["title"]):
        html += f"""        <li style="border-bottom: 1px solid #f1f5f9; padding: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #0f172a; display: block;">{p["title"]}</strong>
                    <span style="color: #64748b; font-size: 12px;">{p["summary"]}</span>
                </div>
                <a href="{p["url"]}" target="_blank" style="background: #2563eb; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: 500;">View Tool</a>
            </div>
        </li>\n"""
        
    html += """    </ul>
    <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px;">
        Powered by the <a href="https://github.com/TechSoup/TechSoup-Product-Bundle" target="_blank" style="color: #2563eb; text-decoration: none;">TechSoup Product Bundle</a>
    </div>
</div>
<!-- End TechSoup Embed -->
"""
    
    output_file = os.path.join(os.path.dirname(__file__), "security_embed.html")
    with open(output_file, "w") as f:
        f.write(html)
        
    print(f"Success! Generated HTML embed at: {output_file}")
    print("You can copy the HTML from this file and paste it directly into your website (e.g., a Custom HTML block in WordPress).")

if __name__ == "__main__":
    generate_html_embed()
