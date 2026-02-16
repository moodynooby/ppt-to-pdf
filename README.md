# PPT to PDF Converter

A modern web-based application to convert PowerPoint (PPT/PPTX) files to PDF format using Flask and LibreOffice.

## Features

- 🎯 **Drag & Drop Interface** - Easy file selection with drag and drop support
- 📁 **Multiple File Support** - Convert multiple files at once
- 🚀 **Fast Conversion** - Uses LibreOffice for high-quality conversion
- 📊 **Real-time Feedback** - Progress tracking and detailed results
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 💾 **Direct Download** - Download converted files directly from the browser

## Prerequisites

- Python 3.12+
- LibreOffice (with headless support)
- pip (Python package manager)

### Installing LibreOffice

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

**macOS:**
```bash
brew install libreoffice
```

**Windows:**
Download and install from [LibreOffice Official Site](https://www.libreoffice.org/download/)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hard02/ppt-to-pdf.git
cd ppt-to-pdf
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Select or drag and drop PowerPoint files (PPT/PPTX)

4. Click "Convert to PDF"

5. Download the converted PDF files

## Project Structure

```
ppt-to-pdf/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Client-side logic
├── uploads/              # Temporary upload folder
├── output/               # Converted PDF files
└── pyproject.toml        # Project metadata
```

## Configuration

Edit `app.py` to customize:

- **MAX_CONTENT_LENGTH** - Maximum file size (default: 500MB)
- **UPLOAD_FOLDER** - Temporary upload directory
- **OUTPUT_FOLDER** - Output directory for PDFs
- **Port** - Change default port (5000)

## API Endpoints

### POST `/api/upload`
Upload PowerPoint files
- Returns: List of uploaded files with metadata

### POST `/api/convert`
Convert uploaded files to PDF
- Body: JSON with file metadata
- Returns: Conversion results (successful + failed)

### GET `/api/files`
Get list of converted PDF files

### GET `/download/<filename>`
Download a converted PDF file

## Troubleshooting

**LibreOffice not found:**
- Ensure LibreOffice is installed and in PATH
- Try: `libreoffice --version`

**Conversion timeout:**
- Increase timeout in `app.py` (_convert_thread method)
- Check if system has enough resources

**Permission denied:**
- Ensure `uploads/` and `output/` folders exist and are writable
- Check folder permissions: `chmod 755 uploads output`

## License

See LICENSE file for details.

## Support

For issues and feature requests, please open an issue on GitHub.
