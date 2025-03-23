import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from tkinter import ttk

# 配置日志记录
logging.basicConfig(filename='dxf_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def show_and_edit_csv(root):
    input_file = filedialog.askopenfilename(title="选择 CSV 文件", filetypes=[("CSV 文件", "*.csv")])
    if not input_file:
        return
    try:
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            data = list(reader)
    except FileNotFoundError:
        messagebox.showerror("错误", f"文件 {input_file} 未找到")
        logging.error(f"文件 {input_file} 未找到")
        return
    except Exception as e:
        messagebox.showerror("错误", f"读取文件 {input_file} 时发生错误: {str(e)}")
        logging.error(f"读取文件 {input_file} 时发生错误: {str(e)}")
        return

    edit_window = tk.Toplevel(root)
    edit_window.title(f"编辑 {input_file}")
    edit_window.geometry("800x600")

    status_var = tk.StringVar()
    status_label = tk.Label(edit_window, textvariable=status_var, anchor='w')
    status_label.pack(side='bottom', fill='x')

    # 添加行号列
    headers = ["行号"] + headers
    tree = ttk.Treeview(edit_window, columns=headers, show='headings')
    for header in headers:
        if header == "行号":
            tree.heading(header, text=header)
            tree.column(header, width=50, stretch=tk.NO)
        else:
            tree.heading(header, text=header)
            tree.column(header, width=100, stretch=tk.YES)

    for i, row in enumerate(data, start=2):
        tree.insert('', 'end', values=[i] + row)

    def edit_cell(event):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column[1:]) - 1
        if col_index == 0:  # 行号列不可编辑
            return
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        x, y, width, height = bbox
        value = tree.item(item, 'values')[col_index]

        entry = tk.Entry(edit_window)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            values = list(tree.item(item, 'values'))
            values[col_index] = new_value
            tree.item(item, values=values)
            entry.destroy()
            row_index = int(tree.index(item))
            data[row_index][col_index - 1] = new_value
            status_var.set(f"第 {row_index + 2} 行 {headers[col_index]} 列已更新")

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    tree.bind("<Button-1>", edit_cell)

    def save_csv():
        try:
            with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers[1:])  # 写入原始表头
                for row in data:
                    writer.writerow(row)
            messagebox.showinfo("成功", f"文件 {input_file} 已保存")
            logging.info(f"文件 {input_file} 已成功保存")
            edit_window.destroy()
        except PermissionError:
            messagebox.showerror("错误", f"没有权限保存文件 {input_file}")
            logging.error(f"没有权限保存文件 {input_file}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件 {input_file} 时发生错误: {str(e)}")
            logging.error(f"保存文件 {input_file} 时发生错误: {str(e)}")

    save_button = tk.Button(edit_window, text="保存", command=save_csv)
    save_button.pack(side='bottom', pady=10)

    tree.pack(side='top', fill='both', expand=True)