from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Intercept GraphQL responses
    graphql_responses = []
    def handle_response(response):
        url = response.url
        status = response.status
        if 'graphql' in url.lower() and status == 200:
            try:
                body = response.json()
                graphql_responses.append({
                    'url': url[:300],
                    'body_preview': json.dumps(body, ensure_ascii=False)[:500]
                })
            except:
                pass
    
    page.on('response', handle_response)
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    print("Page loaded, waiting for React render...", flush=True)
    page.wait_for_timeout(25000)
    
    print(f"\nGraphQL responses captured: {len(graphql_responses)}", flush=True)
    for i, r in enumerate(graphql_responses[:10]):
        print(f"\n--- Response {i+1} ---", flush=True)
        print(f"URL: {r['url']}", flush=True)
        print(f"Body: {r['body_preview']}", flush=True)
    
    # Check rendered DOM
    print("\n\nChecking rendered content...", flush=True)
    rendered = page.evaluate("""() => {
        // Look for product-related elements
        const selectors = [
            '[class*="gallery"]',
            '[class*="product"]', 
            '[class*="Product"]',
            '[class*="search-result"]',
            '[class*="result"]',
            '[data-testid]',
            'article',
            '[class*="card"]',
            '.vtex-search-result-3-x-gallery'
        ];
        let results = {};
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
                results[sel] = {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className.substring(0, 150),
                    childCount: el.children.length,
                    text: el.textContent.substring(0, 150)
                };
            }
        }
        return results;
    }""")
    
    print(f"Rendered elements found: {len(rendered)}", flush=True)
    for sel, info in rendered.items():
        print(f"  {sel}: {json.dumps(info, ensure_ascii=False)[:200]}", flush=True)
    
    # Also try getting the full HTML body for product patterns
    html_snippet = page.evaluate("""() => document.getElementById('render-container')?.innerHTML?.substring(0, 3000) || 'no render-container'""")
    print(f"\nRender container: {html_snippet[:1000]}", flush=True)
    
    browser.close()
