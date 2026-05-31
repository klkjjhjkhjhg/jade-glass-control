#!/usr/bin/env python3
import base64, os, tempfile
from playwright.sync_api import sync_playwright
from pathlib import Path

os.makedirs("jade_web/test_results", exist_ok=True)

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()
html_path = Path("jade_web/index.html")
page.goto(f"file://{html_path.resolve()}")
page.wait_for_timeout(1500)

# Screenshot before
page.screenshot(path="jade_web/test_results/before_upload.png")
print("Screenshot saved: before_upload.png")

# Upload a blue PNG
BLUE_PNG = base64.b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAD0lEQVR4nGNgYPgPRmAKABf2A/1+6zfzAAAAAElFTkSuQmCC')
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp.write(BLUE_PNG)
    tmp_path = tmp.name
try:
    page.set_input_files("#bg_file", tmp_path)
finally:
    os.unlink(tmp_path)
page.wait_for_timeout(1500)
page.screenshot(path="jade_web/test_results/after_upload.png")
print("Screenshot saved: after_upload.png")

print(f"Before size: {os.path.getsize('jade_web/test_results/before_upload.png')}")
print(f"After size: {os.path.getsize('jade_web/test_results/after_upload.png')}")

browser.close()
playwright.stop()