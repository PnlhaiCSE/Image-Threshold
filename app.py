import os
import time
import uuid

import cv2
import numpy as np

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT
    )


def get_hist(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist.flatten().astype(int).tolist()


def get_stats(img):
    total = img.size

    black = int(np.sum(img == 0))
    white = int(np.sum(img == 255))

    black_pct = black / total * 100
    white_pct = white / total * 100

    return {
        "black": black,
        "white": white,
        "black_pct": round(black_pct, 2),
        "white_pct": round(white_pct, 2),
        "total": total,
    }


def global_thresh(img, threshold):
    _, out = cv2.threshold(
        img,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    return out, threshold


def otsu_thresh(img):
    threshold, out = cv2.threshold(
        img,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return out, int(threshold)


def adaptive_thresh(img, block_size, c, method):
    if block_size % 2 == 0:
        block_size += 1

    if block_size < 3:
        block_size = 3

    if method == "mean":
        mode = cv2.ADAPTIVE_THRESH_MEAN_C
    else:
        mode = cv2.ADAPTIVE_THRESH_GAUSSIAN_C

    out = cv2.adaptiveThreshold(
        img,
        255,
        mode,
        cv2.THRESH_BINARY,
        block_size,
        c
    )

    return out, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("image")

    if not file or file.filename == "":
        return jsonify({
            "success": False,
            "message": "Chưa chọn ảnh."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Định dạng ảnh không được hỗ trợ."
        }), 400

    filename = secure_filename(file.filename)

    file_id = uuid.uuid4().hex

    ext = filename.rsplit(".", 1)[1].lower()

    saved_name = f"{file_id}.{ext}"

    path = os.path.join(UPLOAD_DIR, saved_name)

    file.save(path)

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        os.remove(path)

        return jsonify({
            "success": False,
            "message": "Không thể đọc ảnh."
        }), 400

    # Kiểm tra ảnh gốc có phải grayscale không
    original = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if original is None:
        return jsonify({
            "success": False,
            "message": "Không thể đọc ảnh."
        }), 400

    if len(original.shape) != 2:
        os.remove(path)

        return jsonify({
            "success": False,
            "message": "Ứng dụng chỉ hỗ trợ ảnh xám."
        }), 400

    height, width = img.shape

    return jsonify({
        "success": True,
        "file": saved_name,
        "width": width,
        "height": height,
        "histogram": get_hist(img),
        "message": "Upload thành công."
    })


@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()

    filename = data.get("file")
    method = data.get("method")

    if not filename or not method:
        return jsonify({
            "success": False,
            "message": "Thiếu thông tin xử lý."
        }), 400

    path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(path):
        return jsonify({
            "success": False,
            "message": "Không tìm thấy ảnh."
        }), 404

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        return jsonify({
            "success": False,
            "message": "Không thể đọc ảnh."
        }), 400

    start = time.perf_counter()

    try:

        if method == "global":

            threshold = int(data.get("threshold", 127))

            threshold = max(0, min(255, threshold))

            out, threshold = global_thresh(
                img,
                threshold
            )

        elif method == "otsu":

            out, threshold = otsu_thresh(img)

        elif method == "adaptive":

            block_size = int(
                data.get("block_size", 11)
            )

            c = int(
                data.get("c", 2)
            )

            adaptive_method = data.get(
                "adaptive_method",
                "gaussian"
            )

            out, threshold = adaptive_thresh(
                img,
                block_size,
                c,
                adaptive_method
            )

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

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    output_name = (
        f"{uuid.uuid4().hex}.png"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        output_name
    )

    cv2.imwrite(
        output_path,
        out
    )

    stats = get_stats(out)

    return jsonify({
        "success": True,
        "output": output_name,
        "threshold": threshold,
        "time": round(elapsed, 2),
        "stats": stats
    })


@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(
        UPLOAD_DIR,
        filename
    )


@app.route("/outputs/<filename>")
def outputs(filename):
    return send_from_directory(
        OUTPUT_DIR,
        filename
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )