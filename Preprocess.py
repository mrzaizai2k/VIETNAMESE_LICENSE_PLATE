# Preprocess.py
import sys
sys.path.append("")

import cv2
import numpy as np
import math
from utils import read_config


def preprocess(imgOriginal, config):

    GAUSSIAN_SMOOTH_FILTER_SIZE = tuple(config["preprocess"]["GAUSSIAN_SMOOTH_FILTER_SIZE"])  # kích cỡ càng to thì càng mờ
    ADAPTIVE_THRESH_BLOCK_SIZE = config["preprocess"]["ADAPTIVE_THRESH_BLOCK_SIZE"]
    ADAPTIVE_THRESH_WEIGHT = config["preprocess"]["ADAPTIVE_THRESH_WEIGHT"]

    imgGrayscale = extractValue(imgOriginal)
    # imgGrayscale = cv2.cvtColor(imgOriginal,cv2.COLOR_BGR2GRAY) nên dùng hệ màu HSV
    # Trả về giá trị cường độ sáng ==> ảnh gray
    imgMaxContrastGrayscale = maximizeContrast(imgGrayscale)  # để làm nổi bật biển số hơn, dễ tách khỏi nền
    # cv2.imwrite("imgGrayscalePlusTopHatMinusBlackHat.jpg",imgMaxContrastGrayscale)
    height, width = imgGrayscale.shape

    imgBlurred = np.zeros((height, width, 1), np.uint8)
    imgBlurred = cv2.GaussianBlur(imgMaxContrastGrayscale, GAUSSIAN_SMOOTH_FILTER_SIZE, 0)
    # cv2.imwrite("gauss.jpg",imgBlurred)
    # Làm mịn ảnh bằng bộ lọc Gauss 5x5, sigma = 0

    imgThresh = cv2.adaptiveThreshold(
        imgBlurred,
        255.0,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        ADAPTIVE_THRESH_BLOCK_SIZE,
        ADAPTIVE_THRESH_WEIGHT
    )

    # Tạo ảnh nhị phân
    return imgGrayscale, imgThresh
# Trả về ảnh xám và ảnh nhị phân

def extractValue(imgOriginal):
    height, width, numChannels = imgOriginal.shape
    imgHSV = np.zeros((height, width, 3), np.uint8)
    imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

    imgHue, imgSaturation, imgValue = cv2.split(imgHSV)
    
    # màu sắc, độ bão hòa, giá trị cường độ sáng
    # Không chọn màu RBG vì vd ảnh màu đỏ sẽ còn lẫn các màu khác nữa nên khó xđ ra "một màu" 
    return imgValue
 
def maximizeContrast(imgGrayscale):
    # Làm cho độ tương phản lớn nhất 
    height, width = imgGrayscale.shape
    
    imgTopHat = np.zeros((height, width, 1), np.uint8)
    imgBlackHat = np.zeros((height, width, 1), np.uint8)
    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # tạo bộ lọc kernel
    
    imgTopHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, structuringElement, iterations=10)  # nổi bật chi tiết sáng trong nền tối
    # cv2.imwrite("tophat.jpg",imgTopHat)
    imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, structuringElement, iterations=10)  # Nổi bật chi tiết tối trong nền sáng
    # cv2.imwrite("blackhat.jpg",imgBlackHat)
    imgGrayscalePlusTopHat = cv2.add(imgGrayscale, imgTopHat) 
    imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

    # cv2.imshow("imgGrayscalePlusTopHatMinusBlackHat",imgGrayscalePlusTopHatMinusBlackHat)
    # Kết quả cuối là ảnh đã tăng độ tương phản 
    return imgGrayscalePlusTopHatMinusBlackHat


if __name__ == "__main__":
    import os

    # Test function
    img_path = "data/image/1.jpg"
    if not os.path.exists(img_path):
        print(f"⚠️ Image not found: {img_path}")
        sys.exit(1)

    # Read config file
    config_path = "config/config.yaml"
    config = read_config(config_path)

    imgOriginal = cv2.imread(img_path)
    imgGray, imgThresh = preprocess(imgOriginal, config)

    cv2.imshow("Original", imgOriginal)
    cv2.imshow("Gray", imgGray)
    cv2.imshow("Threshold", imgThresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
