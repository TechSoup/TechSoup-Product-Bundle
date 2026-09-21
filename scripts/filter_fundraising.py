#!/usr/bin/env python3
import os
import yaml
import glob

# Example script: Find all fundraising tools in the product bundle

BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products"))

def find_fundraising_tools():
    print("Searching for Fundraising tools...\n")
    
    md_files = glob.glob(os.path.join(BUNDLE_DIR, "**", "*_README.md"), recursive=True)
    count = 0
    
    for filepath in md_files:
        with open(filepath, "r") as f:
            content = f.read()
            
        if content.startswith("---"):
            frontmatter_text = content.split("---")[1]
            try:
                metadata = yaml.safe_load(frontmatter_text)
                x_civic = metadata.get("x-civic", {})
                category = x_civic.get("category", "").lower()
                sub_category = x_civic.get("sub_category", "").lower()
                
                # Check if category or sub_category contains "fundraising"
                if "fundraising" in category or "fundraising" in sub_category:
                    title = metadata.get("title", "Unknown Product")
                    print(f"- {title}")
                    count += 1
            except Exception as e:
                pass
                
    if count == 0:
        print("No fundraising tools found in the current dataset.")

if __name__ == "__main__":
    find_fundraising_tools()
    print("\nNote: This is a demonstration script. Ensure PyYAML is installed (pip install pyyaml).")
