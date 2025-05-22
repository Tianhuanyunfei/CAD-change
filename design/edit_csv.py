import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from tkinter import ttk

# 配置日志记录
logging.basicConfig(filename='dxf_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 用于跟踪当前正在编辑的输入框
current_entry = None


def show_and_edit_csv(root):
    global current_entry
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
    edit_window.state('zoomed')

    status_var = tk.StringVar()
    status_label = tk.Label(edit_window, textvariable=status_var, anchor='w')
    status_label.pack(side='bottom', fill='x')

    # 添加行号列
    headers = ["行号"] + headers
    # 添加表格
    tree = ttk.Treeview(edit_window, columns=headers, show='headings')

    # 创建样式对象
    style = ttk.Style()
    # 尝试更换为 clam 主题
    style.theme_use('clam')
    # 设置垂直滚动条宽度
    style.configure("Custom.Vertical.TScrollbar", thickness=20)
    # 设置水平滚动条宽度
    style.configure("Custom.Horizontal.TScrollbar", thickness=20)

    # 添加垂直滚动条
    y_scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=tree.yview, style="Custom.Vertical.TScrollbar")
    y_scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=y_scrollbar.set)

    # 添加水平滚动条
    x_scrollbar = ttk.Scrollbar(edit_window, orient="horizontal", command=tree.xview, style="Custom.Horizontal.TScrollbar")
    x_scrollbar.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=x_scrollbar.set)

    # 填充内容
    for header in headers:
        if header == "行号":
            tree.heading(header, text=header)
            tree.column(header, width=50, stretch=tk.NO)
        else:
            tree.heading(header, text=header)
            tree.column(header, width=10, stretch=tk.YES)
    # 设置列号，从2开始
    for i, row in enumerate(data, start=1):
        tree.insert('', 'end', values=[i] + row)

    def edit_cell(event):
        global current_entry
        # 如果有正在编辑的输入框，先销毁它
        if current_entry:
            current_entry.destroy()
            current_entry = None

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

        current_entry = tk.Entry(edit_window)
        current_entry.place(x=x, y=y, width=width, height=height)
        current_entry.insert(0, value)
        current_entry.focus()

        def save_edit(event=None):
            global current_entry
            new_value = current_entry.get()
            values = list(tree.item(item, 'values'))
            values[col_index] = new_value
            tree.item(item, values=values)
            current_entry.destroy()
            current_entry = None
            row_index = int(tree.index(item))
            data[row_index][col_index - 1] = new_value
            status_var.set(f"第 {row_index + 1} 行 {headers[col_index]} 列已更新")

        current_entry.bind("<Return>", save_edit)
        current_entry.bind("<FocusOut>", save_edit)

    tree.bind("<Button-1>", edit_cell)

    def save_csv(close_window=False):
        try:
            # 以写入模式打开 CSV 文件，指定编码为 UTF-8，并处理换行符
            with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
                # 创建一个 CSV 写入器对象
                writer = csv.writer(csvfile)
                # 写入原始表头（去除行号列）
                writer.writerow(headers[1:])
                # 遍历数据列表，逐行写入 CSV 文件
                for row in data:
                    writer.writerow(row)
            # 显示保存成功的消息框
            messagebox.showinfo("成功", f"文件 {input_file} 已保存")
            # 记录保存成功的日志信息
            logging.info(f"文件 {input_file} 已成功保存")
            if close_window:
                # 关闭编辑窗口
                edit_window.destroy()
        except PermissionError:
            # 处理没有权限保存文件的异常
            messagebox.showerror("错误", f"没有权限保存文件 {input_file}")
            logging.error(f"没有权限保存文件 {input_file}")
        except Exception as e:
            # 处理其他未知异常
            messagebox.showerror("错误", f"保存文件 {input_file} 时发生错误: {str(e)}")
            logging.error(f"保存文件 {input_file} 时发生错误: {str(e)}")

    button_frame = tk.Frame(edit_window)
    button_frame.pack(side='bottom', pady=10)

    apply_button = tk.Button(button_frame, text="应用", command=lambda: save_csv(close_window=False))
    apply_button.pack(side='left', padx=10)

    save_button = tk.Button(button_frame, text="保存并关闭", command=lambda: save_csv(close_window=True))
    save_button.pack(side='left', padx=10)

    shut_button = tk.Button(button_frame, text="关闭", command=lambda: edit_window.destroy())
    shut_button.pack(side='left', padx=10)

    tree.pack(side='top', fill='both', expand=True)
