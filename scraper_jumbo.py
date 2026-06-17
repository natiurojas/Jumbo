"""
Jumbo.com.ar Scraper - Promociones, Productos y Sucursales
"""
import json, re, os
from datetime import datetime
from playwright.sync_api import sync_playwright

OUTPUT_FILE = "jumbo_data.json"
BASE_URL = "https://www.jumbo.com.ar"
STORE_API = ("https://www.jumbo.com.ar/api/dataentities/NT/search"
             "?_fields=name,geocoordinates,id,state,schedule,services,"
             "paymentMethods,opening,address,phone&an=jumboargentina")


def clean_price(text):
    if not text:
        return None
    text = re.sub(r'[^\d,]', '', text)
    text = text.replace(',', '.')
    try:
        return float(text)
    except:
        return None


def get_full_image_url(src):
    if not src:
        return None
    if src.startswith('//'):
        src = 'https:' + src
    src = re.sub(r'-\d+-\d+', '', src)
    src = re.sub(r'&width=\d+&height=\d+&aspect=true', '', src)
    return src


def resolve_ref(ref, state):
    if isinstance(ref, dict):
        if ref.get('type') == 'id' and ref.get('id') in state:
            return state[ref['id']]
        return ref
    if isinstance(ref, str) and ref in state:
        return state[ref]
    return ref


def extract_state(page):
    raw = page.evaluate(
        "window.__STATE__ ? JSON.parse(JSON.stringify(window.__STATE__)) : null"
    )
    return raw


def scroll_to_load_all(page, target_count=20, max_scrolls=10):
    for i in range(max_scrolls):
        page.evaluate(f"window.scrollTo(0, {i * 800})")
        page.wait_for_timeout(1500)
        count = page.evaluate(
            "document.querySelectorAll('[data-af-element=\"search-result\"]').length"
        )
        if count >= target_count:
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)
            return count
    page.evaluate("window.scrollTo(0, 0)")
    return count


def extract_products_from_page(page, product_list, state):
    items = page.evaluate("""() => {
        const items = document.querySelectorAll('[data-af-element="search-result"]');
        return Array.from(items).map(el => {
            const productId = el.getAttribute('data-af-product-id');
            const nameEl = el.querySelector('.vtex-product-summary-2-x-brandName');
            const brandEl = el.querySelector('.vtex-product-summary-2-x-productBrandName');
            const imgEl = el.querySelector('img.vtex-product-summary-2-x-imageNormal');
            const linkEl = el.querySelector('a.vtex-product-summary-2-x-clearLink');
            const priceEl = el.querySelector('.vtex-price-format-gallery');
            return {
                productId,
                name: nameEl ? nameEl.textContent.trim() : '',
                brand: brandEl ? brandEl.textContent.trim() : '',
                imgSrc: imgEl ? imgEl.getAttribute('src') : '',
                productUrl: linkEl ? linkEl.getAttribute('href') : '',
                priceText: priceEl ? priceEl.textContent.trim() : ''
            };
        });
    }""")

    for item in items:
        product = {
            "id": item['productId'],
            "nombre": item['name'],
            "marca": item['brand'],
            "imagen_url": get_full_image_url(item['imgSrc']),
            "url_producto": BASE_URL + item['productUrl'] if item['productUrl'] else None,
            "precio_actual": clean_price(item['priceText']),
            "precio_anterior": None,
            "codigo_identificacion": None,
            "promociones": [],
            "vigencia": None,
            "tipo_promocion": None,
            "metodo_pago": None,
            "sucursales_validas": [],
            "terminos_condiciones": None
        }

        pid = item['productId']
        prod_key = f"Product:sp-{pid}"
        prod = state.get(prod_key) if state else None

        if prod:
            items_key = next(
                (k for k in prod if k.startswith('items') and 'filter' in k),
                None
            )
            if items_key:
                items_list = prod.get(items_key, [])
                if isinstance(items_list, list) and len(items_list) > 0:
                    sku = resolve_ref(items_list[0], state)
                    if isinstance(sku, dict):
                        if sku.get('ean'):
                            product['codigo_identificacion'] = sku['ean']
                        elif sku.get('itemId'):
                            product['codigo_identificacion'] = sku['itemId']
                        if sku.get('referenceId'):
                            refs = sku['referenceId']
                            if isinstance(refs, list) and len(refs) > 0:
                                ref = resolve_ref(refs[0], state)
                                if isinstance(ref, dict) and ref.get('Value'):
                                    product['codigo_identificacion'] = ref['Value']
                        if sku.get('sellers'):
                            sellers = sku['sellers']
                            if isinstance(sellers, list) and len(sellers) > 0:
                                seller = resolve_ref(sellers[0], state)
                                if isinstance(seller, dict) and seller.get('commertialOffer'):
                                    offer = resolve_ref(seller['commertialOffer'], state)
                                    if isinstance(offer, dict):
                                        lp = offer.get('ListPrice')
                                        sp = offer.get('Price')
                                        if lp and sp:
                                            lp_val = float(lp)
                                            sp_val = float(sp)
                                            product['precio_actual'] = sp_val
                                            if lp_val > sp_val:
                                                product['precio_anterior'] = lp_val
                                        elif sp:
                                            product['precio_actual'] = float(sp)

            if prod.get('productClusters'):
                clusters = prod['productClusters']
                if isinstance(clusters, list):
                    promo_names = []
                    for c in clusters:
                        c_data = resolve_ref(c, state)
                        if isinstance(c_data, dict) and c_data.get('name'):
                            promo_names.append(c_data['name'])
                    product['promociones'] = promo_names

        product_list.append(product)

    return len(items)


