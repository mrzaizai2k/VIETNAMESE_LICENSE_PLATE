import sys
sys.path.append("")

import cv2
import numpy as np
import math
import os
import sys

from Preprocess import preprocess
from utils import read_config, load_knn_model



def preprocess_image(img, config):
    """Apply preprocessing to input image"""
    img = cv2.resize(img, dsize=tuple(config["image"]["resize"]))
    imgGrayscale, imgThresh = preprocess(img, config)
    canny_image = cv2.Canny(imgThresh, 250, 255)  # Canny Edge
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.dilate(canny_image, kernel, iterations=1)  # Dilation
    return img, imgGrayscale, imgThresh, dilated_image


def find_license_plate_contours(img, dilated_image):
    """Detect potential license plate regions"""
    contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # Lấy 10 contours lớn nhất

    screenCnt = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.06 * peri, True)
        [x, y, w, h] = cv2.boundingRect(approx.copy())
        ratio = w / h
        if len(approx) == 4:
            screenCnt.append(approx)
            cv2.putText(img, str(len(approx.copy())), (x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)
    return screenCnt


# ======================= 1️⃣ ANGLE DETECTION ==========================
def find_plate_angle(screenCnt):
    """Calculate the angle of the license plate based on contour coordinates."""
    (x1, y1) = screenCnt[0, 0]
    (x2, y2) = screenCnt[1, 0]
    (x3, y3) = screenCnt[2, 0]
    (x4, y4) = screenCnt[3, 0]
    array = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    array.sort(reverse=True, key=lambda x: x[1])
    (x1, y1) = array[0]
    (x2, y2) = array[1]
    doi = abs(y1 - y2)
    ke = abs(x1 - x2)
    angle = math.atan(doi / ke) * (180.0 / math.pi)
    return angle, x1, x2


# ======================= 2️⃣ CROP & ALIGN ============================
def crop_and_align_plate(img, imgGray, imgThresh, screenCnt, angle, x1, x2):
    """Crop the plate region from the image and align it based on detected angle."""
    mask = np.zeros(imgGray.shape, np.uint8)
    cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))

    roi = img[topx:bottomx, topy:bottomy]
    imgThreshCrop = imgThresh[topx:bottomx, topy:bottomy]
    ptPlateCenter = ((bottomx - topx) / 2, (bottomy - topy) / 2)

    if x1 < x2:
        rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, -angle, 1.0)
    else:
        rotationMatrix = cv2.getRotationMatrix2D(ptPlateCenter, angle, 1.0)

    roi = cv2.warpAffine(roi, rotationMatrix, (bottomy - topy, bottomx - topx))
    imgThreshCrop = cv2.warpAffine(imgThreshCrop, rotationMatrix, (bottomy - topy, bottomx - topx))
    roi = cv2.resize(roi, (0, 0), fx=3, fy=3)
    imgThreshCrop = cv2.resize(imgThreshCrop, (0, 0), fx=3, fy=3)

    return roi, imgThreshCrop


# ======================= 3️⃣ CHARACTER SEGMENTATION =================
def segment_characters(imgThresh):
    """Perform morphological operations and find contours for potential characters."""
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thre_mor = cv2.morphologyEx(imgThresh, cv2.MORPH_DILATE, kernel3)
    contours, _ = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return thre_mor, contours


# ======================= 4️⃣ FILTER CHARACTERS ======================
def filter_characters(contours, roi, config):
    """Filter out noise and select valid character contours."""
    Min_char = config["plate"]["Min_char"]
    Max_char = config["plate"]["Max_char"]

    char_x_ind = {}
    char_x = []
    height, width, _ = roi.shape
    roiarea = height * width

    for ind, cnt in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(cnt)
        ratiochar = w / h
        char_area = w * h

        if (Min_char * roiarea < char_area < Max_char * roiarea) and (0.25 < ratiochar < 0.7):
            if x in char_x:
                x += 1
            char_x.append(x)
            char_x_ind[x] = ind

    char_x = sorted(char_x)
    return char_x, char_x_ind


# ======================= 5️⃣ CHARACTER RECOGNITION ==================
def recognize_characters(kNearest, thre_mor, contours, char_x, char_x_ind, roi, config):
    """Recognize each character using the trained KNN model."""
    RESIZED_IMAGE_WIDTH = config["plate"]["RESIZED_IMAGE_WIDTH"]
    RESIZED_IMAGE_HEIGHT = config["plate"]["RESIZED_IMAGE_HEIGHT"]

    first_line, second_line = "", ""
    height, _, _ = roi.shape

    for i in char_x:
        (x, y, w, h) = cv2.boundingRect(contours[char_x_ind[i]])
        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
        imgROI = thre_mor[y:y + h, x:x + w]
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
        npaROIResized = np.float32(imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT)))

        _, npaResults, _, _ = kNearest.findNearest(npaROIResized, k=config["model"]["k_value"])
        strCurrentChar = str(chr(int(npaResults[0][0])))

        cv2.putText(roi, strCurrentChar, (x, y + 50), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 0), 3)

        if y < height / 3:
            first_line += strCurrentChar
        else:
            second_line += strCurrentChar

    return first_line, second_line


# ======================= MAIN EXTRACTION PIPELINE ===================
def extract_plate_and_characters(img, imgGray, imgThresh, screenCnt, kNearest, config, plate_id=1):
    """Extract, align, and recognize characters from the license plate."""
    for cnt in screenCnt:
        cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)

        # Step 1: find angle
        angle, x1, x2 = find_plate_angle(cnt)

        # Step 2: crop & align
        roi, imgThreshCrop = crop_and_align_plate(img, imgGray, imgThresh, cnt, angle, x1, x2)

        # Step 3: segmentation
        thre_mor, contours = segment_characters(imgThreshCrop)
        cv2.imshow(str(plate_id + 20), thre_mor)

        # Step 4: filter
        char_x, char_x_ind = filter_characters(contours, roi, config)

        # Step 5: recognition
        first_line, second_line = recognize_characters(kNearest, thre_mor, contours, char_x, char_x_ind, roi, config)

        print(f"\n License Plate {plate_id}: {first_line} - {second_line}\n")
        roi = cv2.resize(roi, None, fx=0.75, fy=0.75)
        cv2.imshow(str(plate_id), cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))


# ======================= DETECTION PIPELINE =========================
def detect_license_plate(config, img_path):
    """Main detection pipeline."""
    kNearest = load_knn_model(config)
    img = cv2.imread(img_path)
    img, imgGray, imgThresh, dilated_image = preprocess_image(img, config)

    screenCnt = find_license_plate_contours(img, dilated_image)
    detected = 1 if len(screenCnt) > 0 else 0

    if not detected:
        print("No plate detected")
        return

    extract_plate_and_characters(img, imgGray, imgThresh, screenCnt, kNearest, config)
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    cv2.imshow("License plate", img)
    cv2.waitKey(0)


# ======================= TEST ENTRY POINT ==========================
if __name__ == "__main__":
    img_path = "data/image/10.jpg"
    if not os.path.exists(img_path):
        print(f"⚠️ Image not found: {img_path}")
        sys.exit(1)

    config_path = "config/config.yaml"
    config = read_config(config_path)

    detect_license_plate(config, img_path)

