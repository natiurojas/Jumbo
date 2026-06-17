from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Broader response capture
    api_responses = []
    def handle_response(response):
        url = response.url
        status = response.status
        if status == 200 and ('search' in url.lower() or 'product' in url.lower() or 'graphql' in url.lower()):
            try:
                body = response.text()
                if len(body) > 500 and len(body) < 500000:
                    api_responses.append({
                        'url': url[:250],
                        'size': len(body),
                        'body': body[:800]
                    })
            except:
                pass
    
    page.on('response', handle_response)
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    print("Page loaded, waiting...", flush=True)
    page.wait_for_timeout(30000)
    
    print(f"API responses captured: {len(api_responses)}", flush=True)
    for i, r in enumerate(api_responses[:20]):
        print(f"\n--- Response {i+1} ---", flush=True)
        print(f"URL: {r['url']}", flush=True)
        print(f"Size: {r['size']}", flush=True)
        print(f"Body: {r['body']}", flush=True)
    
    # Get page state info
    state_info = page.evaluate("""() => {
        const info = {
            url: window.location.href,
            title: document.title,
            bodyClasses: document.body.className.substring(0, 300),
        };
        const rc = document.getElementById('render-container');
        if (rc) {
            info.renderContainerHTML = rc.innerHTML.substring(0, 2000);
            info.renderContainerChildren = rc.children.length;
        }
        // Check for rendered products
        const gallery = document.querySelector('.vtex-search-result-3-x-gallery');
        if (gallery) {
            info.galleryItems = gallery.children.length;
            info.galleryHTML = gallery.innerHTML.substring(0, 3000);
        } else {
            info.gallery = 'not found';
        }
        // Look for any product items
        const allItems = document.querySelectorAll('[class*="galleryItem"], [class*="product"], article, [class*="ProductList"]');
        info.productElements = allItems.length;
        const samples = [];
        for (let i = 0; i < Math.min(3, allItems.length); i++) {
            samples.push({
                tag: allItems[i].tagName,
                classes: allItems[i].className.substring(0, 200),
                text: allItems[i].textContent.replace(/\\s+/g, ' ').substring(0, 200)
            });
        }
        info.samples = samples;
        return info;
    }""")
    
    print(f"\n\nPage state:", flush=True)
    print(json.dumps(state_info, ensure_ascii=False, indent=2)[:3000], flush=True)
    
    browser.close()
