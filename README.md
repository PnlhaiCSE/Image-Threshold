# Image Thresholding

Ứng dụng web xử lý ảnh **xám** được xây dựng bằng Flask và OpenCV, cho phép tải ảnh lên, quan sát histogram và so sánh ba phương pháp ngưỡng hóa phổ biến. Giao diện tiếng Việt thân thiện, có hiển thị ảnh gốc, ảnh kết quả, thống kê pixel và thời gian xử lý. ✨📷

> **Student Name:** Phạm Nguyễn Long Hải<br/>
> **Major:** Computer Science<br/>
> **Course:** Xử lý ảnh (Image Processing) 

## Feature

- Tải ảnh lên với các định dạng `PNG`, `JPG`, `JPEG`, `BMP` và `WEBP`.
- Tự động chuyển ảnh màu sang ảnh xám trước khi xử lý.
- Hiển thị ảnh gốc, ảnh nhị phân sau xử lý và histogram 256 mức xám.
- Hỗ trợ ba phương pháp: Global Threshold, Otsu và Adaptive Threshold.
- Tùy chỉnh ngưỡng thủ công, kích thước vùng lân cận, hệ số `C` và kiểu Adaptive (`Mean`/`Gaussian`).
- Tải ảnh kết quả về máy.
- Giao diện trực quan, responsive trên mọi thiết bị.

## Project Structure

```text
Project-Threshold/
|
├── app.py                    # Flask app, route, upload
├── requirements.txt          # Requirements
├── Dockerfile                # Docker
├── docker-compose.yaml       # Orchestration
├── run.sh                    # Script 
├── .env.example              # .env
├── services/                 # Image processing algorithms
├── utils/                    # Utilities
├── templates/                # UI templates
└── public/
	├── image/                # Image upload
	├── outputs/              # Image output
	└── static/               # Static files
```

## Algorithms

### _1. Global Threshold_
Dùng một ngưỡng `T` cho toàn bộ ảnh. Người dùng chọn `T` từ `0–255`. Đơn giản, nhanh, phù hợp ảnh có ánh sáng đồng đều.
### _2. Otsu Threshold_
Tự động tìm ngưỡng tối ưu từ histogram bằng cách tối đa hóa **phương sai giữa hai lớp**. Không cần người dùng chọn `T`. Phù hợp ảnh có foreground và background tương đối rõ.
### _3. Adaptive Threshold_
Tính ngưỡng riêng cho từng vùng ảnh dựa trên vùng lân cận `block_size` và hệ số `C`. Hỗ trợ:
- `Mean`
- `Gaussian`<br/>

Phù hợp ảnh có ánh sáng không đồng đều.

## How It Works

1. Người dùng chọn ảnh từ giao diện.
2. Flask kiểm tra phần mở rộng, lưu ảnh và chuyển ảnh sang grayscale.
3. User chọn thuật toán cùng các tham số cần thiết.
3. Server tính histogram và threshold phù hợp.
5. OpenCV tạo ảnh output, tính thống kê và đo Processing Time.
6. Kết quả được lưu và có thể xem/tải xuống.

## Performance and Security

- Gunicorn chạy 4 workers, 2 threads/worker, timeout 60s. Thời gian xử lý phụ thuộc vào kích thước ảnh, phần cứng và tải hệ thống.
- Upload tối đa 10 MB và áp dụng rate limit cho các API.
- Kiểm tra file, tham số xử lý và sự tồn tại của file trước khi thực hiện.

## License

This repository is developed and maintained by PnlhaiCSE. The source code, interface, configuration, and accompanying resources are the property of the author.<br/>
This project is released under the All Rights Reserved license and is not covered by any Open Source license. The use, copying, distribution, or modification of the source code is subject to the terms of this license.

## Author
Made with ❤️ by PnlhaiCSE