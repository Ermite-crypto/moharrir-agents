#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "The application is not installed. Run: bash termux-install.sh"
  exit 1
fi

mkdir -p data
if [ -f data/termux.pid ] && kill -0 "$(cat data/termux.pid)" 2>/dev/null; then
  echo "Moharrir is already running at http://127.0.0.1:8000"
  exit 0
fi

command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
# shellcheck disable=SC1091
source .venv/bin/activate

nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 \
  > data/termux.log 2>&1 &
echo $! > data/termux.pid
sleep 3

if kill -0 "$(cat data/termux.pid)" 2>/dev/null; then
  echo "Moharrir is running at: http://127.0.0.1:8000"
  command -v termux-open-url >/dev/null 2>&1 && termux-open-url http://127.0.0.1:8000 || true
else
  echo "Startup failed. Log:"
  tail -n 80 data/termux.log
  exit 1
fi
