#!/opt/anaconda3/bin/python3
"""Test all 8 debug passes via drawImage - verify non-blank pixels."""
import os, sys, base64, io
from PIL import Image
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context()

    ctx.add_init_script("""
        (() => {
            const orig = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attrs) {
                if (type === 'webgl2' || type === 'webgl' || type === 'experimental-webgl') {
                    attrs = Object.assign({}, attrs || {}, { preserveDrawingBuffer: true });
                }
                return orig.call(this, type, attrs);
            };
            console.log('[FIX] preserveDrawingBuffer injected');
        })();
    """)

    page = ctx.new_page()
    page.on('console', lambda msg: print(f'CONSOLE: {msg.text}'))
    page.on('pageerror', lambda err: print(f'ERROR: {err}'))

    page.goto('http://localhost:8765/', timeout=15000)
    page.wait_for_timeout(3000)  # Wait for GL context to stabilize

    result = page.evaluate("() => { const c = document.querySelector('canvas'); if(!c) return 'NO CANVAS'; const gl = c.getContext('webgl2') || c.getContext('webgl'); if(!gl) return 'NO GL'; return 'glVersion=' + (gl instanceof WebGL2RenderingContext ? 2 : 1); }")
    print(f'WebGL: {result}')

    size = page.evaluate("() => { const c = document.querySelector('canvas'); return c ? c.width+'x'+c.height : 'no canvas'; }")
    print(f'Canvas: {size}')

    url_len = page.evaluate("() => { const c = document.querySelector('canvas'); return c ? c.toDataURL('image/png').length : 0; }")
    print(f'toDataURL length: {url_len} (non-zero = rendering OK)')

    # Test each debug pass - use page's existing globals
    labels = ['00_normal','01_bg_texture','02_geometry','03_normal','04_shading','05_fresnel','06_sss','07_refraction']
    print(f'\n--- Debug Pass Export Test ---')
    for i, label in enumerate(labels):
        data_url = page.evaluate(f"""
            () => {{
                // Use existing global 'gl' and 'uDebug' from page scope
                gl.uniform1f(uDebug, {i});
                gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
                const c2 = document.createElement('canvas');
                c2.width = document.querySelector('canvas').width;
                c2.height = document.querySelector('canvas').height;
                c2.getContext('2d').drawImage(document.querySelector('canvas'), 0, 0);
                return c2.toDataURL('image/png');
            }}
        """)
        img_data = base64.b64decode(data_url.split(',')[1])
        img = Image.open(io.BytesIO(img_data))
        px = img.load()
        w, h = img.size
        center = px[w//2, h//2]
        non_black = sum(1 for y in range(h) for x in range(w) if sum(px[x,y][:3]) > 30)
        total = w * h
        pct = non_black / total * 100
        status = 'OK' if non_black > 1000 else 'ZERO/BLANK'
        print(f'  [{i:02d}] {label}: center={center}, {non_black}/{total} non-black ({pct:.1f}%) [{status}] len={len(data_url)}')

    # Reset to normal pass
    page.evaluate("() => { gl.uniform1f(uDebug, 0); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); }")
    print('\nDone.')

    browser.close()