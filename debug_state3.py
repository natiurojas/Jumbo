from playwright.sync_api import sync_playwright
import json, re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(15000)
    
    # Get __STATE__
    state = page.evaluate("""() => {
        if (window.__STATE__) return JSON.parse(JSON.stringify(window.__STATE__));
        return null;
    }""")
    
    if state:
        # Check for all key types
        key_types = {}
        for k in state.keys():
            prefix = k.split(':')[0] if ':' in k else 'other'
            key_types[prefix] = key_types.get(prefix, 0) + 1
        
        print("Key types in __STATE__:", flush=True)
        for k, v in sorted(key_types.items(), key=lambda x: -x[1])[:30]:
            print(f"  {k}: {v}", flush=True)
        
        # Check product 311631 in detail
        target_id = "311631"
        for key in state.keys():
            if target_id in key:
                print(f"\nFound key: {key}", flush=True)
                prod = state[key]
                print(f"Type: {type(prod).__name__}", flush=True)
                if isinstance(prod, dict):
                    print(f"Keys: {list(prod.keys())[:30]}", flush=True)
                    
                    # Check productClusters
                    if 'productClusters' in prod:
                        pc = prod['productClusters']
                        print(f"productClusters type: {type(pc).__name__}", flush=True)
                        print(f"productClusters value: {json.dumps(pc, ensure_ascii=False)[:500]}", flush=True)
                    
                    # Check items
                    if 'items' in prod:
                        items = prod['items']
                        print(f"items type: {type(items).__name__}", flush=True)
                        if isinstance(items, list):
                            print(f"items count: {len(items)}", flush=True)
                            if len(items) > 0:
                                print(f"First item: {json.dumps(items[0], ensure_ascii=False)[:300]}", flush=True)
                    
                    # Check priceRange
                    if 'priceRange' in prod:
                        pr = prod['priceRange']
                        print(f"priceRange: {json.dumps(pr, ensure_ascii=False)[:300]}", flush=True)
        
        # Check if there's a different products structure
        print("\n\nSearching for product-like structures...", flush=True)
        for key, val in list(state.items())[:50]:
            if isinstance(val, dict) and 'productName' in val:
                print(f"  Product key: {key}", flush=True)
                print(f"  Name: {val.get('productName')}", flush=True)
                print(f"  Keys: {list(val.keys())[:15]}", flush=True)
                if 'productClusters' in val:
                    print(f"  productClusters: {json.dumps(val['productClusters'], ensure_ascii=False)[:300]}", flush=True)
                break
    
    browser.close()
