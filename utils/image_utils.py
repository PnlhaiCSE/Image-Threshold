import cv2
import numpy as np

def cvtGray(filepath):
    image = cv2.imread(filepath)
    if image is None:
        raise ValueError("Không thể đọc ảnh")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def histogram(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist.flatten().astype(int).tolist()

def calc_stats(img):
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
        "total": total
    }