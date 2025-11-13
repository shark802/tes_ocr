# OCR Document Verification System

A Flask-based web application that verifies names and IDs in uploaded documents using OCR (Optical Character Recognition) with Tesseract.

## Features

- Upload document images (PNG, JPG, JPEG)
- Verify names in the document text
- Optional ID number verification
- Web interface and REST API
- Responsive design

## Prerequisites

- Python 3.9+
- Tesseract OCR
- pip

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ocr-verification.git
   cd ocr-verification
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract**
   - **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt install tesseract-ocr`

## Configuration

1. **Environment Variables**
   Create a `.env` file:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   TESSERACT_CMD=/usr/bin/tesseract  # Update this path
   ```

## Usage

### Web Interface
1. Run the application:
   ```bash
   flask run
   ```
2. Open `http://localhost:5000` in your browser
3. Enter the name to verify
4. (Optional) Enter an ID number
5. Upload a document image
6. Click "Verify"

### API Endpoints

**Verify Document**
- **URL**: `/api/verify`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `name`: (required) Name to verify
  - `id_number`: (optional) ID number to verify
  - `file`: (required) Image file (JPG, PNG)

**Example Request**
```bash
curl -X POST http://localhost:5000/api/verify \
  -F "name=John Doe" \
  -F "id_number=12345" \
  -F "file=@document.jpg"
```

**Example Response**
```json
{
  "success": true,
  "verification": {
    "name": {
      "provided": "John Doe",
      "verified": true,
      "status": "verified"
    },
    "id": {
      "provided": "12345",
      "verified": true,
      "status": "verified"
    },
    "document": {
      "text_extracted": true,
      "text_length": 1250
    }
  }
}
```

## Deployment

### Render.com
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your repository
4. Set environment variables:
   - `PYTHON_VERSION`: 3.9.13
   - `TESSERACT_CMD`: /usr/bin/tesseract
5. Deploy!

## Troubleshooting

- **Tesseract not found**: Ensure Tesseract is installed and the path is correct
- **Image processing errors**: Check file format and size
- **API errors**: Verify all required parameters are provided

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see the [LICENSE](LICENSE) file for details
