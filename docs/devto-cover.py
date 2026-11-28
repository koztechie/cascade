#!/usr/bin/env python3
"""Render docs/devto-cover.html to docs/devto-cover.png — exactly 1000x420.

Run from the repository root:  python3 docs/devto-cover.py
Requires playwright + chromium (same toolchain as video/render_assets.py).
"""
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SRC = HERE / "devto-cover.html"
DST = HERE / "devto-cover.png"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1000, "height": 420},
                            device_scale_factor=1)
    page.goto(SRC.resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(300)              # webfont-free system stack: one paint
    page.screenshot(path=str(DST))
    browser.close()

# exact-size guard: dev.to cover must be 1000x420, no scaling surprises
from PIL import Image                       # noqa: E402
with Image.open(DST) as im:
    assert im.size == (1000, 420), f"expected 1000x420, got {im.size}"
print(f"  OK  {DST.relative_to(REPO)}  1000x420  {DST.stat().st_size // 1024} KB")
