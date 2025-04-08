import sqlite3
import os

DB_PATH = "devicebase.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_connection()
        cursor = conn.cursor()
        with open("Dump20250408.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()

def init_device_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device (
            ma TEXT PRIMARY KEY,
            ten TEXT NOT NULL,
            loai TEXT NOT NULL,
            trang_thai TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_device_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device (
            ma TEXT PRIMARY KEY,
            ten TEXT NOT NULL,
            loai TEXT NOT NULL,
            trang_thai TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_all_devices():
    create_device_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM device")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"ma": row[0], "ten": row[1], "loai": row[2], "trang_thai": row[3]}
        for row in rows
    ]

def add_device(ma, ten, loai, trang_thai):
    create_device_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO device (ma, ten, loai, trang_thai) VALUES (?, ?, ?, ?)", (ma, ten, loai, trang_thai))
    conn.commit()
    conn.close()

def delete_device(ma_thiet_bi):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM device WHERE ma = ?", (ma_thiet_bi,))
        conn.commit()
    except Exception as e:
        print(f"Lỗi khi xóa thiết bị: {e}")
    finally:
        conn.close()

def update_device(ma, ten, loai, trang_thai):
    create_device_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE device SET ten=?, loai=?, trang_thai=? WHERE ma=?", (ten, loai, trang_thai, ma))
    conn.commit()
    conn.close()
