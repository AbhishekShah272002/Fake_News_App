#!/usr/bin/env bash
# setup.sh — One-click environment setup for Fake News Detector (macOS / Linux)
# Run this ONCE after cloning the project.

set -e

echo ""
echo " [1/4] Checking Python..."
if ! command -v python3 &>/dev/null; then
  echo " ERROR: python3 not found. Install it from https://python.org"
  exit 1
fi
python3 --version

echo ""
echo " [2/4] Creating virtual environment in ./venv ..."
if [ -d "venv" ]; then
  echo " venv already exists, skipping creation."
else
  python3 -m venv venv
  echo " venv created."
fi

echo ""
echo " [3/4] Installing dependencies into venv..."
venv/bin/pip install --upgrade pip --quiet
venv/bin/pip install -r requirements.txt

echo ""
echo " [4/4] Setting up .env file..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo " .env created from template."
  echo ""
  echo " ACTION REQUIRED: Open .env and add your API key:"
  echo "   GEMINI_API_KEY=AIza...   (free at https://aistudio.google.com/app/apikey)"
  echo "   OPENAI_API_KEY=sk-...    (at https://platform.openai.com/api-keys)"
else
  echo " .env already exists, skipping."
fi

echo ""
echo "============================================================"
echo " Setup complete!"
echo ""
echo " To activate the environment:"
echo "   source venv/bin/activate"
echo ""
echo " Then run the detector:"
echo "   python detect.py --url https://... --provider gemini"
echo "   python detect.py --text 'article text' --provider openai"
echo "============================================================"
