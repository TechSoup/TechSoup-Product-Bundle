import json
import os
import pathlib
import yaml

def compile_catalog(products_root, output_file):
    all_products = []
    
    # Walk through the products directory searching for [slug]_README.md files at the root of product folders
    for readme_path in pathlib.Path(products_root).rglob('*_README.md'):
        # Ensure we are only looking at READMEs that are direct children of a product folder
        # (products/[category]/[product]/[slug]_README.md)
        if len(readme_path.relative_to(products_root).parts) != 3:
            continue

        with open(readme_path, 'r') as f:
            content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---')
                if len(parts) >= 3:
                    yaml_text = parts[1]
                    try:
                        data = yaml.safe_load(yaml_text)
                        if data:
                            all_products.append(data)
                    except yaml.YAMLError as e:
                        print(f"Error parsing YAML in {readme_path}: {e}")
            
    with open(output_file, 'w') as f:
        json.dump(all_products, f, indent=4)
        
    print(f"Aggregated {len(all_products)} products from [slug]_README.md files into {output_file}")

if __name__ == "__main__":
    # Set base paths relative to this script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
    PROJECT_ROOT = os.path.dirname(VKB_CORE_DIR)
    
    products_dir = os.path.join(VKB_CORE_DIR, 'products')
    output_path = os.path.join(PROJECT_ROOT, 'Offer-Center', 'products.json')
    compile_catalog(products_dir, output_path)
