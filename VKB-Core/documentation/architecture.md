# VKB System Architecture Overview

The Verbose Knowledge Base (VKB) follows a **"Source-of-Truth"** architecture, decoupling data acquisition and intelligence from the end-user presentation.

## High-Level Flow

1.  **VKB-Core (The Engine):**
    *   **Products:** Markdown-based "Intelligent Packages," conformant to the **Open Knowledge Format (OKF)** — each `[slug]_README.md` declares a `type`, the folder/slug path is its identity, and the bundle declares `okf_version` in `VKB-Core/index.md`. YAML frontmatter holds the data; the Markdown body holds the expert knowledge; `agent/` and `content/` hold skills and stubs.
    *   **Registry:** The audit trail of discovery leads, flags, and system activity logs.
2.  **Build Pipeline (`scripts/build_products.py`):**
    *   Parses the root `[slug]_README.md` files (Open Knowledge Format — each declares a `type`).
    *   Loads them into a **SQLite** engine (`vkb.db`) — a queryable layer for tools like the recommender — then **emits a single `products.json`**. SQLite is the disposable build/query engine, rebuilt from the files each run; `products.json` stays the published contract.
    *   A sibling, **`scripts/build_index.py`**, regenerates the OKF `index.md` maps of content (bundle root + one per category) from the same frontmatter — the progressive-disclosure layer (OKF §6), generated like `products.json`, not hand-written.
3.  **Headless API:**
    *   The `products.json` acts as a "Headless API," allowing the `Offer-Center` and third-party tools (like the Cost Optimizer) to consume live data via `fetch`.
4.  **Offer-Center (The View):**
    *   A static web interface that fetches the `products.json` file.
    *   Uses Vanilla JS to perform client-side filtering, searching, and "Mission-Match" UI injection.

## Product Lifecycle & Status Definitions

To support the "Frugal AI" and "Progressive Disclosure" principles, every product in the VKB follows a tiered lifecycle:

1.  **PENDING_INITIALIZATION:** A discovery lead that has been added to the registry but has no physical folder or files yet.
2.  **INITIALIZED (Web-Ready):** 
    *   **The Package:** The folder structure, root `[slug]_README.md` (with Unified Schema v3), and stubs exist.
    *   **User Impact:** The product is visible in the **Offer-Center** (Web Catalog) and searchable by humans.
    *   **Agent Status:** The Entry Agent contains only a generic template; it cannot yet give specific expert advice.
3.  **ACTIVE (Agent-Ready):**
    *   **The Intelligence:** A human expert has populated the `[slug]_README.md` body and the `agent/[product]_skill.md` with "Expert Knowledge."
    *   **Agent Status:** The Entry Agent is now "Activated" and can be used for agentic consultation.

## Design Principles
*   **Frugal AI:** LLM usage is reserved for agentic tasks (discovery, synthesis, link validation) rather than runtime generation.
*   **Maintainable Data:** Data is kept in human-editable formats (Markdown/JSON).
*   **Human-in-the-Loop:** All automated findings (e.g., broken links or new product leads) are routed to a human-readable log (`swarm_activity_log.md`) for verification.
