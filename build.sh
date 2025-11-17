#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Copy Tesseract to /app/bin for easier access
mkdir -p /app/bin
mkdir -p /app/share/tesseract-ocr/tessdata
if [ -f /usr/bin/tesseract ]; then
    cp /usr/bin/tesseract /app/bin/tesseract
    chmod +x /app/bin/tesseract
    echo "Tesseract copied to /app/bin/tesseract"
fi
if [ -d /usr/share/tesseract-ocr/tessdata ]; then
    cp -r /usr/share/tesseract-ocr/tessdata/* /app/share/tesseract-ocr/tessdata/ 2>/dev/null || true
    echo "Tessdata copied to /app/share/tesseract-ocr/tessdata"
fi

# Install Python dependencies
pip install -r requirements.txt
python -m pip install --upgrade pip
