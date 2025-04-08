# gui/bom_form.py
import tkinter as tk
from tkinter import messagebox
from database.bom_db import get_connection

def open_bom_form(parent, ma_san_pham=None, mode="add"):
    top = tk.Toplevel(parent)
    top.title("{} BOM".format("Xem" if mode == "view" else "Sửa" if mode == "edit" else "Thêm"))

    labels = ["Mã sản phẩm", "Tên sản phẩm", "Cycle time", "Trạng thái", "Nhân công", "Version", "Bộ phận"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(top, text=label, anchor='w').grid(row=i, column=0, pady=5, sticky='e')
        entry = tk.Entry(top, width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[label] = entry

    # Nếu sửa hoặc xem thì load dữ liệu lên
    if mode in ("edit", "view") and ma_san_pham:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bom WHERE ma_san_pham = ?", (ma_san_pham,))
        row = cursor.fetchone()
        conn.close()

        if row:
            for i, key in enumerate(labels):
                entries[key].insert(0, row[i+1])
                if mode == "view":
                    entries[key].config(state='disabled')

    def save():
        data = [e.get() for e in entries.values()]
        if not all(data):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        if mode == "edit":
            cursor.execute("""
                UPDATE bom SET ten_san_pham=?, cycle_time=?, trang_thai=?, nhan_cong=?, version=?, bo_phan=?
                WHERE ma_san_pham=?
            """, data[1:] + [data[0]])
        else:
            cursor.execute("""
                INSERT INTO bom (ma_san_pham, ten_san_pham, cycle_time, trang_thai, nhan_cong, version, bo_phan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
        conn.commit()
        conn.close()
        parent.load_data()
        top.destroy()

    if mode != "view":
        tk.Button(top, text="Lưu", command=save, bg="green", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
    else:
        tk.Button(top, text="Đóng", command=top.destroy, bg="gray", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
