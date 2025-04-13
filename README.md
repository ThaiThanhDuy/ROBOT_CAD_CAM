# Cài đặt

##  Cài đặt môi trường và thư viện

1. Kiểm tra Python
- Mở terminal hoặc command prompt và chạy lệnh sau để kiểm tra phiên bản Python.
  
  ```bash
  python3 --version
  ```
- Phiên bản Python đang sử dụng là `3.10`.
- Tải python nếu chưa có.
  ```bash
  sudo apt install python3.10-venv
  ```
2. Tạo môi trường ảo
- Di chuyển đến thư mục dự án trong terminal hoặc command prompt.
- Chạy lệnh sau để tạo môi trường ảo có tên `robot`.

    ```bash
    python3 -m venv ~/qt5_env

    ```
3. Kích hoạt môi trường ảo
   ```bash
   source ~/qt5_env/bin/activate
   ```
  
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
