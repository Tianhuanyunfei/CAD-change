import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import dxf_to_csv
import csv_to_dxf
from edit_csv import show_and_edit_csv
from brb_drawing import brb_drawing


class CADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("阻尼器设计软件")
        self.root.geometry("400x500")  # 增加窗口高度以适应新布局
        self.setup_ui()

    def setup_ui(self):
        """设置主界面UI"""
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 主功能区域（BRB和粘滞产品设计）
        main_functions_frame = tk.LabelFrame(main_frame, text="主功能", font=("SimHei", 12, "bold"))
        main_functions_frame.pack(fill=tk.X, pady=10, ipady=10)

        # BRB产品设计按钮
        brb_btn = tk.Button(main_functions_frame, text="BRB产品设计",
                            command=self.open_brb_design,
                            font=("SimHei", 12),
                            bg="#2196F3", fg="white",
                            height=2)
        brb_btn.pack(fill=tk.X, padx=10, pady=5)

        # 粘滞产品设计按钮
        viscous_btn = tk.Button(main_functions_frame, text="粘滞产品设计",
                                command=self.product_design2,
                                font=("SimHei", 12),
                                bg="#2196F3", fg="white",
                                height=2)
        viscous_btn.pack(fill=tk.X, padx=10, pady=5)

        # 分隔线
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)

        # 辅助功能区域（DXF/CSV转换和CSV编辑）
        auxiliary_functions_frame = tk.LabelFrame(main_frame, text="辅助功能", font=("SimHei", 10, "bold"))
        auxiliary_functions_frame.pack(fill=tk.X, pady=10, expand=True)

        # DXF转CSV按钮
        dxf_to_csv_btn = tk.Button(auxiliary_functions_frame, text="DXF 转 CSV",
                                   command=self.convert_dxf_to_csv,
                                   font=("SimHei", 10))
        dxf_to_csv_btn.pack(fill=tk.X, padx=10, pady=3)

        # CSV转DXF按钮
        csv_to_dxf_btn = tk.Button(auxiliary_functions_frame, text="CSV 转 DXF",
                                   command=self.convert_csv_to_dxf,
                                   font=("SimHei", 10))
        csv_to_dxf_btn.pack(fill=tk.X, padx=10, pady=3)

        # 显示并编辑CSV文件按钮
        edit_csv_btn = tk.Button(auxiliary_functions_frame, text="显示并编辑 CSV 文件",
                                 command=self.show_and_edit_csv,
                                 font=("SimHei", 10))
        edit_csv_btn.pack(fill=tk.X, padx=10, pady=3)

    def convert_dxf_to_csv(self):
        """将DXF文件转换为CSV文件"""
        input_file = filedialog.askopenfilename(filetypes=[("DXF 文件", "*.dxf")])
        if input_file:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV 文件", "*.csv")]
            )
            if output_file:
                try:
                    dxf_to_csv.dxf_to_csv(input_file, output_file)
                    messagebox.showinfo("成功", "DXF转CSV成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"转换失败: {str(e)}")

    def convert_csv_to_dxf(self):
        """将CSV文件转换为DXF文件"""
        input_file = filedialog.askopenfilename(filetypes=[("CSV 文件", "*.csv")])
        if input_file:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".dxf",
                filetypes=[("DXF 文件", "*.dxf")]
            )
            if output_file:
                try:
                    csv_to_dxf.csv_to_dxf(input_file, output_file)
                    messagebox.showinfo("成功", "CSV转DXF成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"转换失败: {str(e)}")

    def show_and_edit_csv(self):
        """显示并编辑CSV文件"""
        show_and_edit_csv(self.root)

    def open_brb_design(self):
        """打开BRB产品设计窗口"""
        design_window = tk.Toplevel(self.root)
        design_window.title("BRB产品设计")
        design_window.geometry("600x700")
        design_window.resizable(True, True)

        # 设置窗口图标和样式
        if hasattr(self.root, 'iconbitmap'):
            try:
                design_window.iconbitmap(self.root.iconbitmap())
            except:
                pass

        # 创建设计表单
        DesignForm(design_window)

    def product_design2(self):
        """打开粘滞产品设计窗口"""
        viscous_window = tk.Toplevel(self.root)
        viscous_window.title("粘滞产品设计")
        viscous_window.geometry("600x700")
        viscous_window.resizable(True, True)

        # 设置窗口图标和样式
        if hasattr(self.root, 'iconbitmap'):
            try:
                viscous_window.iconbitmap(self.root.iconbitmap())
            except:
                pass

        # 创建设计表单
        ViscousDesignForm(viscous_window)


class DesignForm:
    """BRB产品设计表单类"""

    def __init__(self, parent):
        self.parent = parent
        self.length_quantity_rows = []

        # 创建主框架
        main_frame = tk.Frame(parent, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.content_frame = tk.Frame(canvas)

        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建设计表单
        self.create_form()

    def create_form(self):
        """创建设计表单UI"""
        # 标题
        title_label = tk.Label(self.content_frame, text="BRB产品设计参数",
                               font=("SimHei", 14, "bold"))
        title_label.pack(pady=10)

        # 模板选择
        template_frame = tk.Frame(self.content_frame)
        template_frame.pack(fill=tk.X, pady=5)

        tk.Label(template_frame, text="请选择模版:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)

        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                      width=15, font=("SimHei", 10))
        template_combo['values'] = ('王一', '十一', '王工')
        template_combo.current(0)
        template_combo.pack(side=tk.LEFT, padx=5)

        # 基本参数
        params_frame = tk.LabelFrame(self.content_frame, text="基本参数", font=("SimHei", 10))
        params_frame.pack(fill=tk.X, pady=10)

        self.param_entries = {}
        param_labels = [
            "项目名称", "设计力KN", "截面宽度mm",
            "截面高度mm", "板材厚度mm", "芯板焊缝高度mm",
            "方管宽度mm"
        ]

        for label_text in param_labels:
            frame = tk.Frame(params_frame)
            frame.pack(fill=tk.X, pady=3)

            tk.Label(frame, text=f"{label_text}:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(frame, font=("SimHei", 10))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            self.param_entries[label_text] = entry

        # 长度-数量表格
        table_frame = tk.LabelFrame(self.content_frame, text="长度-数量表格", font=("SimHei", 10))
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 表头
        header_frame = tk.Frame(table_frame)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame, text="产品长度(mm)", font=("SimHei", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="数量", font=("SimHei", 10, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="操作", font=("SimHei", 10, "bold"), width=5).pack(side=tk.LEFT, padx=5)

        # 表格内容框架
        self.table_content_frame = tk.Frame(table_frame)
        self.table_content_frame.pack(fill=tk.BOTH, expand=True)

        # 添加第一行
        self.add_row()

        # 添加行按钮
        add_btn_frame = tk.Frame(table_frame)
        add_btn_frame.pack(fill=tk.X, pady=5)

        add_btn = tk.Button(add_btn_frame, text="添加行", command=self.add_row,
                            font=("SimHei", 10))
        add_btn.pack(side=tk.RIGHT, padx=5)

        # 生成按钮
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        generate_btn = tk.Button(btn_frame, text="生成图纸",
                                 command=self.generate_drawing,
                                 font=("SimHei", 12, "bold"),
                                 bg="#4CAF50", fg="white",
                                 height=1, width=15)
        generate_btn.pack(side=tk.RIGHT, padx=10)

    def add_row(self):
        """添加长度-数量行"""
        row_frame = tk.Frame(self.table_content_frame)
        row_frame.pack(fill=tk.X, pady=2)

        length_entry = tk.Entry(row_frame, width=20, font=("SimHei", 10))
        length_entry.pack(side=tk.LEFT, padx=5)

        quantity_entry = tk.Entry(row_frame, width=10, font=("SimHei", 10))
        quantity_entry.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(row_frame, text="删除", command=lambda rf=row_frame: self.remove_row(rf),
                               width=5, font=("SimHei", 10))
        delete_btn.pack(side=tk.LEFT, padx=5)

        self.length_quantity_rows.append((row_frame, length_entry, quantity_entry))

        # 设置焦点到新添加的长度输入框
        length_entry.focus_set()

    def remove_row(self, row_frame):
        """删除指定行"""
        for i, (frame, _, _) in enumerate(self.length_quantity_rows):
            if frame == row_frame:
                del self.length_quantity_rows[i]
                frame.destroy()
                break

        # 如果没有行了，添加一个空行
        if not self.length_quantity_rows:
            self.add_row()

    def get_form_data(self):
        """获取表单数据"""
        data = {
            "template": self.template_var.get(),
            "parameters": {label: entry.get() for label, entry in self.param_entries.items()},
            "length_quantity": []
        }

        for _, length_entry, quantity_entry in self.length_quantity_rows:
            length = length_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if length and quantity:
                try:
                    data["length_quantity"].append((int(length), int(quantity)))
                except ValueError:
                    pass

        return data

    def generate_drawing(self):
        """生成图纸"""
        data = self.get_form_data()

        # 验证必要字段
        if not data["parameters"]["项目名称"]:
            messagebox.showerror("错误", "请输入项目名称")
            return

        if not data["length_quantity"]:
            messagebox.showerror("错误", "请至少添加一组长度-数量数据")
            return

        # 准备参数
        data_table = [{
            "template": data["template"],
            "project_name": data["parameters"]["项目名称"],
            "width": data["parameters"]["截面宽度mm"],  # 截面宽度
            "height": data["parameters"]["截面高度mm"],  # 截面高度
            "thickness": data["parameters"]["板材厚度mm"],  # 板厚
            "force": data["parameters"]["设计力KN"],  # 力
            "tube_width": data["parameters"]["方管宽度mm"],  # 方管宽度
            "weld": data["parameters"]["芯板焊缝高度mm"],  # 焊缝
            "length_quantity": data["length_quantity"]  # 添加长度-数量表格
        }]
        """params = [
            data["template"],
            data["parameters"]["项目名称"],
            data["parameters"]["截面宽度mm"],
            data["parameters"]["截面高度mm"],
            data["parameters"]["板材厚度mm"],
            data["parameters"]["设计力KN"],
            data["parameters"]["方管宽度mm"],
            data["parameters"]["芯板焊缝高度mm"],
            data["length_quantity"]
        ]"""
        print(data_table)

        generate_drawing(data_table)

class ViscousDesignForm:
    """粘滞产品设计表单类"""

    def __init__(self, parent):
        self.parent = parent
        self.length_quantity_rows = []

        # 创建主框架
        main_frame = tk.Frame(parent, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.content_frame = tk.Frame(canvas)

        self.content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建设计表单
        self.create_form()

    def create_form(self):
        """创建设计表单UI"""
        # 标题
        title_label = tk.Label(self.content_frame, text="粘滞产品设计参数",
                               font=("SimHei", 14, "bold"))
        title_label.pack(pady=10)

        # 模板选择
        template_frame = tk.Frame(self.content_frame)
        template_frame.pack(fill=tk.X, pady=5)

        tk.Label(template_frame, text="请选择模版:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)

        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                      width=15, font=("SimHei", 10))
        template_combo['values'] = ('粘滞模版1', '粘滞模版2', '粘滞模版3')
        template_combo.current(0)
        template_combo.pack(side=tk.LEFT, padx=5)

        # 基本参数
        params_frame = tk.LabelFrame(self.content_frame, text="基本参数", font=("SimHei", 10))
        params_frame.pack(fill=tk.X, pady=10)

        self.param_entries = {}
        param_labels = [
            "项目名称", "设计力KN", "油缸直径mm",
            "活塞行程mm", "阻尼系数", "工作介质",
            "安装形式"
        ]

        for label_text in param_labels:
            frame = tk.Frame(params_frame)
            frame.pack(fill=tk.X, pady=3)

            tk.Label(frame, text=f"{label_text}:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
            entry = tk.Entry(frame, font=("SimHei", 10))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            self.param_entries[label_text] = entry

        # 规格-数量表格
        table_frame = tk.LabelFrame(self.content_frame, text="规格-数量表格", font=("SimHei", 10))
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 表头
        header_frame = tk.Frame(table_frame)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame, text="规格型号", font=("SimHei", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="数量", font=("SimHei", 10, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="操作", font=("SimHei", 10, "bold"), width=5).pack(side=tk.LEFT, padx=5)

        # 表格内容框架
        self.table_content_frame = tk.Frame(table_frame)
        self.table_content_frame.pack(fill=tk.BOTH, expand=True)

        # 添加第一行
        self.add_row()

        # 添加行按钮
        add_btn_frame = tk.Frame(table_frame)
        add_btn_frame.pack(fill=tk.X, pady=5)

        add_btn = tk.Button(add_btn_frame, text="添加行", command=self.add_row,
                            font=("SimHei", 10))
        add_btn.pack(side=tk.RIGHT, padx=5)

        # 生成按钮
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        generate_btn = tk.Button(btn_frame, text="生成图纸",
                                 command=self.generate_drawing,
                                 font=("SimHei", 12, "bold"),
                                 bg="#4CAF50", fg="white",
                                 height=1, width=15)
        generate_btn.pack(side=tk.RIGHT, padx=10)

    def add_row(self):
        """添加规格-数量行"""
        row_frame = tk.Frame(self.table_content_frame)
        row_frame.pack(fill=tk.X, pady=2)

        spec_entry = tk.Entry(row_frame, width=20, font=("SimHei", 10))
        spec_entry.pack(side=tk.LEFT, padx=5)

        quantity_entry = tk.Entry(row_frame, width=10, font=("SimHei", 10))
        quantity_entry.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(row_frame, text="删除", command=lambda rf=row_frame: self.remove_row(rf),
                               width=5, font=("SimHei", 10))
        delete_btn.pack(side=tk.LEFT, padx=5)

        self.length_quantity_rows.append((row_frame, spec_entry, quantity_entry))

        # 设置焦点到新添加的规格输入框
        spec_entry.focus_set()

    def remove_row(self, row_frame):
        """删除指定行"""
        for i, (frame, _, _) in enumerate(self.length_quantity_rows):
            if frame == row_frame:
                del self.length_quantity_rows[i]
                frame.destroy()
                break

        # 如果没有行了，添加一个空行
        if not self.length_quantity_rows:
            self.add_row()

    def get_form_data(self):
        """获取表单数据"""
        data = {
            "template": self.template_var.get(),
            "parameters": {label: entry.get() for label, entry in self.param_entries.items()},
            "spec_quantity": []
        }

        for _, spec_entry, quantity_entry in self.length_quantity_rows:
            spec = spec_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if spec and quantity:
                data["spec_quantity"].append((spec, int(quantity)))

        return data

    def generate_drawing(self):
        """生成图纸"""
        data = self.get_form_data()

        # 验证必要字段
        if not data["parameters"]["项目名称"]:
            messagebox.showerror("错误", "请输入项目名称")
            return

        if not data["spec_quantity"]:
            messagebox.showerror("错误", "请至少添加一组规格-数量数据")
            return

        # 准备参数
        params = [
            data["template"],
            data["parameters"]["项目名称"],
            data["parameters"]["设计力KN"],
            data["parameters"]["油缸直径mm"],
            data["parameters"]["活塞行程mm"],
            data["parameters"]["阻尼系数"],
            data["parameters"]["工作介质"],
            data["parameters"]["安装形式"],
            data["spec_quantity"]
        ]

        try:
            # 调用生成图纸函数
            # 注意：这里假设存在一个 generate_viscous_drawing 函数
            # 如果没有，请替换为实际的函数调用
            print(params)
            brb_drawing(*params)
            messagebox.showinfo("成功", "粘滞产品图纸生成成功！")
        except Exception as e:
            messagebox.showerror("错误", f"图纸生成失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()

    # 确保中文显示正常
    try:
        root.iconbitmap("app.ico")  # 如果有图标文件
    except:
        pass

    app = CADApp(root)
    root.mainloop()

# 测试
if __name__ == "__main__":
    main()