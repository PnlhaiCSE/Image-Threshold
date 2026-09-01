import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        count = 1
        while os.path.exists(filepath):
            new_filename = f"{name}_{count}{ext}"
            filepath = os.path.join(upload_folder, new_filename)
            count += 1
        filename = new_filename
    file.save(filepath)
    return filename