from playwright.sync_api import sync_playwright
import json, re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    # Capture the initial HTML response
    initial_html = []
    def handle_response(response):
        if response.url == 'https://www.jumbo.com.ar/promociones?_q=promociones&map=ft' and 'text/html' in response.headers.get('content-type', ''):
            body = response.text()
            initial_html.append(body)
    
    page.on('response', handle_response)
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(1000)
    
    if initial_html:
        html = initial_html[0]
        print(f"Initial HTML size: {len(html)}", flush=True)
        
        # Search for __STATE__ in the raw HTML
        if '__STATE__' in html:
            print("__STATE__ found in initial HTML!", flush=True)
            # Extract __STATE__ content
            match = re.search(r'window\.__STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                state = json.loads(match.group(1))
                print(f"State entries: {len(state)}", flush=True)
                product_keys = [k for k in state.keys() if k.startswith('Product:')]
                print(f"Product entries: {len(product_keys)}", flush=True)
                
                # Check product 311631
                for key in product_keys[:1]:
                    print(f"\nKey: {key}", flush=True)
                    prod = state[key]
                    print(f"Name: {prod.get('productName')}", flush=True)
                    print(f"Keys: {list(prod.keys())[:20]}", flush=True)
                    
                    # Check items
                    if 'items' in prod and isinstance(prod['items'], list) and len(prod['items']) > 0:
                        item_key = prod['items'][0]
                        if isinstance(item_key, str) and item_key in state:
                            item = state[item_key]
                            print(f"Item ean: {item.get('ean')}", flush=True)
                            print(f"Item itemId: {item.get('itemId')}", flush=True)
                            if 'referenceId' in item and isinstance(item['referenceId'], list):
                                for ref in item['referenceId']:
                                    if isinstance(ref, str) and ref in state:
                                        ref_data = state[ref]
                                        print(f"Reference: {ref_data}", flush=True)
        else:
            print("__STATE__ not found in initial HTML", flush=True)
            # Look for other patterns
            for pattern in ['__STATE', '__RUNTIME__', '__APOLLO', 'Product:']:
                if pattern in html:
                    idx = html.find(pattern)
                    print(f"Found {pattern} at position {idx}", flush=True)
                    print(f"Context: {html[max(0,idx-50):idx+200]}", flush=True)
    else:
        print("No initial HTML captured", flush=True)
    
    # Also check after render
    after_state = page.evaluate("""() => {
        const checks = {};
        checks['typeof window.__STATE__'] = typeof window.__STATE__;
        checks['typeof window.__RENDER_8_STATE__'] = typeof window.__RENDER_8_STATE__;
        checks['typeof window.__APOLLO_STATE__'] = typeof window.__APOLLO_STATE__;
        checks['typeof window.__RUNTIME__'] = typeof window.__RUNTIME__;
        if (window.__STATE__) {
            checks['__STATE__ keys count'] = Object.keys(window.__STATE__).length;
            const prodKeys = Object.keys(window.__STATE__).filter(k => k.startsWith('Product:'));
            checks['Product keys in __STATE__'] = prodKeys.length;
        }
        return checks;
    }""")
    
    print(f"\nAfter render state checks:", flush=True)
    for k, v in after_state.items():
        print(f"  {k}: {v}", flush=True)
    
    browser.close()
