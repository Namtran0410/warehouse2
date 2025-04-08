import tkinter as tk
from tkinter import messagebox, filedialog
from database.production_order_db import get_connection

def open_production_order_form(parent, ma=None, mode="add"):
    top = tk.Toplevel(parent)
    top.title("{} Lệnh Sản Xuất".format("Xem" if mode == "view" else "Sửa" if mode == "edit" else "Thêm"))

    # Các trường Label và Entry
    labels = ["Mã lệnh", "Ngày giờ", "Trạng thái", "File đính kèm"]
    entries = {}
    file_path = tk.StringVar()

    # Tạo Label và Entry cho các trường
    for i, label in enumerate(labels[:3]):  # 3 trường đầu
        tk.Label(top, text=label, anchor='w').grid(row=i, column=0, pady=5, sticky='e')
        entry = tk.Entry(top, width=30)
        entry.grid(row=i, column=1, pady=5)
        entries[label] = entry

    # Trường file đính kèm
    tk.Label(top, text=labels[3], anchor='w').grid(row=3, column=0, pady=5, sticky='e')
    tk.Entry(top, textvariable=file_path, width=30, state='readonly').grid(row=3, column=1, pady=5)
    tk.Button(top, text="Chọn file", command=lambda: browse_file(file_path), width=10).grid(row=3, column=2, padx=5)

    # Nếu chế độ là "edit" hoặc "view", tải thông tin từ DB
    if mode in ("edit", "view") and ma:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM production_order WHERE ma_lenh = ?", (ma,))
        row = cursor.fetchone()
        conn.close()

        if row:
            entries["Mã lệnh"].insert(0, row[0])  # ma_lenh
            entries["Ngày giờ"].insert(0, row[1])  # ngay_gio
            entries["Trạng thái"].insert(0, row[2])  # trang_thai
            file_path.set(row[3] if row[3] else "")  # file_path

            if mode == "view":
                for key in entries:
                    entries[key].config(state='disabled')
                tk.Button(top, text="Xem file", command=lambda: open_file(file_path.get()), width=10, state='normal' if file_path.get() else 'disabled').grid(row=3, column=3, padx=5)

    def browse_file(var):
        filename = filedialog.askopenfilename(title="Chọn file lệnh sản xuất")
        if filename:
            var.set(filename)

    def open_file(path):
        if path:
            import webbrowser
            webbrowser.open(path)

    def save():
        data = [e.get() for e in entries.values()]
        data.append(file_path.get())
        
        if not all(data[:3]):  # Chỉ yêu cầu 3 trường đầu bắt buộc
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng điền đầy đủ thông tin bắt buộc.")
            return

        # Kiểm tra xem mã lệnh đã tồn tại chưa
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM production_order WHERE ma_lenh = ?", (data[0],))
        existing_order = cursor.fetchone()
        conn.close()

        if existing_order and mode == "add":
            messagebox.showerror("Lỗi", "Mã lệnh đã tồn tại. Vui lòng nhập mã lệnh khác.")
            return

        # Nếu không có lỗi, tiến hành lưu dữ liệu
        conn = get_connection()
        cursor = conn.cursor()
        
        if mode == "edit":
            cursor.execute(""" 
                UPDATE production_order SET ngay_gio=?, trang_thai=?, file_path=? WHERE ma_lenh=?
            """, (data[1], data[2], data[3], data[0]))
        else:
            cursor.execute(""" 
                INSERT INTO production_order (ma_lenh, ngay_gio, trang_thai, file_path)
                VALUES (?, ?, ?, ?)
            """, (data[0], data[1], data[2], data[3]))
        
        conn.commit()
        conn.close()
        
        # Copy file đến thư mục lưu trữ (nếu có file mới)
        if data[3] and mode == "add":
            import shutil
            import os
            os.makedirs("production_orders", exist_ok=True)
            shutil.copy(data[3], f"production_orders/{data[0]}")
        
        parent.load_data()
        top.destroy()

    # Chỉ tạo nút "Lưu" nếu chế độ không phải là "view"
    if mode != "view":
        tk.Button(top, text="Lưu", command=save, bg="green", fg="white", width=15).grid(row=4, column=0, columnspan=2, pady=10)
    else:
        tk.Button(top, text="Đóng", command=top.destroy, bg="gray", fg="white", width=15).grid(row=4, column=0, columnspan=2, pady=10)