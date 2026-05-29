#!/bin/sh

set -eu

APP_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

export GREENBOX_MOCK_GPIO="${GREENBOX_MOCK_GPIO:-0}"
export GREENBOX_PIN_LIGHT="${GREENBOX_PIN_LIGHT:-18}"
export GREENBOX_FULLSCREEN="${GREENBOX_FULLSCREEN:-1}"

cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" -m frontend.main
