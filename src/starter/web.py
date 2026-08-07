"""Module 4 finale — STARTER FILE. Put the agent in a browser.

Follow docs/04-pydantic-ai.md. Solution: src/solution/web.py

Start it with:

    .venv-agent/bin/uvicorn --app-dir src/starter web:app --port 7932
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

# TODO 1: Turn the agent into a web app with agent.to_web().
#         If CACHED_UI exists, pass html_source=str(CACHED_UI) so it works
#         offline; otherwise call to_web() with no arguments.
app = ...

# TODO 2 (only needed for offline use): serve the vendored JS/CSS.
#         Mount StaticFiles(directory=str(ASSET_DIR)) at "/static".
#         It must be inserted at app.routes[0] — the chat UI registers a
#         catch-all "/{id}" route that would otherwise swallow /static.
