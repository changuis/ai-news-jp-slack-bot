#!/usr/bin/env sh
set -euo pipefail

# Ensure venv tools are reachable
if [ -d "/opt/venv" ]; then
  export PATH="/opt/venv/bin:$PATH"
fi

# Materialize config/config.yaml from env
mkdir -p config
if [ -n "${CONFIG_YAML_BASE64:-}" ]; then
  echo "$CONFIG_YAML_BASE64" | base64 -d > config/config.yaml
elif [ -n "${CONFIG_YAML:-}" ]; then
  printf "%s" "$CONFIG_YAML" > config/config.yaml
else
  echo "Application error: CONFIG_YAML(_BASE64) not set" >&2
  exit 1
fi

# Start the web server (adjust module if needed)
##exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port "${PORT:-8000}"
