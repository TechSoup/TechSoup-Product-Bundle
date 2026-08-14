"""
swarm_initiate.py — scaffold PENDING_INITIALIZATION leads into product packages.

For each lead in offers_registry.csv with Status == PENDING_INITIALIZATION, this
creates the package folder structure and a civic/0.5-conformant `[slug]_README.md`
stub (nested `x-civic` frontmatter), then flips the lead to INITIALIZED.

The emitted frontmatter conforms to schemas/civic_schema.json (type: offer +
x-civic block). A freshly scaffolded record is INITIALIZED (web-ready, visible in
the Offer Center) with a `Discovery` offer placeholder; a human later fills in the
real offer/eligibility and sets it ACTIVE.
"""
import csv
import os
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)

PROFILE = "civic/0.5"


def build_record(product_name, category, vendor_url):
    """Return a civic/0.5-conformant frontmatter dict for a freshly discovered offer.

    Conforms to schemas/civic_schema.json: core `type`/`title` plus the nested
    x-civic block (profile, status, category, offer, eligibility, provenance).
    Placeholder values (Discovery offer, nonprofit audience, TBD summary) are
    meant to be replaced by a human during Expert Review.
    """
    return {
        "type": "offer",
        "title": product_name,
        "x-civic": {
            "profile": PROFILE,
            "status": "INITIALIZED",
            "category": category,
            "sub_category": "General",
            "offer": {
                "type": "Discovery",
                "summary": "TBD",
                "standard_tier": None,
                "savings_estimate": None,
                "badges": ["Discovery"],
            },
            "eligibility": {
                "eligible_audiences": ["nonprofit"],
                "regions": ["ALL"],
                "pcs_subject": ["ALL"],
                "rules": None,
                "min_budget": 0,
                "max_budget": None,
            },
            "provenance": {
                "source": "VKB discovery (swarm_initiate)",
                "vendor_url": vendor_url,
                "last_audited": None,
            },
        },
    }


def initiate():
    leads_path = os.path.join(VKB_CORE_DIR, 'registry', 'offers_registry.csv')
    products_dir = os.path.join(VKB_CORE_DIR, 'products')

    with open(leads_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    updated_rows = []
    for row in rows:
        if row['Status'] == 'PENDING_INITIALIZATION':
            product_name = row['Product Name']
            product_slug = product_name.lower().replace(' ', '_').replace('/', '_')
            cat = row['Probable Domain'].lower()
            target_dir = os.path.join(products_dir, cat, product_slug)

            if not os.path.exists(target_dir):
                print(f"Initializing {product_name} in {cat} (Package Mode)...")

                # Create package folder structure
                os.makedirs(os.path.join(target_dir, "content", "use_cases"), exist_ok=True)
                os.makedirs(os.path.join(target_dir, "content", "case_studies"), exist_ok=True)
                os.makedirs(os.path.join(target_dir, "agent"), exist_ok=True)

                # 1. Root README with civic/0.5 frontmatter
                product_data = build_record(product_name, cat.capitalize(), row['Vendor URL'])
                yaml_content = yaml.dump(product_data, sort_keys=False, default_flow_style=False)
                readme_content = (
                    f"---\n{yaml_content}---\n\n# {product_name}\n\n"
                    f"## Overview\nInitial entry for {product_name} discovered via automation."
                )
                with open(os.path.join(target_dir, f"{product_slug}_README.md"), 'w') as f:
                    f.write(readme_content)

                # 2. Agent skill stub
                with open(os.path.join(target_dir, "agent", f"{product_slug}_skill.md"), 'w') as f:
                    f.write(f"# {product_name} Agent Skill\n\nResponsible for maintaining knowledge about {product_name}.")

                row['Status'] = 'INITIALIZED'
        updated_rows.append(row)

    # Rewrite CSV
    with open(leads_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print("Batch initialization complete.")


if __name__ == "__main__":
    initiate()
