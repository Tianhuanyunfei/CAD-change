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
# 用于行拖动功能
dragging_item = None
# 用于列拖动功能
dragging_column = None
dragging_column_index = -1
column_drag_start_x = 0


def show_and_edit_csv(root):
    global current_entry, dragging_item, dragging_column, dragging_column_index, column_drag_start_x
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
    display_headers = ["行号"] + headers
    # 添加表格
    tree = ttk.Treeview(edit_window, columns=display_headers, show='headings')

    # 创建样式对象
    style = ttk.Style()
    # 尝试更换为clam主题
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
    x_scrollbar = ttk.Scrollbar(edit_window, orient="horizontal", command=tree.xview,
                                style="Custom.Horizontal.TScrollbar")
    x_scrollbar.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=x_scrollbar.set)

    # 填充内容
    for header in display_headers:
        if header == "行号":
            tree.heading(header, text=header)
            tree.column(header, width=50, stretch=tk.NO)
        else:
            tree.heading(header, text=header)
            tree.column(header, width=100, stretch=tk.YES)
    # 设置列号，从1开始
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
            status_var.set(f"第 {row_index + 1} 行 {display_headers[col_index]} 列已更新")

        current_entry.bind("<Return>", save_edit)
        current_entry.bind("<FocusOut>", save_edit)

    tree.bind("<Button-1>", edit_cell)

    def add_row():
        """在表格末尾添加新行"""
        # 创建一个与列数相同的空值列表（减去行号列）
        new_row = [''] * len(headers)
        # 将新行添加到数据列表
        data.append(new_row)
        # 获取新行的行号（数据列表的长度）
        row_number = len(data)
        # 在Treeview中插入新行
        tree.insert('', 'end', values=[row_number] + new_row)
        # 更新状态信息
        status_var.set(f"已添加新行 {row_number}")

    def delete_selected_row():
        """删除选中的行"""
        # 获取选中的项
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要删除的行")
            return
        # 获取选中项的索引
        for item in selected_item:
            row_index = tree.index(item)
            # 从数据列表中删除对应行
            if 0 <= row_index < len(data):
                data.pop(row_index)
                # 从Treeview中删除项
                tree.delete(item)
                # 更新行号
                update_row_numbers()
                status_var.set(f"已删除第 {row_index + 1} 行")
            else:
                messagebox.showerror("错误", "无效的行索引")

    def update_row_numbers():
        """更新所有行的行号"""
        for i, item in enumerate(tree.get_children(), start=1):
            values = list(tree.item(item, 'values'))
            values[0] = i  # 更新行号
            tree.item(item, values=values)

    # 行拖动功能相关函数
    def on_drag_start(event):
        global dragging_item
        item = tree.identify_row(event.y)
        if item:
            dragging_item = item
            tree.selection_set(item)

    def on_drag_motion(event):
        if not dragging_item:
            return

        # 获取鼠标位置对应的行
        y = event.y
        target_item = tree.identify_row(y)

        if target_item and target_item != dragging_item:
            # 获取当前拖动行和目标行的索引
            drag_index = tree.index(dragging_item)
            target_index = tree.index(target_item)

            # 从Treeview中移动行
            tree.move(dragging_item, '', target_index)

            # 更新数据列表中的位置
            data.insert(target_index, data.pop(drag_index))

            # 更新行号
            update_row_numbers()

            # 更新状态信息
            status_var.set(f"已移动行 {drag_index + 1} 到位置 {target_index + 1}")

    def on_drag_end(event):
        global dragging_item
        dragging_item = None

    # 绑定行拖动事件
    tree.bind("<Button-1>", lambda e: [edit_cell(e), on_drag_start(e)] if current_entry is None else on_drag_start(e))
    tree.bind("<B1-Motion>", on_drag_motion)
    tree.bind("<ButtonRelease-1>", on_drag_end)

    # 列拖动功能相关函数
    def on_column_drag_start(event):
        global dragging_column, dragging_column_index, column_drag_start_x
        region = tree.identify_region(event.x, event.y)
        if region == "heading":
            # 获取列标识符
            column_id = tree.identify_column(event.x)
            if column_id:
                # 修正列索引计算方式
                col_index = int(column_id[1:]) - 1  # 调整为实际数据中的索引
                if col_index > 0:  # 排除行号列
                    dragging_column = column_id
                    dragging_column_index = col_index
                    column_drag_start_x = event.x

                    # 高亮显示当前拖动的列头
                    style.configure("Treeview.Heading", background="#a6c9e2")

    def on_column_drag_motion(event):
        global dragging_column, dragging_column_index, column_drag_start_x
        if not dragging_column:
            return

        # 计算拖动距离
        delta_x = event.x - column_drag_start_x

        # 获取当前鼠标位置对应的列
        target_column_id = tree.identify_column(event.x)
        if not target_column_id:
            return

        # 修正目标列索引计算方式
        target_col_index = int(target_column_id[1:]) - 1

        # 确保不拖动行号列
        if target_col_index <= 0:
            return

        # 如果拖动超过半个列宽，交换列位置
        if abs(delta_x) > tree.column(dragging_column, "width") / 2 and target_col_index != dragging_column_index:
            # 交换列位置
            swap_columns(dragging_column_index, target_col_index)

            # 更新拖动列索引
            dragging_column_index = target_col_index
            dragging_column = f"#{target_col_index + 1}"  # 更新列ID
            column_drag_start_x = event.x

    def on_column_drag_end(event):
        global dragging_column
        dragging_column = None
        # 恢复列头背景颜色
        style.configure("Treeview.Heading", background="")

    def swap_columns(index1, index2):
        """交换两列的位置"""
        # 确保不交换行号列
        if index1 <= 0 or index2 <= 0:
            return

        # 调整索引以匹配headers列表（排除行号列）
        header_index1 = index1 - 1
        header_index2 = index2 - 1

        # 交换headers列表中的列名
        headers[header_index1], headers[header_index2] = headers[header_index2], headers[header_index1]

        # 交换display_headers列表中的列名
        display_headers[index1], display_headers[index2] = display_headers[index2], display_headers[index1]

        # 更新表格结构
        tree["columns"] = display_headers

        # 重新配置所有列
        for i, header in enumerate(display_headers):
            if header == "行号":
                tree.heading(header, text=header)
                tree.column(header, width=50, stretch=tk.NO)
            else:
                tree.heading(header, text=header)
                tree.column(header, width=100, stretch=tk.YES)

        # 更新每一行的数据
        for i, item in enumerate(tree.get_children()):
            old_values = list(tree.item(item, "values"))
            # 交换列值（排除行号列）
            old_values[index1], old_values[index2] = old_values[index2], old_values[index1]
            tree.item(item, values=old_values)

            # 同时更新data中的数据
            if i < len(data):
                data[i][header_index1], data[i][header_index2] = data[i][header_index2], data[i][header_index1]

        status_var.set(f"已交换列 {display_headers[index1]} 和 {display_headers[index2]} 的位置")

    # 绑定列拖动事件
    tree.bind("<Button-1>", lambda e: [on_column_drag_start(e), edit_cell(e), on_drag_start(e)]
    if current_entry is None else [on_column_drag_start(e), on_drag_start(e)], add="+")
    tree.bind("<B1-Motion>", lambda e: [on_column_drag_motion(e), on_drag_motion(e)], add="+")
    tree.bind("<ButtonRelease-1>", lambda e: [on_column_drag_end(e), on_drag_end(e)], add="+")

    def save_csv(close_window=False):
        try:
            # 以写入模式打开 CSV 文件，指定编码为 UTF-8，并处理换行符
            with open(input_file, 'w', newline='', encoding='utf-8') as csvfile:
                # 创建一个 CSV 写入器对象
                writer = csv.writer(csvfile)
                # 写入原始表头（去除行号列）
                writer.writerow(headers)
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

    def add_column():
        """添加新列"""
        # 创建对话框获取新列名
        dialog = tk.Toplevel(edit_window)
        dialog.title("添加新列")
        dialog.geometry("400x250")
        dialog.transient(edit_window)
        dialog.grab_set()

        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(frame, text="列名:").pack(pady=(0, 10), anchor=tk.W)
        entry = tk.Entry(frame, width=40)
        entry.pack(fill=tk.X, pady=(0, 20))
        entry.focus()

        def confirm():
            new_col_name = entry.get().strip()
            if not new_col_name:
                messagebox.showerror("错误", "列名不能为空")
                return

            # 检查列名是否已存在
            if new_col_name in headers:
                messagebox.showerror("错误", f"列名 '{new_col_name}' 已存在")
                return

            # 添加到实际数据的表头
            headers.append(new_col_name)
            # 添加到显示的表头
            display_headers.append(new_col_name)

            # 更新表格结构
            tree["columns"] = display_headers
            for header in display_headers:
                if header == "行号":
                    tree.heading(header, text=header)
                    tree.column(header, width=50, stretch=tk.NO)
                else:
                    tree.heading(header, text=header)
                    tree.column(header, width=100, stretch=tk.YES)

            # 为每一行添加新列的空值
            for i, item in enumerate(tree.get_children()):
                values = list(tree.item(item, "values"))
                values.append("")
                tree.item(item, values=values)
                data[i].append("")

            status_var.set(f"已添加列 '{new_col_name}'")
            dialog.destroy()

        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        btn_confirm = tk.Button(button_frame, text="确认", command=confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=(5, 0))

        btn_cancel = tk.Button(button_frame, text="取消", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=(0, 5))

    def delete_column():
        """删除选中的列"""
        if len(headers) == 0:
            messagebox.showinfo("提示", "没有可删除的列")
            return

        # 创建对话框选择要删除的列
        dialog = tk.Toplevel(edit_window)
        dialog.title("删除列")
        dialog.geometry("400x350")
        dialog.transient(edit_window)
        dialog.grab_set()

        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(frame, text="选择要删除的列:").pack(pady=(0, 10), anchor=tk.W)

        # 创建列选择列表
        listbox = tk.Listbox(frame, width=40, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        for col in headers:
            listbox.insert(tk.END, col)
        if headers:
            listbox.select_set(0)

        def confirm():
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请选择要删除的列")
                return

            col_index = selection[0]
            col_name = headers[col_index]

            # 确认对话框
            if messagebox.askyesno("确认", f"确定要删除列 '{col_name}' 吗？"):
                # 从表头中删除
                headers.pop(col_index)
                display_headers.pop(col_index + 1)  # +1 是因为 display_headers 有行号列

                # 更新表格结构
                tree["columns"] = display_headers
                for header in display_headers:
                    if header == "行号":
                        tree.heading(header, text=header)
                        tree.column(header, width=50, stretch=tk.NO)
                    else:
                        tree.heading(header, text=header)
                        tree.column(header, width=100, stretch=tk.YES)

                # 从每一行中删除对应列的值
                for i, item in enumerate(tree.get_children()):
                    values = list(tree.item(item, "values"))
                    values.pop(col_index + 1)  # +1 是因为 values 有行号列
                    tree.item(item, values=values)
                    data[i].pop(col_index)

                status_var.set(f"已删除列 '{col_name}'")
                dialog.destroy()

        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        btn_confirm = tk.Button(button_frame, text="确认", command=confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=(5, 0))

        btn_cancel = tk.Button(button_frame, text="取消", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=(0, 5))

    def rename_column():
        """重命名列"""
        if len(headers) == 0:
            messagebox.showinfo("提示", "没有可重命名的列")
            return

        # 创建对话框选择要重命名的列
        dialog = tk.Toplevel(edit_window)
        dialog.title("重命名列")
        dialog.geometry("500x400")
        dialog.transient(edit_window)
        dialog.grab_set()

        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(frame, text="选择要重命名的列:").pack(pady=(0, 10), anchor=tk.W)

        # 创建列选择列表
        listbox = tk.Listbox(frame, width=45, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        for col in headers:
            listbox.insert(tk.END, col)
        if headers:
            listbox.select_set(0)

        tk.Label(frame, text="新列名:").pack(pady=(0, 10), anchor=tk.W)
        new_name_entry = tk.Entry(frame, width=45)
        new_name_entry.pack(fill=tk.X, pady=(0, 20))

        def confirm():
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请选择要重命名的列")
                return

            col_index = selection[0]
            old_name = headers[col_index]
            new_name = new_name_entry.get().strip()

            if not new_name:
                messagebox.showerror("错误", "新列名不能为空")
                return

            # 检查新列名是否已存在
            if new_name in headers:
                messagebox.showerror("错误", f"列名 '{new_name}' 已存在")
                return

            # 获取Treeview中的列标识符
            tree_column_id = display_headers[col_index + 1]  # +1 是因为 display_headers 有行号列

            # 更新列名
            headers[col_index] = new_name
            display_headers[col_index + 1] = new_name  # +1 是因为 display_headers 有行号列

            # 更新表格头部显示
            tree.heading(tree_column_id, text=new_name)

            status_var.set(f"已将列 '{old_name}' 重命名为 '{new_name}'")
            dialog.destroy()

        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        btn_confirm = tk.Button(button_frame, text="确认", command=confirm)
        btn_confirm.pack(side=tk.RIGHT, padx=(5, 0))

        btn_cancel = tk.Button(button_frame, text="取消", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=(0, 5))

    button_frame = tk.Frame(edit_window)
    button_frame.pack(side='bottom', pady=10)

    # 添加行按钮
    add_button = tk.Button(button_frame, text="添加行", command=add_row)
    add_button.pack(side='left', padx=5)

    # 删除行按钮
    delete_button = tk.Button(button_frame, text="删除选中行", command=delete_selected_row)
    delete_button.pack(side='left', padx=5)

    # 上移按钮
    move_up_button = tk.Button(button_frame, text="上移", command=lambda: move_row(-1))
    move_up_button.pack(side='left', padx=5)

    # 下移按钮
    move_down_button = tk.Button(button_frame, text="下移", command=lambda: move_row(1))
    move_down_button.pack(side='left', padx=5)

    # 添加列按钮
    add_col_button = tk.Button(button_frame, text="添加列", command=add_column)
    add_col_button.pack(side='left', padx=5)

    # 删除列按钮
    delete_col_button = tk.Button(button_frame, text="删除列", command=delete_column)
    delete_col_button.pack(side='left', padx=5)

    # 重命名列按钮
    rename_col_button = tk.Button(button_frame, text="重命名列", command=rename_column)
    rename_col_button.pack(side='left', padx=5)

    # 应用按钮
    apply_button = tk.Button(button_frame, text="应用", command=lambda: save_csv(close_window=False))
    apply_button.pack(side='left', padx=5)

    # 保存按钮
    save_button = tk.Button(button_frame, text="保存并关闭", command=lambda: save_csv(close_window=True))
    save_button.pack(side='left', padx=5)

    # 关闭按钮
    shut_button = tk.Button(button_frame, text="关闭", command=lambda: edit_window.destroy())
    shut_button.pack(side='left', padx=5)

    tree.pack(side='top', fill='both', expand=True)

    def move_row(direction):
        """移动选中的行上移或下移"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要移动的行")
            return

        item = selected[0]
        current_index = tree.index(item)
        new_index = current_index + direction

        # 检查边界条件
        if new_index < 0 or new_index >= len(tree.get_children()):
            return

        # 移动行
        tree.move(item, '', new_index)

        # 更新数据列表
        data.insert(new_index, data.pop(current_index))

        # 更新行号
        update_row_numbers()

        # 更新状态信息
        status_var.set(f"已将行 {current_index + 1} 移动到位置 {new_index + 1}")


def create_new_csv(root):
    """创建新的CSV文件"""
    # 打开文件对话框，获取保存位置和文件名
    file_path = filedialog.asksaveasfilename(
        title="保存新CSV文件",
        defaultextension=".csv",
        filetypes=[("CSV 文件", "*.csv")]
    )

    if not file_path:
        return  # 用户取消了操作

    try:
        # 创建一个设置列名的对话框
        dialog = tk.Toplevel(root)
        dialog.title("设置列名")
        dialog.geometry("500x400")
        dialog.transient(root)
        dialog.grab_set()

        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # 创建一个文本框用于输入列名
        tk.Label(frame, text="列名（多个列名请用逗号分隔）:").pack(pady=(0, 10), anchor=tk.W)
        column_text = tk.Text(frame, height=10, width=50)
        column_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        column_text.insert("1.0", "列1,列2,列3")  # 默认提供一些示例列名

        # 创建确认和取消按钮
        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        def confirm_columns():
            # 获取用户输入的列名
            column_text_content = column_text.get("1.0", "end-1c")
            # 按逗号分割列名
            columns = [col.strip() for col in column_text_content.split(',') if col.strip()]

            if not columns:
                messagebox.showerror("错误", "至少需要一个列名")
                return

            try:
                # 创建并写入新的CSV文件
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)  # 写入列名

                messagebox.showinfo("成功", f"新CSV文件 {file_path} 已创建")
                logging.info(f"新CSV文件 {file_path} 已创建，列名: {', '.join(columns)}")

                # 关闭对话框
                dialog.destroy()

                # 自动打开新创建的CSV文件进行编辑
                show_and_edit_csv(root)

            except Exception as e:
                messagebox.showerror("错误", f"创建文件时发生错误: {str(e)}")
                logging.error(f"创建文件 {file_path} 时发生错误: {str(e)}")

        btn_confirm = tk.Button(button_frame, text="确认", command=confirm_columns)
        btn_confirm.pack(side=tk.RIGHT, padx=(5, 0))

        btn_cancel = tk.Button(button_frame, text="取消", command=dialog.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=(0, 5))

    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {str(e)}")
        logging.error(f"创建新CSV文件对话框时发生错误: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV 文件编辑器")
    root.geometry("400x200")

    # 创建一个按钮，点击时调用 show_and_edit_csv 函数
    open_button = tk.Button(root, text="打开 CSV 文件", command=lambda: show_and_edit_csv(root))
    open_button.pack(pady=10)

    # 创建新CSV文件的按钮
    new_button = tk.Button(root, text="创建新 CSV 文件", command=lambda: create_new_csv(root))
    new_button.pack(pady=10)

    root.mainloop()