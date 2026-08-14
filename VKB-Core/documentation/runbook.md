# VKB Operational Runbook

Welcome to the internal Handoff Runbook for the Verbose Knowledge Base (VKB). This document is designed to help you play with, test, and debate the future of this framework.

> **Note:** This documentation was developed iteratively through AI-assisted prompting.

## 1. Quick Start (Get it running locally)

To begin interacting with the system, follow these steps:

1.  **Clone the Repository**
2.  **Environment Setup**
    - Ensure you have Python 3 installed.
    - Install dependencies: `pip install -r requirements.txt` (notably **PyYAML**, used by the build).
    - Ensure you have the `google-genai` CLI configured, as this system uses your personal authenticated session to interface with the AI models.
3.  **Start the Server**
    - Navigate to the `Offer-Center` directory: `cd Offer-Center`
    - Run the local server: `python3 -m http.server 8000`
    - Open `http://localhost:8000` in your browser.

## 2. Operating the Swarm

The VKB is a "Reactive/Human-Triggered" system. It does not run as a background service. Use the following protocol whenever you are working on the system:

1.  **Discovery Search:** Run `python3 VKB-Core/scripts/discovery_search.py` to find new products and add them to the registry.
2.  **Integrity Sweep:** The VKB has three single-purpose linters — run the relevant ones:
    - `validate.py` — **frontmatter** conformance (against `schemas/civic_schema.json`).
    - `lint_structure.py` — **package structure** (folders/skill/`.gitkeep`, against `schemas/structure_spec.json`); add `--fix-all` to scaffold missing pieces, or `--strict` for a hard CI gate.
    - `agent_link_validator.py` — **links & registry** integrity (writes `link_audit_report.md`).
3.  **Build the catalog:** Run `python3 VKB-Core/scripts/build_products.py` to rebuild the SQLite engine and regenerate `Offer-Center/products.json` from the product files. The build reads two registries under `VKB-Core/registry/`: `pcs_registry.json` (Candid PCS vocabulary) and `audiences.json` (eligibility audiences). It expands each offer's `eligible_audiences` keys into resolved `audience_tuples` and carries the audience registry in the feed's `meta` block. *(One-time OKF conformance was applied via `scripts/migrate_to_okf.py`.)* After building, run `python3 VKB-Core/scripts/check_contract.py` to confirm the rebuild still matches the published `products.json` contract (frozen in `tests/golden_products.json`); the same check runs in CI on every push. Then run `python3 VKB-Core/scripts/build_index.py` to regenerate the `index.md` maps of content (bundle root + each category) from the same frontmatter, and commit them alongside `products.json`.
4.  **Check the Log:** Scan `VKB-Core/registry/swarm_activity_log.md` for any recent activity or `[ACTION_REQUIRED]` items.

## 3. The "Human-in-the-Loop" Workflow

The VKB relies on a hybrid approach where AI scaffolds the data and Humans (or Senior Agents) refine the intelligence.

1.  **Discovery:** New products appear in `VKB-Core/registry/offers_registry.csv` with status `PENDING_INITIALIZATION`. You can trigger this manually or via `discovery_search.py`.
2.  **Scaffolding:** Run `python3 VKB-Core/scripts/swarm_initiate.py`. This moves the lead to `INITIALIZED`, creates the **Product Package** (`[slug]_README.md` + stubs), and adds the product to the web catalog.
3.  **Expert Review:** Navigate to the product's root `[slug]_README.md` file. Add specific nuances, "gotchas," or advice in the body.
4.  **Activation:** Add "Expert Knowledge" to the `agent/[product]_skill.md` file and update the CSV status to `ACTIVE`. 

## 4. Manual Contributions (No Scripts Required)

For humans who want to add a product without using the swarms or Python scripts (e.g., directly via the GitHub UI), we provide boilerplate templates:

*   **Templates Directory:** `VKB-Core/documentation/templates/`
*   **Process:** Follow the instructions in the [Templates README](../documentation/templates/README.md) to create the folder structure and naming conventions (`[slug]_README.md`) manually.

> **Why Activate?** An `ACTIVE` status is the signal to the **Program Manager** that this product is ready for "Agentic Consultation." Only active products will be used by the swarm to generate assessments or provide proactive advice.

## 5. Production Hypotheses
 & Open Questions

While this is a functional prototype, we have identified areas that will require technical debate if we move toward a production-grade internal service. **Please consult Michael Enos regarding the following:**

*   **Security & Infrastructure:** The current setup relies on local authentication and simple file serving. Production hosting (e.g., GitHub Pages, S3, or a secure server) will require a formal review of API key management and AuthN/AuthZ.
*   **Scalability:** We have not performed load testing. The current design is optimized for a team of internal "expert users." A high-traffic public deployment would require a different architectural approach to caching and AI token management.
*   **Analytics:** This prototype has no built-in analytics. We need to define the user success metrics before instrumenting the front-end.
*   **Tech Stack Alignment:** While we chose Vanilla JS to minimize build complexity (and React overhead), we should debate whether this should be ported to the standard TechSoup React stack for easier team adoption.
