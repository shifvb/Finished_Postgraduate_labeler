import tkinter as tk


def debug_mode(instance):
    instance.load_ct_dir_entry.config(textvariable=tk.StringVar(value=r"C:/Users/anonymous/Desktop/PT00998-2/4"))
    instance.load_pet_dir_entry.config(textvariable=tk.StringVar(value=r"C:/Users/anonymous/Desktop/PT00998-2/5"))
