import tkinter as tk
from tkinter import messagebox
from database.production_order_db import get_connection

def open_PO_form(parent, ma=None, mode="add"):
    top = tk.Toplevel(parent)
    top.title("{} Lệnh Sản Xuất".format("Xem" if mode == "view" else "Sửa" if mode == "edit" else "Thêm"))

    # Các trường Label và Entry
    labels = ["Mã PO", "Tên sản phẩm", "Nhân công", "Thiết bị", "Trạng thái"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(top, text=label, anchor='w').grid(row=i, column=0, pady=5, sticky='e')
        entry = tk.Entry(top, width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[label] = entry

    # Nếu chế độ là "edit" hoặc "view", tải thông tin từ DB
    if mode in ("edit", "view") and ma:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM production_order WHERE ma = ?", (ma,))
        row = cursor.fetchone()
        conn.close()

        if row:
            entries["Mã PO"].insert(0, row[0])
            entries["Tên sản phẩm"].insert(0, row[1])
            entries["Nhân công"].insert(0, row[2])
            entries["Thiết bị"].insert(0, row[3])
            entries["Trạng thái"].insert(0, row[4])

            if mode == "view":
                for key in entries:
                    entries[key].config(state='disabled')

    def save():
        data = [e.get() for e in entries.values()]
        if not all(data):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM production_order WHERE ma = ?", (data[0],))
        existing_PO = cursor.fetchone()
        conn.close()

        if existing_PO and mode == "add":
            messagebox.showerror("Lỗi", "Mã PO đã tồn tại. Vui lòng nhập mã PO khác.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        if mode == "edit":
            cursor.execute("""
                UPDATE production_order SET ten=?, nhan_cong=?, thiet_bi=?, trang_thai=? WHERE ma=?
            """, (data[1], data[2], data[3], data[4], data[0]))
        else:
            cursor.execute("""
                INSERT INTO production_order (ma, ten, nhan_cong, thiet_bi, trang_thai)
                VALUES (?, ?, ?, ?, ?)
            """, (data[0], data[1], data[2], data[3], data[4]))

        conn.commit()
        conn.close()
        parent.load_data()
        top.destroy()

    if mode != "view":
        tk.Button(top, text="Lưu", command=save, bg="green", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
    else:
        tk.Button(top, text="Đóng", command=top.destroy, bg="gray", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
