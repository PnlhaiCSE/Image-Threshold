import cv2

def cvtGray(filepath):
    image = cv2.imread(filepath)
    if image is None:
        raise ValueError("Không thể đọc ảnh")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def histogram(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist.flatten().astype(int).tolist()