import os
import re

# Set base paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
products_dir = os.path.join(VKB_CORE_DIR, 'products')

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if already updated
    if 'max_budget' in content:
        return

    # Add max_budget and eligible_countries
    budget_line = 'max_budget: null'
    
    # Intuit has a 10M limit
    if 'intuit' in filepath.lower() or 'quickbooks' in filepath.lower():
        budget_line = 'max_budget: 10000000'

    new_yaml = f"cost: \\1\n{budget_line}\neligible_countries: [\"ALL\"]"
    
    # Replace cost line to inject the new fields right after it
    updated_content = re.sub(r'cost: (.*)', new_yaml, content)

    with open(filepath, 'w') as f:
        f.write(updated_content)

for root, dirs, files in os.walk(products_dir):
    for file in files:
        if file.endswith('.md'):
            update_file(os.path.join(root, file))
