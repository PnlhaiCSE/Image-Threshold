import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './public/image/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

load_dotenv()
app = Flask(
    __name__,
    static_folder="public/static",
    static_url_path="/static"
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv("SECRET_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
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

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({
        "success": True,
        "file": filename
    }), 200

@app.route('/public/image/<filename>')
def uploaded_image(filename):
    return send_from_directory('public/image',filename)

if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST"),
        port=os.getenv('PORT'),
        debug=True
    )