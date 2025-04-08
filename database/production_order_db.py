import sqlite3
import os

DB_PATH = "database/production_orders.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_order_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_order (
            ma_lenh TEXT PRIMARY KEY,
            ngay_gio TEXT NOT NULL,
            trang_thai TEXT NOT NULL,
            file_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_orders():
    init_order_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM production_order")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_order(ma_lenh, ngay_gio, trang_thai, file_path=None):
    init_order_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO production_order (ma_lenh, ngay_gio, trang_thai, file_path) VALUES (?, ?, ?, ?)",
        (ma_lenh, ngay_gio, trang_thai, file_path)
    )
    conn.commit()
    conn.close()

def update_order(ma_lenh, ngay_gio, trang_thai, file_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE production_order SET ngay_gio=?, trang_thai=?, file_path=? WHERE ma_lenh=?",
        (ngay_gio, trang_thai, file_path, ma_lenh)
    )
    conn.commit()
    conn.close()

def delete_order(ma_lenh):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM production_order WHERE ma_lenh=?", (ma_lenh,))
    conn.commit()
    conn.close()
    
    # Xóa file đính kèm nếu có
    file_path = f"production_orders/{ma_lenh}"
    if os.path.exists(file_path):
        os.remove(file_path)