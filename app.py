import os
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
app.config['OUTPUT_FOLDER'] = os.path.abspath('output')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'ppt', 'pptx', 'doc', 'docx'}

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle multiple file uploads"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    uploaded = []
    errors = []
    
    for file in files:
        if file.filename == '':
            errors.append('Empty filename')
            continue
        
        if not allowed_file(file.filename):
            errors.append(f'{file.filename}: Invalid file type. Use .ppt, .pptx, .doc, or .docx')
            continue
        
        filename = secure_filename(file.filename)
        # Add unique ID to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        uploaded.append({
            'id': unique_id,
            'name': file.filename,
            'filename': filename,
            'size': os.path.getsize(filepath)
        })
    
    return jsonify({
        'uploaded': uploaded,
        'errors': errors
    }), 200 if uploaded else 400

@app.route('/api/convert', methods=['POST'])
def convert_files():
    """Convert uploaded files to PDF"""
    data = request.get_json()
    files = data.get('files', [])
    
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    failed = []
    
    for file_info in files:
        filename = file_info.get('filename')
        original_name = file_info.get('name')
        
        if not filename:
            failed.append({'name': original_name, 'error': 'Invalid file info'})
            continue
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            failed.append({'name': original_name, 'error': 'File not found'})
            continue
        
        try:
            # Get the base name without extension for the uploaded file
            base_name = os.path.splitext(filename)[0]
            pdf_name = f"{base_name}.pdf"
            
            # Run LibreOffice conversion
            result = subprocess.run(
                ['libreoffice', '--headless', '--norestore', '--convert-to', 'pdf', 
                 '--outdir', app.config['OUTPUT_FOLDER'], filepath],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Check if PDF was created
                pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_name)
                if os.path.exists(pdf_path):
                    results.append({
                        'name': original_name,
                        'pdf_name': pdf_name,
                        'success': True
                    })
                else:
                    # Log stderr for debugging
                    error_msg = result.stderr.strip() if result.stderr else 'PDF not created'
                    failed.append({'name': original_name, 'error': error_msg})
            else:
                failed.append({
                    'name': original_name,
                    'error': result.stderr or 'Conversion failed'
                })
        
        except subprocess.TimeoutExpired:
            failed.append({'name': original_name, 'error': 'Conversion timeout'})
        except Exception as e:
            failed.append({'name': original_name, 'error': str(e)})
        
        finally:
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
    
    return jsonify({
        'converted': results,
        'failed': failed,
        'output_folder': app.config['OUTPUT_FOLDER']
    }), 200

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of converted PDF files"""
    files = []
    try:
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if filename.endswith('.pdf'):
                filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
    except:
        pass
    
    return jsonify({'files': files}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download converted PDF"""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
