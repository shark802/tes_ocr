# Use the official Python 3.9 image with Debian Buster for better compatibility
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    TESSERACT_CMD=/usr/bin/tesseract \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/ \
    PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/share/tesseract-ocr/4.00/tessdata/ \
    && ln -s /usr/share/tesseract-ocr/tessdata /usr/share/tesseract-ocr/4.00/tessdata \
    && echo "Verifying Tesseract installation..." \
    && ls -la /usr/bin/tesseract* || echo "Warning: No tesseract in /usr/bin" \
    && which tesseract || echo "Warning: tesseract not in PATH" \
    && find /usr -name tesseract -type f 2>/dev/null | head -5 || echo "Warning: tesseract not found in /usr" \
    && tesseract --version \
    && tesseract --list-langs \
    && echo "Tesseract installation verified successfully" \
    && echo "Creating symlinks to ensure accessibility..." \
    && (ln -sf $(which tesseract) /usr/local/bin/tesseract 2>/dev/null || true) \
    && (ln -sf $(which tesseract) /usr/bin/tesseract 2>/dev/null || true) \
    && echo "Final verification..." \
    && /usr/bin/tesseract --version || $(which tesseract) --version

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p static/uploads && \
    chmod -R 755 static/ && \
    chmod +x start.sh

# Expose the port the app runs on (Heroku will set PORT dynamically)
EXPOSE ${PORT:-10000}

# Health check (uses PORT env var or defaults to 10000)
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Command to run the application
CMD ["./start.sh"]
