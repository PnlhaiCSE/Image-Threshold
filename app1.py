import os
import cv2
import io
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from utils import allowed_file, save_file, cvtGray, histogram

UPLOAD_FOLDER = './public/image/'
HOST = os.getenv("HOST")
PORT = os.getenv('PORT')

load_dotenv()
app = Flask(
    __name__,
    static_folder="public/static",
    static_url_path="/static"
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def home():
    return render_template('home.jinja')

@app.route("/threshold")
def hello_world():
    # return "<h1>Hello, World!</h1>"
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('avatar')

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file is None:
        return jsonify({
            "success": False,
            "message": "Không có file"
        }), 400

    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "Chưa chọn file"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Định dạng file không được hỗ trợ"
        }), 400
    
    if file:
        filename = save_file(file, UPLOAD_FOLDER)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        gray = cvtGray(filepath)
        height, width = gray.shape
        hist = histogram(gray)

    return jsonify({
        "success": True,
        "file": filename,
        "histogram": hist,
        "width": width,
        "height": height
    }), 200

@app.route('/image/<filename>')
def uploaded_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    gray = cvtGray(filepath)
    _, buffer = cv2.imencode('.jpg', gray)
    
    return send_file(
        io.BytesIO(buffer),
        mimetype="image/jpeg"
    )

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)