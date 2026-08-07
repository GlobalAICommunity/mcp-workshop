"""Vendor the Pydantic AI chat UI so module 4 works with the wifi off.

Passing `html_source=` to `to_web()` is not by itself enough: the HTML that
Pydantic AI ships still loads its JavaScript, CSS and icons from a CDN. This
script downloads that HTML, pulls down every CDN asset it references, and
rewrites the references to point at local files under `vendor/`.

`src/solution/web.py` then serves `vendor/assets/` as static files.

Run this once while you still have internet:

    .venv-agent/bin/python scripts/download_web_ui.py
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "vendor"
HTML_DEST = VENDOR / "pydantic-ai-ui.html"
ASSET_DIR = VENDOR / "assets"

CDN_URL_RE = re.compile(r'(?:href|src)="(https://cdn\.jsdelivr\.net/[^"]+)"')


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def main() -> int:
    try:
        from pydantic_ai.ui import DEFAULT_HTML_URL
    except ImportError:
        print("Pydantic AI is not installed in this interpreter.")
        print("Use: .venv-agent/bin/python scripts/download_web_ui.py")
        return 1

    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {DEFAULT_HTML_URL}")
    try:
        html = fetch(DEFAULT_HTML_URL).decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"Download failed: {exc}")
        return 1

    urls = sorted(set(CDN_URL_RE.findall(html)))
    print(f"Found {len(urls)} CDN assets to vendor.")

    js_saved = False
    for url in urls:
        name = url.rsplit("/", 1)[-1]
        try:
            (ASSET_DIR / name).write_bytes(fetch(url))
            html = html.replace(url, f"/static/{name}")
            js_saved = js_saved or name.endswith(".js")
            print(f"  saved {name}")
        except Exception as exc:  # noqa: BLE001
            # Icons are cosmetic; a missing one should not fail the workshop.
            print(f"  WARNING could not fetch {name}: {exc}")

    HTML_DEST.write_text(html, encoding="utf-8")
    print(f"\nSaved UI to {HTML_DEST}")

    remaining = CDN_URL_RE.findall(html)
    if remaining:
        print(f"NOTE: {len(remaining)} asset(s) still point at the CDN (probably icons).")
    else:
        print("All assets are local — the chat UI will work fully offline.")

    if not js_saved:
        print("ERROR: the UI JavaScript bundle was not saved; offline will not work.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
