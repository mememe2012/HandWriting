import tkinter as tk
from tkinter import ttk
from math import *

class _input():
    def __init__(self, parent, text, title, color='black'):
        self.input_text = None
        self.top = tk.Toplevel(parent)
        width = 300 + len(text) * 3
        self.top.geometry(f"{width}x150+500+300")
        self.top.resizable(0, 0)
        self.top.iconbitmap('./icon/icon.ico')
        self.top.grab_set()

        self.entry = ttk.Entry(self.top)
        self.entry.pack(pady=20, ipadx=10, ipady=5)

        ttk.Label(self.top, text=text, foreground=color).pack()

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="确认", command=self.on_confirm).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).grid(row=0, column=1, padx=5)

        self.top.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.top.title(title)
        self.top.wait_window()


    def on_confirm(self):
        self.input_text = self.entry.get()
        self.top.destroy()

    def on_cancel(self):
        self.input_text = None
        self.top.destroy()

def get_input(text, title, color='black'):
    root = tk.Tk()
    root.withdraw()
    dialog = _input(root, text, title, color)
    return dialog.input_text

def message_box(text, title, parent, color='black', bg_color='white'):
    root = tk.Toplevel(parent)
    width = 300 + len(text) * 3
    root.geometry(f"{width}x100+500+300")
    root.resizable(0, 0)
    root.grab_set()
    root.iconbitmap('./icon/icon.ico')

    ttk.Label(root, text=text, foreground=color, background=bg_color).pack()

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="确认", command=root.destroy).grid(row=0, column=0, padx=5)

    root.title(title)
    root.wait_window()

def choose_box(parent, title, text, button_1_text, button_2_text, color='black', bg_color='white'):
    root = tk.Toplevel(parent)
    width = 300 + len(text) * 3
    root.geometry(f"{width}x80+500+300")
    root.resizable(0, 0)
    root.grab_set()
    root.iconbitmap('./icon/icon.ico')

    ttk.Label(root, text=text, foreground=color, background=bg_color).pack()

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    choose_ = False

    def _button_1():
        nonlocal choose_
        choose_ = True
        root.destroy()

    def _button_2():
        nonlocal choose_
        choose_ = False
        root.destroy()
    
    ttk.Button(btn_frame, text=button_1_text, command=_button_1).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text=button_2_text, command=_button_2).grid(row=0, column=1, padx=5)

    root.title(title)
    root.wait_window()

    return choose_
