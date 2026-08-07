"""Module 4 finale — the same agent, in a browser.

Pydantic AI can turn any agent into a chat web app with one call. You get a
message thread, streaming responses, and — the interesting part for us — a live
view of every MCP tool call the model makes.

Start it:

    .venv-agent/bin/uvicorn --app-dir src/solution web:app --port 7932

then open http://127.0.0.1:7932

Offline note: `scripts/download_web_ui.py` vendors the UI's HTML *and* its
JavaScript and CSS into `vendor/`. If that vendored copy exists we serve it and
mount the assets at `/static`, so the finale works with the wifi switched off.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_pydantic import build_agent  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHED_UI = REPO_ROOT / "vendor" / "pydantic-ai-ui.html"
ASSET_DIR = REPO_ROOT / "vendor" / "assets"

agent = build_agent()

if CACHED_UI.exists():
    app = agent.to_web(html_source=str(CACHED_UI))
    if ASSET_DIR.is_dir():
        from starlette.routing import Mount
        from starlette.staticfiles import StaticFiles

        # The chat UI claims "/" and "/{id}", and that catch-all would swallow
        # "/static/...", so this mount has to be matched first.
        app.routes.insert(0, Mount("/static", app=StaticFiles(directory=str(ASSET_DIR))))
else:
    # No vendored copy: Pydantic AI fetches its UI from the CDN (needs internet).
    app = agent.to_web()
