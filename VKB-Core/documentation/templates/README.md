# VKB Manual Contribution Templates

This directory contains the templates required to manually add a new product "package" to the Verbose Knowledge Base (VKB).

## How to Manually Add a Product

If you want to add a product without using the automated scripts (or if you are working directly in the GitHub web interface), follow these steps:

### 1. Create the Folder Structure
Navigate to `VKB-Core/products/[category]/` and create a new folder named with the product's "slug" (lowercase, no spaces, e.g., `my_software`).

Inside that folder, create the following structure:
- `agent/` — holds the consultant skill file (used by apps that reason over a product).
- `content/use_cases/` — markdown files, one per **need the product fulfills**.
- `content/case_studies/` — markdown files showing the product **in use by real organizations**.

> **Keep empty folders in git.** `use_cases/` and `case_studies/` often start empty — they hold the *idea* until someone fills them in. Git does not track empty directories, so place an empty **`.gitkeep`** file in each. Without it, the folder silently disappears on clone, which breaks the shared structure other VKB maintainers rely on. Every product must carry the full shape (skill + both content folders) even when the content folders are still stubs.

### 2. Add the Metadata & Knowledge
Copy `product_README_template.md` from this folder into your new product folder.
- **Rename it:** It MUST be named `[slug]_README.md` (e.g., `my_software_README.md`).
- **Fill it out:** Update the YAML frontmatter and the Markdown body with the product details. Keep the `type: offer` line — it's required for Open Knowledge Format conformance.

### 3. Add the Agent Skill
Copy `agent_skill_template.md` into the `agent/` sub-folder.
- **Rename it:** It MUST be named `[slug]_skill.md` (e.g., `my_software_skill.md`).
- **Fill it out:** Customize the persona and add any expert "gotchas."

### 4. Push Your Changes
Once these files are added to the repo, the next time the build pipeline (`python3 VKB-Core/scripts/build_products.py`) is run, your product will appear in the **Offer Center** web view.

---

**Note:** You do not need to download the entire repository to add a product. You can create these folders and files directly in the GitHub UI and commit them to the `VKB-Core` path.
