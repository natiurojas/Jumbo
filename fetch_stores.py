import json
from playwright.sync_api import sync_playwright

STORE_API = "https://www.jumbo.com.ar/api/dataentities/NT/search?_fields=name,grouping,image_maps,geocoordinates,SellerName,id,country,city,neighborhood,number,postalCode,state,street,schedule,services,paymentMethods,opening,hasPickup,hasDelivery,address,url_image,phone&an=jumboargentina"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Use the page's built-in fetch
    result = page.evaluate(f"""
        async () => {{
            try {{
                const resp = await fetch("{STORE_API}");
                if (resp.ok) {{
                    return JSON.stringify(await resp.json());
                }}
                return "ERROR: " + resp.status + " " + resp.statusText;
            }} catch(e) {{
                return "FETCH_ERROR: " + e.message;
            }}
        }}
    """)
    
    if result.startswith("ERROR") or result.startswith("FETCH_ERROR"):
        print(result, flush=True)
    else:
        data = json.loads(result)
        print(f"Total stores found: {len(data)}", flush=True)
        
        # Show all store data
        stores = []
        for store in data:
            coord = store.get('geocoordinates', '')
            lat, lng = '', ''
            if coord:
                parts = coord.split(',')
                if len(parts) == 2:
                    lat, lng = parts[0].strip(), parts[1].strip()
            
            stores.append({
                "nombre": store.get('name', ''),
                "direccion": f"{store.get('street', '')} {store.get('number', '')}, {store.get('city', '')}, {store.get('state', '')}".strip(),
                "telefono": store.get('phone', ''),
                "horarios": store.get('schedule', store.get('opening', '')),
                "coordenadas": {"lat": lat, "lng": lng},
                "descripcion": f"{store.get('grouping', '')} - {store.get('SellerName', '')}".strip()
            })
        
        # Print first 3
        for s in stores[:3]:
            print(json.dumps(s, ensure_ascii=False, indent=2)[:500], flush=True)
            print("---", flush=True)
        
        print(f"\nTotal branches: {len(stores)}", flush=True)
        
        # Save to file
        with open('sucursales.json', 'w', encoding='utf-8') as f:
            json.dump(stores, f, ensure_ascii=False, indent=2)
        print("Saved to sucursales.json", flush=True)
    
    browser.close()
