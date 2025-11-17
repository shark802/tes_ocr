#!/bin/bash
set -e  # Exit on error

# Find Tesseract wherever it's installed
TESSERACT_FOUND=$(which tesseract 2>/dev/null || find /usr /app -name tesseract -type f -executable 2>/dev/null | head -1)

if [ -n "$TESSERACT_FOUND" ] && [ -f "$TESSERACT_FOUND" ]; then
    export TESSERACT_CMD="$TESSERACT_FOUND"
    echo "Found Tesseract at: $TESSERACT_CMD"
else
    # Fallback to common location
    export TESSERACT_CMD=${TESSERACT_CMD:-/usr/bin/tesseract}
    echo "Using default Tesseract path: $TESSERACT_CMD"
fi

# Find tessdata directory
if [ -d /usr/share/tesseract-ocr/tessdata ]; then
    export TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata
elif [ -d /usr/share/tesseract-ocr/4.00/tessdata ]; then
    export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
elif [ -d /app/share/tesseract-ocr/tessdata ]; then
    export TESSDATA_PREFIX=/app/share/tesseract-ocr/tessdata
else
    export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/4.00/tessdata/}
fi

# Ensure PATH includes common locations
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Create necessary directories
mkdir -p $TESSDATA_PREFIX

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
echo "PATH: $PATH"
echo "TESSERACT_CMD: $TESSERACT_CMD"
echo "TESSDATA_PREFIX: $TESSDATA_PREFIX"

# Verify Tesseract installation
if [ -f "$TESSERACT_CMD" ]; then
    echo "Tesseract found at: $TESSERACT_CMD"
    $TESSERACT_CMD --version || echo "Warning: Tesseract found but version check failed"
    $TESSERACT_CMD --list-langs || echo "Warning: Tesseract found but language list failed"
else
    echo "ERROR: Tesseract not found at $TESSERACT_CMD"
    echo "Searching for tesseract..."
    find /usr /app -name "*tesseract*" -type f 2>/dev/null | head -10
    echo "PATH contents: $PATH"
    echo "Trying 'which tesseract': $(which tesseract 2>/dev/null || echo 'not found')"
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
