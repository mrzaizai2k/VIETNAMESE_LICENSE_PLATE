import sys
sys.path.append("")

import os
import cv2
import numpy as np
from utils import read_config
from Preprocess import preprocess
from GenData import save_training_data

def preprocess_rgb(config, img):
    imgGrayscale, imgThresh = preprocess(img, config)
    return imgThresh

def create_knn_data_from_rgb(config, data, show = False):
    npaFlattenedImages = np.empty((0, config["plate"]["RESIZED_IMAGE_WIDTH"] * config["plate"]["RESIZED_IMAGE_HEIGHT"]))
    intClassifications = []
    valid_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (img, label) in enumerate(data):
        label = str(label).upper()
        if label not in valid_chars:
            print(f"Skipping invalid label: {label}")
            continue
        imgThresh = preprocess_rgb(config, img)
        imgResized = cv2.resize(imgThresh, (config["plate"]["RESIZED_IMAGE_WIDTH"], config["plate"]["RESIZED_IMAGE_HEIGHT"]))
        npaFlattenedImage = imgResized.reshape((1, config["plate"]["RESIZED_IMAGE_WIDTH"] * config["plate"]["RESIZED_IMAGE_HEIGHT"]))
        npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0)
        intClassifications.append(ord(label))
        print(f"Processed {i+1}/{len(data)} | Label: {label}")
        # Show preprocessed and resized image
        if show:
            cv2.imshow(f"Thresh: {label}", imgThresh)
            cv2.imshow(f"Resized: {label}", imgResized)
            cv2.waitKey(0)  # Allow display update
    cv2.destroyAllWindows()
    if not intClassifications:
        print("No valid labeled data found.")
        return False
    npaClassifications = np.array(intClassifications, np.float32)
    save_training_data(config, npaClassifications, npaFlattenedImages)
    return True

def create_test_data(folder):
    data = []
    valid_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for filename in sorted(os.listdir(folder)):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(folder, filename)
            img = cv2.imread(path)
            if img is None:
                print(f"Skip unreadable image: {path}")
                continue
            label = os.path.splitext(filename)[0].upper()
            if len(label) != 1 or label not in valid_chars:
                print(f"Invalid label in filename: {filename}")
                continue
            data.append((img, label))
    print(f"Loaded {len(data)} labeled images from '{folder}'")
    return data

if __name__ == "__main__":
    config = read_config("config/config.yaml")
    folder = "data/characters"
    data = create_test_data(folder)
    print("Creating/Updating KNN training data...")
    success = create_knn_data_from_rgb(config, data)
    print("\nDone! Data updated successfully." if success else "\nFailed.")