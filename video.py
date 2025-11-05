import cv2
import os
import math
import numpy as np
from utils import read_config, load_knn_model
from plate_recognition import (
    preprocess_image,
    find_license_plate_contours,
    find_plate_angle,
    crop_and_align_plate,
    segment_characters,
    filter_characters,
    recognize_characters,
)

def process_video(config, video_path, show_steps=False):
    """
    Process a video frame by frame to detect and recognize license plates.
    Uses same pipeline as plate_recognition.py but works on streaming video.
    """
    if not os.path.exists(video_path):
        print(f"⚠️ Video not found: {video_path}")
        return

    # Load KNN model
    kNearest = load_knn_model(config)
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    total_detected = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        # Step 1: Preprocess frame
        try:
            img, imgGray, imgThresh, dilated_image = preprocess_image(frame, config)
        except Exception as e:
            print(f"⚠️ Frame preprocessing error: {e}")
            continue

        # Step 2: Find contours
        screenCnt, annotated_img = find_license_plate_contours(img, dilated_image)

        if not screenCnt:
            continue  # No plate detected in this frame

        # Step 3: Process each contour as a possible plate
        for cnt in screenCnt:
            try:
                angle, x1, x2 = find_plate_angle(cnt)
                roi, imgThreshCrop = crop_and_align_plate(img, imgGray, imgThresh, cnt, angle, x1, x2)
                thre_mor, contours = segment_characters(imgThreshCrop)
                char_x, char_x_ind = filter_characters(contours, roi, config)
                first_line, second_line = recognize_characters(
                    kNearest, thre_mor, contours, char_x, char_x_ind, roi, config
                )

                text = f"{first_line}-{second_line}"
                total_detected += 1

                # Draw result on frame
                cv2.putText(
                    img,
                    text,
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 255),
                    3,
                    cv2.LINE_AA,
                )

                if show_steps:
                    cv2.imshow("Detected Plate ROI", cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))

            except Exception as e:
                print(f"⚠️ Error processing contour: {e}")
                continue

        # Step 4: Display annotated frame
        resized = cv2.resize(img, None, fx=0.5, fy=0.5)
        cv2.imshow("License Plate Detection", resized)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"✅ Processed {total_frames} frames")
    print(f"🚗 Plates detected: {total_detected}")
    if total_frames > 0:
        print(f"📊 Detection rate: {100 * total_detected / total_frames:.2f}%")



if __name__ == "__main__":
    # Configuration
    config_path = "config/config.yaml"
    config = read_config(config_path)

    # Input video
    video_path = "data/video/haihang.mp4"

    # Run
    process_video(config, video_path, show_steps=True)
