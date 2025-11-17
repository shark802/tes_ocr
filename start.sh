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

# Install Python dependencies
pip install -r requirements.txt

# Start Gunicorn with better logging
echo "Starting Gunicorn..."
exec gunicorn --workers 4 --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - wsgi:application
