#!/bin/bash
set -e

# Print environment variables for debugging
echo "Environment variables:"
echo "TESSDATA_PREFIX: ${TESSDATA_PREFIX:-Not Set}"
echo "PATH: $PATH"

# Create necessary directories
mkdir -p static/uploads

# Set permissions
chmod -R 755 static/

# Install Tesseract and its dependencies
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
which tesseract || echo "Tesseract not found in PATH"
tesseract --version || echo "Failed to get Tesseract version"

# Check Tesseract languages
echo "Available Tesseract languages:"
tesseract --list-langs || echo "Failed to list Tesseract languages"

# Install Python dependencies
pip install -r requirements.txt

# Start Gunicorn with better logging
echo "Starting Gunicorn..."
exec gunicorn --workers 4 --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - app:app
