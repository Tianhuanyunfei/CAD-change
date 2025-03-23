import tkinter as tk
from tkinter import filedialog
from dxf_to_csv import dxf_to_csv
from csv_to_dxf import csv_to_dxf
from edit_csv import show_and_edit_csv

# 创建主窗口
root = tk.Tk()
root.title("DXF 和 CSV 转换工具")
root.geometry("300x200")

# DXF 转 CSV 按钮
dxf_to_csv_button = tk.Button(root, text="DXF 转 CSV", command=lambda: dxf_to_csv(
    filedialog.askopenfilename(title="选择 DXF 文件", filetypes=[("DXF 文件", "*.dxf")]),
    filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
))
dxf_to_csv_button.pack(pady=10)

# CSV 转 DXF 按钮
csv_to_dxf_button = tk.Button(root, text="CSV 转 DXF", command=lambda: csv_to_dxf(
    filedialog.askopenfilename(title="选择 CSV 文件", filetypes=[("CSV 文件", "*.csv")]),
    filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF 文件", "*.dxf")])
))
csv_to_dxf_button.pack(pady=10)

# 显示并编辑 CSV 文件按钮
edit_csv_button = tk.Button(root, text="显示并编辑 CSV 文件", command=lambda: show_and_edit_csv(root))
edit_csv_button.pack(pady=10)

# 运行主循环
root.mainloop()