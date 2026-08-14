import csv
import os
from datetime import date

# Set base paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)

def get_current_count():
    path = os.path.join(VKB_CORE_DIR, 'registry', 'offers_registry.csv')
    if not os.path.exists(path): return 0
    with open(path, 'r') as f:
        return sum(1 for row in f) - 1

def run_discovery():
    leads_path = os.path.join(VKB_CORE_DIR, 'registry', 'offers_registry.csv')
    
    # Mocking discovery of 5 new leads per run, looping until 100 total leads reached
    target = 100
    current = get_current_count()
    
    if current >= target:
        print("Registry already has 100+ items.")
        return

    new_leads = [
        [f"Discovered Product {i}", "https://example.com", "Infrastructure", "Nonprofit", "Automated Discovery", "PENDING_INITIALIZATION", str(date.today())]
        for i in range(current + 1, current + 6)
    ]
    
    with open(leads_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_leads)
    print(f"Added 5 leads. Total registry count: {current + 5}")

if __name__ == "__main__":
    run_discovery()
