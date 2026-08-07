"""Check that this machine is ready for the workshop.

Run it from the repo root:

    .venv/bin/python scripts/verify_setup.py

It checks both virtualenvs, the MCP server, and whichever model provider you
configured in `.env`. Every failure prints how to fix it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_VENV = REPO_ROOT / ".venv" / "bin" / "python"
AGENT_VENV = REPO_ROOT / ".venv-agent" / "bin" / "python"
VENDORED_UI = REPO_ROOT / "vendor" / "pydantic-ai-ui.html"
VENDORED_ASSETS = REPO_ROOT / "vendor" / "assets"

sys.path.insert(0, str(REPO_ROOT / "src"))

OK, BAD, WARN = "  ok  ", " FAIL ", " warn "
failures: list[str] = []
warnings: list[str] = []


def report(status: str, label: str, detail: str = "", fix: str = "") -> None:
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    if status == BAD:
        failures.append(f"{label}: {fix or detail}")
    elif status == WARN:
        warnings.append(f"{label}: {fix or detail}")


def run_in(python: Path, code: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [str(python), "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_ROOT,
        )
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def check_python() -> None:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        report(OK, "Python version", f"{major}.{minor}")
    else:
        report(BAD, "Python version", f"{major}.{minor}", "MCP needs Python 3.10 or newer.")


def check_server_venv() -> None:
    if not SERVER_VENV.exists():
        report(BAD, "Server virtualenv", "missing", "Run: make setup  (or see docs/00-setup.md)")
        return
    ok, out = run_in(SERVER_VENV, "import mcp,importlib.metadata as m;print(m.version('mcp'))")
    if not ok:
        report(BAD, "Server virtualenv", "mcp not importable", "Run: make setup")
        return
    version = out.splitlines()[-1]
    if version.startswith("2."):
        report(OK, "Server virtualenv", f"mcp {version}")
    else:
        report(
            BAD,
            "Server virtualenv",
            f"mcp {version}",
            "This workshop targets mcp 2.x. Run: make setup",
        )


def check_agent_venv() -> None:
    if not AGENT_VENV.exists():
        report(WARN, "Agent virtualenv", "missing", "Needed for modules 4-5. Run: make setup")
        return
    ok, out = run_in(
        AGENT_VENV,
        "import importlib.metadata as m;print(m.version('pydantic-ai-slim'))",
    )
    if ok:
        report(OK, "Agent virtualenv", f"pydantic-ai-slim {out.splitlines()[-1]}")
    else:
        report(WARN, "Agent virtualenv", "pydantic-ai not importable", "Run: make setup")


def check_server_runs() -> None:
    if not SERVER_VENV.exists():
        report(WARN, "MCP server", "skipped", "server virtualenv missing")
        return
    code = "\n".join(
        [
            "import asyncio, sys",
            "sys.path.insert(0, 'src/solution')",
            "from mcp import Client",
            "from travel_server import mcp",
            "async def main():",
            "    async with Client(mcp) as c:",
            "        r = await c.list_tools()",
            "        print(len(r.tools), c.protocol_version)",
            "asyncio.run(main())",
        ]
    )
    ok, out = run_in(SERVER_VENV, code)
    if ok and out:
        count, revision = out.splitlines()[-1].split()
        report(OK, "MCP server", f"{count} tools, protocol {revision}")
    else:
        report(BAD, "MCP server", "did not start", out[-200:] or "unknown error")


def check_web_ui() -> None:
    if VENDORED_UI.exists() and any(VENDORED_ASSETS.glob("*.js")):
        report(OK, "Offline chat UI", "vendored")
    else:
        report(
            WARN,
            "Offline chat UI",
            "not downloaded",
            "Run while online: .venv-agent/bin/python scripts/download_web_ui.py",
        )


def check_provider() -> None:
    try:
        import model_config as mc
    except Exception as exc:  # noqa: BLE001
        report(BAD, "Model provider", f"config error: {exc}")
        return

    try:
        choice = mc.get_choice()
    except mc.ConfigError as exc:
        report(BAD, "Model provider", str(exc))
        return

    label = f"{choice.provider} / {choice.model}"

    if choice.provider == "ollama":
        base = os.getenv("OLLAMA_BASE_URL", mc.OPENAI_COMPATIBLE_BASE_URLS["ollama"])
        tags_url = base.rsplit("/v1", 1)[0] + "/api/tags"
        try:
            with urllib.request.urlopen(tags_url, timeout=5) as response:
                names = [m["name"] for m in json.load(response).get("models", [])]
        except (urllib.error.URLError, OSError):
            report(
                BAD,
                "Model provider",
                f"{label} — Ollama is not running",
                "Start it with: ollama serve   (install from https://ollama.com)",
            )
            return

        wanted = choice.model
        if any(n == wanted or n.startswith(wanted + "-") for n in names):
            report(OK, "Model provider", f"{label} — model available")
        else:
            report(
                BAD,
                "Model provider",
                f"{label} — model not pulled",
                f"Run: ollama pull {wanted}    (have: {', '.join(names) or 'none'})",
            )
        return

    key_var = mc.API_KEY_VARS[choice.provider]
    if key_var and not os.getenv(key_var, "").strip():
        report(
            BAD,
            "Model provider",
            f"{label} — {key_var} is not set",
            f"Copy .env.example to .env and set {key_var}. See docs/models.md.",
        )
        return
    if choice.provider == "foundry" and not os.getenv("AZURE_OPENAI_ENDPOINT", "").strip():
        report(BAD, "Model provider", f"{label} — AZURE_OPENAI_ENDPOINT is not set")
        return
    report(OK, "Model provider", f"{label} — credentials present")


def main() -> int:
    print("MCP workshop — setup check\n")
    check_python()
    check_server_venv()
    check_agent_venv()
    check_server_runs()
    check_web_ui()
    check_provider()

    print()
    if failures:
        print(f"{len(failures)} problem(s) to fix:")
        for item in failures:
            print(f"  - {item}")
        return 1
    if warnings:
        print("Ready for modules 1-3. Optional items missing:")
        for item in warnings:
            print(f"  - {item}")
        return 0
    print("All good — you are ready for the workshop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
