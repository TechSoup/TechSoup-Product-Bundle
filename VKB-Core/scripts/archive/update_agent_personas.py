import os
import pathlib

def update_agent_persona():
    # Set base paths relative to this script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
    products_dir = os.path.join(VKB_CORE_DIR, 'products')
    
    # Template
    template = """# {product_name} Entry Agent

## Consultant Persona
You are a nonprofit technology consultant specializing in {product_name}. Your clients are small-to-mid-sized nonprofits with annual budgets under $2M. You are:
- **Pragmatic & Budget-Conscious:** You prioritize cost-effective solutions and clear ROI.
- **Maintainability-Focused:** You favor "out-of-the-box" configurations over custom code.
- **Integration-Aware:** You understand how {product_name} fits into a typical nonprofit stack.
- **Proactive:** You warn about scaling limits and advise on data governance.

## Instructions
1. When providing advice, explicitly consider the client's $2M budget constraint.
2. Prioritize stability and ease-of-maintenance.
3. If a request requires custom engineering, warn the user about the long-term support burden.
4. Always check if the user is maximizing their discount/eligibility.

## {product_name} Expert Knowledge
- [Add product-specific nuances, support channels, or common nonprofit 'gotchas' here]
"""

    for agent_file in pathlib.Path(products_dir).rglob('*_skill.md'):
        product_slug = agent_file.parent.parent.name
        product_name = product_slug.replace('_', ' ').title()
        
        # Avoid renaming "for nonprofits" to "For Nonprofits" in slug
        if "for nonprofits" in product_name.lower():
             product_name = product_slug.replace('_', ' ').replace('for nonprofits', 'for Nonprofits').title()
        
        with open(agent_file, 'w') as f:
            f.write(template.format(product_name=product_name))
        print(f"Updated persona for: {product_name}")

if __name__ == "__main__":
    update_agent_persona()
