#!/usr/bin/env sh
set -e

# Ensure the config dir exists
mkdir -p config

# Prefer base64 to avoid YAML quoting issues
if [ -n "$CONFIG_YAML_BASE64" ]; then
  echo "$CONFIG_YAML_BASE64" | base64 -d > config/config.yaml
elif [ -n "$CONFIG_YAML" ]; then
  # Write raw YAML from the env var
  # Use printf to preserve exact newlines
  printf "%s" "$CONFIG_YAML" > config/config.yaml
else
  echo "Application error: CONFIG_YAML(_BASE64) not set; cannot create config/config.yaml" >&2
  exit 1
fi

# Start your web server (edit to match your app)
# If you followed my earlier advice with FastAPI:
exec uvicorn server:app --host 0.0.0.0 --port "${PORT:-8000}"
