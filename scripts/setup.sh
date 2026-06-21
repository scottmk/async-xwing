#!/usr/bin/env bash
set -e

# If a local .venv already exists, bypass uv and run the script immediately
if [ -d "./.venv" ] && [ -f "./.venv/bin/python" ]; then
    echo "🔄 Local .venv detected. Running setup script..."
    ./.venv/bin/python scripts/setup.py
    exit 0
fi

# Look for uv globally, or check if it was previously downloaded locally
if command -v uv &> /dev/null; then
    UV_BIN="uv"
elif [ -f "./.uv/uv" ]; then
    UV_BIN="./.uv/uv"
else
    echo "📦 uv not found. Downloading a standalone binary locally..."
    mkdir -p ./.uv
    curl -LsSf https://astral.sh | UV_INSTALL_DIR="./.uv" sh --version-override > /dev/null
    UV_BIN="./.uv/uv"
fi

# Use uv to create the .venv and execute your python script
echo "🚀 Bootstrapping environment with uv..."
$UV_BIN run scripts/setup.py
