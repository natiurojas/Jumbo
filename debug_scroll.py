from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(15000)
    
    # Check for show-more button or infinite scroll
    load_mechanism = page.evaluate("""() => {
        // Look for show more / load more buttons
        const buttons = document.querySelectorAll('button, a, [role="button"]');
        const loadMore = [];
        for (const btn of buttons) {
            const text = btn.textContent.trim().toLowerCase();
            if (text.includes('más') || text.includes('mostrar') || text.includes('cargar') || text.includes('ver más') || text.includes('show more')) {
                loadMore.push({
                    text: btn.textContent.trim().substring(0, 100),
                    classes: btn.className.substring(0, 100),
                    visible: btn.offsetParent !== null
                });
            }
        }
        
        // Check for fetchMore dropdown
        const dropdown = document.querySelector('[class*="fetchMoreDropdown"]');
        const fetchMoreInfo = dropdown ? {
            text: dropdown.textContent.trim().substring(0, 200),
            html: dropdown.outerHTML.substring(0, 500)
        } : null;
        
        // Check items count before and what's visible
        const galleryItems = document.querySelectorAll('[data-af-element="search-result"]');
        const allProductDivs = document.querySelectorAll('[class*="galleryItem"]');
        
        return {
            loadMoreButtons: loadMore,
            fetchMoreDropdown: fetchMoreInfo,
            galleryItemsCount: galleryItems.length,
            allProductDivs: allProductDivs.length,
            bodyHeight: document.body.scrollHeight,
            windowHeight: window.innerHeight
        };
    }""")
    
    print(f"Load mechanism:", flush=True)
    import json
    print(json.dumps(load_mechanism, ensure_ascii=False, indent=2)[:2000], flush=True)
    
    # Try clicking a "show more" if it exists
    if load_mechanism.get('loadMoreButtons'):
        for btn in load_mechanism['loadMoreButtons']:
            if btn['visible']:
                print(f"\nClicking: {btn['text']}", flush=True)
                break
    
    # Scroll down gradually
    print("\nScrolling to load more products...", flush=True)
    for i in range(5):
        page.evaluate(f"window.scrollTo(0, {i * 1000})")
        page.wait_for_timeout(2000)
        
        count = page.evaluate("""() => {
            return document.querySelectorAll('[data-af-element="search-result"]').length;
        }""")
        print(f"  Scroll {i+1}: {count} items visible", flush=True)
        
        if count >= 20:
            print("  All items loaded!", flush=True)
            break
    
    browser.close()
