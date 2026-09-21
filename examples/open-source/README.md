# Example: Open Source Tools widget

This is one way to build on the TechSoup Product Bundle: read the OKF
markdown files, compile a small JSON feed, and render it with a plain web
component. Nothing here is specific to "open source" — the [`security`](../security)
example does the same thing with a different filter, over the same source data.

## Files

- **`build_feed.py`** — walks `../../products/**/*_README.md`, keeps `ACTIVE`
  entries whose `x-civic.offer.badges` include `Open Source`, and writes `products.json`.
- **`products.json`** — the generated feed. Checked in so the demo works
  without running Python first; regenerate it after editing the bundle.
- **`ts-offer-list.js`** — a `<ts-offer-list>` custom element. It fetches the
  JSON feed named in its `src` attribute and renders it inside a Shadow DOM,
  so its styles can't collide with whatever page it's dropped into.
- **`index.html`** — the whole demo: one `<script>` tag and one
  `<ts-offer-list>` element.

## Running it

```
python3 build_feed.py    # regenerate products.json from the current bundle
python3 -m http.server   # serve this folder — fetch() needs http(s), not file://
```

Then open `http://localhost:8000/index.html`.

## Adapting this

- `pip install pyyaml` if `build_feed.py` can't find the `yaml` module.
- To change what shows up, edit the filter in `build_feed.py` — anything in
  the [offer entry schema](../../Schema/offer-entry.md) is fair game
  (category, sub-category, eligible audiences, badges, and so on).
- To embed this on a real site, `products.json` and `ts-offer-list.js` need
  to be reachable over http(s) from wherever the page lives — GitHub Pages,
  your own CMS, anywhere you can host two static files. Point the `src`
  attribute at that URL.
