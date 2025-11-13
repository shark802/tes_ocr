#!/bin/bash

# Install Tesseract and its dependencies
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
pip install -r requirements.txt

# Run the Gunicorn server
exec gunicorn --bind 0.0.0.0:$PORT --timeout 500 --workers 2 --threads 4 --worker-class=gthread wsgi:app
