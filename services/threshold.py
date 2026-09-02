import cv2

def global_thresh(img, threshold):
    _, out = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return out, threshold

def otsu_thresh(img):
    threshold, out = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return out, int(threshold)

def adaptive_thresh(img, block_size, c, method):
    if block_size < 3 or block_size % 2 == 0:
        raise ValueError("block_size must be an odd number greater than or equal to 3")

    mode = cv2.ADAPTIVE_THRESH_MEAN_C if method == "mean" else cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    out = cv2.adaptiveThreshold(img, 255, mode, cv2.THRESH_BINARY, block_size, c)
    return out, None

def get_otsu_threshold(img):
    threshold, _ = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )
    return int(threshold)