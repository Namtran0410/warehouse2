import tkinter as tk
from tkinter import ttk, messagebox
from gui.production_order_form import open_production_order_form
from utils.export_csv import export_to_csv
from database.production_order_db import get_all_orders, delete_order
import os
import webbrowser

class ProductionOrderPageUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.selected_orders = set()  # Lưu trữ các lệnh sản xuất được chọn

        tk.Label(self, text="Danh Sách Lệnh Sản Xuất", font=("Helvetica", 18, "bold"), anchor='w').pack(pady=10, anchor='w')

        top_frame = tk.Frame(self)
        top_frame.pack(anchor='w', pady=10)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        tk.Entry(top_frame, textvariable=self.search_var, width=30).grid(row=0, column=0, padx=5)
        ttk.Combobox(top_frame, textvariable=self.status_var, 
                    values=["Tất cả trạng thái", "Hoạt động", "Hoàn thành", "Không hoạt động"], 
                    width=20).grid(row=0, column=1, padx=5)

        tk.Button(top_frame, text="≡ Lọc", command=self.filter_data, bg="DodgerBlue", fg="white", width=10).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="Tải về", command=self.download_selected, bg="green", fg="white", width=10).grid(row=0, column=3, padx=5)
        tk.Button(top_frame, text="Upload", command=lambda: open_production_order_form(self), bg="blue", fg="white", width=10).grid(row=0, column=4, padx=5)
        tk.Button(top_frame, text="Xóa đã chọn", command=self.delete_selected, bg="red", fg="white", width=12).grid(row=0, column=5, padx=5)

        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=30, font=("Helvetica", 10), borderwidth=1, relief="solid")
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 10, "bold"))

        columns = ("chon", "ma_lenh", "ngay_gio", "trang_thai", "hanh_dong")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Custom.Treeview")
        
        # Cấu hình các cột
        self.tree.column("chon", anchor='center', width=50, stretch=False)
        self.tree.column("ma_lenh", anchor='w', width=200)
        self.tree.column("ngay_gio", anchor='center', width=150)
        self.tree.column("trang_thai", anchor='center', width=120)
        self.tree.column("hanh_dong", anchor='center', width=150, stretch=False)
        
        headings = [
            ("chon", "Chọn"),
            ("ma_lenh", "Lệnh sản xuất"),
            ("ngay_gio", "Ngày giờ"),
            ("trang_thai", "Trạng thái"),
            ("hanh_dong", "Hành động")
        ]

        for col, label in headings:
            self.tree.heading(col, text=label)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_double_click)  # Xử lý double click để mở file

        self.load_data()

    def load_data(self):
        rows = get_all_orders()
        
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            ma_lenh = row[0]  # Lấy mã lệnh
            checked = "✓" if ma_lenh in self.selected_orders else ""
            self.tree.insert("", tk.END, values=(checked,) + row + ("👁️     ✏️     🗑️",))

    def filter_data(self):
        search_text = self.search_var.get().strip().lower()
        status_filter = self.status_var.get()

        rows = get_all_orders()
        filtered_rows = []

        for row in rows:
            ma_lenh, _, trang_thai = row
            if search_text and search_text not in ma_lenh.lower():
                continue
            if status_filter == "Hoạt động" and trang_thai != "Hoạt động":
                continue
            if status_filter == "Hoàn thành" and trang_thai != "Hoàn thành":
                continue
            if status_filter == "Không hoạt động" and trang_thai != "Không hoạt động":
                continue
            filtered_rows.append(row)

        self.tree.delete(*self.tree.get_children())
        for row in filtered_rows:
            ma_lenh = row[0]
            checked = "✓" if ma_lenh in self.selected_orders else ""
            self.tree.insert("", tk.END, values=(checked,) + row[1:] + ("👁️     ✏️     🗑️",))

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id:
            return

        # Xử lý khi click vào cột chọn
        if column == '#1':  # Cột chọn là cột thứ 1
            values = self.tree.item(item_id, "values")
            ma_lenh = values[1]  # Mã lệnh ở vị trí thứ 2 (sau cột chọn)
            if ma_lenh in self.selected_orders:
                self.selected_orders.remove(ma_lenh)
            else:
                self.selected_orders.add(ma_lenh)
            self.load_data()
            return

        # Xử lý khi click vào cột hành động
        if column == '#5':  # Cột hành động là cột thứ 5
            col_bbox = self.tree.bbox(item_id, column)
            if not col_bbox:
                return

            x_offset = event.x - col_bbox[0]
            col_width = col_bbox[2]
            
            if x_offset < col_width * 0.33:  # 1/3 đầu (Xem)
                self.view_order(self.tree.item(item_id, "values")[1])
            elif x_offset < col_width * 0.66:  # 1/3 giữa (Sửa)
                self.edit_order(self.tree.item(item_id, "values")[1])
            else:  # 1/3 cuối (Xóa)
                ma_lenh = self.tree.item(item_id, "values")[1]
                result = messagebox.askyesno("Xóa lệnh", f"Bạn có chắc muốn xóa lệnh {ma_lenh}?")
                if result:
                    delete_order(ma_lenh)
                    self.selected_orders.discard(ma_lenh)
                    self.load_data()

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id or column != '#2':  # Chỉ xử lý khi double click vào cột "Lệnh sản xuất"
            return

        ma_lenh = self.tree.item(item_id, "values")[1]
        file_path = f"production_orders/{ma_lenh}"  # Giả sử file lưu trong thư mục production_orders
        if os.path.exists(file_path):
            webbrowser.open(file_path)
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {file_path}")

    def view_order(self, ma_lenh):
        open_production_order_form(self, ma_lenh, mode="view")

    def edit_order(self, ma_lenh):
        open_production_order_form(self, ma_lenh, mode="edit")
        
    def delete_selected(self):
        if not self.selected_orders:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một lệnh để xóa")
            return
            
        result = messagebox.askyesno("Xóa lệnh", f"Bạn có chắc muốn xóa {len(self.selected_orders)} lệnh đã chọn?")
        if result:
            for ma in list(self.selected_orders):
                delete_order(ma)
            self.selected_orders.clear()
            self.load_data()
            messagebox.showinfo("Thành công", "Đã xóa các lệnh đã chọn")

    def download_selected(self):
        if not self.selected_orders:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một lệnh để tải về")
            return
            
        # Giả sử chúng ta sẽ nén các file đã chọn vào 1 file zip
        # Trong thực tế cần thêm code để xử lý nén file
        messagebox.showinfo("Thông báo", f"Đã chuẩn bị tải về {len(self.selected_orders)} lệnh sản xuất")