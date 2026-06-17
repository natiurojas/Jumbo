from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(20000)
    
    # Get full HTML from first gallery item
    item_html = page.evaluate("""() => {
        const items = document.querySelectorAll('[data-af-element="search-result"]');
        const result = [];
        for (let i = 0; i < Math.min(3, items.length); i++) {
            const el = items[i];
            result.push({
                product_id: el.getAttribute('data-af-product-id'),
                html: el.outerHTML.substring(0, 3000),
                inner_items: el.querySelectorAll('a, img, span, div').length
            });
        }
        return result;
    }""")
    
    print("First 3 gallery items:", flush=True)
    for item in item_html:
        print(f"\nProduct ID: {item['product_id']}", flush=True)
        print(f"HTML:\n{item['html']}", flush=True)
        print("---", flush=True)
    
    browser.close()
