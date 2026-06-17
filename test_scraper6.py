from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Set viewport to desktop size
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    print("Page loaded, waiting...", flush=True)
    page.wait_for_timeout(20000)
    
    # Get all content inside render-container
    html = page.evaluate("""() => {
        const rc = document.getElementById('render-container');
        if (!rc) return 'no render-container';
        return rc.innerHTML.substring(0, 10000);
    }""")
    print(f"Render container HTML:\n{html}", flush=True)
    
    # Find all elements with product-related content
    product_elements = page.evaluate("""() => {
        const items = [];
        // Find search result items
        const galleryItems = document.querySelectorAll('[class*="galleryItem"]');
        for (const el of galleryItems) {
            items.push({
                type: 'galleryItem',
                html: el.outerHTML.substring(0, 500),
                classes: el.className.substring(0, 200)
            });
        }
        // If no items, try other selectors
        if (items.length === 0) {
            const allDivs = document.querySelectorAll('#render-container div');
            for (const el of allDivs) {
                const text = el.textContent.trim().substring(0, 100);
                if (text.includes('$') || text.includes('precio') || text.includes('PRECIO')) {
                    items.push({
                        type: 'price-related',
                        classes: el.className.substring(0, 150),
                        text: text.substring(0, 150),
                        outer: el.outerHTML.substring(0, 300)
                    });
                }
            }
        }
        return items.slice(0, 20);
    }""")
    
    print(f"\nProduct elements found: {len(product_elements)}", flush=True)
    for p_el in product_elements[:10]:
        print(f"\n  {json.dumps(p_el, ensure_ascii=False)[:500]}", flush=True)
    
    browser.close()
