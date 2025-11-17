# Use the official Python 3.9 image with Debian Bullseye for better compatibility and security
FROM python:3.9-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    TESSERACT_CMD=/usr/bin/tesseract \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata \
    PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
    LD_LIBRARY_PATH="/usr/local/lib:/usr/lib/x86_64-linux-gnu:/usr/lib"

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-script-latn \
    libleptonica-dev \
    libtesseract-dev \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/tesseract /usr/local/bin/tesseract \
    && tesseract --version \
    && tesseract --list-langs

# Verify Tesseract installation
RUN tesseract --version && \
    tesseract --list-langs

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/static/uploads && \
    chmod -R 755 /app/static/ && \
    chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["/app/start.sh"]

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["./start.sh"]

# Expose the port the app runs on
EXPOSE 10000

# Health check with queue status
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Install additional Python packages for testing and monitoring
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    gunicorn \
    gevent

# Set environment variables for Gunicorn
ENV GUNICORN_CMD_ARGS="--workers=5 --worker-class=gevent --worker-connections=1000 --timeout=120 --bind=0.0.0.0:10000"

# Command to run the application with Gunicorn
CMD ["gunicorn", "app:app"]
