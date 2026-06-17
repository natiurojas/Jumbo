from playwright.sync_api import sync_playwright
import json, re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    # Capture ALL network requests
    all_responses = []
    def handle_response(response):
        url = response.url
        content_type = response.headers.get('content-type', '')
        if 'json' in content_type or 'javascript' in content_type:
            try:
                body = response.text()
                all_responses.append({
                    'url': url[:300],
                    'content_type': content_type,
                    'size': len(body),
                    'body': body[:1000]
                })
            except:
                pass
    
    page.on('response', handle_response)
    
    page.goto('https://www.jumbo.com.ar/sucursales', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(30000)
    
    # Find API-like calls
    print("Checking all responses...", flush=True)
    api_calls = [r for r in all_responses if any(x in r['url'].lower() for x in 
                 ['api', 'graphql', 'rest', 'logistics', 'sucursal', 'store', 'pickup',
                  'location', 'address', 'checkout', 'geo'])]
    
    print(f"Relevant responses: {len(api_calls)}", flush=True)
    for r in api_calls[:20]:
        print(f"\nURL: {r['url']}", flush=True)
        print(f"Type: {r['content_type']}", flush=True)
        print(f"Body: {r['body'][:500]}", flush=True)
    
    # Also check for the store locator component data
    store_script = page.evaluate("""() => {
        const scripts = document.querySelectorAll('script');
        for (const s of scripts) {
            const t = s.textContent || '';
            if (t.includes('storeLocator') || t.includes('StoreLocator') || t.includes('sucursales')) {
                return t.substring(0, 10000);
            }
        }
        return null;
    }""")
    
    if store_script:
        print(f"\n\nStore locator script ({len(store_script)} chars):", flush=True)
        print(store_script[:3000], flush=True)
    
    # Check for __STATE__ on sucursales page
    state = page.evaluate("""() => {
        if (window.__STATE__) return JSON.stringify(window.__STATE__).substring(0, 10000);
        return null;
    }""")
    if state:
        print(f"\n\n__STATE__ on sucursales page:", flush=True)
        print(state[:3000], flush=True)
    
    browser.close()
