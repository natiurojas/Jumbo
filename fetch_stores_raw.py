import json
from playwright.sync_api import sync_playwright

STORE_API = "https://www.jumbo.com.ar/api/dataentities/NT/search?_fields=name,grouping,image_maps,geocoordinates,SellerName,id,country,city,neighborhood,number,postalCode,state,street,schedule,services,paymentMethods,opening,hasPickup,hasDelivery,address,url_image,phone&an=jumboargentina"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    result = page.evaluate(f"""
        async () => {{
            try {{
                const resp = await fetch("{STORE_API}");
                if (resp.ok) {{
                    return JSON.stringify(await resp.json());
                }}
                return "ERROR: " + resp.status;
            }} catch(e) {{
                return "FETCH_ERROR: " + e.message;
            }}
        }}
    """)
    
    if result.startswith("ERROR"):
        print(result, flush=True)
    else:
        data = json.loads(result)
        print(f"Total stores: {len(data)}", flush=True)
        # Show the first store's raw data
        print("\nFirst store raw data:", flush=True)
        print(json.dumps(data[0], ensure_ascii=False, indent=2), flush=True)
        
        # Show all store names
        print("\nAll stores:", flush=True)
        for s in data:
            print(f"  ID={s.get('id')}, Name={s.get('name')}, City={s.get('city')}, Street={s.get('street')} {s.get('number')}, Phone={s.get('phone')}", flush=True)
    
    browser.close()
