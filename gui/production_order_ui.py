import tkinter as tk
from tkinter import ttk, messagebox
from gui.production_order_form import open_PO_form
from utils.export_csv import export_to_csv
from database.production_order_db import get_all_PO, delete_PO
import os


class ProductionOrderPageUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.selected_PO = set()  # Lưu trữ các lệnh sản xuất được chọn

        tk.Label(self, text="Danh Sách Lệnh Sản Xuất", font=("Helvetica", 18, "bold"), anchor='w').pack(pady=10, anchor='w')

        top_frame = tk.Frame(self)
        top_frame.pack(anchor='w', pady=10)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        tk.Entry(top_frame, textvariable= self.search_var, width= 30).grid(row = 0, column= 0, padx= 5)
        ttk.Combobox(top_frame, textvariable= self.status_var, values= ["Tất cả trạng thái", "Đã hoàn thành"
        "Chưa hoàn thành", "Đang thực hiện"]) 

        tk.Button(top_frame, text="≡ Lọc", command=self.filter_data, bg="DodgerBlue", fg="white", width=10).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="Xuất Pdf", command=export_to_csv, bg="green", fg="white", width=10).grid(row=0, column=3, padx=5)
        tk.Button(top_frame, text="+ Thêm PO", command=lambda: open_PO_form(self), bg="blue", fg="white", width=15).grid(row=0, column=4, padx=5)
        tk.Button(top_frame, text="+ Nhập PO", command=lambda: open_PO_form(self), bg="blue", fg="white", width=15).grid(row=0, column=5, padx=5)
        tk.Button(top_frame, text="Xóa tất cả đã chọn", command=self.delete_selected, bg="red", fg="white", width=15).grid(row=0, column=6, padx=5)

        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=30, font=("Helvetica", 10), borderwidth=1, relief="solid")
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 10, "bold"))

        columns = ("chon", "ma", "ten","nhan_cong","thiet_bi", "trang_thai", "hanh_dong")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Custom.Treeview")

        # Cấu hình các cột
        self.tree.column("chon", anchor='center', width=50, stretch=False)
        self.tree.column("hanh_dong", anchor='center', width=150, stretch=False)

        headings = [
            ("chon", "Chọn"),
            ("ma", "Mã PO"),
            ("ten", "Tên sản phẩm"),
            ("nhan_cong", "Nhân công"),
            ("thiet_bi", "Thiết bị"),
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
        rows = get_all_PO()
        
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            ma = row[0]  # Lấy mã thiết bị
            # Tạo checkbox (sử dụng Unicode hoặc ký tự đặc biệt)
            checked = "✓" if ma in self.selected_PO else ""
            self.tree.insert("", tk.END, values=(checked,) + tuple(row) + ("👁️     ✏️     🗑️",))

    def filter_data(self):
        search_text = self.search_var.get().strip().lower()
        status_filter = self.status_var.get()

        rows = get_all_PO()
        filtered_rows = []

        for row in rows:
            ma, ten, nhan_cong, thiet_bi, trang_thai = row
            if search_text and search_text not in ma.lower() and search_text not in ten.lower():
                continue
            if status_filter == "Đã hoàn thành" and trang_thai != "Đã hoàn thành":
                continue
            if status_filter == "Chưa hoàn thành" and trang_thai != "Chưa hoàn thành":
                continue
            if status_filter == "Đang thực hiện" and trang_thai != "Đang thực hiện":
                continue
            filtered_rows.append(row)

        self.tree.delete(*self.tree.get_children())
        for row in filtered_rows:
            ma = row[0]
            checked = "✓" if ma in self.selected_PO else ""
            self.tree.insert("", tk.END, values=(checked,) + tuple(row) + ("👁️     ✏️     🗑️",))

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id:
            return

        # Xử lý khi click vào cột chọn
        if column == '#1':  # Cột chọn là cột thứ 1
            values = self.tree.item(item_id, "values")
            ma = values[1]  # Mã thiết bị ở vị trí thứ 2 (sau cột chọn)
            if ma in self.selected_PO:
                self.selected_PO.remove(ma)
            else:
                self.selected_PO.add(ma)
            self.load_data()  # Tải lại dữ liệu để cập nhật trạng thái checkbox
            return

        # Xử lý khi click vào cột hành động
        if column == '#7':  # Cột hành động
            col_bbox = self.tree.bbox(item_id, column)
            if not col_bbox:
                return

            x_offset = event.x - col_bbox[0]
            col_width = col_bbox[2]

            ma_PO = self.tree.item(item_id, "values")[1]

            if x_offset < col_width * 0.33:
                self.view_PO(ma_PO)
            elif x_offset < col_width * 0.66:
                self.edit_PO(ma_PO)
            else:
                result = messagebox.askyesno("Xóa PO", f"Bạn có chắc muốn xóa PO {ma_PO}?")
                if result:
                    delete_PO(ma_PO)
                    self.selected_PO.discard(ma_PO)
                    self.load_data()

    def view_PO(self, ma_thiet_bi):
        open_PO_form(self, ma_thiet_bi, mode="view")

    def edit_PO(self, ma_thiet_bi):
        open_PO_form(self, ma_thiet_bi, mode="edit")
        
    def delete_selected(self):
        if not self.selected_PO:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một PO để xóa")
            return

        result = messagebox.askyesno("Xóa PO", f"Bạn có chắc muốn xóa {len(self.selected_PO)} PO đã chọn?")
        if result:
            for ma in list(self.selected_PO):  # Tạo bản sao để có thể xóa trong khi lặp
                delete_PO(ma)
            self.selected_PO.clear()
            self.load_data()
            messagebox.showinfo("Thành công", "Đã xóa các PO đã chọn")