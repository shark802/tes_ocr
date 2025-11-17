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

# Find tessdata directory - must have eng.traineddata file
find_tessdata() {
    local paths=(
        "/usr/share/tesseract-ocr/tessdata"
        "/usr/share/tesseract-ocr/4.00/tessdata"
        "/usr/share/tesseract-ocr/5/tessdata"
        "/app/share/tesseract-ocr/tessdata"
    )
    
    for path in "${paths[@]}"; do
        if [ -d "$path" ] && [ -f "$path/eng.traineddata" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # Try to get from tesseract itself
    if command -v tesseract &> /dev/null; then
        local tessdata_path=$(tesseract --print-parameters 2>&1 | grep -i tessdata | head -1 | grep -o '/[^ ]*tessdata' | head -1)
        if [ -n "$tessdata_path" ] && [ -d "$tessdata_path" ] && [ -f "$tessdata_path/eng.traineddata" ]; then
            echo "$tessdata_path"
            return 0
        fi
    fi
    
    # Default fallback
    echo "/usr/share/tesseract-ocr/tessdata"
}

TESSDATA_PREFIX_FOUND=$(find_tessdata)
export TESSDATA_PREFIX="$TESSDATA_PREFIX_FOUND"
echo "TESSDATA_PREFIX set to: $TESSDATA_PREFIX"

# Verify eng.traineddata exists
if [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
    echo "✓ Found eng.traineddata at $TESSDATA_PREFIX/eng.traineddata"
else
    echo "WARNING: eng.traineddata not found at $TESSDATA_PREFIX/eng.traineddata"
    echo "Searching for eng.traineddata..."
    find /usr /app -name "eng.traineddata" 2>/dev/null | head -5
    if [ -n "$(find /usr /app -name "eng.traineddata" 2>/dev/null | head -1)" ]; then
        FOUND_PATH=$(find /usr /app -name "eng.traineddata" 2>/dev/null | head -1 | xargs dirname)
        echo "Found eng.traineddata at: $FOUND_PATH"
        export TESSDATA_PREFIX="$FOUND_PATH"
        echo "Updated TESSDATA_PREFIX to: $TESSDATA_PREFIX"
    fi
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
