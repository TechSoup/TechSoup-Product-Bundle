import csv
import os
import sys
from datetime import date

# Set base paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
REGISTRY_PATH = os.path.join(VKB_CORE_DIR, 'registry', 'offers_registry.csv')

def load_existing_leads():
    """Loads existing product names and URLs to prevent duplicates."""
    existing = set()
    if not os.path.exists(REGISTRY_PATH):
        return existing
    with open(REGISTRY_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.add(row['Product Name'].lower().strip())
            if row['Vendor URL']:
                existing.add(row['Vendor URL'].lower().strip().rstrip('/'))
    return existing

def add_leads(new_leads):
    """
    Adds new leads to the offers_registry.csv registry.
    Expects a list of dictionaries with keys matching CSV headers.
    """
    existing = load_existing_leads()
    added_count = 0
    
    file_exists = os.path.exists(REGISTRY_PATH)
    
    with open(REGISTRY_PATH, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['Product Name', 'Vendor URL', 'Probable Domain', 'Org Type', 'Notes', 'Status', 'Last Audited']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        for lead in new_leads:
            name_key = lead['Product Name'].lower().strip()
            url_key = lead['Vendor URL'].lower().strip().rstrip('/') if lead['Vendor URL'] else ""
            
            if name_key not in existing and (not url_key or url_key not in existing):
                lead['Status'] = 'PENDING_INITIALIZATION'
                lead['Last Audited'] = str(date.today())
                writer.writerow(lead)
                existing.add(name_key)
                if url_key: existing.add(url_key)
                added_count += 1
                print(f"Added: {lead['Product Name']}")
            else:
                print(f"Skipped (Duplicate): {lead['Product Name']}")
                
    return added_count

if __name__ == "__main__":
    print("VKB Discovery Interface")
    print("-----------------------")
    print("This script is a landing point for discovery missions.")
    print("To find new products, use a prompt like:")
    print("'Act as the Discovery Agent, search for X, and use discovery_search.py to add them.'")
    
    # This script can also be used as a module by the agent.
    if len(sys.argv) > 1:
        # Example of how an agent might pass data (this is a stub for future CLI expansion)
        pass
