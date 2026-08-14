import os
import re
import json

# Set base paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(VKB_CORE_DIR)

products_dir = os.path.join(VKB_CORE_DIR, 'products')
output_file = os.path.join(PROJECT_ROOT, 'Offer-Center', 'products.json')

def parse_frontmatter(content):
    meta = {}
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        for line in yaml_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                val = v.strip().strip('\"').strip('\'')
                if val.lower() == 'null':
                    meta[k.strip()] = None
                elif val.startswith('[') and val.endswith(']'):
                    # Basic list parsing
                    items = [i.strip().strip('\"').strip('\'') for i in val[1:-1].split(',')]
                    meta[k.strip()] = items
                else:
                    meta[k.strip()] = val
    return meta

products = []

for root, dirs, files in os.walk(products_dir):
    for file in files:
        if file.endswith('.md'):
            with open(os.path.join(root, file), 'r') as f:
                content = f.read()
            
            meta = parse_frontmatter(content)
            if meta:
                meta['id'] = file.replace('.md', '')
                products.append(meta)

with open(output_file, 'w') as f:
    json.dump(products, f, indent=2)

print(f"Compiled {len(products)} products to {output_file}")
