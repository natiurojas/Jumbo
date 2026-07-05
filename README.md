# Jumbo.com.ar Scraper

Scraper de promociones, productos y sucursales del supermercado **Jumbo Argentina** ([jumbo.com.ar](https://www.jumbo.com.ar)). Automatiza un navegador Chromium con Playwright, navega el sitio, extrae la información estructurada y la guarda en `jumbo_data.json`.

## Requisitos

- **Python** 3.10 o superior
- **Playwright** con Chromium instalado

## Instalación

```bash
# Instalar dependencias
pip install playwright

# Instalar el navegador Chromium
python -m playwright install chromium
```

## Ejecución

```bash
python scraper_jumbo.py
```

La ejecución completa tarda entre 2 y 4 minutos (navega 3 páginas de productos con scroll para carga lazy, más la consulta de sucursales).

## Estructura del proyecto

```
Tarea01-Jumbo/
├── scraper_jumbo.py          # Script principal (único archivo a ejecutar)
├── jumbo_data.json           # Output generado por el scraper
├── README.md                 # Este archivo
└── index.html                # Presentación (vacío / a completar)
```

## Qué datos se extraen

### Productos (≈58)

Obtenidos navegando las 3 páginas de `/promociones`. Por cada producto:

| Campo | Descripción | Fuente |
|---|---|---|
| `id` | ID interno del producto (VTEX) | Atributo `data-af-product-id` en el DOM |
| `nombre` | Nombre completo del producto | DOM renderizado |
| `marca` | Marca del producto | DOM renderizado |
| `imagen_url` | URL completa de la imagen del producto | DOM (se eliminan parámetros de tamaño) |
| `url_producto` | Enlace a la página individual del producto | DOM |
| `precio_actual` | Precio de venta actual | DOM + estado interno VTEX |
| `precio_anterior` | Precio de lista (si es mayor al actual) | Estado interno `window.__STATE__` |
| `codigo_identificacion` | EAN, SKU o Reference ID del producto | Estado interno VTEX |
| `promociones` | Lista de nombres de promociones asociadas | Clusters de producto desde `__STATE__` |

### Promociones (≈28)

Lista única de todas las promociones detectadas entre los productos, con su nombre y tipo genérico.

### Sucursales (15)

Obtenidas desde la API de Master Data de VTEX. Por cada sucursal:

| Campo | Descripción |
|---|---|
| `nombre` | Nombre del local |
| `direccion` | Dirección completa |
| `telefono` | Teléfono de contacto |
| `horarios` | Horarios de atención |
| `coordenadas` | Latitud y longitud |
| `descripcion` | Servicios ofrecidos |

## Arquitectura del scraper

1. **`extract_state()`** — Obtiene `window.__STATE__` (caché Apollo de VTEX) con todos los datos de productos, clusters de promoción y SKUs.
2. **`scrape_all_products()`** — Itera las 3 páginas de resultados. En cada una hace scroll progresivo para forzar la carga lazy de los 20 productos por página.
3. **`extract_products_from_page()`** — Lee el DOM renderizado y enriquece cada producto con datos del estado interno (EAN, precios, clusters de promoción).
4. **`scrape_sucursales()`** — Consulta directamente la API REST de VTEX Master Data (`/api/dataentities/NT/search`) y parsea la respuesta JSON.
5. **`build_output()`** — Arma el JSON final con el esquema solicitado.

## Notas técnicas

- El sitio Jumbo corre sobre **VTEX IO**. Los datos de productos se renderizan con React y se cargan parcialmente con lazy loading (8 productos iniciales, luego más al hacer scroll).
- El estado Apollo `__STATE__` contiene referencias anidadas (ej: `{"type": "id", "id": "..."}`) que el scraper resuelve contra el mismo objeto para obtener los valores reales.
- Las imágenes se devuelven sin los parámetros de tamaño (`&width=230&height=138`) para obtener la URL base de la imagen original.
- Las sucursales se obtienen de una API interna de VTEX que expone datos de las 15 sucursales de Jumbo en Argentina.
