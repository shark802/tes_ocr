#!/bin/bash
set -e  # Exit on error

# Set TESSDATA_PREFIX - check app directory first, then system
if [ -d /app/share/tesseract-ocr/tessdata ]; then
    export TESSDATA_PREFIX=/app/share/tesseract-ocr/tessdata
elif [ -d /usr/share/tesseract-ocr/4.00/tessdata ]; then
    export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
else
    export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/4.00/tessdata/}
fi

# Set TESSERACT_CMD - check app/bin first, then system
if [ -f /app/bin/tesseract ]; then
    export TESSERACT_CMD=/app/bin/tesseract
elif [ -f /usr/bin/tesseract ]; then
    export TESSERACT_CMD=/usr/bin/tesseract
else
    export TESSERACT_CMD=${TESSERACT_CMD:-/app/bin/tesseract}
fi

# Ensure PATH includes /app/bin first, then system paths
export PATH="/app/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Create necessary directories
mkdir -p $TESSDATA_PREFIX

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
echo "PATH: $PATH"
echo "TESSERACT_CMD: $TESSERACT_CMD"
echo "TESSDATA_PREFIX: $TESSDATA_PREFIX"

# Check if tesseract exists in /app/bin first
if [ -f /app/bin/tesseract ]; then
    echo "Tesseract found in /app/bin/tesseract"
    export TESSERACT_CMD=/app/bin/tesseract
    $TESSERACT_CMD --version || echo "Warning: Tesseract found but version check failed"
    $TESSERACT_CMD --list-langs || echo "Warning: Tesseract found but language list failed"
elif [ -f "$TESSERACT_CMD" ]; then
    echo "Tesseract found at: $TESSERACT_CMD"
    $TESSERACT_CMD --version || echo "Warning: Tesseract found but version check failed"
    $TESSERACT_CMD --list-langs || echo "Warning: Tesseract found but language list failed"
else
    echo "Warning: Tesseract not found at $TESSERACT_CMD, trying to find in PATH..."
    
    # Try to find tesseract
    TESSERACT_FOUND=$(which tesseract 2>/dev/null || find /app /usr -name tesseract -type f 2>/dev/null | head -1)
    
    if [ -n "$TESSERACT_FOUND" ] && [ -f "$TESSERACT_FOUND" ]; then
        echo "Found Tesseract at: $TESSERACT_FOUND"
        export TESSERACT_CMD="$TESSERACT_FOUND"
        # Copy to /app/bin if found elsewhere
        if [ "$TESSERACT_FOUND" != "/app/bin/tesseract" ] && [ -d /app/bin ]; then
            echo "Copying Tesseract to /app/bin/tesseract for future use..."
            cp "$TESSERACT_FOUND" /app/bin/tesseract 2>/dev/null || true
            chmod +x /app/bin/tesseract 2>/dev/null || true
            export TESSERACT_CMD=/app/bin/tesseract
        fi
        $TESSERACT_CMD --version || echo "Error: Tesseract version check failed"
    else
        echo "ERROR: Tesseract not found anywhere!"
        echo "Searching for tesseract..."
        find /app /usr -name "*tesseract*" -type f 2>/dev/null | head -10
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
