import os
import shutil
import pathlib

def flatten_products(vkb_core_dir):
    products_dir = os.path.join(vkb_core_dir, 'products')
    
    for product_folder in pathlib.Path(products_dir).glob('*/*'):
        if not product_folder.is_dir():
            continue
            
        print(f"Processing Package: {product_folder.name}")
        
        # 1. Identify source files
        metadata_md = list(product_folder.glob('metadata/*_product.md'))
        content_readme = list(product_folder.glob('content/*_README.md'))
        
        # 2. Extract Data and Knowledge
        frontmatter = ""
        body = f"# {product_folder.name.replace('_', ' ').capitalize()}\n\n"
        
        if metadata_md:
            with open(metadata_md[0], 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---')
                    frontmatter = parts[1]
        
        if content_readme:
            with open(content_readme[0], 'r') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---')
                    body = "---".join(parts[2:]) # Keep everything after frontmatter
                else:
                    body = content
        
        # 3. Create the New [slug]_README.md
        new_readme_content = f"---\n{frontmatter.strip()}\n---\n\n{body.strip()}"
        slug = product_folder.name
        with open(product_folder / f"{slug}_README.md", 'w') as f:
            f.write(new_readme_content)
            
        # 4. Create/Ensure Stubs
        os.makedirs(product_folder / "content" / "use_cases", exist_ok=True)
        os.makedirs(product_folder / "content" / "case_studies", exist_ok=True)
        os.makedirs(product_folder / "agent", exist_ok=True)
        
        # 5. Cleanup
        # Remove metadata folder
        metadata_dir = product_folder / "metadata"
        if metadata_dir.exists():
            shutil.rmtree(metadata_dir)
            
        # Remove the old README in content (but keep the folder for stubs)
        if content_readme:
            os.remove(content_readme[0])
            
    print("\nFlattening complete. All products are now in 'Package' format with [slug]_README.md files.")

if __name__ == "__main__":
    # Set base paths relative to this script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    VKB_CORE_DIR = os.path.dirname(SCRIPT_DIR)
    flatten_products(VKB_CORE_DIR)
