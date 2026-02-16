import os
import subprocess
import threading
from tkinter import Tk, Frame, Button, Label, Listbox, Scrollbar, filedialog, messagebox, StringVar
from tkinter.ttk import Progressbar
from pathlib import Path

class PPTToPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PPT to PDF Converter")
        self.root.geometry("1200x1000")
        self.root.resizable(True, True)
        
        self.files = []
        self.output_folder = os.path.join(os.getcwd(), 'output')
        os.makedirs(self.output_folder, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        title = Label(header_frame, text="PPT to PDF Converter", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=10)
        
        # File list frame
        list_frame = Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        list_label = Label(list_frame, text="Files to Convert:", font=("Arial", 10, "bold"))
        list_label.pack(anchor="w")
        
        # Listbox with scrollbar
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10), height=12)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Enable drag and drop
        self.setup_drag_drop()
        
        # Button frame
        button_frame = Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        add_btn = Button(button_frame, text="Add Files", command=self.add_files, bg="#3498db", fg="white", padx=10, pady=8)
        add_btn.pack(side="left", padx=5)
        
        add_folder_btn = Button(button_frame, text="Add Folder", command=self.add_folder, bg="#3498db", fg="white", padx=10, pady=8)
        add_folder_btn.pack(side="left", padx=5)
        
        remove_btn = Button(button_frame, text="Remove Selected", command=self.remove_file, bg="#e74c3c", fg="white", padx=10, pady=8)
        remove_btn.pack(side="left", padx=5)
        
        clear_btn = Button(button_frame, text="Clear All", command=self.clear_files, bg="#e74c3c", fg="white", padx=10, pady=8)
        clear_btn.pack(side="left", padx=5)
        
        # Progress frame
        progress_frame = Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_label = Label(progress_frame, text="", font=("Arial", 9))
        self.progress_label.pack(anchor="w")
        
        self.progress = Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill="x", pady=5)
        
        # Convert button
        convert_frame = Frame(self.root)
        convert_frame.pack(fill="x", padx=10, pady=10)
        
        self.convert_btn = Button(convert_frame, text="Convert to PDF", command=self.convert_files, bg="#27ae60", fg="white", padx=20, pady=10, font=("Arial", 12, "bold"))
        self.convert_btn.pack(fill="x")
        
        # Status label
        self.status_label = Label(self.root, text="Ready", font=("Arial", 9), fg="#666")
        self.status_label.pack(pady=5)
        
    def setup_drag_drop(self):
        """Enable drag and drop for the listbox"""
        try:
            from tkinterdnd2 import DND_FILES, tkinterdnd
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.drop_files)
        except ImportError:
            # tkinterdnd2 not available, drag-drop won't work but UI still functions
            pass
    
    def drop_files(self, event):
        """Handle dropped files"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            # Remove curly braces if present (from some drag-drop implementations)
            file = file.strip('{}')
            if os.path.isfile(file) and self.is_ppt_file(file):
                if file not in self.files:
                    self.files.append(file)
        self.update_listbox()
    
    def add_files(self):
        """Open file dialog to add files"""
        files = filedialog.askopenfilenames(
            title="Select PowerPoint Files",
            filetypes=[("PowerPoint Files", ("*.ppt", "*.pptx")), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
        self.update_listbox()
    
    def add_folder(self):
        """Open folder dialog to add all PPT files from folder"""
        folder = filedialog.askdirectory(title="Select Folder", initialdir=os.getcwd())
        if folder:
            for file in os.listdir(folder):
                if self.is_ppt_file(file):
                    filepath = os.path.join(folder, file)
                    if filepath not in self.files:
                        self.files.append(filepath)
            self.update_listbox()
    
    def is_ppt_file(self, filename):
        """Check if file is a PowerPoint file"""
        return filename.lower().endswith(('.ppt', '.pptx'))
    
    def remove_file(self):
        """Remove selected file from list"""
        try:
            index = self.file_listbox.curselection()[0]
            del self.files[index]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a file to remove.")
    
    def clear_files(self):
        """Clear all files"""
        if messagebox.askyesno("Clear All", "Remove all files from the list?"):
            self.files = []
            self.update_listbox()
    
    def update_listbox(self):
        """Update the listbox display"""
        self.file_listbox.delete(0, "end")
        for file in self.files:
            self.file_listbox.insert("end", os.path.basename(file))
    
    def convert_files(self):
        """Convert selected files to PDF"""
        if not self.files:
            messagebox.showwarning("No Files", "Please add files to convert.")
            return
        
        # Disable convert button during conversion
        self.convert_btn.config(state="disabled")
        
        # Run conversion in a separate thread
        thread = threading.Thread(target=self._convert_thread)
        thread.start()
    
    def _convert_thread(self):
        """Thread function for file conversion"""
        total = len(self.files)
        self.progress['maximum'] = total
        
        for i, file in enumerate(self.files):
            try:
                pdf_name = os.path.splitext(os.path.basename(file))[0] + '.pdf'
                pdf_path = os.path.join(self.output_folder, pdf_name)
                
                self.update_progress(i, f"Converting {i+1}/{total}: {os.path.basename(file)}")
                
                # Run LibreOffice conversion
                subprocess.run(
                    ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', self.output_folder, file],
                    capture_output=True,
                    check=False
                )
                
                self.progress['value'] = i + 1
                self.root.update_idletasks()
                
            except Exception as e:
                self.update_status(f"Error converting {os.path.basename(file)}: {str(e)}")
        
        self.update_progress(total, "Conversion complete!")
        self.progress['value'] = total
        self.convert_btn.config(state="normal")
        
        messagebox.showinfo("Success", f"Converted {total} file(s) to PDF.\nOutput folder: {self.output_folder}")
        
        # Clear files after successful conversion
        self.files = []
        self.update_listbox()
        self.progress['value'] = 0
        self.progress_label.config(text="")
    
    def update_progress(self, current, message):
        """Update progress label"""
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = Tk()
    app = PPTToPDFConverter(root)
    root.mainloop()
