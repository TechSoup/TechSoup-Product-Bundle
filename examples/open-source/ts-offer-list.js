/**
 * <ts-offer-list src="products.json" title="..." description="...">
 *
 * A minimal web component that fetches a JSON feed (see build_feed.py in
 * this folder) and renders it as a list. Rendering happens inside a Shadow
 * DOM so these styles never leak into, or clash with, the page it's dropped
 * into -- important if you're pasting this into a CMS you don't control.
 */
class TSOfferList extends HTMLElement {
  async connectedCallback() {
    const src = this.getAttribute("src") || "products.json";
    const title = this.getAttribute("title") || "";
    const description = this.getAttribute("description") || "";

    const shadow = this.attachShadow({ mode: "open" });
    shadow.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, -apple-system, sans-serif; }
        .card { border: 1px solid #e2e8f0; border-radius: 8px; max-width: 100%; padding: 24px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); box-sizing: border-box; }
        h3 { margin-top: 0; color: #0f172a; font-size: 18px; }
        p.desc { color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.5; }
        ul { list-style: none; padding: 0; margin: 0; }
        li { border-bottom: 1px solid #f1f5f9; padding: 12px 0; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
        li:last-child { border-bottom: none; }
        strong { color: #0f172a; display: block; font-size: 15px; }
        span.meta { color: #64748b; font-size: 13px; }
        a.view { background: #2563eb; color: #ffffff; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; white-space: nowrap; }
        .footer { margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px; }
        .footer a { color: #2563eb; text-decoration: none; }
        .error { color: #991b1b; }
      </style>
      <div class="card">
        ${title ? `<h3>${title}</h3>` : ""}
        ${description ? `<p class="desc">${description}</p>` : ""}
        <ul id="list"><li>Loading&hellip;</li></ul>
        <div class="footer">Powered by the <a href="https://github.com/TechSoup/TechSoup-Product-Bundle" target="_blank" rel="noopener">TechSoup Product Bundle</a></div>
      </div>
    `;

    const list = shadow.getElementById("list");
    try {
      const res = await fetch(src);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const products = await res.json();

      if (!products.length) {
        list.innerHTML = `<li>No products found.</li>`;
        return;
      }

      list.innerHTML = products.map((p) => `
        <li>
          <div>
            <strong>${escapeHtml(p.title)}</strong>
            <span class="meta">${escapeHtml(p.category)} &bull; ${escapeHtml(p.summary)}</span>
          </div>
          <a class="view" href="${escapeAttr(p.url)}" target="_blank" rel="noopener">View Tool</a>
        </li>
      `).join("");
    } catch (err) {
      list.innerHTML = `<li class="error">Couldn't load products: ${escapeHtml(String(err))}</li>`;
    }
  }
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

function escapeAttr(str) {
  return escapeHtml(str);
}

customElements.define("ts-offer-list", TSOfferList);
