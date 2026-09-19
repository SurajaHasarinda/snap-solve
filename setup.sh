#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
sudo apt-get update && sudo apt-get install -y tesseract-ocr python3-tk python3-venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