def scrape_all_products(page, state):
    all_products = []
    urls = [
        'https://www.jumbo.com.ar/promociones?_q=promociones&map=ft',
        'https://www.jumbo.com.ar/promociones?_q=promociones&map=ft&page=2',
        'https://www.jumbo.com.ar/promociones?_q=promociones&map=ft&page=3'
    ]

    for i, url in enumerate(urls):
        print(f"  Página {i+1}...", flush=True)
        page.goto(url, timeout=120000, wait_until='domcontentloaded')
        page.wait_for_timeout(10000)
        scroll_to_load_all(page, target_count=20)
        page.wait_for_timeout(3000)
        count = extract_products_from_page(page, all_products, state)
        print(f"    {count} productos", flush=True)

    return all_products


def scrape_sucursales(browser):
    print("\n[2] Extrayendo sucursales desde API...", flush=True)
    page = browser.new_page()
    branches = []

    try:
        result = page.evaluate(f"""
            async () => {{
                try {{
                    const resp = await fetch("{STORE_API}");
                    if (resp.ok) return JSON.stringify(await resp.json());
                    return "ERROR:" + resp.status;
                }} catch(e) {{ return "FETCH_ERROR:" + e.message; }}
            }}
        """)

        if result and not result.startswith("ERROR"):
            data = json.loads(result)
            for store in data:
                coord = store.get('geocoordinates', '')
                lat = lng = ''
                if coord and ',' in coord:
                    parts = coord.split(',')
                    lat, lng = parts[0].strip(), parts[1].strip()

                address = store.get('address', '')
                schedule = store.get('schedule', '')

                branch = {
                    "nombre": store.get('name', ''),
                    "direccion": address,
                    "telefono": store.get('phone', ''),
                    "horarios": schedule,
                    "coordenadas": {"lat": lat, "lng": lng},
                    "descripcion": store.get('services', '')
                }
                branches.append(branch)

            print(f"  {len(branches)} sucursales encontradas", flush=True)
        else:
            print(f"  Error al obtener sucursales: {result}", flush=True)

    except Exception as e:
        print(f"  Error: {e}", flush=True)

    page.close()
    return branches


def build_output(products, branches):
    promo_map = {}
    for p in products:
        for promo_name in p.get('promociones', []):
            if promo_name not in promo_map:
                promo_map[promo_name] = {
                    "nombre": promo_name,
                    "tipo": "Descuento / Beneficio",
                    "vigencia": None,
                    "marcas_aplican": [],
                    "categorias_aplican": [],
                    "metodo_pago": None,
                    "sucursales_validas": [],
                    "terminos_condiciones": None
                }

    return {
        "fecha_extraccion": datetime.now().isoformat(),
        "fuente": "Jumbo Argentina - https://www.jumbo.com.ar",
        "total_productos": len(products),
        "total_sucursales": len(branches),
        "total_promociones": len(promo_map),
        "productos": products,
        "sucursales": branches,
        "promociones": sorted(promo_map.values(), key=lambda x: x['nombre'])
    }


def main():
    print("=" * 60)
    print("  Scraper Jumbo.com.ar - Promociones, Productos y Sucursales")
    print("=" * 60)

    with sync_playwright() as p:
        print("\n[1] Iniciando navegador Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        page.set_viewport_size({'width': 1920, 'height': 1080})

        print("\n[1a] Cargando promociones y estado...")
        page.goto(
            'https://www.jumbo.com.ar/promociones?_q=promociones&map=ft',
            timeout=120000, wait_until='domcontentloaded'
        )
        page.wait_for_timeout(15000)

        state = extract_state(page)
        if state:
            prod_keys = [k for k in state if k.startswith('Product:sp-')]
            cluster_keys = [k for k in state if 'productClusters.' in k]
            print(f"  {len(state)} entradas en caché, "
                  f"{len(prod_keys)} productos, "
                  f"{len(cluster_keys)} clusters")

            names = set()
            for k in sorted(cluster_keys):
                v = state[k]
                if isinstance(v, dict) and v.get('name'):
                    names.add(v['name'])
            if names:
                print(f"  {len(names)} promociones únicas detectadas")
        else:
            print("  No se pudo extraer estado")

        print("\n[1b] Extrayendo productos...")
        products = scrape_all_products(page, state)
        print(f"\n  Total: {len(products)} productos")

        branches = scrape_sucursales(browser)
        browser.close()

    output = build_output(products, branches)

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILE)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  RESULTADOS")
    print(f"{'=' * 60}")
    print(f"  Productos:            {len(products)}")
    print(f"  Sucursales:           {len(branches)}")
    print(f"  Promociones únicas:   {len(output['promociones'])}")
    print(f"  Archivo:              {OUTPUT_FILE}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
