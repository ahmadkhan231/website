
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

class DocumentHandler:
    def __init__(self, upload_folder='uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
        self.ensure_upload_folder()
    
    def ensure_upload_folder(self):
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_document(self, file, customer_id, doc_type):
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{customer_id}_{doc_type}_{timestamp}_{filename}"
            file_path = os.path.join(self.upload_folder, new_filename)
            file.save(file_path)
            
            # Save document info
            doc_info = {
                'customer_id': customer_id,
                'document_type': doc_type,
                'original_filename': filename,
                'saved_filename': new_filename,
                'upload_date': datetime.now().isoformat(),
                'file_path': file_path
            }
            
            self.save_document_info(doc_info)
            return new_filename
        return None
    
    def save_document_info(self, doc_info):
        docs_file = 'documents.json'
        if os.path.exists(docs_file):
            with open(docs_file, 'r') as f:
                documents = json.load(f)
        else:
            documents = []
        
        documents.append(doc_info)
        
        with open(docs_file, 'w') as f:
            json.dump(documents, f, indent=4)
