# VIETNAMESE_LICENSE_PLATE using KNN and openCV
Chương trình nhận dạng biển số xe trong kho bãi, được dùng cho biển số xe Việt Nam cả 1 và 2 hàng. Sử dụng xử lý ảnh OpenCV và thuật toán KNN. Chi tiết mình sẽ làm một video youtube cập nhật sau.

This project using the machine learning method called KNN and OpenCV, which is a powerful library for image processing for recognising the Vietnamese license plate in the parking lot. The detail would be in the youtube link below: 

Các bạn có thể tìm hiểu thêm tại [LINK YOUTUBE:](https://youtu.be/7erlCp6d5w8)

Đọc file `Nhận diện biển số xe.docx` để biết thêm lý thuyết.
For more information, please download the `Nhận diện biển số xe.docx` file

## CÁC BƯỚC CHÍNH TRONG CỦA 1 BÀI TOÁN NHẬN DẠNG BIỂN SỐ XE
The main stages in the license plate recoginition algorithm 
1. License Plate Detection
2. Character Segmentation
3. Character Recognition

<p align="center"><img src="https://user-images.githubusercontent.com/40959407/130982072-a4701080-e40d-42c1-8fc5-062da340ca5b.png" width="300"></p>
<p align="center"><i>Hình 1. Các bước chính trong việc nhận diện </i></p>

## PHÁT HIỆN VÀ TÁCH BIỂN SỐ:
The main stages in detecting and extract the license plate
1. Taking picture from the camera
2. Gray scaling
3. Increasing the contrast level
4. Noise Decreasing by Gaussian filter
5. Adaptive threshold for image binarization
6. Canny Edge detection
7. Detect the plate by drawing contours and if..else

<p align="center"><img src="https://user-images.githubusercontent.com/40959407/130982322-86cd6ab1-c4de-48c2-b67a-3d52b75be330.jpg" width="300" ></p>
<p align="center"><i>Hình 2. Xác định và tách biển số </i></p>

