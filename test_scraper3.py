from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Intercept responses
    responses = []
    def handle_response(response):
        url = response.url
        if any(x in url for x in ['graphql', 'api', 'product', 'search']):
            try:
                body = response.text()
                if len(body) > 100 and len(body) < 500000:
                    responses.append({'url': url[:200], 'size': len(body), 'preview': body[:300]})
            except:
                pass
    
    page.on('response', handle_response)
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(20000)
    
    print(f"Captured {len(responses)} responses", flush=True)
    for r in responses[:20]:
        print(f"\nURL: {r['url']}", flush=True)
        print(f"Size: {r['size']}", flush=True)
        print(f"Preview: {r['preview']}", flush=True)
    
    # Also check what's in the DOM for products
    products = page.evaluate("""() => {
        const items = document.querySelectorAll('[class*="product"], [class*="Product"], [data-product]');
        return Array.from(items).slice(0, 3).map(el => ({
            tag: el.tagName,
            id: el.id,
            classes: el.className.substring(0, 200),
            text: el.textContent.substring(0, 200)
        }));
    }""")
    print(f"\n\nDOM products found: {len(products)}", flush=True)
    for p in products:
        print(f"  {json.dumps(p, ensure_ascii=False)[:300]}", flush=True)
    
    # Check page content for product-like patterns
    body_text = page.evaluate("""() => document.body.innerText""")
    if 'promocion' in body_text.lower() or 'producto' in body_text.lower():
        idx = body_text.lower().find('promocion' if 'promocion' in body_text.lower() else 'producto')
        print(f"\nBody text sample around keyword: {body_text[max(0,idx-100):idx+200]}", flush=True)
    
    browser.close()
