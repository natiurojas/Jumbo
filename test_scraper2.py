from playwright.sync_api import sync_playwright
import json, re, sys

print("Starting...", flush=True)

with sync_playwright() as p:
    print("Launching browser...", flush=True)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("Navigating...", flush=True)
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    print("Waiting for content...", flush=True)
    page.wait_for_timeout(15000)
    
    print("Extracting state...", flush=True)
    try:
        state_data = page.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                if (script.textContent && script.textContent.includes('__STATE__')) {
                    return script.textContent.substring(0, 5000);
                }
            }
            return null;
        }""")
        
        if state_data:
            print(f"Found state data, length: {len(state_data)}", flush=True)
            print(f"First 500 chars: {state_data[:500]}", flush=True)
        else:
            print("No __STATE__ found", flush=True)
            # Let's see what scripts are available
            script_sources = page.evaluate("""() => {
                const scripts = document.querySelectorAll('script');
                return Array.from(scripts).map(s => ({ 
                    src: s.src || 'inline', 
                    len: (s.textContent || '').length,
                    hasProducts: (s.textContent || '').includes('productId')
                }));
            }""")
            print(f"Found {len(script_sources)} scripts", flush=True)
            for s in script_sources[:20]:
                print(f"  Script: src={s['src'][:80]}, len={s['len']}, hasProducts={s['hasProducts']}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    browser.close()

print("Done!", flush=True)
