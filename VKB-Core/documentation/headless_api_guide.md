# Developer Guide: Using the VKB as a Headless API

The Verbose Knowledge Base (VKB) is designed to be a "Headless" data source. This means any tool can "tune in" to the live product catalog to power its own features, ensuring everything stays in sync with the VKB-Core.

## 1. The API Endpoint
The VKB build pipeline (`scripts/build_products.py`) loads the OKF source files into a SQLite engine and emits a single `products.json`. You can access the live feed here:

**Endpoint:** `https://vbk-ffb9cph3h5cudacs.a01.azurefd.net/products.json`
*(Note: Requires TechSoup VPN for access during the private beta.)*

## 2. Integration Pattern: "Fetch & Enrich"
To build a tool using this data, we recommend the "Fetch & Enrich" pattern. This allows you to use the VKB for identity/eligibility while keeping your tool-specific logic in your own code.

### Sample Implementation (JavaScript)

```javascript
/**
 * Simple data loader for a VKB-powered tool
 */
async function loadVKBData() {
    const URL = 'https://vbk-ffb9cph3h5cudacs.a01.azurefd.net/products.json';
    
    try {
        const response = await fetch(URL);
        const products = await response.json();
        
        console.log(`Successfully loaded ${products.length} products from VKB.`);
        
        // Use the product_name to find what you need
        const zoom = products.find(p => p.product_name === "Zoom");
        console.log(`The Zoom offer is: ${zoom.cost}`);
        
        return products;
    } catch (error) {
        console.error("Failed to load VKB Headless API", error);
        // Fallback to local data if needed
    }
}
```

## 3. Why Use the Headless API?
*   **Automatic Updates:** When the VKB-Core updates a price or an eligibility rule, your tool updates automatically on the next refresh.
*   **Single Source of Truth:** No more discrepancies between the "Offer Center" and your "Cost Optimizer."
*   **AI-Ready:** The JSON structure is highly predictable, making it easy for LLMs/Agents to parse and reason about.

## 4. Schema Reference
For a full list of available fields (like `savings_estimate`, `min_budget`, etc.), please refer to the [VKB Schema Documentation](./schema.md).
