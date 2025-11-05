import sys
sys.path.append("")

import os
import cv2
import numpy as np
from utils import read_config, check_path


# ------------------------------------------------------------------------------------------------
def preprocess_training_image(config, img_path="training_chars.png"):
    """Read and preprocess training image."""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"❌ Cannot find training image: {img_path}")

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_size = tuple(config["preprocess"]["GAUSSIAN_SMOOTH_FILTER_SIZE"])
    imgBlurred = cv2.GaussianBlur(imgGray, blur_size, 0)

    block_size = config["preprocess"]["ADAPTIVE_THRESH_BLOCK_SIZE"]
    weight = config["preprocess"]["ADAPTIVE_THRESH_WEIGHT"]
    imgThresh = cv2.adaptiveThreshold(
        imgBlurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        weight
    )
    return img, imgThresh


# ------------------------------------------------------------------------------------------------
def save_training_data(config, npaClassifications, npaFlattenedImages):
    """Save or append new labeled data to existing training files."""
    if npaClassifications.size == 0:
        print("⚠️ No new data to save.")
        return

    class_path = config["model"]["classifications_path"]
    flat_path = config["model"]["flattened_images_path"]

    check_path(class_path)
    check_path(flat_path)
    
    if os.path.exists(class_path) and os.path.exists(flat_path):
        print("📂 Existing training files found — appending new data...")
        old_classes = np.loadtxt(class_path, np.float32)
        old_flatten = np.loadtxt(flat_path, np.float32)

        old_classes = old_classes.reshape((old_classes.size, 1))
        new_classes = np.vstack((old_classes, npaClassifications.reshape((npaClassifications.size, 1))))
        new_flatten = np.vstack((old_flatten, npaFlattenedImages))

        np.savetxt(class_path, new_classes)
        np.savetxt(flat_path, new_flatten)
    else:
        print("🆕 No existing data found — creating new training files...")
        np.savetxt(class_path, npaClassifications.reshape((npaClassifications.size, 1)))
        np.savetxt(flat_path, npaFlattenedImages)

    print(f"💾 Saved {len(npaClassifications)} new samples to:")
    print(f"   - {class_path}")
    print(f"   - {flat_path}")


# ------------------------------------------------------------------------------------------------
def collect_training_data(config, imgTrainingNumbers, imgThresh):
    """Manually label characters and build flattened image dataset."""
    MIN_CONTOUR_AREA = 40
    RESIZED_IMAGE_WIDTH = config["plate"]["RESIZED_IMAGE_WIDTH"]
    RESIZED_IMAGE_HEIGHT = config["plate"]["RESIZED_IMAGE_HEIGHT"]

    imgThreshCopy = imgThresh.copy()
    npaContours, hierarchy = cv2.findContours(
        imgThreshCopy,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    npaFlattenedImages = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    intClassifications = []
    intValidChars = [ord(c) for c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    print("💡 Tip: Press ESC anytime to stop and auto-save progress.\n")

    for i, npaContour in enumerate(npaContours):
        if cv2.contourArea(npaContour) > MIN_CONTOUR_AREA:
            [x, y, w, h] = cv2.boundingRect(npaContour)

            cv2.rectangle(imgTrainingNumbers, (x, y), (x+w, y+h), (0, 0, 255), 2)
            imgROI = imgThresh[y:y+h, x:x+w]
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))

            cv2.imshow("ROI", imgROI)
            cv2.imshow("Resized ROI", imgROIResized)
            cv2.imshow("Training Image", imgTrainingNumbers)

            intChar = cv2.waitKey(0)

            if intChar == 27:  # ESC pressed
                print("\n👋 Exit requested by user. Saving progress...")
                # Save everything collected so far before exiting
                npaClassifications_np = np.array(intClassifications, np.float32)
                save_training_data(config, npaClassifications_np, npaFlattenedImages)
                cv2.destroyAllWindows()
                sys.exit(0)

            elif intChar in intValidChars:
                intClassifications.append(intChar)
                npaFlattenedImage = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0)

    cv2.destroyAllWindows()

    print(f"\n✅ Collected {len(intClassifications)} samples.\n")
    return np.array(intClassifications, np.float32), npaFlattenedImages


# ------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    config = read_config("config/config.yaml")

    imgTrainingNumbers, imgThresh = preprocess_training_image(config)
    cv2.imshow("Thresholded", imgThresh)

    npaClassifications, npaFlattenedImages = collect_training_data(config, imgTrainingNumbers, imgThresh)

    # Save at the end (in case user didn’t press ESC)
    save_training_data(config, npaClassifications, npaFlattenedImages)
