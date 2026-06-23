#!/usr/bin/env bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE=project.settings_local

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Python was not found. Install Python 3 first."
    exit 1
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"

"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" manage.py migrate
"$PYTHON" manage.py collectstatic --noinput

echo "Starting local server at http://${HOST}:${PORT}/"
"$PYTHON" manage.py runserver "${HOST}:${PORT}"
