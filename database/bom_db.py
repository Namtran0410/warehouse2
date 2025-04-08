import sqlite3
import os

DB_PATH = "bombase.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_bom_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bom (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_san_pham TEXT NOT NULL,
            ten_san_pham TEXT NOT NULL,
            cycle_time REAL,
            trang_thai TEXT,
            nhan_cong INTEGER,
            version TEXT,
            bo_phan TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_boms():
    init_bom_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bom")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_bom(ma_san_pham):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bom WHERE ma_san_pham = ?", (ma_san_pham,))
    conn.commit()
    conn.close()

def add_bom(ma_san_pham, ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan):
    init_bom_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bom (ma_san_pham, ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (ma_san_pham, ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan))
    conn.commit()
    conn.close()

def update_bom(ma_san_pham, ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bom
        SET ten_san_pham = ?, cycle_time = ?, trang_thai = ?, nhan_cong = ?, version = ?, bo_phan = ?
        WHERE ma_san_pham = ?
    ''', (ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan, ma_san_pham))
    conn.commit()
    conn.close()
