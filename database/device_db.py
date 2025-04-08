import sqlite3
import os

DB_PATH = "database/devicebase.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

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

def get_all_devices():
    init_device_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM device")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_device(ma, ten, loai, trang_thai):
    init_device_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO device (ma, ten, loai, trang_thai) VALUES (?, ?, ?, ?)",
        (ma, ten, loai, trang_thai)
    )
    conn.commit()
    conn.close()

def update_device(ma, ten, loai, trang_thai):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE device SET ten=?, loai=?, trang_thai=? WHERE ma=?",
        (ten, loai, trang_thai, ma)
    )
    conn.commit()
    conn.close()

def delete_device(ma):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM device WHERE ma=?", (ma,))
    conn.commit()
    conn.close()
