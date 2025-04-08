# main.py
import tkinter as tk
from gui.BomPage_ui import BomPageUI
from gui.device_ui import DevicePageUI

class MainUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.geometry("1200x700")
        self.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#ddd", width=180)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.sidebar, text="🍣 Nigata Vietnam", font=("Helvetica", 11, "bold"), bg="#ddd").pack(pady=25)

        self.sidebar_buttons = []
        labels = ["Dashboard", "Quản lý BoM", "Lệnh sản xuất", "Báo cáo sản xuất", "Quản lý thiết bị"]

        for i, label in enumerate(labels):
            btn = tk.Button(self.sidebar, text=label, bg="#eee", relief=tk.FLAT, anchor='w', padx=10)
            btn.pack(fill=tk.X, padx=10, pady=3)
            self.sidebar_buttons.append(btn)

        # Gán hành động cho từng nút
        self.sidebar_buttons[1].configure(command=lambda: self.load_bom_page())
        self.sidebar_buttons[4].configure(command=lambda: self.load_device_page())

        # Content
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.load_bom_page()

    def reset_sidebar_buttons(self):
        for btn in self.sidebar_buttons:
            btn.configure(bg="#eee", fg="black")

    def load_bom_page(self):
        self.reset_sidebar_buttons()
        self.sidebar_buttons[1].configure(bg="green", fg="white")
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        BomPageUI(master=self.content_frame)

    def load_device_page(self):
        self.reset_sidebar_buttons()
        self.sidebar_buttons[4].configure(bg="green", fg="white")
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        DevicePageUI(self.content_frame)  # Thêm vào content_frame để hiển thị


def main():
    root = tk.Tk()
    root.title("Nigata MES")
    app = MainUI(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()