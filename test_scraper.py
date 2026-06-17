from playwright.sync_api import sync_playwright
import json, re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=60000, wait_until='domcontentloaded')
    page.wait_for_timeout(10000)
    
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
            product_keys = [k for k in state.keys() if k.startswith('Product:')]
            print(f'Total Product entries: {len(product_keys)}')
            if product_keys:
                first_key = product_keys[0]
                product = state[first_key]
                print(f'Product name: {product.get("productName", "N/A")}')
                print(f'Product ID: {product.get("productId", "N/A")}')
                print(f'Product ref: {product.get("productReference", "N/A")}')
                print(f'Link: {product.get("link", "N/A")}')
                if product.get('items') and len(product['items']) > 0:
                    first_item = product['items'][0]
                    print(f'Item ID: {first_item.get("itemId", "N/A")}')
                    print(f'Item name: {first_item.get("name", "N/A")}')
                    print(f'EAN: {first_item.get("ean", "N/A")}')
                    if first_item.get('images') and len(first_item['images']) > 0:
                        print(f'Image URL: {first_item["images"][0].get("imageUrl", "N/A")}')
                    if first_item.get('sellers') and len(first_item['sellers']) > 0:
                        offer = first_item['sellers'][0].get('commertialOffer', {})
                        print(f'Price: {offer.get("Price", "N/A")}')
                        print(f'ListPrice: {offer.get("ListPrice", "N/A")}')
                if product.get('productClusters'):
                    print(f'Clusters count: {len(product["productClusters"])}')
                    for c in product['productClusters'][:8]:
                        print(f'  - {c.get("name", "N/A")}')
        else:
            print('No __STATE__ match')
    
    browser.close()
