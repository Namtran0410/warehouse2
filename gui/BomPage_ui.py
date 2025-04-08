# gui/BomPage_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from gui.bom_form import open_bom_form
from utils.export_csv import export_to_csv
from database.bom_db import get_all_boms, delete_bom

class BomPageUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.selected_boms = set()  # Lưu trữ các BOM được chọn

        tk.Label(self, text="Danh Sách BOM", font=("Helvetica", 18, "bold"), anchor='w').pack(pady=10, anchor='w')

        top_frame = tk.Frame(self)
        top_frame.pack(anchor='w', pady=10)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        tk.Entry(top_frame, textvariable=self.search_var, width=30).grid(row=0, column=0, padx=5)
        ttk.Combobox(top_frame, textvariable=self.status_var, values=["Tất cả trạng thái", "Hoạt động", "Không hoạt động"], width=20).grid(row=0, column=1, padx=5)

        tk.Button(top_frame, text="≡ Lọc", command=self.filter_data, bg="DodgerBlue", fg="white", width=10).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="Xuất CSV", command=export_to_csv, bg="green", fg="white", width=10).grid(row=0, column=3, padx=5)
        tk.Button(top_frame, text="+ Thêm BOM", command=lambda: open_bom_form(self), bg="blue", fg="white", width=12).grid(row=0, column=4, padx=5)
        tk.Button(top_frame, text="Xóa tất cả đã chọn", command=self.delete_selected, bg="red", fg="white", width=15).grid(row=0, column=5, padx=5)

        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=30, font=("Helvetica", 10), borderwidth=1, relief="solid")
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 10, "bold"))

        columns = ("chon", "ma_san_pham", "ten_san_pham", "cycle_time", "trang_thai", "nhan_cong", "version", "bo_phan", "hanh_dong")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Custom.Treeview")

        # Cấu hình các cột
        self.tree.column("chon", anchor='center', width=50, stretch=False)
        self.tree.column("hanh_dong", anchor='center', width=150, stretch=False)
        
        headings = [
            ("chon", "Chọn"),
            ("ma_san_pham", "Mã sản phẩm"),
            ("ten_san_pham", "Tên sản phẩm"),
            ("cycle_time", "Cycle time"),
            ("trang_thai", "Trạng thái"),
            ("nhan_cong", "Nhân công"),
            ("version", "Ver"),
            ("bo_phan", "Bộ phận"),
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
        rows = get_all_boms()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            ma_san_pham = row[0]  # Lấy mã sản phẩm
            checked = "✓" if ma_san_pham in self.selected_boms else ""
            self.tree.insert("", tk.END, values=(checked,) + row[1:] + ("👁️     ✏️     🗑️",))

    def filter_data(self):
        search_text = self.search_var.get().strip().lower()
        status_filter = self.status_var.get()

        rows = get_all_boms()
        filtered_rows = []

        for row in rows:
            ma_san_pham, ten_san_pham, _, trang_thai, *_ = row
            if search_text and search_text not in ma_san_pham.lower() and search_text not in ten_san_pham.lower():
                continue
            if status_filter == "Hoạt động" and trang_thai != "Hoạt động":
                continue
            if status_filter == "Không hoạt động" and trang_thai != "Không hoạt động":
                continue
            filtered_rows.append(row)

        self.tree.delete(*self.tree.get_children())
        for row in filtered_rows:
            ma_san_pham = row[0]
            checked = "✓" if ma_san_pham in self.selected_boms else ""
            self.tree.insert("", tk.END, values=(checked,) + row[1:] + ("👁️     ✏️     🗑️",))

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id:
            return

        # Xử lý khi click vào cột chọn
        if column == '#1':  # Cột chọn là cột thứ 1
            values = self.tree.item(item_id, "values")
            ma_san_pham = values[1]  # Mã sản phẩm ở vị trí thứ 2 (sau cột chọn)
            if ma_san_pham in self.selected_boms:
                self.selected_boms.remove(ma_san_pham)
            else:
                self.selected_boms.add(ma_san_pham)
            self.load_data()  # Tải lại dữ liệu để cập nhật trạng thái checkbox
            return

        # Xử lý khi click vào cột hành động
        if column == '#9':  # Cột hành động là cột thứ 9 (sau khi thêm cột chọn)
            col_bbox = self.tree.bbox(item_id, column)
            if not col_bbox:
                return

            x_offset = event.x - col_bbox[0]
            col_width = col_bbox[2]
            icon_width = col_width // 3

            clicked_index = int(x_offset // icon_width)
            ma_san_pham = self.tree.item(item_id, "values")[1]  # Index 1 vì có thêm cột chọn

            if clicked_index == 0:
                self.view_bom(ma_san_pham)
            elif clicked_index == 1:
                self.edit_bom(ma_san_pham)
            elif clicked_index == 2:
                result = messagebox.askyesno("Xóa BOM", "Bạn có chắc chắn muốn xóa BOM này không?")
                if result:
                    delete_bom(ma_san_pham)
                    self.selected_boms.discard(ma_san_pham)  # Xóa khỏi danh sách chọn nếu có
                    self.load_data()
                    messagebox.showinfo("Xóa BOM", f"Đã xóa BOM: {ma_san_pham}")

    def view_bom(self, ma_san_pham):
        open_bom_form(self, ma_san_pham, mode="view")

    def edit_bom(self, ma_san_pham):
        open_bom_form(self, ma_san_pham, mode="edit")
        
    def delete_selected(self):
        if not self.selected_boms:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một BOM để xóa")
            return
            
        result = messagebox.askyesno("Xóa BOM", f"Bạn có chắc muốn xóa {len(self.selected_boms)} BOM đã chọn?")
        if result:
            for ma in list(self.selected_boms):  # Tạo bản sao để có thể xóa trong khi lặp
                delete_bom(ma)
            self.selected_boms.clear()
            self.load_data()
            messagebox.showinfo("Thành công", "Đã xóa các BOM đã chọn")