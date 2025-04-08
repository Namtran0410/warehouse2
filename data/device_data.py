# data/device_data.py
DEVICE_DATA = [
    {"ma": "TB001", "ten": "Máy Ép 01", "loai": "Máy Ép", "trang_thai": "Hoạt động"},
    {"ma": "TB002", "ten": "Máy Cắt 01", "loai": "Máy Cắt", "trang_thai": "Không hoạt động"},
]
import json
import os

DEVICE_FILE = os.path.join(os.path.dirname(__file__), '..', 'database', 'device_data.json')
DEVICE_DATA = []

def load_device_data():
    global DEVICE_DATA
    if os.path.exists(DEVICE_FILE):
        with open(DEVICE_FILE, 'r', encoding='utf-8') as f:
            DEVICE_DATA = json.load(f)
    else:
        DEVICE_DATA = []

def save_device_data():
    with open(DEVICE_FILE, 'w', encoding='utf-8') as f:
        json.dump(DEVICE_DATA, f, ensure_ascii=False, indent=4)

# Tải dữ liệu khi module được import
load_device_data()
