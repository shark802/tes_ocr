#!/bin/bash
set -e

# Set Tesseract path explicitly
export TESSERACT_CMD=${TESSERACT_CMD:-/usr/bin/tesseract}
export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/4.00/tessdata}

# Verify Tesseract is accessible
echo "=== Tesseract Verification ==="
which tesseract
tesseract --version
ls -la /usr/share/tesseract-ocr/4.00/tessdata/

# Print environment variables for debugging
echo "=== Environment Variables ==="
echo "TESSDATA_PREFIX: ${TESSDATA_PREFIX:-Not Set}"
echo "PATH: $PATH"
printenv | sort

# Create necessary directories
mkdir -p /app/static/uploads
chmod -R 755 /app/static/

# Install Python dependencies
pip install -r requirements.txt

# Start Gunicorn
echo "=== Starting Gunicorn ==="
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application --workers 4 --timeout 120 --log-level debug
