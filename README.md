# Cài đặt

##  Cài đặt môi trường và thư viện

1. Kiểm tra Python
- Mở terminal hoặc command prompt và chạy lệnh sau để kiểm tra phiên bản Python.
  
  ```bash
  python3 --version
  ```
- Phiên bản Python đang sử dụng là `3.13`.
2. Tạo môi trường ảo
- Di chuyển đến thư mục dự án trong terminal hoặc command prompt.
- Chạy lệnh sau để tạo môi trường ảo có tên `robot`.

    ```bash
    python3.13 -m venv robot
    ```
3. Kích hoạt môi trường ảo
- Trên Windows: `robot\Scripts\activate`
- Trên macOS và Linux: `source .venv/bin/activate`
  
4.  Cài đặt các thư viện:

    ```bash
    pip install -r requirements.txt
    ```
5. Cập nhật phiên bản thư viện hiện tại
    ```bash
    pip install --upgrade -r requirements.txt
    ```

##  Giao diện 
- Compile giao diện chạy lệnh
  ```bash
  pyuic5 <QT_name.ui> -o <QT_name.py>
  ```
## Chạy code

```bash
    python3 main.py
```
