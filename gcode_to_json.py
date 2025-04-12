import json
import re

# ===== Cấu hình mặc định =====
default_orientation = {"rx": 0.0, "ry": 1.5708, "rz": 0.0}  # giữ hướng TCP cố định
default_feedrate = 1000

# ===== Đọc G-code và phân tích =====
def parse_gcode(file_path):
    tcp_path = []
    current_feedrate = default_feedrate

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip().upper()

            if line.startswith("G1") or line.startswith("G0"):
                # Tìm các tham số
                x = re.search(r'X([-\d.]+)', line)
                y = re.search(r'Y([-\d.]+)', line)
                z = re.search(r'Z([-\d.]+)', line)
                f_val = re.search(r'F([-\d.]+)', line)

                if f_val:
                    current_feedrate = float(f_val.group(1))

                if x or y or z:
                    point = {
                        "x": float(x.group(1)) if x else 0.0,
                        "y": float(y.group(1)) if y else 0.0,
                        "z": float(z.group(1)) if z else 0.0,
                        "rx": default_orientation["rx"],
                        "ry": default_orientation["ry"],
                        "rz": default_orientation["rz"],
                        "feedrate": current_feedrate
                    }
                    tcp_path.append(point)
    return tcp_path

# ===== Lưu ra file JSON =====
def write_json(data, output_path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

# ===== Main =====
if __name__ == "__main__":
    input_file = "path.nc"
    output_file = "tcp_path.json"

    tcp_data = parse_gcode(input_file)
    write_json(tcp_data, output_file)

    print(f"Đã chuyển G-code từ {input_file} sang {output_file}")
