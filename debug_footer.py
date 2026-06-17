from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    page.goto('https://www.jumbo.com.ar/promociones?_q=promociones&map=ft', timeout=120000, wait_until='domcontentloaded')
    page.wait_for_timeout(15000)
    
    # Scroll to bottom to see footer
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(5000)
    
    # Check footer content
    footer_info = page.evaluate("""() => {
        const result = {};
        // Find footer
        const footer = document.querySelector('footer') || document.querySelector('[class*="footer"]');
        if (footer) {
            result.footerHTML = footer.outerHTML.substring(0, 5000);
            result.footerText = footer.textContent.trim().substring(0, 2000);
            
            // Find links in footer
            const links = footer.querySelectorAll('a');
            result.footerLinks = Array.from(links).map(l => ({
                href: l.getAttribute('href'),
                text: l.textContent.trim().substring(0, 100)
            }));
        } else {
            result.footer = 'not found';
        }
        
        // Check for "sucursales" link anywhere on page
        const allLinks = document.querySelectorAll('a');
        result.sucursalesLinks = Array.from(allLinks)
            .filter(l => (l.textContent || '').toLowerCase().includes('sucursal') || 
                         (l.getAttribute('href') || '').toLowerCase().includes('sucursal'))
            .map(l => ({
                href: l.getAttribute('href'),
                text: l.textContent.trim().substring(0, 100)
            }));
        
        return result;
    }""")
    
    print("Footer info:", flush=True)
    import json
    print(json.dumps(footer_info, ensure_ascii=False, indent=2)[:3000], flush=True)
    
    browser.close()
