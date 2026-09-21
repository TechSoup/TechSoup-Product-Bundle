#!/usr/bin/env python3
import os
import yaml
import glob
import html

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "index.html")

def build_widget_html(title, description, products):
    """Generates the raw HTML string for a single widget."""
    widget = f"""<!-- TechSoup Embed: {title} -->
<div style="font-family: system-ui, -apple-system, sans-serif; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 100%; padding: 24px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <h3 style="margin-top: 0; color: #0f172a; font-size: 18px;">{title}</h3>
    <p style="color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.5;">
        {description}
    </p>
    <ul style="list-style: none; padding: 0; margin: 0;">
"""
    for p in sorted(products, key=lambda x: x["title"]):
        widget += f"""        <li style="border-bottom: 1px solid #f1f5f9; padding: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <strong style="color: #0f172a; display: block; font-size: 15px;">{p["title"]}</strong>
                    <span style="color: #64748b; font-size: 13px;">{p["category"]} &bull; {p["summary"]}</span>
                </div>
                <a href="{p["url"]}" target="_blank" style="background: #2563eb; color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; white-space: nowrap; transition: background 0.2s;">View Tool</a>
            </div>
        </li>
"""
    widget += f"""    </ul>
    <div style="margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        Powered by the <a href="https://github.com/TechSoup/TechSoup-Product-Bundle" target="_blank" style="color: #2563eb; text-decoration: none;">TechSoup Product Bundle</a>
    </div>
</div>
<!-- End TechSoup Embed -->"""
    return widget

def generate_demo_page():
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
                
                # Check for Open Source
                if "Open Source" in frontmatter_text:
                    os_products.append(prod_data)
                    
                # Check for Security
                if category == "Security":
                    sec_products.append(prod_data)
                    
            except Exception as e:
                pass

    print(f"Found {len(os_products)} Open Source tools and {len(sec_products)} Security tools.")
    
    os_widget_html = build_widget_html(
        "Recommended Open Source Tools", 
        "A curated list of free and open-source technology solutions available to nonprofits.", 
        os_products
    )
    
    sec_widget_html = build_widget_html(
        "Recommended Security Tools", 
        "A curated list of technology donations and discounts to help secure your nonprofit organization.", 
        sec_products
    )

    # Build the overall index.html layout
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechSoup Component Embed Demo</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background-color: #f8fafc;
            color: #334155;
            margin: 0;
            padding: 0;
        }}
        header {{
            background-color: #1e293b;
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        header h1 {{ margin: 0; font-size: 24px; font-weight: 500; }}
        header p {{ color: #cbd5e1; margin-top: 8px; font-size: 15px; }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 40px;
        }}
        @media (min-width: 800px) {{
            .grid {{ grid-template-columns: 1fr 1fr; }}
        }}
        .demo-column {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .demo-column h2 {{ margin-top: 0; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
        .code-block {{
            margin-top: 30px;
            background: #f1f5f9;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
        }}
        .code-block h4 {{ margin: 0 0 10px 0; color: #475569; }}
        textarea {{
            width: 100%;
            height: 150px;
            font-family: monospace;
            font-size: 12px;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background: #fff;
            box-sizing: border-box;
            resize: vertical;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Mock Partner Website</h1>
        <p>This page simulates a local NGO hub incorporating data from the TechSoup Product Bundle.</p>
    </header>
    
    <div class="container">
        <div class="grid">
            <!-- Open Source Demo Column -->
            <div class="demo-column">
                <h2>Live Widget: Open Source</h2>
                <p style="color: #64748b; font-size: 14px; margin-bottom: 24px;">This is exactly how the widget renders when placed directly onto a webpage.</p>
                
                <!-- THE INJECTED WIDGET -->
                {os_widget_html}
                
                <div class="code-block">
                    <h4>Copy this HTML to embed on your site:</h4>
                    <textarea readonly onclick="this.select()">{html.escape(os_widget_html)}</textarea>
                </div>
            </div>

            <!-- Security Demo Column -->
            <div class="demo-column">
                <h2>Live Widget: Security</h2>
                <p style="color: #64748b; font-size: 14px; margin-bottom: 24px;">This is exactly how the widget renders when placed directly onto a webpage.</p>
                
                <!-- THE INJECTED WIDGET -->
                {sec_widget_html}
                
                <div class="code-block">
                    <h4>Copy this HTML to embed on your site:</h4>
                    <textarea readonly onclick="this.select()">{html.escape(sec_widget_html)}</textarea>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(page_html)
        
    print(f"Success! Built interactive demo at: {OUTPUT_FILE}")
    print("Open this file in your web browser to view the widgets.")

if __name__ == "__main__":
    generate_demo_page()
