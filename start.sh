#!/bin/bash
set -e

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app

# Debug information
echo "=== System Information ==="
uname -a
python --version
pip --version

# Check Tesseract
echo "=== Tesseract Check ==="
which tesseract || echo "Tesseract not found in PATH"
tesseract --version || echo "Could not get Tesseract version"

# Create necessary directories
echo "=== Setting up directories ==="
mkdir -p /app/static/uploads
chmod -R 755 /app/static/

# Install Python dependencies
echo "=== Installing dependencies ==="
pip install -r requirements.txt

# Start Gunicorn with more verbose logging
echo "=== Starting Gunicorn ==="
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
