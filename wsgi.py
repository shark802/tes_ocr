import os
import os
import sys
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment variables
logger.info("=== Environment Variables ===")
for key in os.environ:
    logger.info(f"{key}: {os.environ.get(key)}")

# Log Python path
logger.info("=== Python Path ===")
for path in sys.path:
    logger.info(path)

# Verify Tesseract is accessible
try:
    import pytesseract
    logger.info("=== Tesseract Configuration ===")
    logger.info(f"Tesseract command: {pytesseract.pytesseract.tesseract_cmd}")
    logger.info(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")
    
    # Test Tesseract
    version = pytesseract.get_tesseract_version()
    logger.info(f"Tesseract version: {version}")
    
    langs = pytesseract.get_languages(config='')
    logger.info(f"Available languages: {langs}")
    
except Exception as e:
    logger.error(f"Error initializing Tesseract: {str(e)}")
    raise

# This is used when running with gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)
