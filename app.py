import os
import cv2
import io
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from utils import allowed_file, save_file, cvtGray, histogram, create_out_filename, calc_stats,clear_output
from services import global_thresh, otsu_thresh, adaptive_thresh, get_otsu_threshold
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

UPLOAD_FOLDER = './public/image/'
OUTPUT_FOLDER = './public/outputs/'
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))

app = Flask(
    __name__,
    static_folder="public/static",
    static_url_path="/static"
)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

@app.errorhandler(429)
def ratelimit_hanlder(e):
    return jsonify({
        "success": False,
        "message": "Không được spam! Định hack à??",
        "error": "rate_limit_exceeded"
    }), 429

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = os.getenv("SECRET_KEY")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

@app.route("/")
def home():
    return render_template('home.jinja', name="PnlhaiCSE")

@app.route("/threshold")
def thresPage():
    # return "<h1>Hello, World!</h1>"
    return render_template('index.jinja')

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
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
    
    clear_output(app.config['OUTPUT_FOLDER'])
    filename = save_file(file, UPLOAD_FOLDER)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    gray = cvtGray(filepath)
    otsu_value = get_otsu_threshold(gray)
    height, width = gray.shape
    hist = histogram(gray)

    return jsonify({
        "success": True,
        "file": filename,
        "histogram": hist,
        "width": width,
        "height": height,
        "otsu_threshold": otsu_value
    }), 200

@app.route('/image/<filename>', methods=['GET'])
@limiter.limit("60 per minute")
def uploaded_image(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    gray = cvtGray(filepath)
    _, buffer = cv2.imencode('.jpg', gray)
    
    return send_file(
        io.BytesIO(buffer),
        mimetype="image/jpeg"
    )

@app.route('/process', methods=['POST'])
@limiter.limit("30 per minute")
def process():
    data = request.get_json()
    
    filename = secure_filename(data.get("file"))
    method = data.get("method")
    block_size = data.get("block_size")
    c = data.get("c")
    adaptive_method = data.get("adaptive_method")
    thres = max(0, min(255, data.get("threshold")))

    if not filename or not method:
        return jsonify({
            "success": False,
            "message": "Thiếu thông tin xử lý."
        }), 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(path):
        return jsonify({
            "success": False,
            "message": "Không tìm thấy ảnh."
        }), 404

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    start = time.perf_counter()

    try:
        if method == "global":
            result, threshold = global_thresh(img, thres)
        elif method == "otsu":
            result, threshold = otsu_thresh(img)
        elif method == "adaptive":
            result, threshold = adaptive_thresh(img, block_size, c, adaptive_method)
        else:
            return jsonify({
                "success": False,
                "message": "Phương pháp không hợp lệ."
            }), 400
    except Exception as e:
        return jsonify({
                "success": False,
                "message": str(e)
        }), 400

    elapsed = (time.perf_counter() - start) * 1000
    output_file = create_out_filename(filename, method)
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_file)
    stats = calc_stats(result)
    success = cv2.imwrite(output_path, result)
    if not success:
        return jsonify({
        "success": False,
        "message": "Không thể lưu ảnh kết quả."
    }), 500

    return jsonify({
        "success": True,
        "output": output_file,
        "threshold": threshold,
        "time": round(elapsed, 2),
        "stats": stats
    })

@app.route('/outputs/<filename>', methods=['GET'])
@limiter.limit("60 per minute")
def output_image(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config["OUTPUT_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "message": "Không tìm thấy ảnh kết quả."
        }), 404
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)