#!/usr/bin/env bash
# Module 1 demo — MCP is just newline-delimited JSON-RPC over a pipe.
#
#   ./scripts/raw_jsonrpc.sh                     # server/discover
#   ./scripts/raw_jsonrpc.sh tools/list
#   ./scripts/raw_jsonrpc.sh tools/call '{"name":"get_weather","arguments":{"city":"Tokyo"}}'
#
# No client library, no SDK — just a shell pipe into the server's stdin.
set -euo pipefail

cd "$(dirname "$0")/.."
METHOD="${1:-server/discover}"
PARAMS="${2:-}"
[ -z "$PARAMS" ] && PARAMS='{}'

# Since the 2026-07-28 revision there is no `initialize` handshake. Instead every
# request carries the protocol version and the client's capabilities in `_meta`.
META='"io.modelcontextprotocol/protocolVersion":"2026-07-28",
      "io.modelcontextprotocol/clientCapabilities":{},
      "io.modelcontextprotocol/clientInfo":{"name":"raw-shell-demo","version":"1.0"}'

REQUEST=$(python3 -c '
import json, sys
method, params, meta = sys.argv[1], json.loads(sys.argv[2]), json.loads("{" + sys.argv[3] + "}")
params["_meta"] = meta
print(json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}))
' "$METHOD" "$PARAMS" "$META")

echo "--> $REQUEST" >&2
echo >&2

# The sleep keeps stdin open long enough for the server to finish the call;
# without it the process sees EOF and exits before replying.
{ echo "$REQUEST"; sleep 2; } \
  | .venv/bin/python src/solution/travel_server.py 2>/dev/null \
  | python3 -c 'import json,sys; [print(json.dumps(json.loads(l), indent=2)) for l in sys.stdin if l.strip()]'
