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
    page.wait_for_timeout(20000)
    
    # Get __STATE__
    state_data = page.evaluate("""() => {
        const scripts = document.querySelectorAll('script');
        for (const script of scripts) {
            if (script.textContent && script.textContent.includes('__STATE__')) {
                return script.textContent;
            }
        }
        return null;
    }""")
    
    if state_data:
        match = re.search(r'window\.__STATE__\s*=\s*({.*?});', state_data, re.DOTALL)
        if match:
            state = json.loads(match.group(1))
            
            # Find product entries
            product_keys = [k for k in state.keys() if k.startswith('Product:')]
            print(f"Total Product entries: {len(product_keys)}", flush=True)
            
            # Check a specific product that appeared in our results
            target_id = "311631"
            key = f"Product:sp-{target_id}"
            
            if key in state:
                prod = state[key]
                print(f"\nProduct 311631 structure:", flush=True)
                print(f"  productName: {prod.get('productName')}", flush=True)
                print(f"  productReference: {prod.get('productReference')}", flush=True)
                print(f"  productId: {prod.get('productId')}", flush=True)
                
                # Price Range
                if 'priceRange' in prod:
                    pr = prod['priceRange']
                    print(f"\n  priceRange: {json.dumps(pr, ensure_ascii=False)[:500]}", flush=True)
                
                # Items
                if 'items' in prod and len(prod['items']) > 0:
                    item = prod['items'][0]
                    print(f"\n  Item keys: {list(item.keys())[:20]}", flush=True)
                    print(f"  itemId: {item.get('itemId')}", flush=True)
                    print(f"  ean: {item.get('ean')}", flush=True)
                    if 'referenceId' in item and item['referenceId']:
                        print(f"  referenceId: {item['referenceId']}", flush=True)
                    if 'images' in item and len(item['images']) > 0:
                        print(f"  imageUrl: {item['images'][0].get('imageUrl')}", flush=True)
                    if 'sellers' in item and len(item['sellers']) > 0:
                        offer = item['sellers'][0].get('commertialOffer', {})
                        print(f"  Offer Price: {offer.get('Price')}", flush=True)
                        print(f"  Offer ListPrice: {offer.get('ListPrice')}", flush=True)
                
                # Product clusters
                if 'productClusters' in prod:
                    print(f"\n  productClusters ({len(prod['productClusters'])}):", flush=True)
                    for c in prod['productClusters']:
                        if isinstance(c, dict):
                            print(f"    - {c.get('name')}", flush=True)
                        else:
                            print(f"    - {c}", flush=True)
                
                # Specification groups
                if 'specificationGroups' in prod:
                    for sg in prod['specificationGroups']:
                        if isinstance(sg, dict):
                            print(f"\n  Spec group: {sg.get('name')}", flush=True)
                            for spec in sg.get('specifications', []):
                                if isinstance(spec, dict):
                                    print(f"    {spec.get('name')}: {spec.get('value')}", flush=True)
            else:
                print(f"Key {key} not found", flush=True)
                # Find similar keys
                similar = [k for k in product_keys if target_id in k]
                print(f"Similar keys: {similar[:5]}", flush=True)
    else:
        print("No __STATE__ found", flush=True)
    
    browser.close()
