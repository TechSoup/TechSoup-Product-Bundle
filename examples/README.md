# Examples

Reference implementations showing how to build on the TechSoup Product
Bundle. Each one is self-contained — its own build script, its own generated
JSON feed, its own copy of a small web component — so you can grab a single
folder and have everything you need.

The pattern is the same across all of them: **parse the OKF markdown →
compile a JSON feed → drive your own UI with it.** The web component here is
just one illustrative UI; the JSON feed is the part that actually matters,
and there's nothing stopping you from feeding it into something else
entirely (a static site generator, a chatbot, a spreadsheet).

## [`open-source/`](open-source) — Open Source Tools widget

Filters the bundle to `ACTIVE` entries badged `Open Source`.

## [`security/`](security) — Security Tools widget

Filters the bundle to `ACTIVE` entries in the `Security` category.

## More to come

These two exist to show the shape of the pattern, not to be the last word on
it — more examples (different filters, different output formats entirely)
are expected to land here over time. If you build something on top of the
bundle, a PR adding it here is welcome; see [CONTRIBUTING.md](../CONTRIBUTING.md).
