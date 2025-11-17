#!/bin/bash
set -e  # Exit on error

# Set TESSDATA_PREFIX if not set
export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/4.00/tessdata/}

# Create necessary directories
mkdir -p $TESSDATA_PREFIX

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
tesseract --version || echo "Tesseract not found, installation may be required"

# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run Gunicorn with increased timeout and better logging
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --timeout 3000 \
    --workers 1 \
    --worker-class gthread \
    --threads 4 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --preload \
    wsgi:app
