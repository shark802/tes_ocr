#!/bin/bash
set -e

echo "Installing Tesseract to /app/bin..."

# Create bin directory
mkdir -p /app/bin

# Install Tesseract using apt-get (if available) or download pre-built binary
if command -v apt-get &> /dev/null; then
    echo "Using apt-get to install Tesseract..."
    apt-get update
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng
    
    # Copy tesseract to /app/bin
    if [ -f /usr/bin/tesseract ]; then
        cp /usr/bin/tesseract /app/bin/tesseract
        chmod +x /app/bin/tesseract
        echo "Tesseract copied to /app/bin/tesseract"
    fi
    
    # Copy tessdata if it exists
    if [ -d /usr/share/tesseract-ocr/tessdata ]; then
        mkdir -p /app/share/tesseract-ocr/tessdata
        cp -r /usr/share/tesseract-ocr/tessdata/* /app/share/tesseract-ocr/tessdata/ 2>/dev/null || true
        echo "Tessdata copied to /app/share/tesseract-ocr/tessdata"
    fi
else
    echo "apt-get not available, attempting to download Tesseract binary..."
    # This is a fallback - in practice, apt-get should be available via buildpack
    echo "Please ensure apt-get is available or use Docker deployment"
fi

# Verify installation
if [ -f /app/bin/tesseract ]; then
    /app/bin/tesseract --version
    echo "Tesseract successfully installed to /app/bin/tesseract"
else
    echo "ERROR: Tesseract installation failed"
    exit 1
fi

