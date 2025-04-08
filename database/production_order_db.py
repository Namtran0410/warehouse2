#production_order_db.py
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
            ma TEXT PRIMARY KEY,
            ten TEXT NOT NULL,
            nhan_cong TEXT NOT NULL,
            thiet_bi TEXT NOT NULL,
            trang_thai TEXT NOT NULL,
            file_path TEXT
        )
    """)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(production_order)")
    columns = cursor.fetchall()

    conn.commit()
    conn.close()

def get_all_PO():
    init_order_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM production_order")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_order(ma, ten, nhan_cong, thiet_bi, trang_thai):
    init_order_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO production_order (ma, ten, nhan_cong, thiet_bi, trang_thai) VALUES (?, ?, ?, ?, ?)",
        (ma, ten, nhan_cong, thiet_bi, trang_thai)
    )
    conn.commit()
    conn.close()

def update_order(ma, ten, nhan_cong, thiet_bi, trang_thai):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE production_order SET ngay_gio=?, trang_thai=?, file_path=? WHERE ma_lenh=?",
        (ten, nhan_cong, thiet_bi, trang_thai, ma)
    )

    conn.commit()
    conn.close()

def delete_PO(ma):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM production_order WHERE ma=?", (ma,))
    conn.commit()
    conn.close()