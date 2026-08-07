# Workshop setup, in one place.
#
#   make setup     create both virtualenvs and download the offline chat UI
#   make check     verify this machine is ready
#   make server    run the MCP server over stdio
#   make client    module 3 part A — talk to the server, no LLM
#   make agent     module 3 part B — the hand-written agent loop
#   make pydantic  module 4 — the same agent via Pydantic AI
#   make web       module 4 finale — the browser chat UI
#   make inspector run the MCP Inspector (needs Node 22.19+)
#   make jsonrpc   module 1 — poke the server with raw JSON-RPC
#   make clean     remove virtualenvs and vendored assets

PY ?= python3
SERVER_PY := .venv/bin/python
AGENT_PY := .venv-agent/bin/python
Q ?= What should I pack for a trip to Tokyo?

.PHONY: setup check server client agent pydantic web inspector jsonrpc clean

setup: .venv .venv-agent vendor/pydantic-ai-ui.html
	@echo
	@echo "Setup complete. Now run: make check"

.venv:
	$(PY) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements-server.txt

.venv-agent:
	$(PY) -m venv .venv-agent
	.venv-agent/bin/pip install --upgrade pip
	.venv-agent/bin/pip install -r requirements-agent.txt

vendor/pydantic-ai-ui.html: .venv-agent
	$(AGENT_PY) scripts/download_web_ui.py

check:
	$(SERVER_PY) scripts/verify_setup.py

server:
	$(SERVER_PY) src/solution/travel_server.py

client:
	$(SERVER_PY) src/solution/mcp_client.py

agent:
	$(SERVER_PY) src/solution/agent_raw.py "$(Q)"

pydantic:
	$(AGENT_PY) src/solution/agent_pydantic.py "$(Q)"

web:
	@echo "Open http://127.0.0.1:7932"
	.venv-agent/bin/uvicorn --app-dir src/solution web:app --port 7932

inspector:
	npx @modelcontextprotocol/inspector $(SERVER_PY) src/solution/travel_server.py

jsonrpc:
	./scripts/raw_jsonrpc.sh $(METHOD)

clean:
	rm -rf .venv .venv-agent vendor
