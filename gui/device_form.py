import tkinter as tk
from tkinter import messagebox
from database.device_db import get_connection

def open_device_form(parent, ma=None, mode="add"):
    top = tk.Toplevel(parent)
    top.title("{} Thiết bị".format("Xem" if mode == "view" else "Sửa" if mode == "edit" else "Thêm"))

    # Các trường Label và Entry
    labels = ["Mã thiết bị", "Tên thiết bị", "Loại thiết bị", "Trạng thái"]
    entries = {}

    # Tạo Label và Entry cho các trường
    for i, label in enumerate(labels):
        tk.Label(top, text=label, anchor='w').grid(row=i, column=0, pady=5, sticky='e')
        entry = tk.Entry(top, width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[label] = entry

    # Nếu chế độ là "edit" hoặc "view", tải thông tin thiết bị từ DB
    if mode in ("edit", "view") and ma:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device WHERE ma = ?", (ma,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Sửa lại thứ tự binding dữ liệu
            entries["Mã thiết bị"].insert(0, row[0])  # ma
            entries["Tên thiết bị"].insert(0, row[1])  # ten
            entries["Loại thiết bị"].insert(0, row[2])  # loai
            entries["Trạng thái"].insert(0, row[3])  # trang_thai

            # Nếu là chế độ "view", vô hiệu hóa các trường để người dùng chỉ xem
            if mode == "view":
                for key in entries:
                    entries[key].config(state='disabled')

    def save():
        data = [e.get() for e in entries.values()]
        if not all(data):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin.")
            return

        # Kiểm tra xem mã thiết bị đã tồn tại chưa
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device WHERE ma = ?", (data[0],))
        existing_device = cursor.fetchone()
        conn.close()

        if existing_device and mode == "add":
            messagebox.showerror("Lỗi", "Mã thiết bị đã tồn tại. Vui lòng nhập mã thiết bị khác.")
            return

        # Nếu không có lỗi, tiến hành lưu dữ liệu
        conn = get_connection()
        cursor = conn.cursor()
        
        if mode == "edit":
            cursor.execute(""" 
                UPDATE device SET ten=?, loai=?, trang_thai=? WHERE ma=?
            """, (data[1], data[2], data[3], data[0]))  # Cập nhật thông tin thiết bị
        else:
            cursor.execute(""" 
                INSERT INTO device (ma, ten, loai, trang_thai)
                VALUES (?, ?, ?, ?)
            """, (data[0], data[1], data[2], data[3]))  # Thêm thiết bị mới
        
        conn.commit()
        conn.close()
        parent.load_data()  # Load lại dữ liệu trong bảng
        top.destroy()  # Đóng cửa sổ

    # Chỉ tạo nút "Lưu" nếu chế độ không phải là "view"
    if mode != "view":
        tk.Button(top, text="Lưu", command=save, bg="green", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
    else:
        tk.Button(top, text="Đóng", command=top.destroy, bg="gray", fg="white", width=15).grid(row=len(labels), column=0, columnspan=2, pady=10)
