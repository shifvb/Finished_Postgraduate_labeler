import sys
import tkinter as tk
from tkinter import messagebox


def add_menubar(app) -> None:
    menubar = tk.Menu(app.root)

    # "File" menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=file_menu_exit_callback)
    menubar.add_cascade(label="File", menu=file_menu)

    # "Language" menu
    language_menu = tk.Menu(menubar, tearoff=0)
    language_menu.add_radiobutton(label="English", command=lambda: app.i18n.to_language('en_US'))
    language_menu.add_radiobutton(label="Chinese", command=lambda: app.i18n.to_language('zh_CN'))
    menubar.add_cascade(label="Language", menu=language_menu)

    # "Help" menu
    help_menu = tk.Menu(menubar, tearoff=0)

    help_menu.add_command(label="Help", command=_help_menu_help_callback)
    help_menu.add_separator()
    help_menu.add_command(label="About", command=_help_menu_about_callback)
    menubar.add_cascade(label="Help", menu=help_menu)

    # add menubar to the window
    app.root.config(menu=menubar)


def file_menu_exit_callback():
    _message = "Do you really want to quit?\nAll unsaved progress will be lost."
    _result = messagebox.askyesno("Exit", message=_message)
    if _result is True:
        sys.exit(0)


def _help_menu_help_callback():
    _message = """1. Select a Directory of images in bottom control panel
2. Click Load
3. The first image in the directory should load, along with existing label if any.
4. Select a Class label to be used for next bounding box, in class-control panel
5. After the image is loaded, press x key, or mouse click to draw bounding boxes over the image
6. Click Save in the File Navigation panel in bottom, to save the bounding boxes
7. Labels are saved in folder named LabelData in same directory as the images
8. Can use Left/Right arrows for navigating prev/next images
Note: Default is KITTI format"""
    messagebox.showinfo(title="Help Message", message=_message)


def _help_menu_about_callback():
    _message = """original code from:
    https://github.com/prabindh/euclid
modified by:
    shifvb(shifvb@gmail.com)"""
    messagebox.showinfo(title="About", message=_message)
