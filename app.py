import os
import shutil
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import cv2
import numpy as np

# Set Tesseract command path - works in Docker, Heroku, and local development
def find_tesseract():
    """Find Tesseract executable - use wherever it's actually installed"""
    import logging
    import subprocess
    logger = logging.getLogger(__name__)
    
    # Strategy 1: Check environment variable
    tesseract_cmd = os.environ.get('TESSERACT_CMD')
    if tesseract_cmd and os.path.exists(tesseract_cmd) and os.access(tesseract_cmd, os.X_OK):
        logger.info(f"Tesseract found via TESSERACT_CMD: {tesseract_cmd}")
        return tesseract_cmd
    
    # Strategy 2: Use 'which' command to find where it's actually installed
    try:
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            found_path = result.stdout.strip()
            if found_path and os.path.exists(found_path):
                logger.info(f"Tesseract found via 'which': {found_path}")
                return found_path
    except Exception as e:
        logger.debug(f"'which' command failed: {e}")
    
    # Strategy 3: Use shutil.which (Python's built-in)
    tesseract_path = shutil.which('tesseract')
    if tesseract_path and os.path.exists(tesseract_path):
        logger.info(f"Tesseract found via shutil.which: {tesseract_path}")
        return tesseract_path
    
    # Strategy 4: Try common installation paths
    common_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/app/bin/tesseract',
        '/opt/homebrew/bin/tesseract',  # macOS Apple Silicon
        '/usr/bin/tesseract-ocr',
    ]
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            logger.info(f"Tesseract found at: {path}")
            return path
    
    # Strategy 5: Search filesystem for tesseract executable
    try:
        result = subprocess.run(['find', '/usr', '/app', '-name', 'tesseract', '-type', 'f', '-executable'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            if found_path and os.path.exists(found_path):
                logger.info(f"Tesseract found via find: {found_path}")
                return found_path
    except Exception as e:
        logger.debug(f"'find' command failed: {e}")
    
    # Last resort: return None and let pytesseract handle it
    logger.error("Tesseract not found in any location")
    return None

# Initialize Tesseract path - find it dynamically
tesseract_cmd = find_tesseract()
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    # Let pytesseract try to find it (will use 'tesseract' command)
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

app = Flask(__name__)

# Set TESSDATA_PREFIX - find it dynamically
def find_tessdata():
    """Find tessdata directory with language files"""
    import subprocess
    
    # If already set and exists, use it
    if os.environ.get('TESSDATA_PREFIX'):
        prefix = os.environ.get('TESSDATA_PREFIX')
        if os.path.exists(prefix) and os.path.exists(os.path.join(prefix, 'eng.traineddata')):
            return prefix
    
    # Try common locations
    tessdata_paths = [
        '/usr/share/tesseract-ocr/tessdata',
        '/usr/share/tesseract-ocr/4.00/tessdata',
        '/usr/share/tesseract-ocr/5/tessdata',
        '/app/share/tesseract-ocr/tessdata',
    ]
    
    for path in tessdata_paths:
        if os.path.exists(path):
            # Check if eng.traineddata exists in this path
            eng_file = os.path.join(path, 'eng.traineddata')
            if os.path.exists(eng_file):
                return path
    
    # Try to find using tesseract --print-parameters
    try:
        result = subprocess.run(['tesseract', '--print-parameters'], 
                              capture_output=True, text=True, timeout=2)
        # Look for tessdata path in output
        for line in result.stderr.split('\n'):
            if 'tessdata' in line.lower():
                # Extract path from line
                import re
                match = re.search(r'([/\w]+tessdata)', line)
                if match:
                    potential_path = match.group(1)
                    if os.path.exists(potential_path):
                        return potential_path
    except:
        pass
    
    # Last resort: return default
    return '/usr/share/tesseract-ocr/tessdata'

# Set TESSDATA_PREFIX
tessdata_prefix = find_tessdata()
os.environ['TESSDATA_PREFIX'] = tessdata_prefix

# Verify eng.traineddata exists
eng_file = os.path.join(tessdata_prefix, 'eng.traineddata')
if not os.path.exists(eng_file):
    import logging
    logging.warning(f"eng.traineddata not found at {eng_file}")
    # Try to find it
    import subprocess
    try:
        result = subprocess.run(['find', '/usr', '/app', '-name', 'eng.traineddata', '-type', 'f'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            found_dir = os.path.dirname(found_path)
            logging.warning(f"Found eng.traineddata at {found_path}, updating TESSDATA_PREFIX to {found_dir}")
            os.environ['TESSDATA_PREFIX'] = found_dir
            tessdata_prefix = found_dir
    except:
        pass

# Verify Tesseract is accessible after app creation
def verify_tesseract():
    """Verify Tesseract is accessible and log diagnostics"""
    current_cmd = pytesseract.pytesseract.tesseract_cmd
    
    try:
        version = pytesseract.get_tesseract_version()
        app.logger.info(f"✓ Tesseract found at: {current_cmd}, version: {version}")
        app.logger.info(f"  TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX', 'Not set')}")
        return True
    except pytesseract.TesseractNotFoundError as e:
        app.logger.error(f"✗ Tesseract not found")
        app.logger.error(f"  Current CMD: {current_cmd}")
        app.logger.error(f"  Error: {str(e)}")
        app.logger.error(f"  PATH: {os.environ.get('PATH', 'Not set')}")
        app.logger.error(f"  TESSERACT_CMD: {os.environ.get('TESSERACT_CMD', 'Not set')}")
        
        # Try to find where tesseract might be
        import subprocess
        app.logger.warning("  Attempting to locate Tesseract...")
        
        # Try 'which' command
        try:
            result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True, timeout=2)
            app.logger.warning(f"  'which tesseract' exit code: {result.returncode}, output: {result.stdout.strip() or '(empty)'}")
            if result.returncode == 0:
                found_path = result.stdout.strip()
                if found_path:
                    app.logger.warning(f"  'which tesseract' found: {found_path}")
                    if found_path != current_cmd:
                        app.logger.warning(f"  Attempting to use {found_path}")
                        pytesseract.pytesseract.tesseract_cmd = found_path
                        try:
                            version = pytesseract.get_tesseract_version()
                            app.logger.info(f"✓ Successfully switched to: {found_path}, version: {version}")
                            return True
                        except Exception as retry_error:
                            app.logger.error(f"  Failed to use {found_path}: {retry_error}")
        except Exception as find_error:
            app.logger.error(f"  'which' command failed: {find_error}")
        
        # Try filesystem search
        try:
            app.logger.warning("  Searching filesystem for tesseract...")
            result = subprocess.run(['find', '/usr', '/app', '-name', 'tesseract', '-type', 'f', '-executable', '2>/dev/null'], 
                                  capture_output=True, text=True, timeout=5, shell=False)
            app.logger.warning(f"  'find' exit code: {result.returncode}")
            if result.stdout.strip():
                app.logger.warning(f"  'find' output: {result.stdout.strip()[:200]}")
            if result.returncode == 0 and result.stdout.strip():
                found_paths = result.stdout.strip().split('\n')
                app.logger.warning(f"  Found {len(found_paths)} tesseract executables: {found_paths[:3]}")
                for found_path in found_paths[:3]:
                    if found_path and os.path.exists(found_path):
                        try:
                            app.logger.warning(f"  Trying: {found_path}")
                            pytesseract.pytesseract.tesseract_cmd = found_path
                            version = pytesseract.get_tesseract_version()
                            app.logger.info(f"✓ Successfully using: {found_path}, version: {version}")
                            return True
                        except Exception as try_error:
                            app.logger.debug(f"  Failed to use {found_path}: {try_error}")
                            continue
            else:
                app.logger.error("  'find' found no tesseract executables")
        except Exception as find_error:
            app.logger.error(f"  'find' command failed: {find_error}")
        
        # Check common locations directly
        app.logger.warning("  Checking common installation paths...")
        common_paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract', '/app/bin/tesseract']
        for path in common_paths:
            if os.path.exists(path):
                app.logger.warning(f"  Found at {path}, attempting to use...")
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    version = pytesseract.get_tesseract_version()
                    app.logger.info(f"✓ Successfully using: {path}, version: {version}")
                    return True
                except Exception as try_error:
                    app.logger.debug(f"  Failed to use {path}: {try_error}")
        
        # Check if file exists (only if current_cmd is not None)
        if current_cmd and os.path.exists(current_cmd):
            app.logger.error(f"  File exists at {current_cmd} but may not be executable")
            import stat
            file_stat = os.stat(current_cmd)
            app.logger.error(f"  File permissions: {oct(file_stat.st_mode)}")
        elif current_cmd:
            app.logger.error(f"  File does not exist: {current_cmd}")
        
        app.logger.warning("  Tesseract will not be available. OCR features will fail.")
        return False
    except Exception as e:
        app.logger.error(f"✗ Unexpected error verifying Tesseract: {str(e)}", exc_info=True)
        return False

# Verify on startup (don't crash if not found)
# Delay verification until after app is fully initialized
def init_tesseract():
    """Initialize Tesseract verification - called after app is ready"""
    try:
        verify_tesseract()
    except Exception as e:
        # Use basic logging if app.logger isn't available yet
        try:
            app.logger.error(f"Error during Tesseract verification: {e}", exc_info=True)
        except:
            import logging
            logging.error(f"Error during Tesseract verification: {e}", exc_info=True)

# Don't verify immediately - will be called after app starts
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def clean_date_string(date_str):
    """Clean and normalize date string for comparison"""
    if not date_str:
        return ""
    # Remove all non-alphanumeric characters and convert to lowercase
    cleaned = re.sub(r'[^a-z0-9]', '', date_str.lower())
    
    # Handle month names (convert to numbers if needed)
    # Include full month names, 3-letter abbreviations, and other common variations
    # Order matters: check longer names first to avoid partial matches
    month_map = {
        # Full month names
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        # 3-letter abbreviations
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
        'oct': '10', 'nov': '11', 'dec': '12',
        # Other common variations (keep for backward compatibility)
        'june': '06', 'july': '07'
    }
    
    # Check for month names and convert to numbers
    # Sort by length (longest first) to match full names before abbreviations
    for month, num in sorted(month_map.items(), key=lambda x: len(x[0]), reverse=True):
        if month in cleaned:
            cleaned = cleaned.replace(month, num)
            break
    
    return cleaned

def clean_text_for_matching(text):
    """Clean and normalize text for case-insensitive matching and handle special characters"""
    if not text:
        return ""
    # Convert to lowercase and remove all non-alphanumeric characters
    return re.sub(r'[^a-z0-9]', '', text.lower())

@app.route('/api/verify_student', methods=['POST'])
def verify_student():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    last_name = request.form.get('last_name', '').strip()
    birthday = request.form.get('birthday', '').strip()
    student_id = request.form.get('student_id', '').strip()
    
    if not all([last_name, birthday, student_id]):
        return jsonify({
            'success': False,
            'error': 'Last name, birthday, and student ID are required'
        }), 400

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    try:
        # Process the image and extract text
        image = Image.open(file)
        image = image.convert('L')
        
        # Resize for better OCR
        base_width = 2000
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
        
        # Convert to binary image
        img_array = np.array(image)
        _, binary_image = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        image = Image.fromarray(binary_image)
        
        # Extract text with Tesseract using multiple configurations
        configs = [
            r'--oem 3 --psm 6',
            r'--oem 3 --psm 4',
            r'--oem 3 --psm 11'
        ]
        
        all_text = []
        tesseract_found = False
        
        for config in configs:
            try:
                current_text = pytesseract.image_to_string(image, config=config)
                if current_text.strip():
                    all_text.append(current_text.strip())
                    tesseract_found = True
            except pytesseract.TesseractNotFoundError:
                app.logger.warning(f"Tesseract not found at {pytesseract.pytesseract.tesseract_cmd}, attempting re-detection...")
                # Try to re-detect Tesseract at runtime
                if verify_tesseract():
                    app.logger.info(f"Tesseract re-detected, retrying OCR...")
                    try:
                        current_text = pytesseract.image_to_string(image, config=config)
                        if current_text.strip():
                            all_text.append(current_text.strip())
                            tesseract_found = True
                    except Exception as retry_error:
                        app.logger.error(f"OCR still failed after re-detection: {str(retry_error)}")
                else:
                    app.logger.error(f"Tesseract re-detection failed. CMD: {pytesseract.pytesseract.tesseract_cmd}")
                    # Only return error if this is the first config and we haven't found any text yet
                    if not all_text and config == configs[0]:
                        return jsonify({
                            'success': False,
                            'error': 'Tesseract OCR is not installed or not found in PATH. Please check the server configuration.',
                            'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd,
                            'path': os.environ.get('PATH', 'Not set')
                        }), 500
            except pytesseract.TesseractError as e:
                app.logger.error(f"Tesseract error: {str(e)}")
                # Continue with other configs if one fails
                continue
        
        if not all_text:
            return jsonify({
                'success': False,
                'error': 'Failed to extract text from image. Tesseract may not be properly configured.',
                'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd
            }), 500
        
        # Combine all extracted text
        full_text = ' '.join(all_text)
        
        # Clean and normalize all text for comparison
        clean_extracted = clean_text_for_matching(full_text)
        clean_last_name = clean_text_for_matching(last_name)
        clean_student_id = clean_text_for_matching(student_id).replace(' ', '')
        
        # Special handling for birthday to handle different formats
        clean_birthday = clean_date_string(birthday)
        clean_extracted_date = clean_date_string(full_text)
        
        # Verification
        last_name_found = clean_last_name in clean_extracted
        birthday_found = clean_birthday and clean_birthday in clean_extracted_date
        student_id_found = clean_student_id and clean_student_id in clean_extracted.replace(' ', '')
        
        # Find where the data was found (for debugging)
        def find_match_position(needle, haystack, is_date=False):
            """Find the position of needle in haystack, handling different formats"""
            if not needle:
                return None
                
            # Try exact match first
            needle_lower = needle.lower()
            haystack_lower = haystack.lower()
            
            # For dates, try multiple formats
            if is_date:
                # Try with different separators
                formats_to_try = [
                    needle_lower,
                    needle_lower.replace(' ', ''),
                    needle_lower.replace(',', ''),
                    needle_lower.replace(' ', '').replace(',', '')
                ]
                for fmt in formats_to_try:
                    pos = haystack_lower.find(fmt)
                    if pos != -1:
                        return f"...{haystack[max(0, pos-10):min(len(haystack), pos+len(fmt)+10)]}..."
            else:
                pos = haystack_lower.find(needle_lower)
                if pos != -1:
                    return f"...{haystack[max(0, pos-10):min(len(haystack), pos+len(needle)+10)]}..."
            return None
        
        return jsonify({
            'success': True,
            'verified': all([last_name_found, birthday_found, student_id_found]),
            'verification': {
                'last_name': {
                    'provided': last_name,
                    'verified': last_name_found,
                    'found_in': find_match_position(last_name, full_text)
                },
                'birthday': {
                    'provided': birthday,
                    'verified': birthday_found,
                    'found_in': find_match_position(birthday, full_text, is_date=True),
                    'normalized': clean_birthday,
                    'found_normalized': clean_extracted_date
                },
                'student_id': {
                    'provided': student_id,
                    'verified': student_id_found,
                    'found_in': find_match_position(student_id, full_text)
                }
            },
            'extracted_text': full_text,  # For debugging
            'cleaned_extracted_text': clean_extracted  # For debugging
        })

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f"Error processing request: {str(e)}"
        }), 500
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    # Initialize Tesseract on first health check
    if not hasattr(app, '_tesseract_initialized'):
        try:
            init_tesseract()
            app._tesseract_initialized = True
        except:
            pass
    
    # Try to re-verify Tesseract if not available
    if not is_tesseract_available():
        app.logger.warning("Tesseract not available, attempting to re-detect...")
        try:
            verify_tesseract()
        except:
            pass
    
    return jsonify({
        'status': 'healthy',
        'tesseract': 'available' if is_tesseract_available() else 'unavailable',
        'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd or 'Not found',
        'path': os.environ.get('PATH', 'Not set')
    }), 200

@app.route('/debug/tesseract')
def debug_tesseract():
    """Debug endpoint to check Tesseract installation"""
    import subprocess
    diagnostics = {
        'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd,
        'path': os.environ.get('PATH', 'Not set'),
        'tesseract_env': os.environ.get('TESSERACT_CMD', 'Not set'),
        'tessdata_prefix': os.environ.get('TESSDATA_PREFIX', 'Not set'),
        'file_exists': os.path.exists(pytesseract.pytesseract.tesseract_cmd) if pytesseract.pytesseract.tesseract_cmd else False,
        'is_executable': os.access(pytesseract.pytesseract.tesseract_cmd, os.X_OK) if pytesseract.pytesseract.tesseract_cmd and os.path.exists(pytesseract.pytesseract.tesseract_cmd) else False,
    }
    
    # Try to find tesseract using which
    try:
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True, timeout=2)
        diagnostics['which_tesseract'] = result.stdout.strip() if result.returncode == 0 else 'Not found'
    except:
        diagnostics['which_tesseract'] = 'Error running which'
    
    # Try to find tesseract using find
    try:
        result = subprocess.run(['find', '/usr', '-name', 'tesseract', '-type', 'f'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            diagnostics['find_tesseract'] = result.stdout.strip().split('\n')[:5]  # First 5 results
        else:
            diagnostics['find_tesseract'] = 'Not found'
    except:
        diagnostics['find_tesseract'] = 'Error running find'
    
    # Try to get version
    try:
        version = pytesseract.get_tesseract_version()
        diagnostics['version'] = version
        diagnostics['available'] = True
    except Exception as e:
        diagnostics['version'] = f'Error: {str(e)}'
        diagnostics['available'] = False
    
    return jsonify(diagnostics), 200

def is_tesseract_available():
    """Check if Tesseract is available"""
    try:
        pytesseract.get_tesseract_version()
        return True
    except (pytesseract.TesseractNotFoundError, Exception):
        return False

def clean_text_for_matching(text):
    """Clean and normalize text for matching"""
    return re.sub(r'[^\w\s]', ' ', text.lower())

def is_name_in_text(name, text):
    """
    Check if the name exists in the extracted text with flexible matching
    """
    if not name or not text:
        return False
    
    # Clean and normalize both strings
    clean_name = clean_text_for_matching(name)
    clean_text = clean_text_for_matching(text)
    
    # Check for exact match first
    if clean_name in clean_text:
        return True
    
    # Split name into meaningful parts
    name_parts = [part for part in clean_name.split() 
                 if len(part) > 1 and 
                 part not in ['jr', 'sr', 'ii', 'iii', 'iv', 'v', 'of', 'the', 'and']]
    
    # If we have multiple name parts, try different combinations
    if len(name_parts) > 1:
        # Try first name + last name
        first_last = f"{name_parts[0]} {name_parts[-1]}"
        if first_last in clean_text:
            return True
        
        # Try first name + middle initial + last name
        if len(name_parts) > 2:
            first_middle_last = f"{name_parts[0]} {name_parts[1][0]} {name_parts[2]}"
            if first_middle_last in clean_text.replace(' ', ''):
                return True
    
    # Check if most name parts exist in the text
    matching_parts = []
    for part in name_parts:
        # For longer words, check for partial matches
        if len(part) > 3:
            if (part in clean_text or 
                any(word.startswith(part) or word.endswith(part) 
                    for word in clean_text.split())):
                matching_parts.append(part)
        elif part in clean_text:
            matching_parts.append(part)
    
    # If at least 60% of name parts match, consider it a match
    if len(name_parts) > 0 and len(matching_parts) / len(name_parts) >= 0.6:
        return True
    
    return False

def is_id_in_text(id_number, text):
    """
    Check if the ID exists in the extracted text with flexible matching
    """
    if not id_number or not text:
        return False
    
    # Clean and normalize the ID - keep only digits
    clean_id = re.sub(r'[^\d]', '', id_number)
    if not clean_id:  # If no digits found in the ID
        return False
    
    # Clean the text - keep only digits and spaces
    clean_text = re.sub(r'[^\d\s]', ' ', text)
    
    # Check for exact match first
    if clean_id in clean_text:
        return True
    
    # For longer IDs, check if parts of it exist in the text
    if len(clean_id) > 5:
        # Try first 6 digits if ID is long enough
        first_part = clean_id[:6]
        if first_part in clean_text:
            return True
        
        # Try last 6 digits
        last_part = clean_id[-6:]
        if last_part in clean_text:
            return True
    
    # Check if the ID is present with common separators
    id_formats = [
        clean_id,  # 1234567890
        '-'.join([clean_id[:4], clean_id[4:]]),  # 1234-567890
        ' '.join([clean_id[:4], clean_id[4:]]),  # 1234 567890
        ' '.join([clean_id[i:i+4] for i in range(0, len(clean_id), 4)]),  # 1234 5678 90
    ]
    
    return any(fmt in text for fmt in id_formats if len(fmt) > 3)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    name = request.form.get('name', '').strip()
    id_number = request.form.get('id_number', '').strip()
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload a PNG, JPG, or JPEG image.'}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Open and preprocess the image
        image = Image.open(filepath)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Resize image to improve OCR accuracy
        base_width = 2000
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
        
        # Apply thresholding to get a binary image
        img_array = np.array(image)
        _, binary_image = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        image = Image.fromarray(binary_image)
        
        # Try multiple OCR configurations
        configs = [
            r'--oem 3 --psm 6',  # Assume a single uniform block of text
            r'--oem 3 --psm 4',  # Assume a single column of text of variable sizes
            r'--oem 3 --psm 11'  # Sparse text with OSD
        ]
        
        all_text = []
        tesseract_found = False
        
        for config in configs:
            try:
                current_text = pytesseract.image_to_string(image, config=config)
                if current_text.strip():
                    all_text.append(current_text.strip())
                    tesseract_found = True
            except pytesseract.TesseractNotFoundError:
                app.logger.warning(f"Tesseract not found at {pytesseract.pytesseract.tesseract_cmd}, attempting re-detection...")
                # Try to re-detect Tesseract at runtime
                if verify_tesseract():
                    app.logger.info(f"Tesseract re-detected, retrying OCR...")
                    try:
                        current_text = pytesseract.image_to_string(image, config=config)
                        if current_text.strip():
                            all_text.append(current_text.strip())
                            tesseract_found = True
                    except Exception as retry_error:
                        app.logger.error(f"OCR still failed after re-detection: {str(retry_error)}")
                else:
                    app.logger.error(f"Tesseract re-detection failed. CMD: {pytesseract.pytesseract.tesseract_cmd}")
                    # Only return error if this is the first config and we haven't found any text yet
                    if not all_text and config == configs[0]:
                        return jsonify({
                            'error': 'Tesseract OCR is not installed or not found in PATH. Please check the server configuration.',
                            'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd,
                            'path': os.environ.get('PATH', 'Not set')
                        }), 500
            except pytesseract.TesseractError as e:
                app.logger.error(f"Tesseract error: {str(e)}")
                # Continue with other configs if one fails
                continue
        
        if not all_text:
            return jsonify({
                'error': 'Failed to extract text from image. Tesseract may not be properly configured.',
                'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd
            }), 500
        
        # Combine all extracted text and remove duplicate lines
        unique_lines = []
        seen = set()
        for text in all_text:
            for line in text.split('\n'):
                line = line.strip()
                if line and line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
        
        # Join lines with newlines for better readability
        final_text = '\n'.join(unique_lines)
        
        # Perform name verification if name is provided
        name_found = is_name_in_text(name, final_text) if name else False
        
        # Perform ID verification if ID is provided
        id_found = is_id_in_text(id_number, final_text) if id_number else False
        
        return jsonify({
            'success': True,
            'text': final_text,
            'image_url': f'/static/uploads/{filename}',
            'name_found': name_found,
            'id_found': id_found
        })
        
    except Exception as e:
        app.logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error processing request: {str(e)}',
            'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
