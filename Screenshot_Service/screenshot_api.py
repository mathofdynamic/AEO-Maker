#!/usr/bin/env python3
"""
Screenshot API
---------------
Flask API that accepts a URL, loads it with Selenium Chrome in headless mode,
waits for Client-Side Rendering (CSR), scrolls to the bottom to trigger lazy
content, then captures a full-page screenshot and saves it in the project
under the `screenshots/` directory.

Design notes:
- Uses Selenium 4 + Chrome DevTools Protocol to capture a single, full-height
  screenshot (no external imaging libraries required).
- Waits for `document.readyState === 'complete'` and then performs incremental
  scrolls to ensure CSR/lazy-loaded content appears.
- Saves files with a timestamped, URL-derived name for easy organization.
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Tuple

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


app = Flask(__name__)


# ---------- Configuration ----------
DEFAULT_TIMEOUT_SECONDS = 30  # Max time to wait for initial load
SCROLL_STEP_PX = 1200        # Vertical pixels per scroll step while loading
SCROLL_PAUSE_SEC = 0.6        # Pause between scroll steps
DEFAULT_VIEWPORT_WIDTH = 1366 # Base width to emulate while loading

# Screenshots will be saved into this folder inside the project
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def _build_driver() -> webdriver.Chrome:
    """Create and return a configured headless Chrome WebDriver.

    We keep options minimal and compatible with headless environments.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={DEFAULT_VIEWPORT_WIDTH},900")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(DEFAULT_TIMEOUT_SECONDS)
    return driver


def _wait_for_dom_ready(driver: webdriver.Chrome, timeout: int) -> None:
    """Block until the page's document ready state is 'complete'."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    # Ensure the body exists (guards against edge cases)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def _progressive_scroll(driver: webdriver.Chrome) -> None:
    """Scroll down the page in steps to trigger lazy-loading/CSR content.

    We scroll until further scrolling no longer increases the total scrollable
    height or we hit a reasonable upper bound of attempts.
    """
    import time

    last_height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
    )

    # Reasonable cap to prevent endless loops on pages that continuously append
    # content (e.g. infinite feeds).
    for _ in range(30):
        driver.execute_script("window.scrollBy(0, arguments[0]);", SCROLL_STEP_PX)
        time.sleep(SCROLL_PAUSE_SEC)
        new_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
        )
        if new_height <= last_height:
            break
        last_height = new_height

    # Return to top so the captured image starts at the top of the page
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.3)


def _capture_fullpage_png_base64(driver: webdriver.Chrome) -> Tuple[bytes, int, int]:
    """Capture a full-page screenshot via Chrome DevTools and return PNG bytes.

    Returns a tuple of (png_bytes, width, height).
    """
    # Determine full page dimensions
    total_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth, window.innerWidth)")
    total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, window.innerHeight)")

    # Ensure sane minimums
    total_width = max(int(total_width), DEFAULT_VIEWPORT_WIDTH)
    total_height = max(int(total_height), 1)

    # Emulate the full size so Chrome can render and capture in one shot
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "mobile": False,
        "width": total_width,
        "height": total_height,
        "deviceScaleFactor": 1,
        "screenWidth": total_width,
        "screenHeight": total_height,
    })

    # Capture from surface (avoids viewport-only screenshots)
    result = driver.execute_cdp_cmd("Page.captureScreenshot", {
        "format": "png",
        "fromSurface": True
    })

    png_bytes = base64.b64decode(result.get("data", b""))
    return png_bytes, total_width, total_height


def _safe_filename_from_url(url: str) -> str:
    """Create a filesystem-safe filename from a URL with a timestamp suffix."""
    safe = (
        url.replace("http://", "")
           .replace("https://", "")
           .replace("/", "_")
           .replace("?", "_")
           .replace(":", "_")
           .replace("&", "_")
           .replace("=", "_")
    )
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{safe}_{timestamp}.png"


@app.route("/health", methods=["GET"])
def health() -> tuple:
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "screenshot_api"}), 200


@app.route("/screenshot", methods=["POST"])
def screenshot() -> tuple:
    """Accept JSON {"url": "https://..."} and return the saved file path.

    Steps:
    1) Validate and normalize URL.
    2) Load page with headless Chrome and wait for DOM ready.
    3) Perform progressive scroll to trigger CSR/lazy content.
    4) Capture a full-page PNG via DevTools.
    5) Save file under `screenshots/` and respond with metadata.
    """
    body = request.get_json(silent=True) or {}
    raw_url = (body.get("url") or "").strip()

    if not raw_url:
        return jsonify({"success": False, "error": "Field 'url' is required."}), 400

    if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
        raw_url = "https://" + raw_url

    try:
        driver = _build_driver()
    except WebDriverException as e:
        return jsonify({"success": False, "error": f"WebDriver init error: {e}"}), 500

    saved_path = None
    try:
        try:
            driver.get(raw_url)
        except TimeoutException:
            # Continue; some sites keep network active. We'll rely on DOM ready below.
            pass

        _wait_for_dom_ready(driver, DEFAULT_TIMEOUT_SECONDS)
        _progressive_scroll(driver)

        png_bytes, width, height = _capture_fullpage_png_base64(driver)

        filename = _safe_filename_from_url(raw_url)
        dated_dir = SCREENSHOTS_DIR / datetime.utcnow().strftime("%Y%m%d")
        dated_dir.mkdir(exist_ok=True)
        saved_path = dated_dir / filename
        with open(saved_path, "wb") as f:
            f.write(png_bytes)

        return jsonify({
            "success": True,
            "url": raw_url,
            "file_path": str(saved_path),
            "width": width,
            "height": height,
        }), 200

    except TimeoutException:
        return jsonify({"success": False, "error": "Timed out waiting for page to load."}), 504
    except Exception as e:
        return jsonify({"success": False, "error": f"Unexpected error: {e}"}), 500
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    # Run with: python screenshot_api.py
    # Then POST: curl -X POST http://127.0.0.1:5002/screenshot -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
    app.run(host="0.0.0.0", port=5002, debug=False)


