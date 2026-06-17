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
    
    # Find pagination info
    pagination = page.evaluate("""() => {
        const info = {};
        // Total products
        const countEl = document.querySelector('[class*="productCount"]');
        if (countEl) info.productCount = countEl.textContent.trim();
        
        // Pagination
        const paginationEl = document.querySelector('[class*="pagination"], nav[aria-label*="pagin"], [class*="Pagination"]');
        if (paginationEl) {
            info.paginationHTML = paginationEl.outerHTML.substring(0, 3000);
        } else {
            // Look for any navigation with page numbers
            const allNavs = document.querySelectorAll('nav, [class*="page"], [class*="Page"]');
            info.possiblePagination = [];
            for (const nav of allNavs) {
                if (nav.textContent.trim().match(/\\d+/)) {
                    info.possiblePagination.push({
                        html: nav.outerHTML.substring(0, 500),
                        text: nav.textContent.trim().substring(0, 200)
                    });
                }
            }
        }
        
        // Gallery counts
        const items = document.querySelectorAll('[data-af-element="search-result"]');
        info.itemsFound = items.length;
        
        // Next page button
        const nextButtons = document.querySelectorAll('[class*="next"], [aria-label*="siguiente"], [class*="Next"]');
        info.nextButtons = [];
        for (const btn of nextButtons) {
            info.nextButtons.push({
                html: btn.outerHTML.substring(0, 300),
                disabled: btn.hasAttribute('disabled') || btn.getAttribute('aria-disabled')
            });
        }
        
        return info;
    }""")
    
    print("Pagination info:", flush=True)
    print(json.dumps(pagination, ensure_ascii=False, indent=2), flush=True)
    
    browser.close()
