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
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation and set up paths
RUN echo "Verifying Tesseract installation..." && \
    TESSERACT_PATH=$(which tesseract) && \
    if [ -z "$TESSERACT_PATH" ]; then \
        echo "ERROR: Tesseract not found after installation!" && \
        find /usr -name "*tesseract*" -type f 2>/dev/null | head -10 && \
        exit 1; \
    fi && \
    echo "Tesseract found at: $TESSERACT_PATH" && \
    $TESSERACT_PATH --version && \
    $TESSERACT_PATH --list-langs && \
    mkdir -p /usr/share/tesseract-ocr/4.00/tessdata/ && \
    if [ -d /usr/share/tesseract-ocr/tessdata ]; then \
        ln -sf /usr/share/tesseract-ocr/tessdata /usr/share/tesseract-ocr/4.00/tessdata; \
    fi && \
    echo "Creating symlinks..." && \
    ln -sf "$TESSERACT_PATH" /usr/local/bin/tesseract && \
    ln -sf "$TESSERACT_PATH" /usr/bin/tesseract && \
    echo "Final verification..." && \
    /usr/bin/tesseract --version && \
    echo "Tesseract installation verified successfully"

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
