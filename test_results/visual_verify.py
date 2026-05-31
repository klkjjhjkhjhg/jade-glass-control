#!/usr/bin/env python3
"""Full visual verification with screenshots — jade-glass-control"""
import base64, os, tempfile, sys
from playwright.sync_api import sync_playwright
from pathlib import Path
from PIL import Image
import numpy as np

os.makedirs("jade_web/test_results", exist_ok=True)

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()
html_path = Path("jade_web/index.html")
page.goto(f"file://{html_path.resolve()}")
page.wait_for_timeout(1500)

# === Procedural BG screenshot ===
page.screenshot(path="jade_web/test_results/01_procedural_bg.png")
print("[1] Screenshot: 01_procedural_bg.png")

# Analyze procedural screenshot
img1 = Image.open("jade_web/test_results/01_procedural_bg.png").convert('RGB')
arr1 = np.array(img1)
h, w = arr1.shape[:2]
center1 = arr1[h//2, w//2]
print(f"    Center pixel (procedural): RGB={center1.tolist()}")

# === Upload blue PNG as BG ===
BLUE_PNG = base64.b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAD0lEQVR4nGNgYPgPRmAKABf2A/1+6zfzAAAAAElFTkSuQmCC')
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp.write(BLUE_PNG)
    tmp_path = tmp.name
try:
    page.set_input_files("#bg_file", tmp_path)
finally:
    os.unlink(tmp_path)
page.wait_for_timeout(1500)

page.screenshot(path="jade_web/test_results/02_blue_bg.png")
print("[2] Screenshot: 02_blue_bg.png")

img2 = Image.open("jade_web/test_results/02_blue_bg.png").convert('RGB')
arr2 = np.array(img2)
center2 = arr2[h//2, w//2]
print(f"    Center pixel (blue BG):   RGB={center2.tolist()}")
print(f"    Color changed: {center1.tolist() != center2.tolist()}")

# === Reset BG ===
page.click("#bg_clear")
page.wait_for_timeout(500)
page.screenshot(path="jade_web/test_results/03_after_reset.png")
print("[3] Screenshot: 03_after_reset.png")

img3 = Image.open("jade_web/test_results/03_after_reset.png").convert('RGB')
arr3 = np.array(img3)
center3 = arr3[h//2, w//2]
print(f"    Center pixel (after reset): RGB={center3.tolist()}")

# === Final verdict ===
print("\n" + "="*60)
print("  VERDICT")
print("="*60)

# Procedural BG should be jade green (center RGB ~ [138-142, 204-209, 133-136])
jade_green = all(c > 130 and c < 215 for c in center1[:3])
print(f"  Procedural BG jade center:  {'✅ PASS' if jade_green else '❌ FAIL'} RGB={center1.tolist()}")

# Blue BG should be blue-shifted at center
blue_dominant = center2[2] > center1[2]  # Blue channel higher than procedural
print(f"  Blue BG changes jade color:  {'✅ PASS' if blue_dominant else '❌ FAIL'} (center B: {center2[2]} > {center1[2]})")

# Reset should bring back similar color to procedural
reset_matches = abs(int(center3[0]) - int(center1[0])) < 20
print(f"  Reset restores procedural:   {'✅ PASS' if reset_matches else '❌ FAIL'} RGB={center3.tolist()}")

all_pass = jade_green and blue_dominant and reset_matches
print(f"\n  Overall: {'✅ ALL TESTS PASS' if all_pass else '❌ SOME TESTS FAIL'}")

browser.close()
playwright.stop()
sys.exit(0 if all_pass else 1)