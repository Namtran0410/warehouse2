# app.py
from tkinter import Tk
from gui.main_ui import MainUI

if __name__ == '__main__':
    root = Tk()
    root.title("Dashboard - Quản lý sản xuất")
    root.geometry("1100x650")
    app = MainUI(root)
    root.mainloop()