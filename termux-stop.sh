#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -f data/termux.pid ]; then
  PID="$(cat data/termux.pid)"
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    echo "Moharrir stopped."
  else
    echo "Moharrir was not running."
  fi
  rm -f data/termux.pid
else
  echo "Moharrir was not running."
fi

command -v termux-wake-unlock >/dev/null 2>&1 && termux-wake-unlock || true
