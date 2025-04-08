import tkinter as tk
from tkinter import ttk, messagebox
from gui.device_form import open_device_form
from utils.export_csv import export_to_csv
from database.device_db import get_all_devices, delete_device

class DevicePageUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.selected_devices = set()  # Lưu trữ các thiết bị được chọn

        tk.Label(self, text="Danh Sách Thiết Bị", font=("Helvetica", 18, "bold"), anchor='w').pack(pady=10, anchor='w')

        top_frame = tk.Frame(self)
        top_frame.pack(anchor='w', pady=10)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        tk.Entry(top_frame, textvariable=self.search_var, width=30).grid(row=0, column=0, padx=5)
        ttk.Combobox(top_frame, textvariable=self.status_var, values=["Tất cả trạng thái", "Hoạt động", "Không hoạt động"], width=20).grid(row=0, column=1, padx=5)

        tk.Button(top_frame, text="≡ Lọc", command=self.filter_data, bg="DodgerBlue", fg="white", width=10).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="Xuất CSV", command=export_to_csv, bg="green", fg="white", width=10).grid(row=0, column=3, padx=5)
        tk.Button(top_frame, text="+ Thêm Thiết Bị", command=lambda: open_device_form(self), bg="blue", fg="white", width=15).grid(row=0, column=4, padx=5)
        tk.Button(top_frame, text="Xóa tất cả đã chọn", command=self.delete_selected, bg="red", fg="white", width=15).grid(row=0, column=5, padx=5)

        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=30, font=("Helvetica", 10), borderwidth=1, relief="solid")
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 10, "bold"))

        columns = ("chon", "ma", "ten", "loai", "trang_thai", "hanh_dong")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Custom.Treeview")
        
        # Cấu hình các cột
        self.tree.column("chon", anchor='center', width=50, stretch=False)
        self.tree.column("hanh_dong", anchor='center', width=150, stretch=False)
        
        headings = [
            ("chon", "Chọn"),
            ("ma", "Mã thiết bị"),
            ("ten", "Tên thiết bị"),
            ("loai", "Loại thiết bị"),
            ("trang_thai", "Trạng thái"),
            ("hanh_dong", "Hành động")
        ]

        for col, label in headings:
            self.tree.heading(col, text=label)
            if col not in ("chon", "hanh_dong"):
                self.tree.column(col, anchor='w', width=130, minwidth=100)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        self.load_data()

    def load_data(self):
        rows = get_all_devices()
        
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            ma = row[0]  # Lấy mã thiết bị
            # Tạo checkbox (sử dụng Unicode hoặc ký tự đặc biệt)
            checked = "✓" if ma in self.selected_devices else ""
            self.tree.insert("", tk.END, values=(checked,) + row + ("👁️     ✏️     🗑️",))

    def filter_data(self):
        search_text = self.search_var.get().strip().lower()
        status_filter = self.status_var.get()

        rows = get_all_devices()
        filtered_rows = []

        for row in rows:
            ma, ten, loai, trang_thai = row
            if search_text and search_text not in ma.lower() and search_text not in ten.lower():
                continue
            if status_filter == "Hoạt động" and trang_thai != "Hoạt động":
                continue
            if status_filter == "Không hoạt động" and trang_thai != "Không hoạt động":
                continue
            filtered_rows.append(row)

        self.tree.delete(*self.tree.get_children())
        for row in filtered_rows:
            ma = row[0]
            checked = "✓" if ma in self.selected_devices else ""
            self.tree.insert("", tk.END, values=(checked,) + row + ("👁️     ✏️     🗑️",))

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id:
            return

        # Xử lý khi click vào cột chọn
        if column == '#1':  # Cột chọn là cột thứ 1
            values = self.tree.item(item_id, "values")
            ma = values[1]  # Mã thiết bị ở vị trí thứ 2 (sau cột chọn)
            if ma in self.selected_devices:
                self.selected_devices.remove(ma)
            else:
                self.selected_devices.add(ma)
            self.load_data()  # Tải lại dữ liệu để cập nhật trạng thái checkbox
            return

        # Xử lý khi click vào cột hành động
        if column == '#6':  # Cột hành động là cột thứ 6 (sau khi thêm cột chọn)
            col_bbox = self.tree.bbox(item_id, column)
            if not col_bbox:
                return

            x_offset = event.x - col_bbox[0]
            col_width = col_bbox[2]
            
            if x_offset < col_width * 0.33:  # 1/3 đầu (Xem)
                self.view_device(self.tree.item(item_id, "values")[1])  # Index 1 vì có thêm cột chọn
            elif x_offset < col_width * 0.66:  # 1/3 giữa (Sửa)
                self.edit_device(self.tree.item(item_id, "values")[1])  # Index 1 vì có thêm cột chọn
            else:  # 1/3 cuối (Xóa)
                ma_thiet_bi = self.tree.item(item_id, "values")[1]  # Index 1 vì có thêm cột chọn
                result = messagebox.askyesno("Xóa thiết bị", f"Bạn có chắc muốn xóa thiết bị {ma_thiet_bi}?")
                if result:
                    delete_device(ma_thiet_bi)
                    self.selected_devices.discard(ma_thiet_bi)  # Xóa khỏi danh sách chọn nếu có
                    self.load_data()

    def view_device(self, ma_thiet_bi):
        open_device_form(self, ma_thiet_bi, mode="view")

    def edit_device(self, ma_thiet_bi):
        open_device_form(self, ma_thiet_bi, mode="edit")
        
    def delete_selected(self):
        if not self.selected_devices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một thiết bị để xóa")
            return
            
        result = messagebox.askyesno("Xóa thiết bị", f"Bạn có chắc muốn xóa {len(self.selected_devices)} thiết bị đã chọn?")
        if result:
            for ma in list(self.selected_devices):  # Tạo bản sao để có thể xóa trong khi lặp
                delete_device(ma)
            self.selected_devices.clear()
            self.load_data()
            messagebox.showinfo("Thành công", "Đã xóa các thiết bị đã chọn")