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
    
    # Try to find tesseract
    TESSERACT_FOUND=$(which tesseract 2>/dev/null || find /usr -name tesseract -type f 2>/dev/null | head -1)
    
    if [ -n "$TESSERACT_FOUND" ] && [ -f "$TESSERACT_FOUND" ]; then
        echo "Found Tesseract at: $TESSERACT_FOUND"
        export TESSERACT_CMD="$TESSERACT_FOUND"
        # Create symlink if needed
        if [ ! -f "/usr/bin/tesseract" ]; then
            echo "Creating symlink from $TESSERACT_FOUND to /usr/bin/tesseract"
            ln -sf "$TESSERACT_FOUND" /usr/bin/tesseract 2>/dev/null || true
        fi
        $TESSERACT_FOUND --version || echo "Error: Tesseract version check failed"
    else
        echo "ERROR: Tesseract not found anywhere!"
        echo "Searching for tesseract..."
        find /usr -name "*tesseract*" -type f 2>/dev/null | head -10
        echo "PATH contents: $PATH"
    fi
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
