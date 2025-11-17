#!/bin/bash
set -e  # Exit on error

# Set TESSDATA_PREFIX if not set
export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/4.00/tessdata/}

# Set TESSERACT_CMD if not set
export TESSERACT_CMD=${TESSERACT_CMD:-/usr/bin/tesseract}

# Ensure PATH includes /usr/bin
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Create necessary directories
mkdir -p $TESSDATA_PREFIX

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
echo "PATH: $PATH"
echo "TESSERACT_CMD: $TESSERACT_CMD"
echo "TESSDATA_PREFIX: $TESSDATA_PREFIX"

# Check if tesseract exists
if [ -f "$TESSERACT_CMD" ]; then
    echo "Tesseract found at: $TESSERACT_CMD"
    $TESSERACT_CMD --version || echo "Warning: Tesseract found but version check failed"
    $TESSERACT_CMD --list-langs || echo "Warning: Tesseract found but language list failed"
else
    echo "Warning: Tesseract not found at $TESSERACT_CMD, trying to find in PATH..."
    which tesseract || echo "Error: Tesseract not found in PATH"
    tesseract --version || echo "Error: Tesseract version check failed"
fi

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
