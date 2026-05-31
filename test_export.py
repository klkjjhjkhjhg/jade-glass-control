#!/opt/anaconda3/bin/python3
"""Test exportAllLayers in real browser with preserveDrawingBuffer fix."""
import os, sys
from playwright.sync_api import sync_playwright

DOWNLOADS = '/Users/klkjjhjkhjhg/Downloads'
os.makedirs(DOWNLOADS, exist_ok=True)

# Clean downloads first
for f in os.listdir(DOWNLOADS):
    if f.endswith('.png') and f.startswith('0'):
        os.remove(os.path.join(DOWNLOADS, f))
        print(f'Removed {f}')

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(downloads_path=DOWNLOADS)

    # Inject preserveDrawingBuffer fix BEFORE page loads
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

    # Load the page
    page.goto('http://localhost:8765/', timeout=15000)
    page.wait_for_timeout(2000)

    # Verify WebGL works
    result = page.evaluate("""() => {
        const c = document.querySelector('canvas');
        if (!c) return 'NO CANVAS';
        const gl = c.getContext('webgl2') || c.getContext('webgl');
        if (!gl) return 'NO GL';
        return 'glVersion=' + (gl instanceof WebGL2RenderingContext ? 2 : 1);
    }""")
    print(f'WebGL: {result}')

    # Check canvas size
    size = page.evaluate("""() => {
        const c = document.querySelector('canvas');
        return c ? c.width + 'x' + c.height : 'no canvas';
    }""")
    print(f'Canvas: {size}')

    # Check toDataURL (should be non-zero after render)
    url_len = page.evaluate("""() => {
        const c = document.querySelector('canvas');
        return c ? c.toDataURL('image/png').length : 0;
    }""")
    print(f'toDataURL length: {url_len} (non-zero = rendering OK)')

    # Click Debug Layers button
    page.click('#debug_export')
    page.wait_for_timeout(3000)

    # Count downloaded files
    downloaded = sorted([f for f in os.listdir(DOWNLOADS) if f.endswith('.png') and f.startswith('0')])
    print(f'\nDownloaded files ({len(downloaded)}):')
    for f in downloaded:
        path = os.path.join(DOWNLOADS, f)
        size_kb = os.path.getsize(path) / 1024
        print(f'  {f}: {size_kb:.1f} KB')

    # Check pixel values if any file downloaded
    if downloaded:
        import struct, zlib
        for fname in downloaded[:2]:  # Check first 2
            path = os.path.join(DOWNLOADS, fname)
            with open(path, 'rb') as f:
                data = f.read()
            print(f'\n{f} raw bytes: {len(data)}')
            # Just check signature
            PNG_SIG = b'\x89PNG\r\n\x1a\n'
            print(f'  PNG signature OK: {data[:8] == PNG_SIG}')

    browser.close()
    print('\nDone.')