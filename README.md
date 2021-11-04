# VIETNAMESE_LICENSE_PLATE using KNN and openCV
**English below**
Chương trình nhận dạng biển số xe trong kho bãi, được dùng cho biển số xe Việt Nam cả 1 và 2 hàng. Sử dụng xử lý ảnh OpenCV và thuật toán KNN. Chi tiết mình sẽ làm một video youtube cập nhật sau.

This project using the machine learning method called KNN and OpenCV, which is a powerful library for image processing for recognising the Vietnamese license plate in the parking lot. The detail would be in the youtube link below: 

Các bạn có thể tìm hiểu thêm tại [LINK YOUTUBE:](https://youtu.be/7erlCp6d5w8)

Đọc file `Nhận diện biển số xe.docx` để biết thêm lý thuyết.
For more information, please download the `Nhận diện biển số xe.docx` file

## CÁC BƯỚC CHÍNH TRONG CỦA 1 BÀI TOÁN NHẬN DẠNG BIỂN SỐ XE
**The main stages in the license plate recoginition algorithm**
1. License Plate Detection
2. Character Segmentation
3. Character Recognition

<p align="center"><img src="https://user-images.githubusercontent.com/40959407/130982072-a4701080-e40d-42c1-8fc5-062da340ca5b.png" width="300"></p>
<p align="center"><i>Hình 1. Các bước chính trong việc nhận diện </i></p>

## PHÁT HIỆN VÀ TÁCH BIỂN SỐ:
**The main stages in detecting and extract the license plate**
1. Taking picture from the camera
2. Gray scaling
3. Increasing the contrast level
4. Noise Decreasing by Gaussian filter
5. Adaptive threshold for image binarization
6. Canny Edge detection
7. Detect the plate by drawing contours and if..else

<p align="center"><img src="https://user-images.githubusercontent.com/40959407/130982322-86cd6ab1-c4de-48c2-b67a-3d52b75be330.jpg" width="300" ></p>
<p align="center"><i>Hình 2. Xác định và tách biển số </i></p>

Đầu tiên từ clip ta sẽ cắt từng frame ảnh ra từ clip đầu vào để xử lý, tách biển số. Ở phạm vi đồ án này, ý tưởng chủ yếu là nhận diện được biển số từ sự thay đổi đột ngột về cường độ ánh sáng giữa biển số và môi trường xung quanh nên ta sẽ loại bỏ các dữ liệu màu sắc RGB bằng cách chuyển sang ảnh xám. Tiếp theo ta tăng độ tương phản với hai phép toán hình thái học Top Hat và Black Hat để làm nổi bật thêm biển số giữa phông nền, hỗ trợ cho việc xử lý nhị phân sau này. Sau đó, ta giảm nhiễu bằng bộ lọc Gauss để loại bỏ những chi tiết nhiễu có thể gây ảnh hưởng đến quá trình nhận diện, đồng thời làm tăng tốc độ xử lý.

Việc lấy ngưỡng sẽ giúp ta tách được thông tin biển số và thông tin nền, ở đây em chọn lấy ngưỡng động (Adaptive Threshold). Tiếp đó ta sử dụng thuật toán phát hiện cạnh Canny để trích xuất những chi tiết cạnh của biển số. Trong quá trình xử lý máy tính có thể nhầm lẫn biển số với những chi tiết nhiễu, việc lọc lần cuối bằng các tỉ lệ cao/rộng hay diện tích của biển số sẽ giúp xác định được đúng biển số. Cuối cùng, ta sẽ xác định vị trí của biển số trong ảnh bằng cách vẽ Contour bao quanh. 

To analyze and separate the number plate, we will first trim each picture frame from the input footage. The main goal of this project is to detect a license plate based on a quick shift in light intensity between the license plate and the surroundings, thus we'll transform a gray image to remove the RGB color data. Then, using the morphological procedures Top Hat and Black Hat, we raise the contrast to emphasize more number plates in the background, allowing for binary processing later. Then, using a Gaussian filter, we minimize noise and boost processing speed while removing noisy details that might damage the recognition process.

<p align="center"><img src="result/maximize contrast.PNG" width="500" ></p>
<p align="center"><i>Hình 2. Maximize Contrast </i></p>

Using a threshold will assist us distinguish license plate data from background data; in this case, we'll use Adaptive Threshold. After that, we apply the Canny edge detection technique to retrieve the license plate's edge information. The number plate may be confused with noisy features during computer processing; final filtering by high/wide ratios or the license plate area will aid in identifying the proper number plate. Finally, we'll draw a Contour around the number plate in the picture to determine its location.

<p align="center"><img src="result/canny.jpg" width="500" ></p>
<p align="center"><i>Hình 2. Canny Edge Detection </i></p>

<p align="center"><img src="result/1.1.jpg" width="200" ></p>
<p align="center"><i>Hình 2. Drawing contour and extract the information </i></p>

## Phân tách kí tự:
**Character segmentation**

Đầu tiên cần xoay biển số về đúng chính diện

To begin, we need to rotate the image to the right direction

Phương pháp xoay ảnh sử dụng ở đây là:
* Lọc ra tọa độ 2 đỉnh A,B nằm dưới cùng của biển số
*	Từ 2 đỉnh có tọa độ lần lượt là A(x1, y1) và B(x2,y2) ta có thể tính được cạnh đối và cạnh kề của tam giác ABC
*	Tính góc quay bằng hàm tan()
*	Xoay ảnh theo góc quay đã tính. Nếu ngược lại điểm A nằm cao hơn điểm B ta cho góc quay âm


The method to rotate the image I use here is:
* Filter out the coordinates of 2 vertices A, B located at the bottom of the number plate
* From 2 vertices with coordinates A(x1, y1) and B(x2,y2) respectively, we can calculate the opposite and adjacent sides of triangle ABC.
* Calculate rotation angle using tan() function 
* Rotate the image according to the calculated rotation angle. Otherwise, point A is higher than point B, we give negative rotation angle 

<p align="center"><img src="result/chuaxoay.jpg" width="250" >                      <img src="result/xoay.jpg" width="250" ></p>
<p align="center"><i>Hình 2. Rotation </i></p>

Từ ảnh nhị phân, ta lại tìm contour cho các kí tự (phần màu trắng). Sau đó vẽ những hình chữ nhật bao quanh các kí tự đó. Tuy nhiên việc tìm contour này cũng bị nhiễu dẫn đến việc máy xử lý sai mà tìm ra những hình ảnh không phải kí tự. Ta sẽ áp dụng các đặc điểm về tỉ lệ chiều cao/rộng của kí tự, diện tích của kí tự so với biển số 

The contour for the letters is reconstructed from the binary picture (the white part). Then, around those characters, draw rectangles. However, locating this contour is difficult, resulting in inaccurate outcome and the discovery of non-character objects. We'll use the height/width ratio of the character, as well as the character's area in comparison to the number plate.
















