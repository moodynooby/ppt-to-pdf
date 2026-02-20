class PPTConverter {
    constructor() {
        this.files = [];
        this.init();
    }

    init() {
        this.setupDragDrop();
        this.setupEventListeners();
    }

    setupDragDrop() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // Keyboard support
        uploadArea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    setupEventListeners() {
        document.getElementById('convertBtn').addEventListener('click', () => this.convert());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
    }

    handleFiles(fileList) {
        for (let file of fileList) {
            if (this.isValidFile(file)) {
                const fileObj = {
                    id: this.generateId(),
                    name: file.name,
                    size: file.size,
                    file: file
                };
                this.files.push(fileObj);
            }
        }
        this.updateFilesList();
    }

    isValidFile(file) {
        const validTypes = ['ppt', 'pptx', 'doc', 'docx'];
        const extension = file.name.split('.').pop().toLowerCase();
        return validTypes.includes(extension);
    }

    generateId() {
        return `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    updateFilesList() {
        const filesList = document.getElementById('filesList');
        const fileCount = document.getElementById('fileCount');

        fileCount.textContent = `${this.files.length} file${this.files.length !== 1 ? 's' : ''}`;

        if (this.files.length === 0) {
            filesList.innerHTML = '<p class="empty-state">No files selected. Drag and drop or click to add files.</p>';
            document.getElementById('convertBtn').disabled = true;
            return;
        }

        document.getElementById('convertBtn').disabled = false;

        filesList.innerHTML = this.files.map(file => `
            <div class="file-item" data-id="${file.id}">
                <div class="file-item-info">
                    <div class="file-item-icon">
                        ${this.getFileExtension(file.name)}
                    </div>
                    <div class="file-item-details">
                        <div class="file-item-name">${this.escapeHtml(file.name)}</div>
                        <div class="file-item-size">${this.formatSize(file.size)}</div>
                    </div>
                </div>
                <button class="file-item-remove" onclick="converter.removeFile('${file.id}')" aria-label="Remove ${this.escapeHtml(file.name)}">×</button>
            </div>
        `).join('');
    }

    getFileExtension(filename) {
        return filename.split('.').pop().toUpperCase();
    }

    formatSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    removeFile(id) {
        this.files = this.files.filter(f => f.id !== id);
        this.updateFilesList();
    }

    clearAll() {
        if (this.files.length === 0) return;

        if (confirm('Are you sure you want to clear all files?')) {
            this.files = [];
            this.updateFilesList();
            document.getElementById('fileInput').value = '';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('generalError');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    }

    async convert() {
        if (this.files.length === 0) {
            this.showError('Please add files to convert');
            return;
        }

        const errorDiv = document.getElementById('generalError');
        if (errorDiv) errorDiv.style.display = 'none';

        // Create FormData and upload files
        const formData = new FormData();
        this.files.forEach(file => {
            formData.append('files', file.file);
        });

        try {
            document.getElementById('convertBtn').disabled = true;
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            // Upload files
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const uploadData = await uploadResponse.json();

            if (!uploadResponse.ok) {
                throw new Error(uploadData.error || 'Upload failed');
            }

            // Convert files
            const convertResponse = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    files: uploadData.uploaded
                })
            });

            const convertData = await convertResponse.json();

            if (!convertResponse.ok) {
                throw new Error(convertData.error || 'Conversion failed');
            }

            this.showResults(convertData);

        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            document.getElementById('convertBtn').disabled = false;
            document.getElementById('progressSection').style.display = 'none';
        }
    }

    showResults(data) {
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

        const successResults = document.getElementById('successResults');
        const failedResults = document.getElementById('failedResults');
        const successList = document.getElementById('successList');
        const failedList = document.getElementById('failedList');

        // Show successful conversions
        if (data.converted.length > 0) {
            successResults.style.display = 'block';
            successList.innerHTML = data.converted.map(result => `
                <div class="result-item success">
                    <div>
                        <div class="result-name">${this.escapeHtml(result.name)}</div>
                    </div>
                    <a href="/download/${encodeURIComponent(result.pdf_name)}" class="result-action" download>Download</a>
                </div>
            `).join('');
        } else {
            successResults.style.display = 'none';
        }

        // Show failed conversions
        if (data.failed.length > 0) {
            failedResults.style.display = 'block';
            failedList.innerHTML = data.failed.map(result => `
                <div class="result-item error">
                    <div>
                        <div class="result-name">${this.escapeHtml(result.name)}</div>
                        <div class="result-error">${this.escapeHtml(result.error)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            failedResults.style.display = 'none';
        }

        // Clear files list after conversion
        this.files = [];
        this.updateFilesList();
        document.getElementById('fileInput').value = '';
    }
}

// Initialize converter when DOM is ready
let converter;
document.addEventListener('DOMContentLoaded', () => {
    converter = new PPTConverter();
});
