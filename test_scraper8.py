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
    
    # Get complete HTML including prices
    items = page.evaluate("""() => {
        const items = document.querySelectorAll('[data-af-element="search-result"]');
        const result = [];
        for (let i = 0; i < 5; i++) {
            const el = items[i];
            if (!el) break;
            result.push(el.outerHTML);
        }
        return result;
    }""")
    
    print(f"Full HTML for 5 items:\n", flush=True)
    for i, html in enumerate(items):
        print(f"\n=== ITEM {i+1} ===", flush=True)
        print(html, flush=True)
    
    browser.close()
