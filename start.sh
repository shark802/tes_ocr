#!/bin/bash
set -e

# Set Tesseract path explicitly
export TESSERACT_CMD="/usr/bin/tesseract"
export TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata"

echo "=== System Information ==="
uname -a
lsb_release -a 2>/dev/null || echo "lsb_release not available"

echo "=== Checking Tesseract Installation ==="
# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "Tesseract not found in PATH. Searching in common locations..."
    # Search for tesseract in common locations
    for path in /usr/bin/tesseract /usr/local/bin/tesseract /app/.apt/usr/bin/tesseract; do
        if [ -f "$path" ]; then
            export TESSERACT_CMD="$path"
            echo "Found Tesseract at: $path"
            break
        fi
    done
else
    export TESSERACT_CMD=$(which tesseract)
    echo "Tesseract found at: $TESSERACT_CMD"
fi

# Verify Tesseract is accessible
echo "\n=== Tesseract Verification ==="
ls -la /usr/bin/tesseract || echo "Tesseract not found in /usr/bin/tesseract"
ls -la /usr/local/bin/tesseract || echo "Tesseract not found in /usr/local/bin/tesseract"
ls -la /app/.apt/usr/bin/tesseract || echo "Tesseract not found in /app/.apt/usr/bin/tesseract"

# Try to get Tesseract version
if [ -f "$TESSERACT_CMD" ]; then
    echo "\n=== Tesseract Version ==="
    $TESSERACT_CMD --version || echo "Failed to get Tesseract version"
    
    echo "\n=== Tesseract Languages ==="
    $TESSERACT_CMD --list-langs || echo "Failed to list Tesseract languages"
    
    echo "\n=== Tesseract Data Directory ==="
    ls -la /usr/share/tesseract-ocr/4.00/tessdata/ || \
    ls -la /usr/share/tesseract-ocr/tessdata/ || \
    ls -la /app/.apt/usr/share/tesseract-ocr/4.00/tessdata/ || \
    echo "Could not find Tesseract data directory"
else
    echo "\n!!! WARNING: Tesseract not found in any standard location !!!"
    echo "TESSERACT_CMD: $TESSERACT_CMD"
    echo "PATH: $PATH"
fi

# Print environment variables for debugging
echo "\n=== Environment Variables ==="
echo "TESSERACT_CMD: $TESSERACT_CMD"
echo "TESSDATA_PREFIX: $TESSDATA_PREFIX"
echo "PATH: $PATH"
printenv | sort

# Create necessary directories
echo "\n=== Setting up directories ==="
mkdir -p /app/static/uploads
chmod -R 755 /app/static/

# Install Python dependencies if needed
echo "\n=== Installing Python dependencies ==="
pip install -r requirements.txt

# Start Gunicorn
echo "\n=== Starting Gunicorn ==="
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application --workers 4 --timeout 120 --log-level debug
