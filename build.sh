#!/usr/bin/env bash
# Render build script — installs system dependencies then Python packages
set -e

echo "==> Installing system dependencies (Tesseract OCR + Poppler)..."
apt-get update -y
apt-get install -y tesseract-ocr poppler-utils

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Build complete."
