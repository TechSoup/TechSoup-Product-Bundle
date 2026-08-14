# Maintaining the VKB — a Workflow (and why there's no admin UI)

*A possible workflow for the people who tend the knowledge. This is a direction to react to and refine — the point is the **idea** (edit files, in Obsidian), not the exact tool choices. Companion to `V2_HANDOFF.md` and the product spec.*

## The short version

You maintain the VKB by **editing files** — not by using a web app. The product knowledge *is* markdown files. You edit them the way you'd edit notes (ideally in **Obsidian**, which turns the folder into a friendly, navigable workspace), and a one-line build turns those files into what the Offer Center serves.

## Who maintains it

**Gardeners** — vetted people (TechSoup staff and partners) who tend the knowledge. They do **not** need to be developers. They need Obsidian, a couple of plugins, and GitHub Desktop.

## The interface: Obsidian over Git

Open the repo folder as an **Obsidian vault**. Then:

- **Edit a product:** open its `[slug]_README.md`. The YAML frontmatter (price, eligibility, audit date…) appears in Obsidian's **Properties** panel as labeled fields — no raw colons and brackets. The body below it is the expert "what to know" knowledge, written as normal prose.
- **Add a product:** use the template (Templater) — it scaffolds the folder and a ready `[slug]_README.md` (already including `type: offer`). Fill in the fields.
- **Explore:** backlinks and the graph view let you *wander* the knowledge — see what connects to what, find gaps, spot related offers. This is how you find work, not just do it.
- **Dashboards:** Dataview renders live tables **inside Obsidian** — e.g. "everything not audited in 90 days," "all Communications offers," a status board — generated from the files, no separate tool to build or host.

## Publishing (making your edits live)

1. Run `python3 VKB-Core/scripts/build_products.py` — rebuilds the engine and regenerates `products.json`.
2. Run `python3 VKB-Core/scripts/build_index.py` — regenerates the `index.md` maps of content (the bundle root + each category) from the same product frontmatter.
3. **Commit and push** in GitHub Desktop (commit the regenerated `products.json` and `index.md` files along with your file edits).

The push triggers the Azure Static Web Apps deploy, which **uploads `Offer-Center/` exactly as committed** — it does *not* rebuild or regenerate `products.json` (the workflow sets `skip_app_build: true`). So the live catalog is always the one you built and pushed from your desktop.

> **Until go-live, the build stays on the desktop — on purpose.** Do not add a GitHub Action that *builds and commits* `products.json` in CI yet. Building locally and committing `products.json` keeps the deployed Azure file from being regenerated/overwritten by automation while the format is still in flux. (Revisit once we go live.)
>
> The **VKB Contract Guard** action is *not* a violation of this: it rebuilds in a throwaway temp dir purely to verify the published contract is preserved, and it never commits or deploys `products.json`. The build that produces the deployed file still happens only on your desktop.

The Offer Center — and any other tool — picks up the new `products.json` on its next refresh.

## Archiving an offer (when it's no longer valid)

When an offer dies — discontinued, acquired, eligibility changed — **archive it; don't delete it.** Keeping the record means we won't waste time re-adding it, and we can later ask *why* offers were retired and what became of them.

```sh
python3 VKB-Core/scripts/archive.py <slug> \
  --reason "Acquired by GoFundMe; no longer a standalone offer." \
  --disposition acquired            # acquired | discontinued | merged | superseded | eligibility-changed | duplicate
  # --successor <slug>              # optional: the replacement offer, if any
```

This sets the record to `ARCHIVED`, adds an "ARCHIVED" banner above the original content, **moves the folder to `products/<category>/_archive/`**, flips the offer's row in the discovery registry so it's never re-added, and rebuilds `products.json` (the offer drops out). Then commit and push as usual.

> **`_archive/` is intentionally out of the way.** A Gardener browsing in Obsidian — and any bot surfacing the active tree — should skip `_archive/`. Archived records stay on disk for audit and "don't re-add" checks, but they don't clutter the live knowledge or spend AI attention.

## How more than one person works on it

Each maintainer has their own **clone** of the repo (their own Obsidian vault). **Git is the sync layer:** commit your edits, pull others'. It is *not* real-time co-editing like Google Docs — it's propose / commit / pull, which also gives you full history and the ability to undo anything. Two people editing the same file is rare at this scale, and Git handles it.

## What a maintainer needs

- **Obsidian** (free) + plugins: **Properties** (built-in), **Templater**, **Dataview**.
- **GitHub Desktop** for commit/sync.
- For a quick one-off edit without any local setup, you can also edit a file directly in the **GitHub web UI** — fine as a fallback.

## The boundary to hold

- **Obsidian / the files = how the knowledge is *maintained*** (private, by Gardeners).
- **The Offer Center = the public *output*** (what nonprofits see).

Keep these separate. We don't build an interface to *maintain*; we make the public *output* good. Maintenance is editing files.

## Why this, not a custom app

- **No build step, no lock-in** — it's markdown, readable in any editor for decades.
- **Non-developers can contribute** — Properties + templates, not a database schema.
- **Exploration is free** — backlinks and the graph surface connections a form never would.
- **It models the thesis** — files as the source of truth, which is the whole point of the VKB.
- **It federates** — partners clone and sync over Git; there's no central app to build, host, or secure.

---

*Honest limits: Obsidian has a small learning curve for non-technical staff, and it isn't multiplayer (Git is the sync). Both are acceptable trade-offs for keeping the knowledge in open, portable files instead of a bespoke application.*
