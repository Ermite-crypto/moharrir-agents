#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[1/4] Updating Termux packages..."
pkg update -y

echo "[2/4] Installing build tools and Python..."
pkg install -y python git rust clang make pkg-config libffi openssl

echo "[3/4] Creating virtual environment..."
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade setuptools wheel

echo "[4/4] Installing Moharrir dependencies..."
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-1}"
python -m pip install --prefer-binary -r requirements-termux.txt
mkdir -p data

echo
echo "Installation complete. Run: bash termux-run.sh"
