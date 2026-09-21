#!/usr/bin/env python3
import os
import yaml
import glob

# Example script: Find products suitable for a small, brand-new nonprofit
# (budget $0 - $500k, easy to implement)

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))

def find_small_npo_products():
    print("Searching for products suited for small, brand-new nonprofits...\n")
    
    # We look through all _README.md files in the products directory
    md_files = glob.glob(os.path.join(BUNDLE_DIR, "**", "*_README.md"), recursive=True)
    
    for filepath in md_files:
        with open(filepath, "r") as f:
            content = f.read()
            
        # Very simple frontmatter parser for demonstration
        if content.startswith("---"):
            frontmatter_text = content.split("---")[1]
            try:
                metadata = yaml.safe_load(frontmatter_text)
                x_civic = metadata.get("x-civic", {})
                eligibility = x_civic.get("eligibility", {})
                
                # Check for small budget (min_budget == 0)
                min_budget = eligibility.get("min_budget")
                if min_budget == 0:
                    title = metadata.get("title", "Unknown Product")
                    category = x_civic.get("category", "Uncategorized")
                    print(f"- {title} ({category})")
            except Exception as e:
                pass

if __name__ == "__main__":
    find_small_npo_products()
    print("\nNote: This is a demonstration script. Ensure PyYAML is installed (pip install pyyaml).")
